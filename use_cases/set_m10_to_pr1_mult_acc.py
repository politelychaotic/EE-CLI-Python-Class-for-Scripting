from py_ee_cli import RunCLI


###########################################################################################
#                                                                                         #
# This script uses the RunCLI class to change M10 cameras across sub-accounts -> PR1      #
#                                                                                         #
###########################################################################################



if __name__ == '__main__':
    account = input("Enter account ID: ")
    username = input("Enter Username: ")
    password = input("Enter Password: ")
    my_cli = RunCLI(account_id=account, username=username, password=password)


    #my_cli.login()
    my_cli.get_accounts()
    

    for i in range(len(my_cli.account_list)):
        my_cli.switch_account_from_list()
        all_cameras = my_cli.get_all_cams()

        unknown_settings, unmatched, matched = my_cli.get_all_camera_settings_by_esn(cameras=all_cameras, setting=cloud_retention, option=cloud_option, key=cloud_key)
        unknown_status, failed, passed = my_cli.update_cameras_by_esn(camera_list=matched, setting=pr1_setting, set_value=pr1_enable, option=pr1_option)
