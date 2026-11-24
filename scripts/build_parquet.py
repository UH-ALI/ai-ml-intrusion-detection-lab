"""Clean raw CIC CSVs into Parquet, one file at a time.

    python scripts/build_parquet.py cic2017 <raw_csv_dir> <out_dir>
    python scripts/build_parquet.py cse2018 <raw_csv_dir> <out_dir>
"""

import sys

from idslab.data import DATASETS, build_parquet

if __name__ == "__main__":
    if len(sys.argv) != 4 or sys.argv[1] not in DATASETS:
        sys.exit(__doc__)
    build_parquet(sys.argv[2], sys.argv[3], sys.argv[1])
