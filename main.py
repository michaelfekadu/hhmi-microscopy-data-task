#!/usr/bin/env python3
"""Run all scripts in ./scripts in parallel."""

import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path


SCRIPTS_DIR = Path(__file__).resolve().parent / "scripts"
MAX_WORKERS = 2


def all_scripts():
    return sorted(SCRIPTS_DIR.glob("*.py"))


def run_one(path):
    print(f"Starting {path.name}")
    code = subprocess.run([sys.executable, str(path)]).returncode
    return path.name, code


def run_all_parallel(paths):
    max_workers = min(MAX_WORKERS, len(paths)) if paths else 1
    final_code = 0
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = [pool.submit(run_one, path) for path in paths]
        for future in as_completed(futures):
            name, code = future.result()
            if code == 0:
                print(f"Finished {name}")
            else:
                print(f"Failed {name} (exit code {code})")
                final_code = code
    return final_code


def main():
    scripts = all_scripts()
    if not scripts:
        print("No Python scripts found in ./scripts")
        return 1
    return run_all_parallel(scripts)


if __name__ == "__main__":
    raise SystemExit(main())

