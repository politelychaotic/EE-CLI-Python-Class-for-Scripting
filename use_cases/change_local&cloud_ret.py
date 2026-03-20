from py_ee_cli import ee_cli
from json_parser import json_parser

if __name__ == "__main__":
    account = ""
    username = ""
    password = ""
    cli = ee_cli(account_id=account, username=username, password=password)
    cli.login()

    subaccount = ""
    cli.switch_account(subaccount)

    cloud_setting = "cloud-retention"
    cloud_option = "30"
    cloud_set_val = "30"
    cloud_key = "cloud_30d"

    max_local_setting = "maximum-premise-retention"
    max_local_set_val = "1"
    max_local_option = "1"
    max_local_key = "max_local_1d"

    min_local_setting = "minimum-premise-retention"
    min_local_set_val = "0"
    min_local_option = "0"
    min_local_key = "min_local_0d"

    all_cams = cli.get_all_cams()

    unknown_cloud, not_cloud_30d, cloud_30d = cli.get_all_camera_settings_by_esn(cameras=all_cams, setting=cloud_setting, option=cloud_option, key=cloud_key)
    unknown_max_local, not_max_local_1d, max_local_1d = cli.get_all_camera_settings_by_esn(cameras=all_cams, setting=max_local_setting, option=max_local_option, key=max_local_key)
    unknown_min_local, not_min_local_0d, min_local_0d = cli.get_all_camera_settings_by_esn(cameras=all_cams, setting=min_local_setting, option=min_local_option, key=min_local_key)
    #parser = json_parser(f"test_report_{account}.json")
    #cams_on_m10 = parser.get_key(cloud_key)
    #print(cams_on_m10)

    unknown_cloud, failed_cloud, passed_cloud = cli.update_cameras_by_esn(camera_list=all_cams, setting=cloud_setting, set_value=cloud_set_val, option=cloud_option)
    unknown_maxl, failed_maxl, passed_maxl = cli.update_cameras_by_esn(camera_list=passed_cloud, setting=max_local_setting, set_value=max_local_set_val, option=max_local_option)
    unknown_minl, failed_minl, passed_minl = cli.update_cameras_by_esn(camera_list=passed_maxl, setting=min_local_setting, set_value=min_local_set_val, option=min_local_option)

    cli.update_dict(cli.current_account, cli.current_account_list)
    cli.create_json_report(f"camera_update_report_{account}.json")

