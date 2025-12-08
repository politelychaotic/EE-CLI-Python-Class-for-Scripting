from py_ee_cli import RunCLI


###########################################################################################
#                                                                                         #
# This script uses the RunCLI class to change M10 cameras across sub-accounts -> PR1      #
#                                                                                         #
###########################################################################################



if __name__ == '__main__':
    account = ""            # Reseller account ID
    username = ""           # Your user email
    password = ""           # Your user password
    my_cli = RunCLI(account_id=account, username=username, password=password)


    # settings and options
    setting = ""               # What setting are we updating?
    option = ""                # What result do we expect on successful update?
    set_value = ""             # What do we want to set the setting's value to? 
    key = ""                   # Key for successful update


    #my_cli.login()
    my_cli.get_accounts()
    

    for i in range(len(my_cli.account_list)):
        my_cli.switch_account_from_list()
        all_cameras = my_cli.get_all_cams()

        unknown_settings, unmatched, matched = my_cli.get_all_camera_settings_by_esn(cameras=all_cameras, setting=setting, option=option, key=key)
        unknown_status, failed, passed = my_cli.update_cameras_by_esn(camera_list=unmatched, setting=setting, set_value=set_value, option=option)      # Change list used depending on need
