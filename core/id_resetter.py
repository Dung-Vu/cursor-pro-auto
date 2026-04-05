import os
import sys
import json
import uuid
import hashlib
import shutil
import sqlite3
import re
import tempfile
import winreg
from datetime import datetime
from colorama import Fore, Style, init

init()

class IDResetter:
    def __init__(self):
        self.appdata = os.getenv("APPDATA")
        self.localappdata = os.getenv("LOCALAPPDATA")
        
        self.storage_path = os.path.join(self.appdata, "Cursor", "User", "globalStorage", "storage.json")
        self.sqlite_path = os.path.join(self.appdata, "Cursor", "User", "globalStorage", "state.vscdb")
        self.machine_id_path = os.path.join(self.appdata, "Cursor", "machineId")
        
        # Cursor paths
        self.cursor_pkg_path = os.path.join(self.localappdata, "Programs", "Cursor", "resources", "app", "package.json")
        self.cursor_main_path = os.path.join(self.localappdata, "Programs", "Cursor", "resources", "app", "out", "main.js")
        
    def log_info(self, msg):
        print(f"{Fore.CYAN}[INFO] {msg}{Style.RESET_ALL}")
        
    def log_success(self, msg):
        print(f"{Fore.GREEN}[SUCCESS] {msg}{Style.RESET_ALL}")
        
    def log_error(self, msg):
        print(f"{Fore.RED}[ERROR] {msg}{Style.RESET_ALL}")

    def generate_new_ids(self):
        dev_device_id = str(uuid.uuid4())
        machine_id = hashlib.sha256(os.urandom(32)).hexdigest()
        mac_machine_id = hashlib.sha512(os.urandom(64)).hexdigest()
        sqm_id = "{" + str(uuid.uuid4()).upper() + "}"

        return {
            "telemetry.devDeviceId": dev_device_id,
            "telemetry.macMachineId": mac_machine_id,
            "telemetry.machineId": machine_id,
            "telemetry.sqmId": sqm_id,
            "storage.serviceMachineId": dev_device_id,
        }

    def update_storage_json(self, new_ids):
        if not os.path.exists(self.storage_path):
            self.log_error(f"storage.json not found at {self.storage_path}")
            return False
            
        try:
            with open(self.storage_path, "r", encoding="utf-8") as f:
                config = json.load(f)

            # Backup
            backup_path = f"{self.storage_path}.bak.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            shutil.copy2(self.storage_path, backup_path)

            # Update
            config.update(new_ids)

            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=4)
            self.log_success("Updated storage.json")
            return True
        except Exception as e:
            self.log_error(f"Failed to update storage.json: {e}")
            return False

    def update_sqlite_db(self, new_ids):
        if not os.path.exists(self.sqlite_path):
            return False
        try:
            conn = sqlite3.connect(self.sqlite_path)
            cursor = conn.cursor()
            cursor.execute("CREATE TABLE IF NOT EXISTS ItemTable (key TEXT PRIMARY KEY, value TEXT)")
            for key, value in new_ids.items():
                cursor.execute("INSERT OR REPLACE INTO ItemTable (key, value) VALUES (?, ?)", (key, value))
            conn.commit()
            conn.close()
            self.log_success("Updated state.vscdb (SQLite)")
            return True
        except Exception as e:
            self.log_error(f"Failed to update SQLite: {e}")
            return False

    def update_machine_id_file(self, machine_id):
        try:
            os.makedirs(os.path.dirname(self.machine_id_path), exist_ok=True)
            with open(self.machine_id_path, "w", encoding="utf-8") as f:
                f.write(machine_id)
            self.log_success("Updated machineId txt file")
        except Exception as e:
            self.log_error(f"Failed to write machineId file: {e}")

    def update_windows_registry(self):
        try:
            # Update MachineGuid
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Cryptography", 0, winreg.KEY_WRITE | winreg.KEY_WOW64_64KEY)
            winreg.SetValueEx(key, "MachineGuid", 0, winreg.REG_SZ, str(uuid.uuid4()))
            winreg.CloseKey(key)
            self.log_success("Updated Registry (Cryptography/MachineGuid)")
            
            # Update SQMClient
            try:
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\SQMClient", 0, winreg.KEY_WRITE | winreg.KEY_WOW64_64KEY)
            except FileNotFoundError:
                key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\SQMClient")
            winreg.SetValueEx(key, "MachineId", 0, winreg.REG_SZ, "{" + str(uuid.uuid4()).upper() + "}")
            winreg.CloseKey(key)
            self.log_success("Updated Registry (SQMClient/MachineId)")
        except PermissionError:
            self.log_error("Registry update failed: Please run as Administrator!")
        except Exception as e:
            self.log_error(f"Registry update failed: {e}")

    def patch_main_js(self):
        if not os.path.exists(self.cursor_main_path):
            self.log_error(f"Cannot find main.js at {self.cursor_main_path}")
            return False
            
        try:
            with open(self.cursor_main_path, "r", encoding="utf-8") as f:
                content = f.read()

            patterns = {
                r"async getMachineId\(\)\{return [^??]+\?\?([^}]+)\}": r"async getMachineId(){return \1}",
                r"async getMacMachineId\(\)\{return [^??]+\?\?([^}]+)\}": r"async getMacMachineId(){return \1}",
            }
            
            has_changes = False
            for pattern, replacement in patterns.items():
                if re.search(pattern, content):
                    content = re.sub(pattern, replacement, content)
                    has_changes = True

            if has_changes:
                backup = f"{self.cursor_main_path}.bak.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                shutil.copy2(self.cursor_main_path, backup)
                with open(self.cursor_main_path, "w", encoding="utf-8") as f:
                    f.write(content)
                self.log_success("Patched main.js core logic")
            else:
                self.log_info("main.js already patched or pattern not found.")
            return True
        except Exception as e:
            self.log_error(f"Failed to patch main.js: {e}")
            return False

    def reset_all(self):
        self.log_info("=== Droid Cursor ID Resetter ===")
        print(f"{Fore.YELLOW}Killing Cursor tasks...{Style.RESET_ALL}")
        os.system("taskkill /f /im cursor.exe >nul 2>&1")
        
        new_ids = self.generate_new_ids()
        self.log_info("Generated new IDs:")
        for k, v in new_ids.items():
            print(f"  {k}: {Fore.MAGENTA}{v}{Style.RESET_ALL}")
            
        self.update_storage_json(new_ids)
        self.update_sqlite_db(new_ids)
        self.update_machine_id_file(new_ids["telemetry.machineId"])
        self.update_windows_registry()
        self.patch_main_js()
        self.log_success("Machine ID Reset complete. You can now use a fresh trial!")
        return True

if __name__ == "__main__":
    resetter = IDResetter()
    resetter.reset_all()
