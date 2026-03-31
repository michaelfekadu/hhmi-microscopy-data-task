#!/usr/bin/env python3
"""
Download EMPIAR-11759 dataset and metadata.
https://www.ebi.ac.uk/empiar/EMPIAR-11759/

Data: 16 .dm3 slices, 1 XML file, and a trakem2 folder with nested subfolders.
Metadata: JSON from the EMPIAR REST API.

Requirements: pip install requests tqdm
Usage:        python download_empiar.py
"""

import json
import re
import requests
from pathlib import Path
from tqdm import tqdm

ENTRY_ID = 11759
API_URL = f"https://www.ebi.ac.uk/empiar/api/entry/EMPIAR-{ENTRY_ID}"
DATA_URL = f"https://ftp.ebi.ac.uk/empiar/world_availability/{ENTRY_ID}/data"
OUTPUT_DIR = Path(f"./data/empiar_{ENTRY_ID}")


def download(url, path):
    """Download a file with a progress bar."""
    path.parent.mkdir(parents=True, exist_ok=True)
    resp = requests.get(url, stream=True, timeout=600)
    resp.raise_for_status()
    total = int(resp.headers.get("content-length", 0))
    with open(path, "wb") as f:
        with tqdm(total=total, unit="B", unit_scale=True, desc=path.name) as pbar:
            for chunk in resp.iter_content(8192):
                f.write(chunk)
                pbar.update(len(chunk))


def download_directory(url, local_dir):
    """Download all files in an HTTPS directory listing, recursing into subdirs."""
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    links = re.findall(r'href="([^"?][^"]*)"', resp.text)

    for link in links:
        if link in ("../", "/") or link.startswith("?") or link.startswith("/"):
            continue
        full_url = f"{url}/{link.rstrip('/')}"
        if link.endswith("/"):
            download_directory(full_url, local_dir / link.rstrip("/"))
        else:
            path = local_dir / link
            if path.exists():
                print(f"  Skipping {link} (exists)")
                continue
            download(full_url, path)


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Metadata
    print("Fetching metadata...")
    resp = requests.get(API_URL, timeout=30)
    resp.raise_for_status()
    with open(OUTPUT_DIR / "metadata.json", "w") as f:
        json.dump(resp.json(), f, indent=2)
    print("Metadata saved.\n")

    # 2. Data
    print("Downloading data...")
    download_directory(DATA_URL, OUTPUT_DIR / "data")
    print(f"\nDone. Files in {OUTPUT_DIR}")


if __name__ == "__main__":
    main()