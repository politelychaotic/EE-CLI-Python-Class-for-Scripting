from py_ee_cli import CLI
import json


class ParseJSON:
    def __init__(self, filepath: str, setting1: str, setting2: str):
        self.filepath = filepath
        self.settings = [setting1, setting2]
        self.iterator = 0

        with open(filepath, "r") as read_json:
            self.my_dict = json.load(read_json) 

        self.all_keys = list(self.my_dict.keys())
        self.subaccounts = self.my_dict['sub_accounts']

        self.current_account = self.my_dict['parent']
    
    def switch_account(self):
        if len(self.subaccounts) > 1:
            try:
                #subaccounts = self.all_keys[2:]
                subaccounts = self.subaccounts
                self.current_account = subaccounts[self.iterator]
                account_dict = self.my_dict[self.current_account]
                self.iterator = self.iterator + 1

                return account_dict
            
            except KeyError as err:
                print(f"Key Error for {self.current_account}:{err}")

    def check_not_empty(self, value):
        if value:
            return 0
        return 1

    
    def get_keys(self):
        compare_list = []
        for setting in self.settings:
            value = self.find_key(account=self.current_account, key=setting)
            compare_list.append(value)
        
        return compare_list

    def find_differences(self, compare: list):
        key_1 = set(compare[0])
        key_2 = set(compare[1])
        diff = key_1 ^ key_2
        return diff



    def find_account_dict(self, account):
        pass

    def find_key(self, account, key) -> list:
        key_dict = next((item for item in self.my_dict[account] if key in item), None)
        if key_dict:
            key_value = key_dict[key]
            return key_value
        
        return key_dict

    
    def find_difference(self, value_1: list, value_2: list) -> set:
        cmp1 = set(value_1)
        cmp2 = set(value_2)
        difference = cmp1 ^ cmp2

        return difference
    
    def determine_list(self, item1: set, item2: list):
        common_elements = item1.intersection(set(item2))

        return common_elements

