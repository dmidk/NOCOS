
#from read_config import read_configfile
#configs=read_configfile()

######################################################

def read_ice_data(configs):
    import xarray as xr
    print(configs['multiCAT']) 
    ds = xr.open_mfdataset(configs['ice_filename']) # Will try to infer automatically in which dimension (e.g. time) the files should be concatenated.
#    icedataraw = xr.open_mfdataset(configs['ice_filename'], concat_dim=configs['coordinates']['time_name'])


    time_slice = slice(configs['sel']['t1'], configs['sel']['t2'])  
    lon_slice=slice(configs['sel']['x1'], configs['sel']['x2'])  
    lat_slice=slice(configs['sel']['y1'], configs['sel']['y2'])  
    icedataraw=ds.sel(time_counter=time_slice,y=lat_slice, x=lon_slice)
    

    # Sanity checks
    ######################
    # ToDO: Check if all provided variable names actually exist in icedataraw
    # to be implemented
    
    # Check if NCAT matches to dimensions in icedataraw:
    if configs['multiCAT']:
        # Check siitdconc
        if icedataraw[configs['variables']['siitdconc_name']][configs['coordinates']['ncat_name']].shape[0] != configs['coordinates']['ncat']:
            raise RuntimeError("The given number for NCAT doesn't match the dimension 'ncat_name' for siitdconc_name.")
 
    
    ## Select relevant variables from input file(s) and assign them standard names
    ##########################################
    if configs['multiCAT']:
        relevantvars_list=[configs['variables']['siitdconc_name'], configs['variables']['siitdthick_name']]
        rename_vardict={configs['variables']['siitdconc_name']:'sic_c', configs['variables']['siitdthick_name']:'sit_c'}
    elif configs['multiCAT']==False:
        relevantvars_list=[configs['variables']['siconc_name'], configs['variables']['sithick_name']]
        rename_vardict={configs['variables']['siconc_name']:'sic', configs['variables']['sithick_name']:'sit'}
    
    if configs['RIDGE_method']['Lthickconc']:
        relevantvars_list.append(configs['variables']['siconc_name'])
        relevantvars_list.append(configs['variables']['sithick_name'])
    
    if configs['RIDGE_method']['Ldthick']:
        relevantvars_list.append(configs['variables']['sithick_name'])
       
    icedata = icedataraw[relevantvars_list].rename(rename_vardict)
#    icedata = icedataraw[relevantvars_list]
     
    return(icedata)
