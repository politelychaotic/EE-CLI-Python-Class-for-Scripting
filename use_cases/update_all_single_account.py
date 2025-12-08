from py_ee_cli import EE_CLI


if __name__ == '__main__':
    account = ""            # Reseller account ID
    username = ""           # Your user email
    password = ""           # Your user password
    my_cli = EE_CLI(account_id=account, username=username, password=password)


    # settings and options
    setting = ""               # What setting are we updating?
    option = ""                # What result do we expect on successful update?
    set_value = ""             # What do we want to set the setting's value to? 
    key = ""                   # Key for successful update

    account = ""  #Sub account ID

    
    my_cli.switch_account(account)
    all_cameras = my_cli.get_all_cams()
    unknown, unmatched, matched = my_cli.get_all_camera_settings_by_esn(cameras=all_cameras, setting=setting, option=option, key=key)              # Checks all camera settings
    unknown, failed, passed = my_cli.update_cameras_by_esn(camera_list=unmatched, setting=setting, set_value=set_value, option=option)             # Updates cameras that do not match setting we are checking
        
    my_cli.update_dict(my_cli.current_account, my_cli.current_account_list)                                                                        # Update dictionary 
    my_cli.create_json_report(f"{account}_{setting}_report.json")                                                                                  # Write dictionary to report file
