#!/usr/bin/env python3
"""
Download 3D EM dataset from EPFL CVLAB.
https://www.epfl.ch/labs/cvlab/data/data-em/

CA1 hippocampus, 1065x2048x1536, ~5nm isotropic voxels, multipage TIF.

"""

import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from tqdm import tqdm

# Note the %20 (space) before ElectronMicroscopy — this is in the original URLs
BASE = "https://documents.epfl.ch/groups/c/cv/cvlab-unit/www/data/%20ElectronMicroscopy_Hippocampus"
OUTPUT_DIR = Path("./data/epfl_em")

FILES = [
    "volumedata.tif",
    "training.tif",
    "testing.tif",
    "training_groundtruth.tif",
    "testing_groundtruth.tif",
]


def download(url, path):
    resp = requests.get(url, stream=True, timeout=300)
    resp.raise_for_status()
    total = int(resp.headers.get("content-length", 0))
    with open(path, "wb") as f:
        with tqdm(total=total, unit="B", unit_scale=True, desc=path.name) as pbar:
            for chunk in resp.iter_content(8192):
                f.write(chunk)
                pbar.update(len(chunk))


def download_file(name):
    out = OUTPUT_DIR / name
    if out.exists():
        return f"Skipped {name} (already exists)"
    url = f"{BASE}/{name}"
    download(url, out)
    return f"Done: {name}"


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(download_file, name): name for name in FILES}
        for future in as_completed(futures):
            try:
                print(future.result())
            except requests.HTTPError as e:
                name = futures[future]
                print(f"  Failed {name}: {e}")

    print(f"Done. Files in {OUTPUT_DIR}")


if __name__ == "__main__":
    main()