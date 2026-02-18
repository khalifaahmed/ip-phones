from netmiko import ConnectHandler

# 1. Connection Details
cme_router = {
    'device_type': 'cisco_ios',
    'host': '10.100.100.15',  
    'username': 'user',
    'password': 'user',
}

# 2. Define the Phone Data
dn_number = "5001"
extension_label = "IT_Support"
phone_mac = "0011.2233.4455"  # MAC Address of the Cisco Phone
button_config = "1:1"         # Button 1 linked to DN 1

# 3. Configuration Commands
commands = [
    # Define the Directory Number (DN)
    'ephone-dn 1',
    f'number {dn_number}',
    f'label {extension_label}',
    'description Support Desk',
    'exit',
    
    # Define the physical Ephone
    'ephone 1',
    f'mac-address {phone_mac}',
    'type 7945',             # Phone model
    f'button {button_config}',
    'exit'
]

def push_config():
    try:
        # Connect to Router
        net_connect = ConnectHandler(**cme_router)
        net_connect.enable()
        
        print(f"Connecting to {cme_router['host']}...")
        
        # Send Config Commands
        output = net_connect.send_config_set(commands)
        print("Configuration Output:")
        print(output)
        
        # Save Config
        net_connect.send_command('write memory')
        print("Configuration Saved Successfully.")
        
        net_connect.disconnect()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    push_config()


