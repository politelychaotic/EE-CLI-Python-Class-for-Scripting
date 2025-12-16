import subprocess
import os
from typing import Optional
from pathlib import Path
import re
import json


CLI = "./een"


ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')


class ee_cli:
    """
    Class to manage CLI for scripts.

    :init: account_id, username, password
    :run: handle CLI output to PIPE to a file automatically
    :login: username, password
    :get_bridges:
    :get_all_cams:
    :get_cams_per_bridge:
    :get_camera_settings_by_esn: camfile, setting
    :update_cams_by_esn: camfile, setting
    """

    def __init__(self, account_id: str, username: str, password: str, new_session=True):
        self.account_id = account_id
        self.current_account = account_id
        self.index = 0
        self.account_list = []
        self.username = username
        self.password = password

        if new_session:
            self.new_session()

        self.keys = {'cloud-preview-only': ['pr1', 'pr1_failed'], 'scene-analytics': ['scene_analytics_enabled', 'no_scene_analytics'], 'cloud-retention': ['not_m10', 'm10']}
        self.responses = {'cloud-preview-only': ['yes', 'no'], 'scene_analytics': ['yes'], 'cloud-retention': [(2, 365*5), (0,1)]} 

        self.my_dict = {
            "parent": self.account_id,
            "sub_accounts": [],
        }

        self.current_account_list = []
        
        # Creating directory for output
        self.working_directory = Path.cwd()
        self.out_dir = self.working_directory / Path("output" + "_" + self.account_id)
        self.account_dir = self.out_dir

        try:
            self.out_dir.mkdir(exist_ok=True)
        except Exception as e:
            print(f"An error occurred creating the output directory: {e}")


    def check_if_logged_in(self, msg="[->] logging back in..."):
        logged_in = subprocess.run([CLI, "user", "list"], capture_output=True, text=True)
        print(f"{logged_in.stderr}")
        if logged_in.stderr.strip() == "error: please login to continue" or logged_in.stderr.strip() == "error: token expired please login again to continue":
            self.login()
            
            
    def login(self):
        """
        Log in to either a reseller or subaccount
        """
        try:
            self.run([CLI, "auth", "login", "--username", self.username, "--password", self.password])

        except Exception as e:
            print(f"[!!] An error occurred: {e}")


    def new_session(self, msg="[->] Starting new session..."):
        """
        :param self: Description
        Logout of previous session
        """
        result = self.run([CLI, "user", "list"])
        if result != "error: please login to continue" or result != "error: token expired please login again to continue":
            print(msg)
            self.logout()
            self.login()




    def logout(self):
        """
        Log out of the current session
        """
        try:
            self.run([CLI, "auth", "logout"])

        except Exception as e:
            print(f"[!!] An error occurred: {e}")


    def get_accounts(self):

        self.check_if_logged_in()

        accounts = self.run([CLI, "account", "list", "-s", "--include", "id"])

        accounts = ansi_escape.sub('', accounts)  #fixed getting weird output like: ['\x1b[1m00111817\x1b[0m

        self.update_account_list(accounts)    # update account list in instance automatically when you get accounts

        if self.account_list:
            self.my_dict['sub_accounts'] = self.account_list

        self.number_of_accounts = len(self.account_list)

    
    def update_account_list(self, accounts: str):
        accounts = accounts.split()
        for account in accounts:
            account = account.strip()
            self.account_list.append(account)


    def switch_account_from_list(self) -> None:
        """
        Uses accounts.txt to switch accounts
        Takes no Arguments, updates my_dict before moving to a new account

        NOTE Please in loops manually update dictionary: self.update_dict(self.current_account, self.current_account_list)
        
        :return:  None
        """

        self.check_if_logged_in()

        self.current_account_list = []                                           # Set the list to empty before we switch to a new account

        new_account = self.account_list[self.index]
        print(f"[->] Switching from {self.current_account} -> {new_account}...")
        
        try:
            subprocess.run([CLI, "account", "switch", "-s", new_account], capture_output=True, text=True)
            self.current_account = new_account
            self.index = self.index + 1
        
        except Exception as e:
            print(f"[!!] Error Switching accounts: {e}")
    
            

    
    def switch_account(self, new_account: str) -> None:

        self.check_if_logged_in()
        
        print(f"[->] Switching from {self.account_id} -> {new_account}...")
        
        try:
            subprocess.run([CLI, "account", "switch", "-s", new_account], capture_output=True, text=True)
            self.current_account = new_account
            self.account_dir = new_account

        
        except Exception as e:
            print(f"[!!] Error Switching accounts: {e}")


    def set_current_account(self, current_account):
        """
        Sets self.current_account to the current account using the account ID
        """
        self.current_account = current_account

    
    def get_bridges(self):
        bridge_file = "bridges.txt"
        filepath = self.account_dir / bridge_file
        filepath = str(filepath)

        self.check_if_logged_in()
        

        self.run([CLI, "bridge", "list", "--include", "esn"], filepath)

    
    def get_all_cams(self) -> list[str]:
        self.check_if_logged_in()
        
        cameras = self.run([CLI, "camera", "list", "--include", "esn"]) #, filepath)

        cameras = cameras.split()
        self.current_account_list.append({"cameras": cameras})

        return cameras
    

    def get_cams_per_bridge(self):
        filepath = self.account_dir / "bridges.txt"

        filepath = str(filepath)

        self.check_if_logged_in()

        with open(filepath, "r", encoding="utf-8") as bridges:
            for bridge in bridges:
                bridge = bridge.strip()
                bridge_dir = self.account_dir / bridge  # Create directory for each bridge
                bridge_dir.mkdir(exist_ok=True)         # and store cameras to a file there
                camera_file = str(bridge_dir)+"/cameras.txt"  

                self.run([CLI, "camera", "list", "--bridge-esn", bridge, "--include", "esn"], camera_file)


    def update_cameras_by_esn(self, camera_list: list[str], setting: str, set_value: str, option: Optional[str] = None) -> tuple[list, list, list]:
        """
        Will update a setting for all cameras in provided camera list to be set to set_option.

        :param camera_list: list of cameras to update
        :param setting: the setting to change
        :param set_value: the value to set the setting to
        :returns: tuple[unknown list, failed list, passed list]
        """

        failed = []
        passed = []
        unknown = []

        if not option:
            option = set_value
        
        # Update this to use key dict
        key_passed = setting+"_"+option
        key_failed = setting+"_"+"_failed"
        key_unknown = setting+"_"+"_unknown"

        self.check_if_logged_in()


        for camera in camera_list:
            self.run([CLI, "camera", "set", setting, set_value, "--esn", camera])
            status = self.run([CLI, "camera", "get", setting, "--esn", camera])

            # check and sort cameras by figuring out if they passed or failed to update settings
            try:
                setting_value = status.split()[-1]

                if setting_value == option:
                    passed.append(camera)
                elif setting_value != option:
                    failed.append(camera)

            except IndexError as err:
                print(f'[!!] Index error for {camera}:{err}')
                print(f"[+] Adding {camera} -> unknown list...")
                unknown.append(camera)

            

        if failed:
            self.current_account_list.append({key_failed: failed})
        if passed:
            self.current_account_list.append({key_passed: passed})
        if unknown:
            self.current_account_list.append({key_unknown: unknown})
        

        return unknown, failed, passed
            

    def get_all_camera_settings_by_esn(self, cameras: list[str], setting: str, option: Optional[list[str]] = None, key: Optional[str] = None) -> tuple[list, list, list]:
        """
        :param cameras: list of cameras on account
        :param setting: the setting we want to check
        :param key: optional argument to set a custom key value, scheme for this is: matched -> <key>, unmatched -> not_<key>
        :return: tuple[unknown list, unmatched list, matched list]
        """

        unmatched = []
        matched = []
        unknown = []

        

        if not key:
            key_off = self.keys[setting][0]                                       #  enabled
            key_on = self.keys[setting][1]                                        #  not enabled
        elif key:
            key_off = "not_" + key                                           #  enabled                                          
            key_on = key                                                     #  not enabled

        if not option:
            option = self.responses[setting][0]  #  enabled
            option = self.responses[setting][1]  #  not enabled 

        
        self.check_if_logged_in()  # Ensure we are still logged in. Will work on a better solution...

        if type(option) == int:
            option = str(option)

        for camera in cameras:
            setting_value = self.run([CLI, "camera", "get", setting, "--esn", camera])
            try:
                setting_value = setting_value.split()[-1]
            except IndexError as err:
                print(f'[!!] Index error for {camera}:{err}')
                print(f"[+] Adding {camera} -> unknown list...")
                unknown.append(camera)
            


            if type(option) == str: 
                if setting_value == option:
                    matched.append(camera)
                elif setting_value != option:
                    unmatched.append(camera)
            
            elif type(option) == list:
                if setting_value in option:
                    matched.append(camera)
                else:
                    unmatched.append(camera)
            
        if unmatched:
            self.current_account_list.append({key_off: unmatched})
        if matched:
            self.current_account_list.append({key_on: matched})
        if unknown:
            self.current_account_list.append({"unknown": unknown})
        
        return unknown, unmatched, matched
    
    
    def update_dict(self, key: str, data):
        """
        Write all in JSON format -> file.
        """
        if key in self.my_dict:
            self.my_dict[key].append(data)
        
        else:
            self.my_dict[key] = data
            
    
    def get_data_by_key(self, key: str):
        """
        Function to return data in my_dict via key

        :param key: lookup key for value(s)

        :returns: Any | str
        """
        try:
            result = next((item for item in self.my_dict[self.current_account] if key in item), None)
            if result != None:
                result = result[key]
        
        except KeyError as key_err:
            result = f"[!!] Key Error for {key}:{key_err}"

        return result
                

    def create_json_report(self, file = None) -> str:
        """
        Generate a JSON report from my_dict to save output.

        :param file: optional argument for file name
        :return: filepath: str
        """

        if file:
            filepath = str(self.working_directory)+"/"+file
        else: 
            filepath = str(self.working_directory)+"/"+"output_"+self.account_id+"/report.json"
        
        with open(filepath, "w") as json_writer:
            json.dump(self.my_dict, json_writer, indent=4)
        
        return filepath
        

    @staticmethod
    def __clean_up___():
        """
        Helper that removes all files and directories created by this script under the /output directory
        :return: None
        """

        # find a directory matching the pattern of output or output_<number>
        #subprocess.run(["rm", "-rf", ""])

    
    @staticmethod
    def run(cmd: list[str]) -> str:
        """
        Running CLI command and returning STDOUT

        :filename: if not None, tee to file
        """
        print(f"[+] Running command: {' '.join(cmd)}")
        """Run CLI command and return stdout."""
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
        except subprocess.CalledProcessError as e:
            if e.returncode == 1:
                print(f"Subprocess failed with expected exit status 1: {e.cmd}")
                print(f"Stderr: {e.stderr}")
            else:
                print(f"Subprocess failed with unexpected exit status {e.returncode}: {e.cmd}")
                print(f"Stderr: {e.stderr}")

            return e.stderr
        
        '''if result.returncode != 0:
            print(f"[!!] Command failed: {result.stderr}")
            raise subprocess.CalledProcessError(result.returncode, cmd)'''
        
        return result.stdout
