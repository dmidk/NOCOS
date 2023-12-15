def read_configfile(*argv):
    import yaml
    
# Open the config file
######################
    if len(argv)==1:
        config_filename=argv[0]  # Given as input argument
    elif len(argv)==0:
        config_filename='conda-env_NOCOS-RIDGING.yml' # Default filename
    else:
        raise RuntimeError("READ_CONFIGFILE can only be called with zero or one argument, not with "+str(len(argv)))
        
    with open(config_filename,"r") as ymlfile:
         configs = yaml.load(ymlfile,  Loader=yaml.Loader)
         
         
    if configs['coordinates']['ncat'] == 1:
        configs['multiCAT']=False                 
    else:
        configs['multiCAT']=True     
    
    
# f) Check output settings
    if configs['output']['filename_automatic']!=True and configs['output']['filename']==None:
        raise RuntimeError("You need to set FILENAME_AUTOMATIC to True if you don't provide an output filename.")
    if configs['output']['output_folder']==None:
        configs['output']['output_folder']="."  # If no output folder is given, set it to the current working directory
    
    print("These are the configurations you have chosen:")
    print(configs)
    print()
    
    return configs

