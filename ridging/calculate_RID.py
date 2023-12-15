# -*- coding: utf-8 -*-
"""
@author: Andrea Gierisch, DMI
@author: Ilja Maljutenko, MSI

"""

def calc_RID_multicat(icedata,configs):

    import numpy as np
    import warnings
    import time # for sleep and cputime measurement
    import sys # For flushing of buffer to stdout
    
    # Simpler names for relevant variables
    ############################################
    timestr=configs['coordinates']['time_name']
    nistr=configs['coordinates']['ncat_name']
#    print(nistr)
    nt = icedata[configs['coordinates']['time_name']].shape[0] # Number of time steps
    ni = icedata.sit_c.shape[1] 
    ny = icedata.sit_c.shape[2] # Number of grid points in y-direction
    nx = icedata.sit_c.shape[3] # Number of grid points in x-direction
    sit= icedata.sit_c.sel(ncatice=slice(ni-7,ni))
    sic= icedata.sic_c.sel(ncatice=slice(ni-7,ni))
 #   print(sic)
    sits=sit.sum(dim='ncatice')
    sics=sic.sum(dim='ncatice')
# Set up an empty output array
#    ridgfinal=np.array(np.nan*np.zeros([ny,nx]))
#    print(  nt, ny,nx)
    thr_thck=0.01
    mask_t=sits.where(sits > thr_thck, 0) 
    thr_conc=0.01
    mask_c=sics.where(sics > thr_conc, 0) 
    mask_ct=mask_c #*mask_t
    mask_ct=mask_ct.sum(dim=timestr)/(nt)
#    print(nt)    
#    mask_ct=mask_ct.sum(dim=timestr)/(nt)
    ridgfinal=mask_ct                             
    return(ridgfinal)


def calc_RID_intcat(icedata,configs):

    import numpy as np
    import warnings
    import time # for sleep and cputime measurement
    import sys # For flushing of buffer to stdout
#    print(icedata)
    # Simpler names for relevant variables
    ############################################
    timestr=configs['coordinates']['time_name']
    nt = icedata[configs['coordinates']['time_name']].shape[0] # Number of time steps
    ny = icedata.sit.shape[1] # Number of grid points in y-direction
    nx = icedata.sit.shape[2] # Number of grid points in x-direction
    sit= icedata.sit
    sic= icedata.sit
# Set up an empty output array
#    ridgfinal=np.array(np.nan*np.zeros([ny,nx]))
#    print(  nt, ny,nx)
    thr_thck=0.7 #0.6
    mask_t=sit.where(sit > thr_thck, 0) 
    thr_conc=0.95
    mask_c=sic.where(sic > thr_conc, 0) 
#    mask_ct = (sit> thr_thck) & (sic > thr_conc)
#    mask_ct=mask_ct.where(mask_ct > 0, 1)     
    mask_ct=mask_c*mask_t
    ridged_ice=mask_ct.sum(dim=timestr)/(nt)
#    mask_ct=mask_c*mask_t
#    mask_ct_p=mask_t.sum(dim=timestr) #/(nt)
#    ridgfinal=mask_ct_p                             
    return(ridged_ice)

################################################
################################################

if __name__ == "__main__":
    # If this script is called directly without RIOengine_NOCOS-py, do everything necessary using config from config_RIOcalc.yml
    from read_config import read_configfile
    from read_ice_data import read_ice_data
    from output_RID import save_RID_toNetCDF
    
    configs=read_configfile()
    icedata=read_ice_data(configs)
    riodata=calc_RID_multicat(icedata,configs)
    save_RID_toNetCDF(riodata,icedata,configs)
