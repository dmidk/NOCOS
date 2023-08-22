
def save_toNetcdf(riodata,icedata,configs):

    import xarray as xr
    import datetime
    import os
    
    shipclasses = configs['output']['shipclasses']
    
    if configs['output']['filename_automatic']==True:
        outfile=configs['output']['output_folder']+'/RIO_'+os.path.basename(configs['ice_filename']).replace('*','XXX').replace('?','X')
    else:
        outfile=configs['output']['output_folder']+'/'+configs['output']['filename']
    
    timespace_coords=[configs["coordinates"]["lon_name"], configs["coordinates"]["lat_name"], configs["coordinates"]["time_name"]]
    #riods=icedata[["time","TLAT","TLON"]] # Create an "empty" DataSet with same time and space dimentions as in icedata
    riods=icedata[timespace_coords] # Create an "empty" DataSet with same time and space dimentions as in icedata
    #rio_dims = icedata.siitdconc.dims # e.g. ('time', 'nc', 'nj', 'ni')
    rio_dims = (icedata.siitdconc.dims[0],'shipclass',icedata.siitdconc.dims[2],icedata.siitdconc.dims[3])
    
    riods.coords["shipclass"] =  shipclasses
    #riods.coords["shipclass"] =  np.array(shipclasses, dtype='S') # Tried as string to help ncview to read shipclass names. Doesn't help.
    
    
    #rio_coords=configs["coordinates"]["lon_name"] +' '+ configs["coordinates"]["lat_name"] +' shipclass '+ configs["coordinates"]["time_name"]
    #riods["RIO"] = (rio_dims, riofinal, {'coordinates':rio_coords})
    riods["RIO"] = (rio_dims, riodata)
    rio_attrs={'long_name':'Risk Index Outcome (POLARIS)',
                'units':'[]',
                'comment':"Ship classes given in levels: "+', '.join(shipclasses)
                }
    riods.RIO.attrs=rio_attrs
    #riods.RIO.encoding["coordinates"]=rio_coords
    
    riods.attrs={
    'title':configs['output']['title'],
    'histroy':'Created by .....py on '+datetime.datetime.today().strftime("%Y-%m-%d"),
    'description':'Used RIO calculation method: '+[i for i in configs['RIOmethod'] if configs['RIOmethod'][i]==True][0]+'; number of ice categories: '+str(configs['coordinates']['ncat']),
    'institution':"Finnish and Danish Meteorological Institutes, FMI/DMI",
    'references':'https://www.nautinst.org/uploads/assets/uploaded/2f01665c-04f7-4488-802552e5b5db62d9.pdf'
    }
    
    riods.to_netcdf(outfile, unlimited_dims=configs["coordinates"]["time_name"], encoding={'time':{"dtype": "double", 'units': "days since 1900-01-01 00:00:00"}})
