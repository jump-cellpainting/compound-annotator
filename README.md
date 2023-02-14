# compound-annotator

Credits: [Lewis Mervin](https://github.com/lewismervin1) for the orignal source code.

## Setup

1. [Install Python](https://www.python.org/downloads/)
1. [Install Poetry](https://python-poetry.org/docs/#installation)
1. [Install Poetry Environment](https://python-poetry.org/docs/basic-usage/#installing-dependencies): `poetry install`

For Linux, see

- <https://github.com/python-poetry/poetry/issues/1917#issuecomment-1380429197> if installing six fails
- <https://stackoverflow.com/a/75435100> if you get "does not contain any element" warning when running `poetry install`

## Run

### Create annotation file

On a VM with >40G disk space, download ChEMBL SQLite database (4.2G compressed, 23G uncompressed)

```sh
wget https://ftp.ebi.ac.uk/pub/databases/chembl/ChEMBLdb/latest/chembl_31_sqlite.tar.gz
tar -xvzf chembl_31_sqlite.tar.gz
```

This produces a directory `chembl_31_sqlite` with the following structure:

```sh
chembl_31
└── chembl_31_sqlite
    ├── INSTALL_sqlite
    └── chembl_31.db
```

Run SQL query to extract ChEMBL annotation

```sh
sqlite3 -header -csv chembl_31/chembl_31_sqlite/chembl_31.db < sql/extract_chembl_annotation.sql | gzip > data/chembl_annotation.csv
```

View the top 5 rows of the annotation file

```sh
head -n 5 <(gzcat data/chembl_annotation.csv.gz)
```

```text
assay_chembl_id,target_chembl_id,assay_type,molecule_chembl_id,pchembl_value,confidence_score,standard_inchi_key,pref_name
1714633,CHEMBL3987582,B,CHEMBL4107559,6.07,7,UVVXRMZCPKQLAO-OAHLLOKOSA-N,
1714649,CHEMBL3987582,B,CHEMBL4107559,5.86,7,UVVXRMZCPKQLAO-OAHLLOKOSA-N,
1714633,CHEMBL3987582,B,CHEMBL4108338,6.15,7,OZBMIGDQBBMIRA-CQSZACIVSA-N,
1714649,CHEMBL3987582,B,CHEMBL4108338,5.84,7,OZBMIGDQBBMIRA-CQSZACIVSA-N,
```

Rendered as a table:

| assay_chembl_id | target_chembl_id | assay_type | molecule_chembl_id | pchembl_value | confidence_score | standard_inchi_key          | pref_name |
|-----------------|------------------|------------|--------------------|---------------|------------------|-----------------------------|-----------|
| 1714633         | CHEMBL3987582    | B          | CHEMBL4107559      | 6.07          | 7                | UVVXRMZCPKQLAO-OAHLLOKOSA-N |           |
| 1714649         | CHEMBL3987582    | B          | CHEMBL4107559      | 5.86          | 7                | UVVXRMZCPKQLAO-OAHLLOKOSA-N |           |
| 1714633         | CHEMBL3987582    | B          | CHEMBL4108338      | 6.15          | 7                | OZBMIGDQBBMIRA-CQSZACIVSA-N |           |
| 1714649         | CHEMBL3987582    | B          | CHEMBL4108338      | 5.84          | 7                | OZBMIGDQBBMIRA-CQSZACIVSA-N |           |

### Create filtered annotation file

Filter the annotation file to only include rows with `standard_inchi_key` that are present in the `compound.csv.gz` file

```sh
wget https://raw.githubusercontent.com/jump-cellpainting/datasets/0682dd2d52e4d68208ab4af3a0bd114ca557cb0e/metadata/compound.csv.gz
mv compound.csv.gz data/
```

```sh
gzcat data/compound.csv.gz | csvcut -c Metadata_InChIKey| tail -n +2 | sort | uniq > data/compound_inchi_key.csv
```

Now find rows in `data/chembl_annotation.csv` that have `standard_inchi_key` that are present in `data/compound_inchi_key.csv`

```sh
csvgrep -c standard_inchi_key -f data/compound_inchi_key.csv <(gzcat data/chembl_annotation.csv.gz) | gzip > data/chembl_annotation_filtered.csv.gz
```

View the top 5 rows of the filtered annotation file

```sh
head -n 5 <(gzcat data/chembl_annotation_filtered.csv.gz)
```

```text
assay_chembl_id,target_chembl_id,assay_type,molecule_chembl_id,pchembl_value,confidence_score,standard_inchi_key,pref_name
1931436,CHEMBL4523105,B,CHEMBL3716578,5.75,9,GUUWHOSUKOCRHG-UHFFFAOYSA-N,
1931437,CHEMBL4523105,B,CHEMBL3716578,5.85,9,GUUWHOSUKOCRHG-UHFFFAOYSA-N,
1931437,CHEMBL4523105,B,CHEMBL4571346,5.01,9,ILKYRSSTSHMXTC-UHFFFAOYSA-N,
446514,CHEMBL2094132,B,CHEMBL1112,6.3,5,CEUORZQYGODEFX-UHFFFAOYSA-N,ARIPIPRAZOLE
```

Rendered as a table:

| assay_chembl_id | target_chembl_id | assay_type | molecule_chembl_id | pchembl_value | confidence_score | standard_inchi_key          | pref_name    |
|-----------------|------------------|------------|--------------------|---------------|------------------|-----------------------------|--------------|
| 1931436         | CHEMBL4523105    | B          | CHEMBL3716578      | 5.75          | 9                | GUUWHOSUKOCRHG-UHFFFAOYSA-N |              |
| 1931437         | CHEMBL4523105    | B          | CHEMBL3716578      | 5.85          | 9                | GUUWHOSUKOCRHG-UHFFFAOYSA-N |              |
| 1931437         | CHEMBL4523105    | B          | CHEMBL4571346      | 5.01          | 9                | ILKYRSSTSHMXTC-UHFFFAOYSA-N |              |
| 446514          | CHEMBL2094132    | B          | CHEMBL1112         | 6.3           | 5                | CEUORZQYGODEFX-UHFFFAOYSA-N | ARIPIPRAZOLE |
