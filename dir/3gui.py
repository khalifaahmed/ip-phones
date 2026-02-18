import customtkinter as ctk
from tkinter import filedialog, messagebox
import pandas as pd
from netmiko import ConnectHandler
import threading

# Set the appearance and color theme
ctk.set_appearance_mode("Dark")  # Options: "Dark", "Light", "System"
ctk.set_default_color_theme("blue")

class CMEApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Cisco CME Automation Pro")
        self.geometry("600x700")

        # --- Grid Configuration ---
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(7, weight=1) # Log area takes up extra space

        # --- Header ---
        self.label_title = ctk.CTkLabel(self, text="CME Bulk Provisioner", font=ctk.CTkFont(size=24, weight="bold"))
        self.label_title.grid(row=0, column=0, padx=20, pady=20)

        # --- Inputs Container ---
        self.entry_host = ctk.CTkEntry(self, placeholder_text="Router IP (e.g., 192.168.1.1)", width=400)
        self.entry_host.grid(row=1, column=0, padx=20, pady=10)

        self.entry_user = ctk.CTkEntry(self, placeholder_text="Username", width=400)
        self.entry_user.grid(row=2, column=0, padx=20, pady=10)

        self.entry_pwd = ctk.CTkEntry(self, placeholder_text="Password", show="*", width=400)
        self.entry_pwd.grid(row=3, column=0, padx=20, pady=10)

        # --- File Selection ---
        self.file_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.file_frame.grid(row=4, column=0, padx=20, pady=10)
        
        self.entry_file = ctk.CTkEntry(self.file_frame, placeholder_text="Select Excel file...", width=300)
        self.entry_file.pack(side="left", padx=(0, 10))
        
        self.btn_browse = ctk.CTkButton(self.file_frame, text="Browse", width=90, command=self.browse_file)
        self.btn_browse.pack(side="left")

        # --- Progress Bar ---
        self.progress = ctk.CTkProgressBar(self, width=400)
        self.progress.grid(row=5, column=0, padx=20, pady=20)
        self.progress.set(0)

        # --- Action Button ---
        self.btn_run = ctk.CTkButton(self, text="START DEPLOYMENT", font=ctk.CTkFont(weight="bold"), 
                                    fg_color="#28a745", hover_color="#218838", command=self.start_thread)
        self.btn_run.grid(row=6, column=0, padx=20, pady=10)

        # --- Log Output ---
        self.log_output = ctk.CTkTextbox(self, width=500, height=200, font=("Consolas", 12))
        self.log_output.grid(row=7, column=0, padx=20, pady=20, sticky="nsew")

    def browse_file(self):
        filename = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xls")])
        if filename:
            self.entry_file.delete(0, "end")
            self.entry_file.insert(0, filename)

    def update_log(self, message):
        self.log_output.insert("end", f"> {message}\n")
        self.log_output.see("end")

    def start_thread(self):
        # Prevent freezing and start the task
        threading.Thread(target=self.run_automation, daemon=True).start()

    def run_automation(self):
        host = self.entry_host.get()
        user = self.entry_user.get()
        pwd = self.entry_pwd.get()
        file_path = self.entry_file.get()

        if not all([host, user, pwd, file_path]):
            messagebox.showerror("Error", "Missing information!")
            return

        try:
            self.update_log("Reading spreadsheet data...")
            df = pd.read_excel(file_path)
            total = len(df)

            device = {
                'device_type': 'cisco_ios',
                'host': host,
                'username': user,
                'password': pwd,
            }

            self.update_log(f"Establishing SSH connection to {host}...")
            net_connect = ConnectHandler(**device)
            net_connect.enable()

            all_cmds = []
            for i, row in df.iterrows():
                self.update_log(f"Processing: {row['name']}")
                all_cmds.extend([
                    f"ephone-dn {row['id']}",
                    f"number {row['extension']}",
                    f"label {row['name']}",
                    "exit",
                    f"ephone {row['id']}",
                    f"mac-address {row['mac']}",
                    f"button 1:{row['id']}",
                    "exit"
                ])
                # Update progress visually
                self.progress.set((i + 1) / total)

            self.update_log("Pushing configurations...")
            net_connect.send_config_set(all_cmds)
            net_connect.send_command("write memory")
            net_connect.disconnect()

            self.update_log("DONE: All phones provisioned successfully!")
            messagebox.showinfo("Success", "CME Configuration Updated!")
            
        except Exception as e:
            self.update_log(f"CRITICAL ERROR: {str(e)}")
            messagebox.showerror("Connection Failed", str(e))
        finally:
            self.progress.set(0)

if __name__ == "__main__":
    app = CMEApp()
    app.mainloop()
