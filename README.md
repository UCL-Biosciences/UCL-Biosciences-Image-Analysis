# Image-Analysis-Summer-Project
Repo for hosting key info for the summer placement: plan, resources, progress, outputs

## Background
Analysing bioimage data is becoming increasingly complex. File sizes, the number of images and samples, and complex algorithms require specialised knowledge.

Resources are required to support researchers handling complex datasets and analysis techniques.

In particular, many efficient and reproducible workflows are implemented in coding languages, such as python, which can be a barrier for researchers without coding experience.

Through this project, we will develop resources to help researchers run python-based image analysis workflows.

## A reproducible workflow
Our resources will demonstrate a robust and reproducible workflow, from data generation to data publishing. This covers three main themes:
1. Data management - store and transfer data securely
2. Data analysis - robust and reproducible analyses
3. Data publishing - promote FAIR principles through good practice when publishing results

![Computational support for image analysis](Imaging-plan-20250716.svg)

### Data Management
Transfer data and confirm with md5
Store on RDSS

### Data Analysis
Use scripting approach to generate repeatable, reproducible workflows.

Configure workflows without needing to change code. I.e. through config files. Make it accessible to non-coders.

Validate pipeline outputs by using test datasets with expected results.

Job scripts for running analyses on HPC clusters, again with minimal coding experience needed.

### Data Publishing
Demo of how to upload to archives, how to generate Zenodo DOI, what is needed for reproducibility (annotated code, environments etc).

## Image Analysis
We will generate resources for common analysis steps e.g. segmentation (2D and 3D), counting cells/nuclei, shape/size analysis, quantifying light intensity.

## Datasets
We will use a combination of [publicly available benchmark datasets](https://bbbc.broadinstitute.org/image_sets) and data generated within Biosciences to test and demonstrate pipelines.
