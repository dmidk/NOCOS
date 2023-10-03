# -*- coding: utf-8 -*-
"""

@author: Andrea Gierisch, DMI (original RIO)
modifyed from RIO for LF by Imke Sievers, DMI
"""
# Load LF functions
from read_config import read_configfile
from datetime import date, timedelta
import psutil
import numpy as np
import os
import xarray as xr
import pandas as pd
from subprocess import DEVNULL, STDOUT, check_call,call
import gc
import time # for sleep and cputime measurement
# Read config file
configs=read_configfile() # Reads config_LFcalc_default.yml


current=date(configs['selectdata']['start_year'],configs['selectdata']['start_month'],configs['selectdata']['start_day'])
end_date=date(configs['selectdata']['end_year'],configs['selectdata']['end_month'],configs['selectdata']['end_day'])


def daterange(start_date, end_date):
        for n in range(int((end_date - start_date).days)):
            yield start_date + timedelta(n)

print('current date =',current)
print('end date =',end_date)

while current<end_date:
    # Read ice data

    if check_call(["ls", "runNOCOS_LF"], stdout=DEVNULL, stderr=STDOUT)!=0:
        check_call(["mkdir" ,"runNOCOS_LF"])
        print('made new run dir')

    if call("test -e".format("runNOCOS_LF/*.nc"),shell=True, stdout=DEVNULL, stderr=STDOUT)==0:
        call("rm runNOCOS_LF/*.nc",shell=True)


    for single_date in daterange(current, current+timedelta(7)):
        datenow=single_date.strftime(configs['selectdata']['Dformat'])
        if check_call(["ls " + configs['path']+configs['ice_filename']+datenow+"*.nc"],shell=True, stdout=DEVNULL, stderr=STDOUT)==0:
            check_call(["ln -s "+configs['path']+configs['ice_filename']+datenow+"*.nc runNOCOS_LF/."],shell=True, stdout=DEVNULL, stderr=STDOUT)
        else:
            print('the files you are trying to proccess are not existing, please check you *.yml file ')

    if check_call(["ls /home/imksie/runNOCOS/runNOCOS_LF/*.nc"],shell=True, stdout=DEVNULL, stderr=STDOUT)==0:
        print('open files')
        icedataraw = xr.open_mfdataset("runNOCOS_LF/*.nc")
    relevantvars_list=[configs['variables']['siconc_name'], configs['variables']['siu_name'], configs['variables']['siv_name']]
    rename_vardict={configs['variables']['siconc_name']:'siconc', configs['variables']['siu_name']:'siu', configs['variables']['siv_name']:'siv'}
    icedataraw.close()
    icedata = icedataraw[relevantvars_list].rename(rename_vardict)

    print('RAM memory % used:', psutil.virtual_memory()[2])
    # Create the output filename
    if configs['output']['filename_automatic']==True:
        outfile=configs['output']['output_folder']+'/LF-_'+os.path.basename(configs['ice_filename']).replace('*','XXX').replace('?','X')+current.strftime(configs['selectdata']['Dformat'])+'.nc'
    else:
        outfile=configs['output']['output_folder']+'/'+current.strftime(configs['selectdata']['Dformat'])+configs['output']['filename']+'.nc'

    # Make an empty dataset with basic coordinates for the netcdf file, copied from the icedata-file
    lfdata=icedata.siconc.isel(time=1)
    #print('RAM memory % used before calcLF:', psutil.virtual_memory()[2])
    ############################calculatet LF area##################################################
    ny = icedata.siu.shape[1] # Number of grid points in y-direction
    nx = icedata.siu.shape[2] # Number of grid points in x-direction
    # Set up an empty output array
    lffinal=np.array(np.nan*np.zeros([ny,nx]))
    cputime=time.time()
    # 7 days are needed to eusre that no data point in the central arctic are included
    d1=current+timedelta(7)
    #calculating velociety
    speed=np.sqrt((icedata.siv.sel(time=slice(str(current), str(d1))).where(icedata.siconc.sel(time=slice(str(current), str(d1)))>0.15)**2 +icedata.siu.sel(time=slice(str(current), str(d1))).where(icedata.siconc.sel(time=slice(str(current), str(d1)))>0.15)**2)/2)
    #mask spans all time steps within the one week fom which the landfast ice is calculated
    mask=np.zeros(speed.shape)+1
    #speed < 5.e-04 is the first condition for landfast ice
    mask[speed.values>=5.e-04]=np.nan
    #sic > 15% is the condition condition for landfast ice
    mask[np.isnan(icedata.siconc.values)]=np.nan
    mask[icedata.siconc.sel(time=slice(str(current), str(d1))).values<0.15]=np.nan
    Mmask=np.nansum(mask[:,:,:],0)
    #timsepts within 7 days
    ll=speed.shape[0]
    #the first and second conditions need to be fullfild over 7 days
    Mmask[Mmask<ll]=np.nan
    Mmask[~np.isnan(Mmask)]=1
    lffinal[:,:]=Mmask
    print("Calculation time: "+str(int(time.time()-cputime))+' s')
    del d1
    del cputime
    del ny
    del nx
    del(ll)
    del(mask)
    del(speed)
    del Mmask

    lfdata.values=lffinal #calcLF(icedata,configs,current)
    #print('RAM memory % used after calcLF:', psutil.virtual_memory()[2])
    lfdata=lfdata.rename('LFmask')
    lfdata.attrs['long_name']='landfast ice mask'
    #print('RAM memory % before make ds:', psutil.virtual_memory()[2])
    ds = xr.Dataset({'LFmask':lfdata})   # enter data here
    #print('RAM memory % used after make ds:', psutil.virtual_memory()[2])
    # Write netcdf file
    ds=ds.drop('ULON')
    ds=ds.drop('ULAT')
    #print(ds)
    lfdata.close()
    #print('RAM memory % before save ds:', psutil.virtual_memory()[2])
    ds.to_netcdf(outfile, unlimited_dims=configs["coordinates"]["time_name"],encoding={'time':{"dtype": "double", 'units': "days since 1900-01-01 00:00:00"}})
    #print('RAM memory % after save ds:', psutil.virtual_memory()[2])
    ds.close()
    #print('RAM memory % after close ds:', psutil.virtual_memory()[2])
    del lffinal
    del lfdata
    del ds
    del icedata
    del datenow
    del relevantvars_list
    del rename_vardict
    del icedataraw 
    gc.collect()
    print('RAM memory % used after del:', psutil.virtual_memory()[2])
    current=current+timedelta(configs['selectdata']['freuqancy'])
