
def save_RID_toNetCDF(ridg_data,icedata,configs):

    import numpy as np
    import datetime
    import os
    
    # RIDmethod as string
    rid_method=[i for i in configs['RIDGE_method'] if configs['RIDGE_method'][i]==True][0]
    # Create the output filename
    if configs['output']['filename_automatic']==True:
        outfile=configs['output']['output_folder']+'/RID-'+rid_method+'_'+os.path.basename(configs['ice_filename']).replace('*','_XXX').replace('?','X')
    else:
        outfile=configs['output']['output_folder']+'/'+configs['output']['filename']
    
    # Make an empty dataset with basic coordinates for the netcdf file, copied from the icedata-file
    timespace_coords=[configs["coordinates"]["lon_name"], configs["coordinates"]["lat_name"], configs["coordinates"]["time_name"]]
    ridds=icedata[timespace_coords] # Create an "empty" DataSet with same time and space dimentions as in icedata

    # Add coordinate for shipclasses
#    shipclasses = configs['output']['shipclasses']
#    ridds.coords["shipclass"] =  np.array(configs['output']['shipclassNUMs'], dtype='int32') # Would be nice with ship classes as string values, but cdo cannot handle that. Therefore we use integer values.
    
    # Add the RID variable with dimensions, attributes and data from riddata
    rid_dims = (icedata.sic_c.dims[2],icedata.sic_c.dims[3]) # (time, shipclass, y, x)
    ridds["RID"] = (rid_dims, ridg_data)
    rid_attrs={'long_name':'ridging probability',
                'units':'[]',
                'comment':"Ridging probability based on ice thickness and concentration ",
                }
    ridds.RID.attrs=rid_attrs

    ## Try to correct the attribute 'coordinates' of the RIO variable in netcdf. For DMI data, xarray's automatic does it wrongly. But this doesn't work:
    #rio_coords=configs["coordinates"]["lon_name"] +' '+ configs["coordinates"]["lat_name"] +' shipclass '+ configs["coordinates"]["time_name"]
    #riods["RIO"] = (rio_dims, riofinal, {'coordinates':rio_coords})
    #riods.RIO.encoding["coordinates"]=rio_coords
    
    # Set global attributes of the netcdf file
    ridds.attrs={
    'title':configs['output']['title'],
    'histroy':'Created by ridg_engine_NOCOS.py on '+datetime.datetime.today().strftime("%Y-%m-%d"),
    'description':'Used ridging calculation method: '+rid_method ,
    'institution':"Marine Systems Deprtment at TalTech, MSI",
    'references':'-'
    }
    
    # Write netcdf file
    ridds.to_netcdf(outfile)
#, unlimited_dims=configs["coordinates"]["time_name"], encoding={'RID':{'_FillValue':np.nan},'time':{"dtype": "double", 'units': "days since 1900-01-01 00:00:00"}})
    print("RIDGING output written to: "+outfile)


def plot_RID(ridg_data,icedata,configs):

    import matplotlib.pyplot as plt
    import numpy as np
    import datetime
    import os
        
        #print(ridg_data)
    plt.imshow(ridg_data, cmap='Blues', origin='lower',vmin=0., vmax=1. )
    plt.title('Ridged Ice Distribution')
    plt.colorbar(label='Ridged Ice Probability')
    plt.xticks([])  # Remove x-axis ticks
    plt.yticks([])  # Remove y-axis ticks
    plt.gcf().set_facecolor('#F0F0F0')  # Use a hex code for light gray
    plt.savefig('figure_plot.png', dpi=300, bbox_inches='tight')
    return
