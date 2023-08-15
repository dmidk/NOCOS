# -*- coding: utf-8 -*-
"""

@author: gierisch
"""
from read_config import read_configfile
from read_ice_data import read_ice_data
configs=read_configfile()
icedata=read_ice_data(configs)


#import sys
#def calcRIO_multicat_Lthick(icedata,configs):

import numpy as np
#from netCDF4 import Dataset
import warnings
#import datetime
import time # for sleep and cputime measurement
import sys # For flushing of buffer to stdout

############################################

sithicat= icedata.siitdthick
siconcat= icedata.siitdconc 
#siagecat= f.variables[siagecat_varname][:,:,:,:]      
#salincat= f.variables[salincat_varname][:,:,:,:]   

#    salMY = 5.0 # ppt



#filename='eO025L7501_2005_03.nc'
#    shipclasses = ['PC1','PC2','PC3','PC4','PC5','PC6','PC7','1ASuper','1A','1B','1C','noclass'] #['PC1','PC5'] 
shipclasses = configs['output']['shipclasses'] 


############################################
# Define functions
############################################

def addopenwater(siconcat,sithicat,*argv): # argv could be siagecat
    cww = np.array([1.-np.sum(siconcat)]+[x for x in siconcat])
    hww = np.array([0.]+[x for x in sithicat])
    if len(argv) == 0 :
        return (cww,hww)
    elif len(argv) == 1 :
        ageww = np.array([0.]+[x for x in argv[0]])
        return (cww,hww,ageww)
    else:
        raise RuntimeError('The function ADDOPENWATER can only be called with 2 or 3 arguments, not with: '+str(len(argv)))

#------------------------------------------------

# This is according to MSC Circ1
def polaris(dattype,shipclass,season,*argv):
    if dattype == 'mod':
        if not len(argv)==3:
            raise RuntimeError("If DATTYPE is 'mod', then you have to provide 3 additional arguments: CCAT, HCAT and SalCAT (AgeCAT).")
        else:
            ccat=argv[0]
            hcat=argv[1]
            #agecat=argv[2]
            salcat=argv[2]                    
        if np.sum(ccat) < 0.99:
            raise RuntimeError("The ice concentrations in CCAT do not sum up to 100%. Did you forget to include the open water fraction?")
    elif dattype == 'modnoage':
        if not len(argv)==2:
            raise RuntimeError("If DATTYPE is 'mod', then you have to provide 2 additional arguments: CCAT and HCAT.")
        else:
            ccat=argv[0]
            hcat=argv[1]
        if np.sum(ccat) < 0.99:
            raise RuntimeError("The ice concentrations in CCAT do not sum up to 100%. Did you forget to include the open water fraction?")
    else:
        print(dattype)
        raise ValueError("DATTYPE has to be one of ['mod','modnoage']")
                    
    if not (shipclass in ['PC1','PC2','PC3','PC4','PC5','PC6','PC7','1ASuper','1A','1B','1C','noclass']):
        raise ValueError("shipclass has to be one of ['PC1','PC2','PC3','PC4','PC5','PC6','PC7','1ASuper','1A','1B','1C','noclass']")
    # http://joshuakugler.com/archives/30-BetweenDict,-a-Python-dict-for-value-ranges.html
    class BetweenDict(dict):
        def __init__(self, d = {}):
            for k,v in d.items():
                self[k] = v
    
        def lookup(self, key):
            for k, v in self.items():
                if k[0] <= key < k[1]:
                    return v
            warnings.warn("Key '%s' is not between any values in the BetweenDict" % key)
            return {np.nan:np.nan} # Return a dictionary so that rv.lookup(thi[icl])[shipclass] will raise a KeyError.
