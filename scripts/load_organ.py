#!/usr/bin/env python3
"""
Download OpenOrganelle dataset jrc_mus-nacc-2.
https://openorganelle.janelia.org/datasets/jrc_mus-nacc-2

Data: s3://janelia-cosem-datasets/jrc_mus-nacc-2/jrc_mus-nacc-2.zarr

"""

import json
import os
import requests
import s3fs
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from tqdm import tqdm

DATASET_ID = "jrc_mus-nacc-2"
S3_PATH = f"janelia-cosem-datasets/{DATASET_ID}/{DATASET_ID}.zarr"
FIGSHARE_SEARCH = "https://api.figshare.com/v2/articles/search"
OUTPUT_DIR = Path(f"./data/openorganelle_{DATASET_ID}")
MAX_WORKERS = 32


def download_key(fs, s3_key, local_path):
    """Download a single S3 key to a local file."""
    local_path.parent.mkdir(parents=True, exist_ok=True)
    fs.get(s3_key, str(local_path))
    return s3_key


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    fs = s3fs.S3FileSystem(anon=True)

    # 1. Metadata from Figshare
    print(f"Searching Figshare for '{DATASET_ID}'...")
    try:
        resp = requests.post(FIGSHARE_SEARCH,
                             json={"search_for": DATASET_ID, "institution": 625},
                             timeout=30)
        resp.raise_for_status()
        results = resp.json()
        if results:
            detail = requests.get(results[0]["url_public_api"], timeout=30).json()
            with open(OUTPUT_DIR / "metadata.json", "w") as f:
                json.dump(detail, f, indent=2)
            print(f"Metadata saved ({detail.get('title', '')}).\n")
    except Exception as e:
        print(f"Metadata fetch failed: {e}\n")

    # 2. List all keys in the zarr
    print(f"Listing s3://{S3_PATH} ...")
    all_keys = fs.find(S3_PATH)
    print(f"Found {len(all_keys)} files.\n")

    # 3. Download in parallel
    local_root = OUTPUT_DIR / f"{DATASET_ID}.zarr"
    print(f"Downloading with {MAX_WORKERS} threads...")

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futures = {}
        for key in all_keys:
            rel = key[len(S3_PATH) + 1:]  # relative path within zarr
            local_path = local_root / rel
            if local_path.exists():
                continue
            futures[pool.submit(download_key, fs, key, local_path)] = rel

        with tqdm(total=len(futures), unit="file") as pbar:
            for fut in as_completed(futures):
                try:
                    fut.result()
                except Exception as e:
                    print(f"\n  Failed: {futures[fut]}: {e}")
                pbar.update(1)

    print(f"Done. Saved to {local_root}")


if __name__ == "__main__":
    main()