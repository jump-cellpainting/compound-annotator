# compound-annotator

Credits: [Lewis Mervin](@lewismervin1) for the orignal source code.

## Setup

1. [Install Python](https://www.python.org/downloads/)
1. [Install Poetry](https://python-poetry.org/docs/#installation)
1. [Install Poetry Environment](https://python-poetry.org/docs/basic-usage/#installing-dependencies): `poetry install`

## Run

Download ChEMBL SQLite database

```sh
wget https://ftp.ebi.ac.uk/pub/databases/chembl/ChEMBLdb/latest/chembl_31_sqlite.tar.gz
```

Run SQL query

```sh
sqlite3 chembl_31_sqlite/chembl_31_sqlite/chembl_31.db < sql/extract_chembl_annotation.sql > data/chembl_annotation.tsv
```