#AGI            raise KeyError("Key '%s' is not between any values in the BetweenDict" % key)
    
        def setrange(self, key, value):
            try:
                if len(key) == 2:
                    if key[0] < key[1]:
                        dict.__setitem__(self, (key[0], key[1]), value)
                    else:
                        raise RuntimeError('First element of a BetweenDict key '
                                           'must be strictly less than the '
                                           'second element')
                else:
                    raise ValueError('Key of a BetweenDict must be an iterable '
                                     'with length two')
            except TypeError:
                raise TypeError('Key of a BetweenDict must be an iterable '
                                 'with length two')
    
        def __contains__(self, key):
            try:
                return bool(self[key]) or True
            except KeyError:
                return False
    
    if dattype == 'mod':
    # RIV standard (decayed/summer conditions are never used, because state of decay has to be proven by captain)
        riv = BetweenDict()
        riv.setrange([0.  ,0.001],{'PC1':[3],'PC2':[3],'PC3':[3],'PC4':[3],'PC5':[3],  'PC6':[3],'PC7':[3],  '1ASuper':[3],'1A':[3],'1B':[3],'1C':[3],'noclass':[3]}) # no ice
        riv.setrange([0.001,0.10],{'PC1':[3],'PC2':[3],'PC3':[3],'PC4':[3],'PC5':[3],  'PC6':[2],'PC7':[2],  '1ASuper':[2],'1A':[2],'1B':[2],'1C':[2],'noclass':[1]}) # new ice
        riv.setrange([0.10,0.15],{'PC1':[3],'PC2':[3],'PC3':[3],'PC4':[3],'PC5':[3],  'PC6':[2],'PC7':[2],  '1ASuper':[2],'1A':[2],'1B':[2],'1C':[1],'noclass':[0]}) # grey ice
        riv.setrange([0.15,0.30],{'PC1':[3],'PC2':[3],'PC3':[3],'PC4':[3],'PC5':[3],  'PC6':[2],'PC7':[2],  '1ASuper':[2],'1A':[2],'1B':[1],'1C':[0],'noclass':[-1]}) # grey-white
        riv.setrange([0.30,0.50],{'PC1':[2],'PC2':[2],'PC3':[2],'PC4':[2],'PC5':[2],  'PC6':[2],'PC7':[1],  '1ASuper':[2],'1A':[1],'1B':[0],'1C':[-1],'noclass':[-2]}) # thin FY 1
        riv.setrange([0.50,0.70],{'PC1':[2],'PC2':[2],'PC3':[2],'PC4':[2],'PC5':[2],  'PC6':[1],'PC7':[1],  '1ASuper':[1],'1A':[0],'1B':[-1],'1C':[-2],'noclass':[-3]}) # thin FY 2
        riv.setrange([0.70,1.00],{'PC1':[2],'PC2':[2],'PC3':[2],'PC4':[2],'PC5':[1],  'PC6':[1],'PC7':[0],  '1ASuper':[0],'1A':[-1],'1B':[-2],'1C':[-3],'noclass':[-4]}) # medium FY < 1m
        riv.setrange([1.00,1.20],{'PC1':[2],'PC2':[2],'PC3':[2],'PC4':[2],'PC5':[1],  'PC6':[0],'PC7':[-1], '1ASuper':[-1],'1A':[-2],'1B':[-3],'1C':[-4],'noclass':[-5]}) # medium FY > 1m
        riv.setrange([1.20,2.00],{'PC1':[2,2],'PC2':[2,1],'PC3':[2,1],'PC4':[1,0],'PC5':[0,-1],  'PC6':[-1,-2],'PC7':[-2,-3],  '1ASuper':[-2,-3],'1A':[-3,-4],'1B':[-4,-5],'1C':[-5,-6],'noclass':[-6,-7]}) # thick FY / SY / MY<
        riv.setrange([2.00,2.50],{'PC1':[2,1],'PC2':[1,1],'PC3':[1,0],'PC4':[0,-1],'PC5':[-1,-2], 'PC6':[-2,-3],'PC7':[-3,-3],  '1ASuper':[-3,-4],'1A':[-4,-5],'1B':[-5,-6],'1C':[-6,-7],'noclass':[-7,-8]}) # SY / SY / MY<
        riv.setrange([2.50,99.9],{'PC1':[1],'PC2':[0],'PC3':[-1],'PC4':[-2],'PC5':[-2],  'PC6':[-3],'PC7':[-3],  '1ASuper':[-4],'1A':[-5],'1B':[-6],'1C':[-8],'noclass':[-8]}) # MY

        #riv.setrange([thick FY],{'PC1':2,      'PC2':2,      'PC3':2      ,'PC4':1      ,'PC5':0,        'PC6':-1,      'PC7':-2,        '1ASuper':-2,      '1A':-3,      '1B':-4,      '1C':-5,      'noclass':-6}) # thick FY
        #riv.setrange([SY      ],{'PC1':2,      'PC2':1,      'PC3':1      ,'PC4':0      ,'PC5':-1      ,  'PC6':-2,      'PC7':-3,        '1ASuper':-3,      '1A':-4,      '1B':-5,      '1C':-6,      'noclass':-7}) # Second year
        #riv.setrange([MY <2.5 ],{'PC1':1,      'PC2':1,      'PC3':0      ,'PC4':-1     ,'PC5':-2,        'PC6':-3,      'PC7':-3,        '1ASuper':-4,      '1A':-5,      '1B':-6,      '1C':-7,      'noclass':-8}) # MY < 2.5
       
        rv = riv

        ## riv = BetweenDict()
        ## riv.setrange([0.  ,0.01],{'PC1':3,'PC2':3,'PC3':3,'PC4':3,'PC5':3,  'PC6':3,'PC7':3,  '1ASuper':3,'1A':3,'1B':3,'1C':3,'noclass':3}) # no ice
        ## riv.setrange([0.01,0.10],{'PC1':3,'PC2':3,'PC3':3,'PC4':3,'PC5':3,  'PC6':2,'PC7':2,  '1ASuper':2,'1A':2,'1B':2,'1C':2,'noclass':1}) # new ice
        ## riv.setrange([0.10,0.15],{'PC1':3,'PC2':3,'PC3':3,'PC4':3,'PC5':3,  'PC6':2,'PC7':2,  '1ASuper':2,'1A':2,'1B':2,'1C':1,'noclass':0}) # grey ice
        ## riv.setrange([0.15,0.30],{'PC1':3,'PC2':3,'PC3':3,'PC4':3,'PC5':3,  'PC6':2,'PC7':2,  '1ASuper':2,'1A':2,'1B':1,'1C':0,'noclass':-1}) # grey-white
        ## riv.setrange([0.30,0.50],{'PC1':2,'PC2':2,'PC3':2,'PC4':2,'PC5':2,  'PC6':2,'PC7':1,  '1ASuper':2,'1A':1,'1B':0,'1C':-1,'noclass':-2}) # thin FY 1
        ## riv.setrange([0.50,0.70],{'PC1':2,'PC2':2,'PC3':2,'PC4':2,'PC5':2,  'PC6':1,'PC7':1,  '1ASuper':1,'1A':0,'1B':-1,'1C':-2,'noclass':-3}) # thin FY 2
        ## riv.setrange([0.70,1.00],{'PC1':2,'PC2':2,'PC3':2,'PC4':2,'PC5':1,  'PC6':1,'PC7':0,  '1ASuper':0,'1A':-1,'1B':-2,'1C':-3,'noclass':-4}) # medium FY < 1m
        ## riv.setrange([1.00,1.20],{'PC1':2,'PC2':2,'PC3':2,'PC4':2,'PC5':1,  'PC6':0,'PC7':-1,  '1ASuper':-1,'1A':-2,'1B':-3,'1C':-4,'noclass':-5}) # medium FY > 1m
        ## riv.setrange([thick FY],{'PC1':2,      'PC2':2,      'PC3':2      ,'PC4':1      ,'PC5':0,        'PC6':-1,      'PC7':-2,        '1ASuper':-2,      '1A':-3,      '1B':-4,      '1C':-5,      'noclass':-6}) # thick FY
        ## riv.setrange([SY      ],{'PC1':2,      'PC2':1,      'PC3':1      ,'PC4':0      ,'PC5':-1      ,  'PC6':-2,      'PC7':-3,        '1ASuper':-3,      '1A':-4,      '1B':-5,      '1C':-6,      'noclass':-7}) # Second year
        ## riv.setrange([MY <2.5 ],{'PC1':1,      'PC2':1,      'PC3':0      ,'PC4':-1     ,'PC5':-2,        'PC6':-3,      'PC7':-3,        '1ASuper':-4,      '1A':-5,      '1B':-6,      '1C':-7,      'noclass':-8}) # MY < 2.5
        ## riv.setrange([MY thick],{'PC1':1,'PC2':0,'PC3':-1,'PC4':-2,'PC5':-2,  'PC6':-3,'PC7':-3,  '1ASuper':-4,'1A':-5,'1B':-6,'1C':-8,'noclass':-8}) # MY
    
    else: # modnoage 
        # RV summer (old values)
        rvs = BetweenDict()
