from collections import Counter
from multiprocessing import Pool
from rdkit import rdBase
from rdkit.Chem import MolFromSmiles, MolToSmiles, MolToInchi, MolToInchiKey
from rdkit.Chem.MolStandardize import Standardizer
from typing import Union
import fire
import logging
import numpy as np
import pandas as pd
import requests
import tqdm


class StandardizeMolecule:
    def __init__(
        self,
        input: Union[str, pd.DataFrame],
        output: str = None,
        num_cpu: int = 1,
        limit_rows: int = None,
    ):
        """
        Initialize the class.

        :param input: Input file name (TSV/TXT/CSV) or a pandas dataframe containing the SMILES
        :param output: Output file name (optional)
        :param num_cpu: Number of CPUs to use
        :param limit_rows: Limit the number of rows to be processed (optional)

        """
        self.input = input
        self.output = output
        self.num_cpu = num_cpu
        self.limit_rows = limit_rows

        # Disable RDKit logging
        rdBase.DisableLog("rdApp.*")

        # Set logging level
        logging.basicConfig(level=logging.INFO)

    def _standardize_structure(self, smiles):
        """
        Standardize the given SMILES using MolVS and RDKit.

        :param smiles: Input SMILES from the given structure data file
        :return: dataframe: Pandas dataframe containing the original SMILES, standardized SMILES, InChI, and InChIKey

        """
        standardizer = Standardizer()

        smiles_orginal = smiles

        # Read SMILES and convert it to RDKit mol object
        mol = MolFromSmiles(smiles)

        # Check if the input SMILES has been converted into a mol object
        if mol is None:
            logging.error(f"Reading Error, {smiles}")
            return np.nan, np.nan

        try:
            smiles_clean_counter = Counter()
            mol_dict = {}
            is_finalize = False

            for _ in range(5):
                # standardize molecules using MolVS and RDKit
                mol = standardizer.charge_parent(mol)
                mol = standardizer.isotope_parent(mol)
                mol = standardizer.stereo_parent(mol)
                mol = standardizer.tautomer_parent(mol)
                mol = standardizer.standardize(mol)
                standardized_mol = mol

                # convert mol object back to SMILES
                standardized_smiles = MolToSmiles(standardized_mol)

                if smiles == standardized_smiles:
                    is_finalize = True
                    break

                smiles_clean_counter[standardized_smiles] += 1
                if standardized_smiles not in mol_dict:
                    mol_dict[standardized_smiles] = standardized_mol

                smiles = standardized_smiles
                mol = MolFromSmiles(smiles)

            if not is_finalize:
                # If the standardization process is not finalized, we choose the most common SMILES from the counter
                standardized_smiles = smiles_clean_counter.most_common()[0][0]
                # ... and the corresponding mol object
                standardized_mol = mol_dict[standardized_smiles]

            # Convert the mol object to InChI
            standardized_inchi = MolToInchi(standardized_mol)
            # Convert the InChI to InChIKey
            standardized_inchikey = MolToInchiKey(standardized_mol)

        except (ValueError, AttributeError) as e:
            standardized_smiles = np.nan
            standardized_inchi = np.nan
            standardized_inchikey = np.nan
            logging.error(f"Standardization error, {smiles}, Error Type: {str(e)}")

        # return as a dataframe
        return pd.DataFrame(
            {
                "SMILES_original": [smiles_orginal],
                "SMILES": [standardized_smiles],
                "InChI": [standardized_inchi],
                "InChIKey": [standardized_inchikey],
            }
        )

    def _run_standardize(self, smiles_list):
        """
        Run the standardization process in parallel using multiprocessing.

        :param smiles_list: List of SMILES to be standardized
        :param num_cpu: Number of CPUs to use
        """
        with Pool(processes=self.num_cpu) as pool:
            standardized_dfs = list(
                tqdm.tqdm(
                    pool.imap(self._standardize_structure, smiles_list),
                    total=len(smiles_list),
                )
            )
        return pd.concat(standardized_dfs, ignore_index=True)

    def skip_rows_bang(self, file_or_url):
        """
        Return the rows that start with a bang.

        :param file_or_url: Input file name, either a local file or a URL

        """
        # Check if the input is a URL
        if file_or_url.startswith("http://") or file_or_url.startswith("https://"):
            response = requests.get(file_or_url)
            content = response.content.decode("utf-8")
            lines = content.splitlines()
        else:
            with open(file_or_url, "r") as f:
                lines = f.readlines()

        exclamation_indices = [
            index for index, line in enumerate(lines) if line.startswith("!")
        ]

        return exclamation_indices

    def _load_input(self):
        """
        Read the input and return a pandas dataframe containing the SMILES.

        :return: dataframe: Pandas dataframe containing the SMILES
        """
        if isinstance(self.input, str):
            # read the input file, and figure out if it is a csv or a tsv file
            if self.input.endswith(".csv"):
                sep = ","
            elif self.input.endswith((".tsv", ".txt")):
                sep = "\t"
            else:
                raise ValueError("Input file must be either a csv or a tsv/txt file.")

            self.input = pd.read_csv(
                self.input,
                sep=sep,
                skiprows=self.skip_rows_bang(self.input),
            )

            # if there are no rows, raise an error
            if len(self.input) == 0:
                raise ValueError("Input file must contain at least one row.")

            # if the columns SMILES or smiles is not present, raise an error
            if (
                "SMILES" not in self.input.columns
                and "smiles" not in self.input.columns
            ):
                raise ValueError(
                    "Input file must contain a column named SMILES or smiles."
                )

            # if the column SMILES is not present, rename the column smiles to SMILES
            if "SMILES" not in self.input.columns:
                self.input = self.input.rename(columns={"smiles": "SMILES"})

            # if both SMILES and smiles are present, raise an error
            if "SMILES" in self.input.columns and "smiles" in self.input.columns:
                raise ValueError(
                    "Input file must contain only one column named SMILES."
                )

        elif isinstance(self.input, pd.DataFrame):
            pass
        else:
            raise ValueError("Input must be either a filename or a pandas dataframe.")

        # if self.limit_rows is not None, limit the number of rows to self.limit_rows
        if self.limit_rows is not None:
            self.input = self.input.head(self.limit_rows)

        # select only the SMILES column
        self.input = self.input[["SMILES"]]

        # drop missing values
        self.input = self.input.dropna()

        # drop duplicates
        self.input = self.input.drop_duplicates()

    def run(self):
        """
        Run the standardization process.
        """
        self._load_input()

        standardized_df = self._run_standardize(self.input["SMILES"])

        # if self.output is not None, save the standardized dataframe to a csv file
        if self.output is not None:
            standardized_df.to_csv(self.output, index=False)
            return self.output
        else:
            return standardized_df


if __name__ == "__main__":
    fire.Fire(StandardizeMolecule)
