"""Run one experiment config: python scripts/run_experiment.py configs/smoke.yaml"""

import sys

from idslab.experiment import run

if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    run(sys.argv[1])