#                rvs.setrange([0.  ,0.01],{'PC1':3,'PC2':3,'PC3':3,'PC4':3,'PC5':3,  'PC6':3,'PC7':3,  '1ASuper':3,'1A':3,'1B':3,'1C':3,'noclass':3}) # no ice
#                rvs.setrange([0.01,0.10],{'PC1':3,'PC2':3,'PC3':3,'PC4':3,'PC5':3,  'PC6':2,'PC7':2,  '1ASuper':2,'1A':2,'1B':2,'1C':2,'noclass':1}) # new ice
#                rvs.setrange([0.10,0.15],{'PC1':3,'PC2':3,'PC3':3,'PC4':3,'PC5':3,  'PC6':2,'PC7':2,  '1ASuper':2,'1A':2,'1B':2,'1C':1,'noclass':0}) # grey ice
#                rvs.setrange([0.15,0.30],{'PC1':3,'PC2':3,'PC3':3,'PC4':3,'PC5':3,  'PC6':2,'PC7':2,  '1ASuper':2,'1A':2,'1B':1,'1C':0,'noclass':-1}) # grey-white
#                rvs.setrange([0.30,0.50],{'PC1':2,'PC2':2,'PC3':2,'PC4':2,'PC5':2,  'PC6':2,'PC7':1,  '1ASuper':2,'1A':1,'1B':0,'1C':-1,'noclass':-2}) # thin FY 1
#                rvs.setrange([0.50,0.70],{'PC1':2,'PC2':2,'PC3':2,'PC4':2,'PC5':2,  'PC6':1,'PC7':1,  '1ASuper':1,'1A':0,'1B':-1,'1C':-2,'noclass':-2}) # thin FY 2
#                rvs.setrange([0.70,0.95],{'PC1':2,'PC2':2,'PC3':2,'PC4':2,'PC5':2,  'PC6':2,'PC7':1,  '1ASuper':1,'1A':0,'1B':-1,'1C':-1,'noclass':-2}) # medium FY 1
#                rvs.setrange([0.95,1.20],{'PC1':2,'PC2':2,'PC3':2,'PC4':2,'PC5':2,  'PC6':1,'PC7':0,  '1ASuper':0,'1A':-1,'1B':-1,'1C':-2,'noclass':-2}) # medium FY 2
#                rvs.setrange([1.20,2.00],{'PC1':2,'PC2':2,'PC3':2,'PC4':1,'PC5':1,  'PC6':0,'PC7':-1,  '1ASuper':-1,'1A':-2,'1B':-2,'1C':-3,'noclass':-3}) # thick FY
#                rvs.setrange([2.00,2.50],{'PC1':2,'PC2':1,'PC3':1,'PC4':0,'PC5':-1,  'PC6':-2,'PC7':-3,  '1ASuper':-3,'1A':-4,'1B':-4,'1C':-4,'noclass':-5}) # Second year ice
#                rvs.setrange([2.50,3.00],{'PC1':1,'PC2':1,'PC3':0,'PC4':-1,'PC5':-2,  'PC6':-3,'PC7':-3,  '1ASuper':-4,'1A':-4,'1B':-5,'1C':-5,'noclass':-6}) # light MY
#                rvs.setrange([3.00,99.9],{'PC1':1,'PC2':0,'PC3':-1,'PC4':-2,'PC5':-2,  'PC6':-3,'PC7':-3,  '1ASuper':-4,'1A':-4,'1B':-5,'1C':-6,'noclass':-6}) # heavy MY
        
        # RV winter (old values)
