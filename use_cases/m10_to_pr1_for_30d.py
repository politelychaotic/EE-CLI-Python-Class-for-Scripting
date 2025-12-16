from py_ee_cli import ee_cli
from json_parser import json_parser

if __name__ == "__main__":
    account = ""
    username = ""
    password = ""
    cli = ee_cli(account_id=account, username=username, password=password)

    cloud_setting = "cloud-retention"
    cloud_option = 1
    cloud_set_val = "30"
    cloud_key = "m10"

    pr1_setting = "cloud-preview-only"
    pr1_set_val = "--enable"
    pr1_option = "yes"

    all_cams = cli.get_all_cams()

    unknown, cams_not_m10, cams_on_m10 = cli.get_all_camera_settings_by_esn(cameras=all_cams, setting=cloud_setting, option=cloud_option, key=cloud_key)
    #parser = json_parser(f"test_report_{account}.json")
    #cams_on_m10 = parser.get_key(cloud_key)
    #print(cams_on_m10)

    unknown, failed_pr1, passed_pr1 = cli.update_cameras_by_esn(camera_list=cams_on_m10, setting=pr1_setting, set_value=pr1_set_val, option=pr1_option)
    cli.update_cameras_by_esn(camera_list=passed_pr1, setting=cloud_setting, set_value=cloud_set_val)

    cli.update_dict(cli.current_account, cli.current_account_list)
    cli.create_json_report(f"update_report_{account}.json")

