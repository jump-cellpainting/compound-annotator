# This command line tool is used to convert a CSV file into a markdown table
# Usage: python csv2md.py <file.csv>
#

import sys
import csv


def main():
    if len(sys.argv) != 2:
        print("Usage: python csv2md.py <file.csv>")
        sys.exit(1)

    with open(sys.argv[1], "r") as f:
        reader = csv.reader(f)
        header = next(reader)
        rows = [row for row in reader]
        print("| {} |".format(" | ".join(header)))
        print("| {} |".format(" | ".join(["---" for _ in header])))
        for row in rows:
            print("| {} |".format(" | ".join(row)))


if __name__ == "__main__":
    main()
