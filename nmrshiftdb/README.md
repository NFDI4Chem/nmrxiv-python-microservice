## Purpose
This directory has python files to help:
- Downloading NMRShiftDB database as a collection of NMReData files.
- Downloading the experimental data from the links in the NMReData.
- Unzipping and structuring the files and folders in a compatible manner with nmrXiv submission requirements.

## Running
After navigating to the current folder, "nmrshiftdb", run: python3 nmrshiftdb-download.py

## Structure
The folder contains two python files:
- helpers.py has the functions.
- nmrshiftdb-download.py is the script that we run.
- output folder generated after running the script, containing the NMReData, along with folders organized and named after the unique combinations of authors found in NMRShiftDB. Within each folder one can find all the molecules credited to those authors structured as folders containing the Bruker datasets folder and the corresponding NMReData files. Datasets are named after the spectra IDs in NMRShiftDB. 

## Findings: 
- There are 38 unique combinations of authors, which corresponds to 38 nmrXiv projects.
- There are 96 molecules corresponding to nmrXiv studies.
- There are 559 spectra corresponding to nmrXiv datasets.
- CDCl3 is the only solvent used. 
- All temperatures are in Kelvin.

