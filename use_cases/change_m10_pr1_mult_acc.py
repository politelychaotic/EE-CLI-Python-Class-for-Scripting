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


    # settings and options
    cloud_retention = "cloud-retention"
    cloud_opt = 1

    pr1_setting = "cloud-preview-only"
    pr1_option = "--enable"




    #my_cli.login()
    my_cli.get_accounts()

    for i in range(len(my_cli.account_list)):
        my_cli.switch_account_from_list()
        all_cams = my_cli.get_all_cams()

        print("account_dir",my_cli.account_dir)
        m10_file = str(my_cli.account_dir)+"/not_set_cams.txt"
        print(m10_file)
        set_to_m10 = my_cli.get_all_camera_settings_by_esn(file=all_cams, setting=cloud_retention, ret=1)
        my_cli.update_cameras_by_esn(camfile=m10_file, setting=pr1_setting, option=pr1_option)









