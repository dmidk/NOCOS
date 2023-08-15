# -*- coding: utf-8 -*-
"""


@author: gierisch
"""

import sys

def main(filename):

 
    
    ##############################
    # Save RIO to netCDF file
    ##############################
    
    if savedata:
          
        datatosave=np.ma.filled(riofinal)[:]   
          
        # Read en existing NetCDF data file and create a new one
        # f is the existing NetCDF file and g is the new file.
        ###########################################################
        
        f=Dataset(filename,'r') # r is for read only
        g=Dataset('RIO_'+filename,'w') # if the file exists it the file will be deleted to write on it
        
        # Set global attributes
        setattr(g,'Conventions',"CF-1.5")
        setattr(g,'histroy',"made by transform_to_RIOsalinity.py")
        setattr(g,'name','RIO_'+filename)
        setattr(g,'description',"POLARIS RIO calculated from global NEMO-LIM3 model, salinity threshold for MY ice: 5 ppt")
        setattr(g,'title',"POLARIS RIO")
        setattr(g,'institution',"Finnish Meteorological Institute")
        setattr(g,'references',"http://www.nautinst.org/filemanager/root/site_assets/forums/ice/msc.1-circ.1519_-_guidance_on_methodologies_for_assessing_operational_capabilities_and_limitations_in_ice_secretariat_1_.pdf")
    
        # Create new dimensions (number of ship classes)
        g.createDimension('ship', len(shipclasses))
        
        # copy the old dimension of the netCDF file
        print('Looping through dimensions:')
        for dimname,dim in f.dimensions.iteritems():
            print dimname
            if not(dimname in ['ncatice']): # We don't want to create dimensions ncatice and nb2
                if dim.isunlimited():
                    g.createDimension(dimname,None)
                else:
                    g.createDimension(dimname,dim.__len__())
        
        # copy the variables
        print()
        print('Looping through variables:')
        for varname,ncvar in f.variables.iteritems():
            vardim=len(ncvar.dimensions)
            # Template for RIO
            if varname=='siconcat':
                varfillvalue = None
                if '_FillValue' in ncvar.ncattrs():
                    varfillvalue=getattr(ncvar,'_FillValue')
                newvar = g.createVariable('RIO','float', ('time_counter','ship','y','x'), zlib=True, fill_value=varfillvalue)
                # set RIO attributes
                for attname in ncvar.ncattrs():  
                    setattr(newvar,'long_name','Risk Index Outcome calculated from NEMO')
                    setattr(newvar,'units','RIO')
                    setattr(newvar,'coordinates','nav_lon nav_lat')
                    setattr(newvar,'missing_value',1.e+20)
                    setattr(newvar,'comment',"Order of ship classes given in levels: "+', '.join(shipclasses))
                # Write the data
                newvar[:] = datatosave[:]  
            # Copy all other relevant variables
            if varname in ['time_counter_bnds','time_counter','nav_lon','nav_lat']:
                data=ncvar[:]
                copyvar = g.createVariable(varname,ncvar.dtype, ncvar.dimensions)
                # copy the variable attributes
                for attname in ncvar.ncattrs(): 
                    setattr(copyvar,attname,getattr(ncvar,attname)) # Attribute _FillValue has been set already when creating the variable record.
                # copy the variable data
                copyvar[:] = data[:]                
    
        f.close()
        g.close()


###############################################
###############################################

if __name__ == "__main__":
#    main('eO025L7501_1979-2015.nc')
    if len(sys.argv)!=2:
        raise RuntimeError('You need to provide a nc-file with the NEMO model output from which RIO should be calculated.')
    else:
        main(sys.argv[1])

