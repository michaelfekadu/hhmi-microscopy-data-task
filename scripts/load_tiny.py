#!/usr/bin/env python3
"""
Download a random 1000x1000x1000 crop from the FlyEM Hemibrain dataset.
https://tinyurl.com/hemibrain-ng

The full volume (34431 x 39743 x 41407 @ 8nm) is stored on Google Cloud
Storage in Neuroglancer Precomputed format. We use CloudVolume to read
a random 1000^3 subregion.

Source: gs://neuroglancer-janelia-flyem-hemibrain/emdata/raw/jpeg

Requirements: pip install cloud-volume numpy tifffile
Usage:        python download_hemibrain.py
"""

import json
import random
import numpy as np
from pathlib import Path

from cloudvolume import CloudVolume

SOURCE = "precomputed://gs://neuroglancer-janelia-flyem-hemibrain/emdata/raw/jpeg"
CROP_SIZE = 1000
OUTPUT_DIR = Path("./data/hemibrain")


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Open the volume (use_https=True avoids needing GCP credentials)
    print("Connecting to hemibrain volume...")
    vol = CloudVolume(SOURCE, use_https=True, mip=0, progress=True, parallel=True)

    # Print info
    shape = vol.shape[:3]  # (X, Y, Z)
    print(f"Volume shape: {shape}")
    print(f"Resolution:   {vol.resolution} nm")
    print(f"Dtype:        {vol.dtype}")

    # Save metadata
    with open(OUTPUT_DIR / "metadata.json", "w") as f:
        json.dump({
            "source": SOURCE,
            "shape": list(shape),
            "resolution_nm": list(vol.resolution),
            "dtype": str(vol.dtype),
            "info": vol.info,
        }, f, indent=2, default=str)

    # Pick a random origin that fits a 1000^3 crop inside the volume
    max_x = shape[0] - CROP_SIZE
    max_y = shape[1] - CROP_SIZE
    max_z = shape[2] - CROP_SIZE

    x0 = random.randint(0, max_x)
    y0 = random.randint(0, max_y)
    z0 = random.randint(0, max_z)

    print(f"\nRandom crop origin: ({x0}, {y0}, {z0})")
    print(f"Crop size: {CROP_SIZE}^3")
    print(f"Downloading...")

    # Download the crop (CloudVolume returns shape [X, Y, Z, C])
    crop = vol[x0:x0+CROP_SIZE, y0:y0+CROP_SIZE, z0:z0+CROP_SIZE]
    crop = np.squeeze(crop)  # remove channel dim
    print(f"Downloaded shape: {crop.shape}, dtype: {crop.dtype}")

    # Save as TIFF
    import tifffile
    out_path = OUTPUT_DIR / f"hemibrain_crop_{x0}_{y0}_{z0}.tif"
    # tifffile expects (Z, Y, X) order; CloudVolume returns (X, Y, Z)
    crop_zyx = np.transpose(crop, (2, 1, 0))
    tifffile.imwrite(str(out_path), crop_zyx)
    print(f"Saved to {out_path}")

    # Also save crop coordinates for reproducibility
    with open(OUTPUT_DIR / "crop_info.json", "w") as f:
        json.dump({
            "origin_xyz": [x0, y0, z0],
            "size": CROP_SIZE,
            "output_file": str(out_path),
        }, f, indent=2)

    print(f"Done. Saved to {OUTPUT_DIR}")



if __name__ == "__main__":
    main()