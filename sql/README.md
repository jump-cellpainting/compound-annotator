# SQL queries

## `extract_chembl_annotation.sql`

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

1. `activities.assay_ID`: This is the unique identifier for a specific bioactivity assay in the ChEMBL database. An assay is an experimental procedure designed to measure the biological activity or effect of compounds on their targets.
1. `target_dictionary.chembl_id`: This is the unique ChEMBL identifier for a molecular target. A target is typically a protein, nucleic acid, or other biomolecule that a compound interacts with, often resulting in a biological effect.
1. `assays.assay_type`: This column indicates the type of bioactivity assay performed. Common assay types include 'B' for binding assays, 'F' for functional assays, 'A' for ADMET assays, and 'T' for toxicity assays.
1. `molecule_dictionary.chembl_id`: This is the unique ChEMBL identifier for a molecule (e.g., a small molecule or drug) in the database.
1. `activities.pchembl_value`: This is the standardized measure of a compound's potency or efficacy in a bioactivity assay, calculated as the negative logarithm to base 10 (-log10) of the compound's effective concentration (EC50) or inhibitory concentration (IC50).
1. `assays.confidence_score`: This is a numeric value (0-9) that indicates the level of confidence in the assignment of a molecular target to an assay. Higher values indicate higher confidence, with 9 being the highest confidence.
1. `compound_structures.standard_inchi_key`: This is the unique standard InChI key for the chemical structure of a compound. InChI keys are alphanumeric strings that serve as unique identifiers for chemical substances, making it easier to compare and share chemical information.
1. `molecule_dictionary.pref_name`: This column contains the preferred name or common name for a molecule in the ChEMBL database, making it easier for users to recognize and refer to the molecule.

## `extract_chebi_inchikey_mapping.sql`

This SQL query retrieves unique molecular data from the ChEMBL database by joining the `compound_structures` and `molecule_dictionary` tables using the `molregno` column.
It selects the ChEMBL ID, standard InChI key, and preferred name of each molecule.
