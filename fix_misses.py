from json_parser_class import JSONAccountParser
from py_ee_cli import ee_cli, CLI
import subprocess
import argparse



ext = 'json'

if __name__ == "__main__":
    # Initialize parser
    augur = argparse.ArgumentParser(description="Fix cameras that were not updated in previous script run.")
    augur.add_argument("-p", "--parent", required=True, help="Parent account ID")
    augur.add_argument("-a", "--accounts", required=True, help="Sub account ID")
    augur.add_argument("-s", "--setting", required=True, help="Setting keyword to check and update")
    augur.add_argument("-t", "--set_to", required=True, help="Value to set the setting to (e.g. --enable or --disable)")
    augur.add_argument("-r", "--positive_result", required=True, help="The expected value of the setting if it was set correctly (e.g. yes or no)")
    augur.add_argument("-f", "--filename", required=True, help="Filename of the JSON report to parse")

    args = augur.parse_args()
    parent = args.parent
    sub = args.accounts
    settings_keyword = args.setting
    set_to = args.set_to
    positive_result = args.positive_result
    filename = args.filename

    user = 'username'  # Replace with actual computer username if needed

    filepath = f'/home/{user}/ee_cli/output/{filename}'

    not_matching = 'failed'
    matching = 'passed'
    unknown = 'unknown'

    username = f'mpaoli+{parent}@een.com'
    password = 'SuperSecure'
    my_cli = ee_cli(account_id=parent, username=username, password=password)
    my_cli.switch_account(sub)

    parser = JSONAccountParser(filepath)


    
    # Get parent account
    print(f"Parent Account: {parser.get_parent_account()}")
    print(f"Sub Accounts: {parser.get_sub_accounts()}")
    print()
    
    # Get all accounts
    print(f"All Accounts: {parser.get_all_accounts()}")
    print()
    
    # Get sections for account
    account_id = parser.get_all_accounts()[0]
    print(f"Sections in {account_id}: {parser.get_sections_for_account(account_id)}")
    print()
    
    # Get items by section
    sections = parser.get_sections_for_account(account_id)
    for section in sections:
        items = parser.get_items_by_section(account_id, section)
        print(f"  {section}: {len(items)} items")
    print()
    
    # Get all sections by account
    all_sections = parser.get_all_sections_by_account()
    for acc_id, sections_dict in all_sections.items():
        print(f"Account {acc_id}:")
        for section, items in sections_dict.items():
            print(f"  {section}: {len(items)} items")
    print()
    
    # Get item counts
    print("Item counts by account:")
    counts = parser.count_items_by_account()
    for account_id, count in counts.items():
        print(f"  {account_id}: {count} items")



    ## Example of how to use the parser to update cameras based on the JSON report ##
    all_accounts = parser.get_all_accounts()

    for account in all_accounts:
        sections = parser.get_sections_for_account(account)
        print(f"Account {account} has sections: {sections}")

        ## Format of sections goes: cameras, failed, passed, unknown. sections[0] is always cameras ##
        print()
        unmatched_items = []
        result = next((s for s in sections if s.endswith(not_matching)), None)
        if result:
            items = parser.get_items_by_section(account, result)
            print(f"  {result} has {len(items)} items: {items}")
            print(f'[->] Updating cameras in {result} for account {account}...')
            
            for item in items:
                command = subprocess.run([CLI, 'camera', 'get', settings_keyword, '--esn', item], capture_output=True, text=True)
                print(command.stdout)
                try:
                    setting_value = command.stdout.split()[-1]
                except IndexError:
                    setting_value = "No"
                print(setting_value)
                if setting_value != positive_result:
                    unmatched_items.append(item)
            print()

        result = next((s for s in sections if s.endswith(unknown)), None)
        if result:
            items = parser.get_items_by_section(account, result)
            print(f"  {result} has {len(items)} items: {items}")
            print(f'[->] Updating cameras in {result} for account {account}...')
            for item in items:
                command = subprocess.run([CLI, 'camera', 'get', settings_keyword, '--esn', item], capture_output=True, text=True)
                print(command.stdout)
                setting_value = command.stdout.split()[-1]
                print(setting_value)
                if setting_value != positive_result:
                    unmatched_items.append(item)
            print()
        
        print(f"[!!] Unmatched items: {unmatched_items}")

        failed_items = []
        for item in unmatched_items:
            print(f'[->] Updating camera {item} to: {settings_keyword} {set_to}...')
            command = subprocess.run([CLI, 'camera', 'set', settings_keyword, set_to, '--esn', item], capture_output=True, text=True)
            print(command.stdout)
            setting_value = command.stdout.split()[-1]
            print(setting_value)
            if setting_value != positive_result:
                failed_items.append(item)
        
        if failed_items:
            print(f"[!!] Failed to update items: {failed_items}")
        else:
            print("[!!] All items updated successfully!")
