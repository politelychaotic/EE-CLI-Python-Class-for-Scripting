from py_ee_cli import ee_cli
import argparse


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Check camera settings across multiple accounts.')
    parser.add_argument('--account', required=True, help='Parent account ID')
    parser.add_argument('--subs', nargs='+', required=True, help='List of sub account IDs')
    parser.add_argument('--username', required=True, help='Username')
    parser.add_argument('--password', required=True, help='Password')
    parser.add_argument('--check_setting', required=True, help='Setting to check')
    parser.add_argument('--check_option', type=int, required=True, help='Option value to check')
    parser.add_argument('--check_key', required=True, help='Key to check')
    args = parser.parse_args()

    account = args.account
    subs = args.subs
    username = args.username
    password = args.password
    check_setting = args.check_setting
    check_option = args.check_option
    check_key = args.check_key

    login = f"{username}+{account}@een.com"

    my_cli = ee_cli(account_id=account, username=login, password=password)


    my_cli.account_list = subs
    
    
    for i in range(len(my_cli.account_list)):
        my_cli.switch_account_from_list()
        all_cameras = my_cli.get_all_cams()

        unknown, unmatched, matched = my_cli.get_all_camera_settings_by_esn(cameras=all_cameras, setting=check_setting, option=check_option, key=check_key)
        print(f"\nMatched cameras for account {my_cli.current_account}: {matched}\n")
        
        my_cli.update_dict(my_cli.current_account, my_cli.current_account_list)
    my_cli.create_json_report(f"camera_settings_{my_cli.current_account}.json")
