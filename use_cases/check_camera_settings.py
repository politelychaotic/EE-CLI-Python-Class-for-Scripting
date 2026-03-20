from py_ee_cli import ee_cli
import argparse


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Check camera settings.')
    parser.add_argument('--account', required=True, help='Parent account ID')
    parser.add_argument('--sub', required=True, help='Sub account ID')
    parser.add_argument('--username', required=True, help='Username')
    parser.add_argument('--password', required=True, help='Password')
    parser.add_argument('--check_setting', required=True, help='Setting to check')
    parser.add_argument('--check_option', nargs='+', required=True, help='Option values to check')
    parser.add_argument('--check_key', required=True, help='Key to check')
    parser.add_argument('--keyword', required=True, help='Keyword for filename')
    args = parser.parse_args()

    account = args.account
    sub = args.sub
    username = args.username
    password = args.password
    my_cli = ee_cli(account_id=account, username=username, password=password)
    keyword = args.keyword
    cloud_retention = args.check_setting
    cloud_option = args.check_option
    cloud_key = args.check_key

    my_cli.switch_account(sub)
    
    all_cameras = my_cli.get_all_cams()

    unknown, unmatched, matched = my_cli.get_all_camera_settings_by_esn(cameras=all_cameras, setting=cloud_retention, option=cloud_option, key=cloud_key)
    print(f"\nMatched cameras for account {my_cli.current_account}: {matched}\n")
        
    my_cli.update_dict(my_cli.current_account, my_cli.current_account_list)
    my_cli.create_json_report(f"camera_settings_{my_cli.current_account}_{keyword}.json")
