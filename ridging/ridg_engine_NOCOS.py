# -*- coding: utf-8 -*-
"""

@author: Andrea Gierisch, DMI
@author: Ilja Maljutenko, MSI

"""
# Load RID functions
from read_config import read_configfile
from read_ice_data import read_ice_data
from calculate_RID import calc_RID_multicat
from calculate_RID import calc_RID_intcat
from output_RID import save_RID_toNetCDF
from output_RID import plot_RID


# Read config file
configs=read_configfile('config_ridg_calc_REF.yml')

# Read ice data
icedata=read_ice_data(configs)
print(icedata)
# Calculate ridging
if configs['multiCAT']==True:
    ridg_data=calc_RID_multicat(icedata,configs)
elif configs['multiCAT']==False:
    ridg_data=calc_RID_intcat(icedata,configs)


save_RID_toNetCDF(ridg_data,icedata,configs)
plot_RID(ridg_data,icedata,configs)