#                rvw = BetweenDict()
#                rvw.setrange([0.  ,0.01],{'PC1':3,'PC2':3,'PC3':3,'PC4':3,'PC5':3,  'PC6':3,'PC7':3,  '1ASuper':3,'1A':3,'1B':3,'1C':3,'noclass':3}) # no ice
#                rvw.setrange([0.01,0.10],{'PC1':3,'PC2':3,'PC3':3,'PC4':3,'PC5':3,  'PC6':2,'PC7':2,  '1ASuper':2,'1A':2,'1B':2,'1C':2,'noclass':1}) # new ice
#                rvw.setrange([0.10,0.15],{'PC1':3,'PC2':3,'PC3':3,'PC4':3,'PC5':3,  'PC6':2,'PC7':2,  '1ASuper':2,'1A':2,'1B':2,'1C':1,'noclass':0}) # grey ice
#                rvw.setrange([0.15,0.30],{'PC1':3,'PC2':3,'PC3':3,'PC4':3,'PC5':3,  'PC6':2,'PC7':2,  '1ASuper':2,'1A':2,'1B':1,'1C':0,'noclass':-1}) # grey-white
#                rvw.setrange([0.30,0.50],{'PC1':2,'PC2':2,'PC3':2,'PC4':2,'PC5':2,  'PC6':2,'PC7':1,  '1ASuper':2,'1A':1,'1B':0,'1C':-1,'noclass':-2}) # thin FY 1
#                rvw.setrange([0.50,0.70],{'PC1':2,'PC2':2,'PC3':2,'PC4':2,'PC5':2,  'PC6':1,'PC7':1,  '1ASuper':1,'1A':0,'1B':-1,'1C':-2,'noclass':-2}) # thin FY 2
#                rvw.setrange([0.70,0.95],{'PC1':2,'PC2':2,'PC3':2,'PC4':2,'PC5':2,  'PC6':1,'PC7':0,  '1ASuper':0,'1A':-1,'1B':-2,'1C':-2,'noclass':-3}) # medium FY 1
#                rvw.setrange([0.95,1.20],{'PC1':2,'PC2':2,'PC3':2,'PC4':2,'PC5':1,  'PC6':0,'PC7':-1,  '1ASuper':-1,'1A':-2,'1B':-3,'1C':-3,'noclass':-3}) # medium FY 2
#                rvw.setrange([1.20,2.00],{'PC1':2,'PC2':2,'PC3':2,'PC4':1,'PC5':0,  'PC6':-1,'PC7':-2,  '1ASuper':-2,'1A':-3,'1B':-3,'1C':-4,'noclass':-4}) # thick FY
#                rvw.setrange([2.00,2.50],{'PC1':2,'PC2':1,'PC3':1,'PC4':0,'PC5':-1,  'PC6':-2,'PC7':-3,  '1ASuper':-3,'1A':-4,'1B':-4,'1C':-4,'noclass':-5}) # Second year ice
#                rvw.setrange([2.50,3.00],{'PC1':1,'PC2':1,'PC3':0,'PC4':-1,'PC5':-2,  'PC6':-3,'PC7':-3,  '1ASuper':-4,'1A':-4,'1B':-5,'1C':-5,'noclass':-6}) # light MY
#                rvw.setrange([3.00,99.9],{'PC1':1,'PC2':0,'PC3':-1,'PC4':-2,'PC5':-2,  'PC6':-3,'PC7':-3,  '1ASuper':-4,'1A':-4,'1B':-5,'1C':-6,'noclass':-6}) # heavy MY
        
        rvw = BetweenDict()
        rvw.setrange([0.  ,0.01],{'PC1':3,'PC2':3,'PC3':3,'PC4':3,'PC5':3,  'PC6':3,'PC7':3,  '1ASuper':3,'1A':3,'1B':3,'1C':3,'noclass':3}) # no ice
        rvw.setrange([0.01,0.10],{'PC1':3,'PC2':3,'PC3':3,'PC4':3,'PC5':3,  'PC6':2,'PC7':2,  '1ASuper':2,'1A':2,'1B':2,'1C':2,'noclass':1}) # new ice
        rvw.setrange([0.10,0.15],{'PC1':3,'PC2':3,'PC3':3,'PC4':3,'PC5':3,  'PC6':2,'PC7':2,  '1ASuper':2,'1A':2,'1B':2,'1C':1,'noclass':0}) # grey ice
        rvw.setrange([0.15,0.30],{'PC1':3,'PC2':3,'PC3':3,'PC4':3,'PC5':3,  'PC6':2,'PC7':2,  '1ASuper':2,'1A':2,'1B':1,'1C':0,'noclass':-1}) # grey-white
        rvw.setrange([0.30,0.50],{'PC1':2,'PC2':2,'PC3':2,'PC4':2,'PC5':2,  'PC6':2,'PC7':1,  '1ASuper':2,'1A':1,'1B':0,'1C':-1,'noclass':-2}) # thin FY 1
        rvw.setrange([0.50,0.70],{'PC1':2,'PC2':2,'PC3':2,'PC4':2,'PC5':2,  'PC6':1,'PC7':1,  '1ASuper':1,'1A':0,'1B':-1,'1C':-2,'noclass':-3}) # thin FY 2
        rvw.setrange([0.70,1.00],{'PC1':2,'PC2':2,'PC3':2,'PC4':2,'PC5':1,  'PC6':1,'PC7':0,  '1ASuper':0,'1A':-1,'1B':-2,'1C':-3,'noclass':-4}) # medium FY < 1m
        rvw.setrange([1.00,1.20],{'PC1':2,'PC2':2,'PC3':2,'PC4':2,'PC5':1,  'PC6':0,'PC7':-1,  '1ASuper':-1,'1A':-2,'1B':-3,'1C':-4,'noclass':-5}) # medium FY > 1m
        rvw.setrange([1.20,2.00],{'PC1':2,      'PC2':2,      'PC3':2      ,'PC4':1      ,'PC5':0,        'PC6':-1,      'PC7':-2,        '1ASuper':-2,      '1A':-3,      '1B':-4,      '1C':-5,      'noclass':-6}) # thick FY
        rvw.setrange([2.00,2.50],{'PC1':2,      'PC2':1,      'PC3':1      ,'PC4':0      ,'PC5':-1      ,  'PC6':-2,      'PC7':-3,        '1ASuper':-3,      '1A':-4,      '1B':-5,      '1C':-6,      'noclass':-7}) # Second year
        rvw.setrange([2.50,3.00],{'PC1':1,      'PC2':1,      'PC3':0      ,'PC4':-1     ,'PC5':-2,        'PC6':-3,      'PC7':-3,        '1ASuper':-4,      '1A':-5,      '1B':-6,      '1C':-7,      'noclass':-8}) # MY < 2.5
        rvw.setrange([3.00,99.9],{'PC1':1,'PC2':0,'PC3':-1,'PC4':-2,'PC5':-2,  'PC6':-3,'PC7':-3,  '1ASuper':-4,'1A':-5,'1B':-6,'1C':-8,'noclass':-8}) # MY
    
        if season in ['w','winter']:
            rv = rvw
        elif season in ['s','summer']:
            rv = rvs
        else:
            raise ValueError("season has to be one of ['winter','summer','w','s']")       

    if dattype == 'mod':
        # Part for MOD with siagecat
        ##############
        thi=hcat #+ scat (we do not add snow thickness anymore because RIO definition was developed without taking care of snow)
        # RIO = (C1xRV1)+(C2xRV2)+(C3xRV3)+...(CnxRVn)
        rio = 0.
        for icl in range(len(ccat)): # 5 model ice categories
            try:
                salindex=not(min(1,int(np.floor(salcat[icl]/salMY)))) #0: saltier than salMY=> FY 1: fresh => less saline than salMY => MY  [more exactly: for 120-200 cm: FY or SY, for 200-150cm: SY or MY]   
                #for ice age: 
                #ageindex=min(2,int(np.floor(agecat[icl]))) # 0=FY, 1=SY, 2=MY
                rv_all =  2*rv.lookup(thi[icl])[shipclass] #Set to 3 for ice age!! # lookup-table returns lists with 1 or 2 elements. We want to duplicate (times 2) all 1-element lists, because the respectice RV is valid for ALL ice ages. It does not hurt to duplicate also 2-element lists.
                rio += (10.*ccat[icl]) * rv_all[salindex] # *10 because C is in ice concentration in tenths.  
                #rio += (10.*ccat[icl]) * rv_all[ageindex] # *10 because C is in ice concentration in tenths.  
            except KeyError: # This happens if POLARIS get a NaN value (because of land grid cells). Then POLARIS's lookup returns an empty dictonary.
                return np.nan # Return NaN to keep land areas masked.
        return rio
            
    if dattype == 'modnoage':
        # Part for MOD without ice age information
        ##############
        thi=hcat #+ scat (we do not add snow thickness anymore because RIO definition was developed without taking care of snow)
        # RIO = (C1xRV1)+(C2xRV2)+(C3xRV3)+...(CnxRVn)
        rio = 0.
        for icl in range(len(ccat)): # 5 model ice categories
            try:
                rio += (10.*ccat[icl]) * rv.lookup(thi[icl])[shipclass] # *10 because C is in ice concentration in tenths.        
            except KeyError: # This happens if POLARIS get a NaN value (because of land grid cells). Then POLARIS's lookup returns an empty dictonary.
                return np.nan # Return NaN to keep land areas masked.
        return rio
 
 # End functions
