# compound-annotator

Credits: [Lewis Mervin](https://github.com/lewismervin1) for the orignal source code.

## Setup

1. [Install Python](https://www.python.org/downloads/)
1. [Install Poetry](https://python-poetry.org/docs/#installation)
1. [Install Poetry Environment](https://python-poetry.org/docs/basic-usage/#installing-dependencies): `poetry install`

For Linux, see

- <https://github.com/python-poetry/poetry/issues/1917#issuecomment-1380429197> if installing six fails
- <https://stackoverflow.com/a/75435100> if you get "does not contain any element" warning when running `poetry install`

## Produce ChEMBL annotations

The steps below produce the following files:

- `data/chembl_annotation.csv.gz`: ChEMBL annotation file. This is the raw output of a SQL query run on the ChEMBL SQLite database to get a subset of the data that we need.
- `data/chembl_annotation_filtered.csv.gz`: ChEMBL annotation file filtered to only include rows with `standard_inchi_key` that are present in the `compound.csv.gz` file (this is the metadata file from the jump-cellpainting/datasets repo).
- `data/inchikey_chembl_filtered.csv.gz`: Mapping of `standard_inchi_key` to `molecule_chembl_id` from the filtered ChEMBL annotation file. This will allow us to map the `compound_id` in the `compound.csv.gz` file to the `molecule_chembl_id` in the ChEMBL annotation file.

Using these files, we can annotate the `compound.csv.gz` file with the `molecule_chembl_id` column.

### Create annotation file

On a VM with >40G disk space, download ChEMBL SQLite database (4.2G compressed, 23G uncompressed)

```sh
wget https://ftp.ebi.ac.uk/pub/databases/chembl/ChEMBLdb/latest/chembl_31_sqlite.tar.gz
tar -xvzf chembl_31_sqlite.tar.gz
tree chembl_31
# chembl_31
# └── chembl_31_sqlite
#     ├── INSTALL_sqlite
#     └── chembl_31.db
```

Run a SQL query to extract ChEMBL annotation

```sh
sqlite3 -header -csv chembl_31/chembl_31_sqlite/chembl_31.db < sql/extract_chembl_annotation.sql | gzip > data/chembl_annotation.csv.gz
```

<details>

GPT-4 summary:

This SQL query retrieves a list of bioactivity data for small molecules with a focus on human targets from the ChEMBL database. The query is designed to filter and return specific information from multiple tables within the database. Here's a breakdown of what the query is doing:

1. `SELECT` clause: Defines the columns and data to be retrieved from the tables. These include assay ID, target ChEMBL ID, assay type, molecule ChEMBL ID, pChEMBL value, confidence score, standard InChI key, and preferred name of the molecule.
2. `FROM` clause: Lists the tables from which data will be fetched. These include compound_properties, compound_structures, compound_records, molecule_dictionary, activities, assays, target_dictionary, target_components, component_sequences, and source tables.
3. `WHERE` clause: Applies various conditions to filter the data based on the desired criteria:
    - Joins multiple tables by matching their key columns (e.g., molregno, assay_ID, tid, component_id, src_id).
    - Retrieves data only for human targets (`organism` = 'Homo sapiens').
    - Filters the data based on specific bioactivity types (`standard_type`: IC50, Ki, Kd, EC50, AC50).
    - Sets a minimum pChEMBL value (`pchembl_value` >= 5) and minimum confidence score (confidence_score >= 5).
    - Filters for specific assay types (`assay_type`: 'B' or 'F').
    - Excludes potential duplicate data and entries with data validity comments.
    - Ensures that the molecule is not a polymer (`polymer_flag` = 0) and has a non-null pChEMBL value.
4. `GROUP BY` clause: Groups the results based on unique combinations of `component_sequences.accession`, `molecule_dictionary.chembl_id`, `activities.assay_ID`, and `activities.pchembl_value`.

After running the query, you will obtain a list of small molecules and their bioactivity data against human targets, filtered by the specified criteria.

Notes:

- `assay_type` 'B' refers to binding assays. Binding assays are experiments designed to measure the interaction between a target molecule (often a protein) and a ligand (such as a drug or small molecule). This type of assay is used to evaluate the affinity, specificity, or other characteristics of the interaction.
- `assay_type` 'F' refers to functional assays. Functional assays are designed to measure the biological activity or effect of a molecule, such as a drug or small molecule, on its target. These assays evaluate how the molecule influences the target's function, such as its enzymatic activity, cellular response, or signal transduction. Functional assays can provide important insights into the efficacy and mechanism of action of a compound.
- `pchembl_value` is a standardized representation of the potency or efficacy of a compound in a bioactivity assay in the ChEMBL database. It is calculated by taking the negative logarithm to base 10 (-log10) of the compound's effective concentration, EC50, or inhibitory concentration, IC50, expressed in molar units (M). The pChEMBL value allows for easier comparison of bioactivity data across different compounds and assays. A higher pChEMBL value indicates a more potent compound (i.e., it is effective at a lower concentration). Typically, a pChEMBL value of 6 or higher is considered to be of biological interest for drug discovery purposes, although this threshold may vary depending on the specific target and disease area.

</details>

View the top 5 rows of the annotation file

```sh
python csv2md.py <(gzcat data/chembl_annotation.csv.gz|head -n 5)
```

| assay_chembl_id | target_chembl_id | assay_type | molecule_chembl_id | pchembl_value | confidence_score | standard_inchi_key          | pref_name |
|-----------------|------------------|------------|--------------------|---------------|------------------|-----------------------------|-----------|
| 1714633         | CHEMBL3987582    | B          | CHEMBL4107559      | 6.07          | 7                | UVVXRMZCPKQLAO-OAHLLOKOSA-N |           |
| 1714649         | CHEMBL3987582    | B          | CHEMBL4107559      | 5.86          | 7                | UVVXRMZCPKQLAO-OAHLLOKOSA-N |           |
| 1714633         | CHEMBL3987582    | B          | CHEMBL4108338      | 6.15          | 7                | OZBMIGDQBBMIRA-CQSZACIVSA-N |           |
| 1714649         | CHEMBL3987582    | B          | CHEMBL4108338      | 5.84          | 7                | OZBMIGDQBBMIRA-CQSZACIVSA-N |           |

1. `activities.assay_ID`: This is the unique identifier for a specific bioactivity assay in the ChEMBL database. An assay is an experimental procedure designed to measure the biological activity or effect of compounds on their targets.
1. `target_dictionary.chembl_id`: This is the unique ChEMBL identifier for a molecular target. A target is typically a protein, nucleic acid, or other biomolecule that a compound interacts with, often resulting in a biological effect.
1. `assays.assay_type`: This column indicates the type of bioactivity assay performed. Common assay types include 'B' for binding assays, 'F' for functional assays, 'A' for ADMET assays, and 'T' for toxicity assays.
1. `molecule_dictionary.chembl_id`: This is the unique ChEMBL identifier for a molecule (e.g., a small molecule or drug) in the database.
1. `activities.pchembl_value`: This is the standardized measure of a compound's potency or efficacy in a bioactivity assay, calculated as the negative logarithm to base 10 (-log10) of the compound's effective concentration (EC50) or inhibitory concentration (IC50).
1. `assays.confidence_score`: This is a numeric value (0-9) that indicates the level of confidence in the assignment of a molecular target to an assay. Higher values indicate higher confidence, with 9 being the highest confidence.
1. `compound_structures.standard_inchi_key`: This is the unique standard InChI key for the chemical structure of a compound. InChI keys are alphanumeric strings that serve as unique identifiers for chemical substances, making it easier to compare and share chemical information.
1. `molecule_dictionary.pref_name`: This column contains the preferred name or common name for a molecule in the ChEMBL database, making it easier for users to recognize and refer to the molecule.

Count the number of rows in the annotation file

```sh
gzcat data/chembl_annotation.csv.gz | wc -l
# 1185184
```

Count the number of unique values of each column in the annotation file

```sh
function count_unique_values() {
    data_file=$1
    colnames=$2
    for colname in ${colnames}; do
        echo -n $colname:
        gzcat ${data_file} | csvcut -c ${colname} | tail -n +2 | sort | uniq | wc -l | tr -s " "
    done
}
```

```sh
data_file=data/chembl_annotation.csv.gz
colnames="assay_chembl_id target_chembl_id assay_type molecule_chembl_id standard_inchi_key pref_name"
count_unique_values ${data_file} "${colnames}"
```

```text
assay_chembl_id: 99298
target_chembl_id: 3076
assay_type: 2
molecule_chembl_id: 556272
standard_inchi_key: 56272
pref_name: 6536
```

### Create filtered annotation file

Filter the annotation file to only include rows with `standard_inchi_key` that are present in the `compound.csv.gz` file

```sh
wget https://raw.githubusercontent.com/jump-cellpainting/datasets/0682dd2d52e4d68208ab4af3a0bd114ca557cb0e/metadata/compound.csv.gz
mv compound.csv.gz data/
```

```sh
gzcat data/compound.csv.gz | csvcut -c Metadata_InChIKey| tail -n +2 | sort | uniq > data/compound_inchi_key.txt
```

Now find rows in `data/chembl_annotation.csv` that have `standard_inchi_key` that are present in `data/compound_inchi_key.txt`

```sh
csvgrep -c standard_inchi_key -f data/compound_inchi_key.txt <(gzcat data/chembl_annotation.csv.gz) | gzip > data/chembl_annotation_filtered.csv.gz
```

Count the number of rows in the filtered annotation file

```sh
gzcat data/chembl_annotation_filtered.csv.gz | wc -l
# 44018
```

Count the number of unique values of each column in the filtered annotation file

```sh
data_file=data/chembl_annotation_filtered.csv.gz
colnames="assay_chembl_id target_chembl_id assay_type molecule_chembl_id standard_inchi_key pref_name"
count_unique_values ${data_file} "${colnames}"
```

```text
assay_chembl_id: 18856
target_chembl_id: 1744
assay_type: 2
molecule_chembl_id: 4718
standard_inchi_key: 4718
pref_name: 1340
```

Here are all the commands in one place to create `chembl_annotation_filtered.csv.gz` from `chembl_annotation.csv.gz` and `compound.csv.gz`:

```sh
commit=0682dd2d52e4d68208ab4af3a0bd114ca557cb0e

wget https://raw.githubusercontent.com/jump-cellpainting/datasets/${commit}/metadata/compound.csv.gz

mv compound.csv.gz data/

gzcat data/compound.csv.gz | csvcut -c Metadata_InChIKey| tail -n +2 | sort | uniq > data/compound_inchi_key.txt

csvgrep -c standard_inchi_key -f data/compound_inchi_key.txt <(gzcat data/chembl_annotation.csv.gz) | gzip > data/chembl_annotation_filtered.csv.gz
```

### Create mapping between `standard_inchi_key` and `chembl_id`

Run SQL query to get mapping between `standard_inchi_key` and `chembl_id`

```sh
sqlite3 -header -csv chembl_31/chembl_31_sqlite/chembl_31.db < sql/extract_chembl_inchikey_mapping.sql  | gzip > data/inchikey_chembl.csv.gz
```

<details>

GPT4 summary:

This SQL query retrieves unique molecular data from the ChEMBL database by joining the `compound_structures` and `molecule_dictionary` tables using the `molregno` column.
It selects the ChEMBL ID, standard InChI key, and preferred name of each molecule.

</details>

View the top 5 rows of the `inchikey_chembl.csv.gz` file

```sh
python csv2md.py <(gzcat data/inchikey_chembl.csv.gz|head -n 5)
```

| molecule_chembl_id | standard_inchi_key          | pref_name |
|--------------------|-----------------------------|-----------|
| CHEMBL592894       | AAAJHRMBUHXWLD-UHFFFAOYSA-N |           |
| CHEMBL268868       | AAALVYBICLMAMA-UHFFFAOYSA-N | DAPH      |
| CHEMBL1734241      | AAAZRMGPBSWFDK-UHFFFAOYSA-N |           |
| CHEMBL3449946      | AABSTWCOLWSFRA-UHFFFAOYSA-N |           |

Count the number of rows in the `inchikey_chembl.csv.gz` file

```sh
gzcat data/inchikey_chembl.csv.gz | wc -l
# 2304876
```

Count the number of rows in the `compound_inchi_key.txt` file

```sh
wc -l data/compound_inchi_key.txt
# 116753
```

Now find rows in `data/inchikey_chembl.csv.gz` that have `standard_inchi_key` that are present in `data/compound_inchi_key.txt`

```sh
csvgrep -c standard_inchi_key -f data/compound_inchi_key.txt <(gzcat data/inchikey_chembl.csv.gz) | gzip > data/inchikey_chembl_filtered.csv.gz
```

Count the number of unique values of each column in `inchikey_chembl_filtered.csv.gz`

```sh
data_file=data/inchikey_chembl_filtered.csv.gz
colnames="molecule_chembl_id standard_inchi_key pref_name"
count_unique_values ${data_file} "${colnames}"
```

```text
molecule_chembl_id: 30072
standard_inchi_key: 30072
pref_name: 2508
```
