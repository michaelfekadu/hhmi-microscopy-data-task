# HHMI Microscopy Data Task

Simple, reproducible download scripts for microscopy datasets that are hosted
in different storage systems.

## Repository Structure

- `main.py`: single entry point to run all scripts or only selected scripts
- `scripts/`: dataset-specific download scripts (kept as-is)
- `data/raw/`: downloaded dataset files
- `data/manifests/`: optional run manifests/checksums for reproducibility
- `requirements.txt`: Python dependencies

## Quick Start

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run downloads:

```bash
# List scripts in ./scripts
python3 main.py --list

# Run all scripts
python3 main.py --all

# Run only selected scripts (with or without .py)
python3 main.py load_tiny
python3 main.py load_idr.py load_em
```

