import pandas as pd
from netmiko import ConnectHandler

# 1. Router Connection Data
cme_router = {
    'device_type': 'cisco_ios',
    'host': '10.100.100.15',
    'username': 'user',
    'password': 'user',
}

def bulk_upload_cme(excel_file):
    # 2. Read the Excel File
    df = pd.read_excel(excel_file)
    
    try:
        print("Connecting to CME Router...")
        net_connect = ConnectHandler(**cme_router)
        net_connect.enable()
        
        all_commands = []
        
        # 3. Loop through each row in Excel
        for index, row in df.iterrows():
            ephone_id = row['id']
            dn_number = row['extension']
            phone_mac = row['mac']
            phone_name = row['name']
            phone_model = row['model']
            
            print(f"Preparing config for: {phone_name} ({dn_number})")
            
            # Build the CLI commands for this specific phone
            commands = [
                f"ephone-dn {ephone_id}",
                f"number {dn_number}",
                f"label {phone_name}",
                "description Created via Python Automation",
                "exit",
                f"ephone {ephone_id}",
                f"mac-address {phone_mac}",
                f"type {phone_model}",
                f"button 1:{ephone_id}",
                "exit"
            ]
            all_commands.extend(commands)

        # 4. Push all commands at once
        print("Pushing configuration to router...")
        output = net_connect.send_config_set(all_commands)
        
        # 5. Save and Disconnect
        net_connect.send_command('write memory')
        print("Bulk Upload Complete!")
        net_connect.disconnect()
        
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    bulk_upload_cme('users.xlsx')
    
