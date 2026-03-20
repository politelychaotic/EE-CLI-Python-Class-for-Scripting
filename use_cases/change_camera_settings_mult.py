from py_ee_cli import ee_cli
import argparse


if __name__ == '__main__':
    """
    python change_camera_settings_mult.py \
  --account <parent_account_id> \
  --subs <sub_account_id1> <sub_account_id2> ... \
  --username <username_prefix> \
  --password <password> \
  --setting_to_check <setting_name> \
  --check_option <option_value> \
  --result_key <key_name> \
  --setting_to_change <target_setting> \
  --enable <enable_flag> \
  --positive_result <expected_result>
    """


    parser = argparse.ArgumentParser(description='Change camera settings across multiple accounts.')
    parser.add_argument('--account', required=True, help='Parent account ID')
    parser.add_argument('--username', required=True, help='Username')
    parser.add_argument('--password', required=True, help='Password')
    parser.add_argument('--check_option', type=int, required=True, help='Check option value')
    parser.add_argument('--setting_to_change', required=True, help='Setting to change')
    parser.add_argument('--enable', required=True, help='Enable value')
    parser.add_argument('--positive_result', required=True, help='Positive result value')
    args = parser.parse_args()

    account = args.account
    subs = args.subs
    username = args.username
    password = args.password


    email = f"{username}+{account}@een.com"
    my_cli = ee_cli(account_id=account, username=email, password=password)


    # settings and options
    setting_to_check = args.setting_to_check
    check_option = args.check_option
    result_key = args.result_key

    setting_to_change = args.setting_to_change
    enable = args.enable
    positive_result = args.positive_result

    my_cli.account_list = subs

    cleaned_accounts = "_".join(str(s) for s in my_cli.account_list)
    
    for i in range(len(my_cli.account_list)):
        my_cli.switch_account_from_list()
        all_cameras = my_cli.get_all_cams()

        #unknown, unmatched, matched = my_cli.get_all_camera_settings_by_esn(cameras=all_cameras, setting=setting_to_check, option=check_option, key=result_key)
        matched = all_cameras
        unknown, failed, passed = my_cli.update_cameras_by_esn(camera_list=matched, setting=setting_to_change, set_value=enable, option=positive_result)
        
        my_cli.update_dict(my_cli.current_account, my_cli.current_account_list)
    my_cli.create_json_report(f"{cleaned_accounts}_{setting_to_change}.json")
