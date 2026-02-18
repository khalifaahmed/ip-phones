import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
from netmiko import ConnectHandler
import threading

def run_automation():
    # Get data from Entry fields
    host = entry_host.get()
    user = entry_user.get()
    pwd = entry_pwd.get()
    file_path = entry_file.get()

    if not all([host, user, pwd, file_path]):
        messagebox.showerror("Error", "All fields and file selection are required!")
        return

    # Run in a separate thread so the GUI doesn't freeze
    def task():
        try:
            log_text.insert(tk.END, "Reading Excel...\n")
            df = pd.read_excel(file_path)
            
            cme_router = {
                'device_type': 'cisco_ios',
                'host': host,
                'username': user,
                'password': pwd,
            }

            log_text.insert(tk.END, f"Connecting to {host}...\n")
            net_connect = ConnectHandler(**cme_router)
            net_connect.enable()
            
            all_commands = []
            for _, row in df.iterrows():
                log_text.insert(tk.END, f"Adding {row['name']}...\n")
                commands = [
                    f"ephone-dn {row['id']}",
                    f"number {row['extension']}",
                    f"label {row['name']}",
                    "exit",
                    f"ephone {row['id']}",
                    f"mac-address {row['mac']}",
                    f"button 1:{row['id']}",
                    "exit"
                ]
                all_commands.extend(commands)

            net_connect.send_config_set(all_commands)
            net_connect.send_command('write memory')
            net_connect.disconnect()
            
            log_text.insert(tk.END, "SUCCESS: Bulk upload complete!\n")
            messagebox.showinfo("Done", "Configuration uploaded successfully!")
        except Exception as e:
            log_text.insert(tk.END, f"ERROR: {str(e)}\n")
            messagebox.showerror("Failed", f"An error occurred: {e}")

    threading.Thread(target=task).start()

def browse_file():
    filename = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xls")])
    entry_file.delete(0, tk.END)
    entry_file.insert(0, filename)

# --- GUI Setup ---
root = tk.Tk()
root.title("Cisco CME Bulk Provisioner")
root.geometry("450x550")

# Input Fields
tk.Label(root, text="Router IP:").pack(pady=5)
entry_host = tk.Entry(root)
entry_host.insert(0, "192.168.1.1")
entry_host.pack()

tk.Label(root, text="Username:").pack(pady=5)
entry_user = tk.Entry(root)
entry_user.pack()

tk.Label(root, text="Password:").pack(pady=5)
entry_pwd = tk.Entry(root, show="*")
entry_pwd.pack()

tk.Label(root, text="Excel File:").pack(pady=5)
entry_file = tk.Entry(root, width=40)
entry_file.pack()
tk.Button(root, text="Browse", command=browse_file).pack(pady=2)

# Run Button
tk.Button(root, text="START PROVISIONING", bg="green", fg="white", font=('Arial', 10, 'bold'), command=run_automation).pack(pady=20)

# Log Area
tk.Label(root, text="Activity Log:").pack()
log_text = tk.Text(root, height=10, width=50)
log_text.pack(padx=10, pady=10)

root.mainloop()