##################   

  

# Set up empty output array
riofinal=np.ma.array(np.nan*np.zeros([siconcat.shape[0],len(shipclasses),siconcat.shape[2],siconcat.shape[3]]),mask=1)

#########################
# Calculate RIO
########################

# Loop through time steps
for jt in range(icedata[configs['coordinates']['time_name']].shape[0]):
    print(icedata[configs['coordinates']['time_name']][jt].data)
    #Loop through ship classes
    for shipclassnr,shipclass in enumerate(shipclasses):
        print(shipclass)
    
        print("Calculating RIO...")
        sys.stdout.flush()
        cputime=time.time()
        
        # Rio calculation is much faster, if normal arrays are used instead of masked arrays.
#        siconcatnomask=siconcat.data[jt,:,:,:]
#        siconcatnomask[siconcat.mask[jt,:,:,:]]=0.
#        sithicatnomask=sithicat.data[jt,:,:,:]

        siconcatnomask=siconcat.data[jt,:,:,:].compute()
#        siconcatnomask[siconcat.mask[jt,:,:,:]]=0.
        sithicatnomask=sithicat.data[jt,:,:,:].compute()

        #siagecatnomask=siagecat.data[jt,:,:,:]     
#        salincatnomask=salincat.data[jt,:,:,:]                   

        rionomask = np.nan*np.zeros([siconcat.shape[2],siconcat.shape[3]])
        
        for jjk in range(siconcat.shape[2]):
            for jik in range(siconcat.shape[3]):
                if np.isnan(siconcatnomask[:,jjk,jik].sum()):
                    rionomask[jjk,jik]=np.nan
                elif siconcatnomask[:,jjk,jik].sum() <=0.: # If siconcat.sum == 0 : open water
                    rionomask[jjk,jik]=30.
                else:
                    #(plotcww, plothww, plotageww) = addopenwater(siconcatnomask[:,jjk,jik],sithicatnomask[:,jjk,jik],salincatnomask[:,jjk,jik])        
                    ##(plotcww, plothww, plotageww) = addopenwater(siconcatnomask[:,jjk,jik],sithicatnomask[:,jjk,jik],siagecatnomask[:,jjk,jik])            
                    #rionomask[jjk,jik]=polaris('mod',shipclass,'w',plotcww,plothww,plotageww)
                    (plotcww, plothww) = addopenwater(siconcatnomask[:,jjk,jik],sithicatnomask[:,jjk,jik])        
                    rionomask[jjk,jik]=polaris('modnoage',shipclass,'w',plotcww,plothww)                        
                    
        # Reapply mask
#        riotoplot=np.ma.array(rionomask,mask=siconcat.mask[jt,0,:,:])
        riotoplot=rionomask
        print(["Time to calculate RIO: ",str(time.time()-cputime)])
        
        riofinal[jt,shipclassnr,:,:]=riotoplot
            


################################################
################################################
#
#if __name__ == "__main__":
##    main('eO025L7501_1979-2015.nc')
#    if len(sys.argv)!=2:
#        raise RuntimeError('You need to provide a nc-file with the NEMO model output from which RIO should be calculated.')
#    else:
#        main(sys.argv[1])

