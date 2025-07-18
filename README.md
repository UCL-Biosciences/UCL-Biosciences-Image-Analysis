# Image Segmentation With Cellpose

A modular pipeline for segmenting time-lapse microscopy images using Cellpose and validating segmentation quality.

## Project Structure

cellpose-segmentation-demo/

├── config/              # Configuration files

│   └── params.yaml      # Main parameter settings
├── notebooks/           # Jupyter notebooks for development
├── scripts/             # Core Python modules (segmentation, validation, etc.)
├── jobs/                # HPC batch scripts
└── output/              # Generated outputs (ignored by Git)

## Requirements

- Python 3.8+
- conda
- configs/celltrack-env-myriad.yml

## Quick Start

Clone the repository:

git clone <your-repo-url>
cd image_tracking_project

Set up environment:

conda create -n cellpose_env python=3.9
conda activate cellpose_env
pip install cellpose
pip install -r requirements.txt  # (optional)

Edit configuration:

Update config/params.yaml with your image folder and settings.

Run pipeline:

python main.py --config config/params.yaml

