# Deploying Maia on Binder
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/amehri-upvd/testMaiaBinder/HEAD)

Interactive Tutorial with voilà : 
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/amehri-upvd/testMaiaBinder/HEAD?urlpath=voila%2Frender%2Fnotebooks_with_voila%2FCompute_centers+_with_voila.ipynb)



This repository contains configuration files for running MAIA on a MyBinder environment.

## Features

- Support libhdf5-openmpi-dev
- h5py built with MPI support for parallel I/O operations
- Proper MPI environment configuration
- MAIA scientific computing framework installation

## Configuration Files

- **apt.txt**: System dependencies 
- **requirements.txt**: Python package dependencies 
- **postBuild**: Script that clones, installs Maia, and builds h5py with parallel support
- **start**: Sets up the environment variables for the Jupyter session

## Usage

When the Binder environment launches, all dependencies and pachages will be installed, allowing Maia to perform operations.
