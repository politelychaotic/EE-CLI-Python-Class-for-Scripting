import pathlib
import subprocess
import os
from typing import Optional
import tempfile
from pathlib import Path
import csv
import re
import contextlib
import json


CLI = "./een"


CHECK = ["0", "-", "no"]


CHECK_CLOUD_RET = ["1"]

AFFIRM = ["yes"]

PATTERN = r"^[1-9]\d*$"

ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')


class RunCLI:
    """
    Class to manage CLI for scripts.

    :init: account_id, username, password
    If you do not login or switch accounts while using this script, use set_current_account so class can function properly

    :run: handle CLI output to PIPE to a file automatically

    :login: username, password

    :get_bridges:

    :get_all_cams:

    :get_cams_per_bridge:

    :get_camera_settings_by_esn: camfile, setting

    :update_cams_by_esn: camfile, setting

    """
    def __init__(self, account_id: str, username: str, password: str):
        self.account_id = account_id
        self.current_account = account_id
        self.index = 0
        self.account_list = []
        self.username = username
        self.password = password

        self.check_if_logged_in("[+] Logging in...")    # Log in if not logged in on init


        # Creating directory for output
        self.working_directory = Path.cwd()
        self.out_dir = self.working_directory / Path("output" + "_" + self.account_id)
        self.account_dir = self.out_dir

        try:
            self.out_dir.mkdir(exist_ok=True)
        except Exception as e:
            print(f"An error occurred creating the output directory: {e}")



    def check_if_logged_in(self, msg: Optional[str] = None):
        logged_in = subprocess.run([CLI, "account", "list"], capture_output=True, text=True)
        if logged_in.stderr.strip() == "error: please login to continue":
            if msg:
                print(msg)
            else:
                print("[->] logging back in...")
            
            self.login()


    def login(self):
        """
        Log in to either a reseller or subaccount
        """
        try:
            self.run([CLI, "auth", "login", "--username", self.username, "--password", self.password])

        except Exception as e:
            print(f"[!!] An error occurred: {e}")

    
    def get_bridges(self):
        bridge_file = "bridges.txt"
        filepath = self.account_dir / bridge_file
        filepath = str(filepath)

        self.check_if_logged_in()
        

        self.run([CLI, "bridge", "list", "--include", "esn"], filepath)

    
    def get_all_cams(self):
        cam_on_acct = "total_cams.txt"

        self.check_if_logged_in()

        # Getting list of cameras on an account
        filepath = str(self.account_dir)+"/"+cam_on_acct
        
        self.run([CLI, "camera", "list", "--include", "esn"], filepath)

        return filepath

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

    @staticmethod
    def run(cmd: list[str], filename: Optional[Path]=None) -> str | None:
        """
        Running CLI command and returning STDOUT

        :filename: if not None, tee to file
        """
        print(f"[+] Running command: {' '.join(cmd)}")

        if filename:
            try:
                with open(filename, "w") as f:
                    # Popen to pipe the command's stdout to tee
                    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, text=True)
                    # Popen to pipe tee's output to the file and stdout
                    tee_process = subprocess.Popen(["tee", filename], stdin=process.stdout, text=True)

                    # Allow process.stdout to close
                    process.stdout.close()

                    tee_process.wait()
                    process.wait()

            except FileNotFoundError:
                print(f"Error: Command '{cmd[0]}' or 'tee' not found.")
            except Exception as e:
                print(f"An error occurred: {e}")

        elif not filename:
            """Run CLI command and return stdout."""
            #print(f"Running: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"Command failed: {result.stderr}")
                raise subprocess.CalledProcessError(result.returncode, cmd)
            return result.stdout
        return None

    def get_accounts(self):
        account_file = "accounts.txt"

        self.check_if_logged_in()

        accounts = subprocess.run([CLI, "account", "list", "-s", "--include", "id"], capture_output=True, text=True)
        #print(accounts.stdout)

        accounts = ansi_escape.sub('', accounts.stdout)  #fixed this: ['\x1b[1m00111817\x1b[0m

        self.update_account_list(accounts)    # update account list in instance automatically when you get accounts
        #print("accounts", self.account_list)

        if self.account_list:
            filepath = str(self.out_dir)+"/"+account_file

            with open(filepath, "w", encoding="utf-8") as writer:
                writer.write(accounts)    #might fix this: ['\x1b[1m00111817\x1b[0m
            writer.close()

    
    def update_account_list(self, accounts: str):
        accounts = accounts.split()
        for account in accounts:
            account = account.strip()
            self.account_list.append(account)


    def switch_account_from_list(self) -> None:
        """
        Uses accounts.txt to switch accounts
        Takes no Arguments
        :return:  None
        """

        self.check_if_logged_in()

        new_account = self.account_list[self.index]
        print(f"[->] Switching from {self.current_account} -> {new_account}...")
        
        try:
            subprocess.run([CLI, "account", "switch", "-s", new_account], capture_output=True, text=True)
            self.current_account = new_account
            self.index = self.index + 1
            
            #create new dir for the current account
            self.account_dir = Path(self.out_dir / self.current_account)
            self.account_dir.mkdir(exist_ok=True)
        
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


    def update_cameras_by_esn(self, camfile, setting, option):
        """
        :camfile: Name of file has camera list we want to use
        :setting: Setting to change

        Returns a list of passed cameras
        """

        self.check_if_logged_in()
        
        passed = self.account_dir / "passed.txt"
        failed = self.account_dir / "failed.txt"
        passed = str(passed)
        failed = str(failed)

        
        pass_list = []
        failed_list = []

        with open(camfile, "r", encoding="utf-8") as file:
            cameras = file.readlines()
            for camera in cameras:
                camera = camera.strip()
                print(f"[+] Running: {CLI} camera set {setting} {option} --esn {camera}")
                subprocess.run([CLI, "camera", "set", setting, option, "--esn", camera], capture_output=True, text=True)
                status = subprocess.run([CLI, "camera", "get", setting, "--esn", camera], capture_output=True, text=True)
                try:
                    if status.stdout.split()[-1] in CHECK:
                        failed_list.append(status.stdout)
                    elif status.stdout.split()[-1] in AFFIRM or re.match(PATTERN, status.stdout.split()[-1]) and setting != "cloud-retention": # Make sure setting is NOT cloud ret as 1 is the val for M10
                        pass_list.append(status.stdout)
                    elif status.stdout.split()[-1] in AFFIRM or re.match(PATTERN, status.stdout.split()[-1]) and status.stdout.split()[-1] > 1:  # Add for adding cloud ret above M10 value
                        pass_list.append(status.stdout)
                    else:
                        print(f"[!!] Error with {camera} : {status.stdout.split()[-1]}")

                except IndexError as e:
                    print('Index Error:{e}')

        file.close()

        if pass_list:
            for cam in pass_list:
                with open(passed, "w", encoding="utf-8") as pwrite:
                    pwrite.write(cam+"\n")
                pwrite.close()

        if failed_list:
            for cam in failed_list:
                with open(failed, "w", encoding="utf-8") as fwrite:
                    fwrite.write(cam+"\n")
                fwrite.close()

        return pass_list
    

    @staticmethod
    def update_camera_by_esn(esn: str, setting: str, option: str) -> str:
        """
        Update one camera at a time for better control in script writing.

        Use a for loop if you need a list of cameras to be updated.
        """

        self.check_if_logged_in()

        output = ""
        print(f"[+] Running: {CLI} camera set {setting} {option} --esn {esn}")
        subprocess.run([CLI, "camera", "set", setting, option, "--esn", esn], capture_output=True, text=True)
        status = subprocess.run([CLI, "camera", "get", setting, "--esn", esn], capture_output=True, text=True)
        if status.stdout.split()[-1] not in CHECK:
            output = f"[+] Successfully updated {esn} to {setting} {option}: status {status}"
        elif status.stdout.split()[-1] in CHECK:
            output = f"[!!] Failed to update {esn} to {setting} {option}: status {status}"

        return output
          
        
    def get_all_camera_settings_by_esn(self, file: str, setting: str, ret: int, save: Optional[bool]=True) -> list | tuple[list,list] | None:
        """
        :save: chose to save files or not, set to False to overide save
        :ret: returns a list: 0 -> not_set_cams, 1 -> set_cams, 2 -> unknown_file, 3 -> not_set_cams, set_cams
        """

        not_set_cams = []
        set_cams = []
        unknown = []

        not_set_file = self.account_dir / Path("not_set_cams.txt")
        set_file = self.account_dir / Path("set_cams.txt")
        unknown_file = self.account_dir / Path("unknown_settings.txt")
        not_set_file = str(not_set_file)
        set_file = str(set_file)
        unknown_file = str(unknown_file)

        
        self.check_if_logged_in()

    
        with open(file, "r", encoding="utf-8") as reader:
            cameras = reader.readlines()
            
            if setting == "cloud-retention":     # Make sure correct CHECK list is used depending on the setting we are checking
                check = CHECK_CLOUD_RET
            else:
                check = CHECK
                
            for camera in cameras:
                camera = camera.strip()
                print(f"[+] Getting camera settings {camera}")
                setting_value = subprocess.run([CLI, "camera", "get", setting, "--esn", camera], capture_output=True, text=True)
                try:
                    setting_value = setting_value.stdout.split()[-1]    # Get last column and interpret as setting value
                    if setting_value in check:
                        not_set_cams.append(camera)
                    elif setting_value not in check:
                        set_cams.append(camera)
                except IndexError as e:
                    print(f'[!!] Index error {e} for {camera}: {setting_value}')
                    print(f'[=>] Saving {camera} -> Unknown settings list: {unknown_file}')
                    unknown.append(camera)
        
        reader.close()

        print(f"[+] Cameras NOT found in CHECK: {set_cams}")
        print(f"[+] Cameras found in CHECK: {not_set_cams}")
        print(f"[+] Cameras with UNKNOWN settings: {unknown}")


        if save:
            with open(set_file, "w", encoding="utf-8") as has_value:
                for cam in set_cams:
                    has_value.write(cam+"\n")
            has_value.close()

            with open(not_set_file, "w", encoding="utf-8") as no_value:
                for cam in not_set_cams:
                    no_value.write(cam+"\n")
            no_value.close()

            with open(unknown_file, "w", encoding='utf-8') as unknown_value:
                for cam in unknown:
                    unknown_value.write(cam+"\n")
            unknown_value.close()
        

        # return list based on what we want returned for our use case
        if ret == 0:
            return not_set_cams
        elif ret == 1:
            return set_cams
        elif ret == 2:
            return unknown_file
        elif ret == 3:
            return unknown_file, not_set_cams, set_cams
        
        return None
    
                

    
    def report_json(self, fname: str, data: list):
        """
        Write all in JSON format -> file.
        """
        pass
                

    def create_csv_report(self):
        pass


    def save_to_file(self, fname: str, data: str):
        """
        Function to save output to a file.
        :param fname: filepath to write to in str format
        :param data: data to write to file in str format
        """
        pass
        

    @staticmethod
    def __clean_up___():
        """
        Helper that removes all files and directories created by this script under the /output directory
        :return: None
        """

        # find a directory matching the pattern of output or output_<number>
        #subprocess.run(["rm", "-rf", ""])
