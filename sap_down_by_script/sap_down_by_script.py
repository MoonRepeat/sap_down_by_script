import time
import yaml

import library as lib

if __name__ == '__main__':
    # Read the "sap_setting.yaml" file for sap_setting dict
    with open('.\\sap_setting.yaml', 'r', encoding='utf-8') as f:
        sap_setting = yaml.load(f, Loader=yaml.FullLoader)

    # Read the "run_sap_script" list in sap_setting dict
    # and excute them in order
    for i, operation in enumerate(sap_setting['run_sap_script'], start=1):
        # Read the script setting file to be executed
        # and save it script_setting dic
        with open(f'{sap_setting["sap_script_path"]}{operation}.yaml',
                  'r', encoding='utf-8') as f:
            script_setting = yaml.load(f, Loader=yaml.FullLoader)
        
        # Create an object with the name of the sap script to be excuted
        locals()[operation] = lib.SapDown(operation, 
                                          script_setting, 
                                          sap_setting=sap_setting)
        print("===== {}/{} Start -{}- Script ====="\
            .format(str(i), len(sap_setting['run_sap_script']), operation))

        # If the created object needs a reference DataFrame,
        # it copies my DataFrame of another object.
        if len(script_setting['reference_data']) != 0:
            locals()[operation].set_reference_df(
                locals()[script_setting['reference_data']].get_my_df()
                )
        
        # Make folder for downloading files
        lib.SapUtils.make_file_path(script_setting['file_save_path'])
        lib.SapUtils.make_file_path(sap_setting['tempfile_save_path'])
        
        # Delete the old files
        lib.SapUtils.delete_file(file_path=sap_setting['tempfile_save_path'],
                                 file_all=True)
        lib.SapUtils.delete_file(file_path=script_setting['file_save_path'],
                                 file_all=True)
        
        # Restart SAP Client
        locals()[operation].restart_sap_client()
        
        # Run SAP Script and download files
        file_name_list = locals()[operation].down_file_sap()
    
    locals()[sap_setting['run_sap_script'][0]].end_sap_client()
    print("Run is complete.")
    time.sleep(600)