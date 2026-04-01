# HHMI Microscopy Data Task

Simple, reproducible download scripts for microscopy datasets that are hosted
in different storage systems.

## Repository Structure

- `main.py`: single entry point to run all scripts in parallel
- `scripts/`: dataset-specific download scripts (kept as-is)
- `data/`: downloaded dataset files
- `requirements.txt`: Python dependencies

## Quick Start

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run all downloads:

```bash
python3 main.py
```

Or run a single script directly:

```bash
python3 scripts/load_epfl.py
```

