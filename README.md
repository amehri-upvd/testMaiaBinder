# MAIA MyBinder Environment with Parallel h5py Support
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/BJKhalil/test_binder.git/HEAD)

This repository contains configuration files for running MAIA in a MyBinder environment with parallel HDF5/h5py support.

## Features

- Parallel HDF5 support through libhdf5-openmpi-dev
- h5py built with MPI support for parallel I/O operations
- Proper MPI environment configuration
- MAIA scientific computing framework installation

## Configuration Files

- **apt.txt**: System dependencies including parallel HDF5 and MPI libraries
- **requirements.txt**: Python package dependencies (h5py is installed separately with parallel support)
- **postBuild**: Script that builds h5py with parallel support and installs MAIA
- **start**: Sets up the environment variables for the Jupyter session

## Usage

When the Binder environment launches, h5py will be configured with parallel support, allowing MAIA to perform parallel I/O operations.
