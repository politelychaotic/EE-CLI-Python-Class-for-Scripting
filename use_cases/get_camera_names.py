from py_ee_cli import ee_cli
import argparse


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Get camera names by ESNs.')
    parser.add_argument('--camera_esns', nargs='+', required=True, help='List of camera ESNs')
    parser.add_argument('--account', required=True, help='Account ID')
    parser.add_argument('--username', required=True, help='Username')
    parser.add_argument('--password', required=True, help='Password')
    args = parser.parse_args()

    camera_esns = args.camera_esns
    account = args.account
    username = args.username
    password = args.password
    my_cli = ee_cli(account_id=account, username=username, password=password)


    
    all_cameras = my_cli.get_all_cams()

    my_cli.get_camera_names_by_esn(cameras=camera_esns)
        
    my_cli.update_dict(my_cli.current_account, my_cli.current_account_list)
    my_cli.create_json_report(f"{account}_failed_camera_names.json")
