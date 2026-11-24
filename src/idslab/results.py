"""Writing and reading per-run result files with their provenance."""

import json
import os
import platform
import subprocess
from importlib import metadata
from pathlib import Path

LIBRARIES = ("scikit-learn", "pandas", "numpy", "pyarrow", "lightgbm", "scipy")


def _git(*args):
    try:
        return subprocess.run(["git", *args], capture_output=True, text=True,
                              check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def run_metadata():
    versions = {}
    for lib in LIBRARIES:
        try:
            versions[lib] = metadata.version(lib)
        except metadata.PackageNotFoundError:
            versions[lib] = None
    try:
        ram_gb = os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES") / 1e9
    except (ValueError, OSError, AttributeError):
        ram_gb = None
    return {
        "git_commit": _git("rev-parse", "HEAD"),
        "git_dirty": bool(_git("status", "--porcelain")),
        "python": platform.python_version(),
        "libraries": versions,
        "hardware": {"platform": platform.platform(), "cpus": os.cpu_count(),
                     "ram_gb": round(ram_gb, 1) if ram_gb else None},
    }


def save_result(path, result):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2, default=str))


def load_results(results_dir):
    return [json.loads(p.read_text()) for p in sorted(Path(results_dir).rglob("seed*.json"))]
