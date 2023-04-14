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
