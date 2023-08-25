Installation
#############

Software requirements:
Python 3.9 with following packages:
  - numpy
  - xarray (including dask, netCDF4 and bottleneck)
  - pyyaml

Use the provided file conda-env_NOCOS-RIO.yml to install a suitable conda environment.

Running
############
1) Adjust the configuration file config_RIOcalc_default.yml or make a new one and provide its name inside RIOengine_NOCOS.py
2) conda activate rioNOCOS
3) python3 RIOengine_NOCOS.py

Info
#############

We use variable names as defined by CMIP6/CMOR:
siconc
sithick
sivol
siitdconc
siitdthick
siage
sisali
(See explanations in config_RIOcalc_default.yml)


