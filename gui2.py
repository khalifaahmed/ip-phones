import tkinter as tk
from tkinter import filedialog, messagebox
import ttkbootstrap as ttk  # Better looking widgets
from ttkbootstrap.constants import *
import pandas as pd
from netmiko import ConnectHandler
import threading

def run_automation():
    host = entry_host.get()
    user = entry_user.get()
    pwd = entry_pwd.get()
    file_path = entry_file.get()

    if not all([host, user, pwd, file_path]):
        messagebox.showerror("Error", "All fields are required!")
        return

    def task():
        try:
            update_log("Reading Excel file...")
            df = pd.read_excel(file_path)
            total_rows = len(df)
            
            cme_router = {
                'device_type': 'cisco_ios',
                'host': host,
                'username': user,
                'password': pwd,
            }

            update_log(f"Connecting to {host}...")
            net_connect = ConnectHandler(**cme_router)
            net_connect.enable()
            
            all_commands = []
            for index, row in df.iterrows():
                update_log(f"Configuring: {row['name']}...")
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
                
                # Update Progress Bar
                progress_val = ((index + 1) / total_rows) * 100
                progress_bar['value'] = progress_val

            update_log("Sending commands to Router...")
            net_connect.send_config_set(all_commands)
            net_connect.send_command('write memory')
            net_connect.disconnect()
            
            update_log("SUCCESS: Bulk upload complete!")
            messagebox.showinfo("Done", "Configuration uploaded successfully!")
        except Exception as e:
            update_log(f"ERROR: {str(e)}")
            messagebox.showerror("Failed", f"An error occurred: {e}")
        finally:
            progress_bar['value'] = 0

    threading.Thread(target=task, daemon=True).start()

def update_log(msg):
    log_text.insert(tk.END, f"> {msg}\n")
    log_text.see(tk.END)

def browse_file():
    filename = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xls")])
    entry_file.delete(0, tk.END)
    entry_file.insert(0, filename)

# --- Modern UI Setup ---
app = ttk.Window(themename="superhero") # Options: darkly, flatly, superhero, cosmo
app.title("Cisco CME Automation Pro")
app.geometry("600x650")

# Main Container
main_frame = ttk.Frame(app, padding=20)
main_frame.pack(fill=BOTH, expand=YES)

# Title
ttk.Label(main_frame, text="CME Provisioning Tool", font=("Helvetica", 18, "bold"), bootstyle=INFO).grid(row=0, column=0, columnspan=3, pady=(0, 20))

# Input Section
labels = ["Router IP:", "Username:", "Password:"]
entries = []

for i, label_text in enumerate(labels):
    ttk.Label(main_frame, text=label_text).grid(row=i+1, column=0, sticky=W, pady=10)
    entry = ttk.Entry(main_frame, width=40)
    if label_text == "Password:":
        entry.config(show="*")
    if label_text == "Router IP:":
        entry.insert(0, "192.168.1.1")
    entry.grid(row=i+1, column=1, columnspan=2, sticky=EW, pady=10)
    entries.append(entry)

entry_host, entry_user, entry_pwd = entries

# File Selection Section
ttk.Label(main_frame, text="Excel Data:").grid(row=4, column=0, sticky=W, pady=10)
entry_file = ttk.Entry(main_frame)
entry_file.grid(row=4, column=1, sticky=EW, pady=10)
ttk.Button(main_frame, text="Browse", command=browse_file, bootstyle=SECONDARY).grid(row=4, column=2, padx=5)

# Progress Bar
progress_bar = ttk.Progressbar(main_frame, orient=HORIZONTAL, mode='determinate', bootstyle=SUCCESS)
progress_bar.grid(row=5, column=0, columnspan=3, sticky=EW, pady=20)

# Start Button
start_btn = ttk.Button(main_frame, text="DEPLOY TO ROUTER", command=run_automation, bootstyle=SUCCESS)
start_btn.grid(row=6, column=0, columnspan=3, sticky=EW, pady=10)

# Log Area
ttk.Label(main_frame, text="System Log:").grid(row=7, column=0, sticky=W, pady=(10, 0))
log_text = tk.Text(main_frame, height=8, font=("Consolas", 10), bg="#2b3e50", fg="white", borderwidth=0)
log_text.grid(row=8, column=0, columnspan=3, sticky=NSEW, pady=10)

app.mainloop()
