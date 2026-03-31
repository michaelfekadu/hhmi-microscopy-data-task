#!/usr/bin/env python3
"""
Download 3D EM image from IDR.
https://idr.openmicroscopy.org/webclient/img_detail/9846137/?dataset=10740

1121 x 775 x 184 Z-sections, uint8, 20nm isotropic.
Downloads each Z-plane as rendered JPEG, stacks into TIFF.

Note: This gives 8-bit rendered data, not raw pixels.
For raw data use Aspera/Globus via https://idr.openmicroscopy.org/study/idr0086/

Requirements: pip install requests numpy tifffile tqdm Pillow
Usage:        python download_idr.py
"""

import json
import numpy as np
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from io import BytesIO
from pathlib import Path
from PIL import Image
from tqdm import tqdm

BASE = "https://idr.openmicroscopy.org"
IMAGE_ID = 9846137
OUTPUT_DIR = Path("./data/idr")
MAX_WORKERS = 8


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    session = requests.Session()

    # 1. Metadata
    print("Fetching metadata...")
    resp = session.get(f"{BASE}/webgateway/imgData/{IMAGE_ID}/")
    resp.raise_for_status()
    meta = resp.json()
    with open(OUTPUT_DIR / "metadata.json", "w") as f:
        json.dump(meta, f, indent=2)

    nz = meta["size"]["z"]
    ch = meta["channels"][0]
    c_param = f"1|{ch['window']['start']}:{ch['window']['end']}${ch['color']}"
    print(f"Image: {meta['size']['width']}x{meta['size']['height']}x{nz}, {c_param}")

    # 2. Download Z-planes in parallel
    def download_plane(z):
        url = f"{BASE}/webgateway/render_image/{IMAGE_ID}/{z}/0/?c={c_param}&m=g"
        r = session.get(url, timeout=60)
        r.raise_for_status()
        arr = np.array(Image.open(BytesIO(r.content)))
        if arr.ndim == 3:
            arr = arr[:, :, 0]
        return z, arr

    print(f"Downloading {nz} Z-planes ({MAX_WORKERS} threads)...")
    planes = [None] * nz
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futures = {pool.submit(download_plane, z): z for z in range(nz)}
        for fut in tqdm(as_completed(futures), total=nz, unit="plane"):
            z, arr = fut.result()
            planes[z] = arr

    # 3. Save
    volume = np.stack(planes, axis=0)
    import tifffile
    out = OUTPUT_DIR / f"image_{IMAGE_ID}.tif"
    tifffile.imwrite(str(out), volume, imagej=True)
    print(f"\nDone. Files in {out}")


if __name__ == "__main__":
    main()