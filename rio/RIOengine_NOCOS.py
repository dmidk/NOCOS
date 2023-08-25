# -*- coding: utf-8 -*-
"""

@author: Andrea Gierisch, DMI
"""
# Load RIO functions
from read_config import read_configfile
from read_ice_data import read_ice_data
from save_RIO_toNetCDF import save_toNetcdf
from calculate_RIO import calcRIO_multicat

# Read config file
#configs=read_configfile() # Reads config_RIOcalc_default.yml
configs=read_configfile('config_RIOcalc_DMI-HYCOM-CICE.yml')

# Read ice data
icedata=read_ice_data(configs)

# Calculate RIO
if configs['multiCAT']==True:
    riodata=calcRIO_multicat(icedata,configs)
elif configs['multiCAT']==False:
    raise NotImplementedError()

# Save RIO data to netcdf file
save_toNetcdf(riodata,icedata,configs)


