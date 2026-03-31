#!/usr/bin/env python3
"""
Download 3D EM dataset from EPFL CVLAB.
https://www.epfl.ch/labs/cvlab/data/data-em/

CA1 hippocampus, 1065x2048x1536, ~5nm isotropic voxels, multipage TIF.

Note: The EPFL download links contain a literal space in the URL path.
      If documents.epfl.ch returns 401, the files may require EPFL login.
      In that case, use Academic Torrents as a fallback:
      https://academictorrents.com/details/3ada3ae6ec71097e63d897cf878051bba3eaba25

Requirements: pip install requests tqdm
Usage:        python download_epfl.py
"""

import requests
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


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for name in FILES:
        out = OUTPUT_DIR / name
        if out.exists():
            print(f"Skipping {name} (already exists)")
            continue

        url = f"{BASE}/{name}"
        print(f"Downloading {name} ...")
        try:
            download(url, out)
        except requests.HTTPError as e:
            print(f"  Failed: {e}")
            print(f"  The EPFL server may require authentication.")
            print(f"  Fallback: download via Academic Torrents:")
            print(f"  https://academictorrents.com/details/3ada3ae6ec71097e63d897cf878051bba3eaba25")
            return

    print(f"Done. Files in {OUTPUT_DIR}")


if __name__ == "__main__":
    main()