from json_parser import ParseJSON

if __name__ == '__main__':
    filepath = ""
    setting1 = ""
    setting2 = ""
    parser = ParseJSON(filepath, setting1=setting1, setting2=setting2)
    
    matched = []
    unmatched = []
    unset = []


    for i in range(len(parser.subaccounts)):
        account = parser.switch_account()
        
        keys = parser.get_keys()
        if keys[0] and keys[1]:
            difference = parser.find_differences(keys)
            in_list1 = parser.determine_list(difference, keys[0])
            #print(f"Only in list 1: {in_list1}")

            if difference:
                #print(f"Account: {parser.current_account} Difference: {difference}")
                if in_list1:
                    #print(f"Device(s): {in_list1} are only set to: {setting1}")
                    unset.append({parser.current_account: list(in_list1)})
                unmatched.append(parser.current_account)
            if not difference:
                #print(f"Account: {parser.current_account} No Difference.")
                matched.append(parser.current_account)
    print("\n\n")
    if not unmatched:
        print(f"[+] All Accounts updated successfully")
    if unmatched:
        if matched:
            print(f"[+] Accounts updated successfully: {matched}")
            print(f"[+] Accounts NOT updated successfully: {unmatched}")
        else:
            print(f"[!] No accounts updated successfully")


    print("\n\n")
    print(f"Devices NOT updated:\n")
    for account in unset:
        for key in account.keys():
            print(f"[+] Account: {key}")
            print("\t", end="")
            print('\n\t'.join(account[key]))
    
    print("\n\n")
