import os
import time
import random
from colorama import Fore, Style, init

# Ensure we can import from the same folder
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dummy_translator import translator
from cursor_auth import CursorAuth
from id_resetter import IDResetter
from new_tempemail import NewTempEmail
from new_signup import main as new_signup_main

init()

class CursorRegistration:
    def __init__(self):
        os.environ['BROWSER_HEADLESS'] = 'False'
        self.browser = None
        self.controller = None
        self.email_address = None
        self.signup_tab = None
        self.email_tab = None
        
        self.password = self._generate_password()
        
        first_names = ["James", "John", "Robert", "Michael", "William", "David", "Emma", "Olivia", "Ava", "Isabella", "Sophia", "Oliver", "Elijah"]
        last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Thomas", "Moore", "Jackson", "Lee"]
        
        fname = random.choice(first_names)
        self.first_name = random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ") + fname[1:]
        self.last_name = random.choice(last_names)
        
        print(f"\n{Fore.CYAN}[INFO] Generated Account Details:{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Name: {self.first_name} {self.last_name}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Password: {self.password}{Style.RESET_ALL}")

    def _generate_password(self, length=12):
        chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*"
        return ''.join(random.choices(chars, k=length))

    def setup_email(self):
        try:
            print(f"{Fore.CYAN}[START] Preparing Temporary Email...{Style.RESET_ALL}")
            self.temp_email = NewTempEmail(translator)
            email_address = self.temp_email.create_email()
            
            if not email_address:
                print(f"{Fore.RED}[ERROR] Failed to get temp email.{Style.RESET_ALL}")
                return False
                
            self.email_address = email_address
            self.email_tab = self.temp_email 
            print(f"{Fore.GREEN}[SUCCESS] Email Acquired: {self.email_address}{Style.RESET_ALL}")
            return True
        except Exception as e:
            print(f"{Fore.RED}[ERROR] Email Setup Failed: {e}{Style.RESET_ALL}")
            return False

    def register_cursor(self):
        browser_tab = None
        try:
            print(f"{Fore.CYAN}[START] Initiating Cursor Sign-up...{Style.RESET_ALL}")
            
            result, browser_tab = new_signup_main(
                email=self.email_address,
                password=self.password,
                first_name=self.first_name,
                last_name=self.last_name,
                email_tab=self.email_tab,
                controller=self.controller,
                translator=translator
            )
            
            if result:
                self.signup_tab = browser_tab
                success = self._get_account_info()
                if browser_tab:
                    try:
                        browser_tab.quit()
                    except:
                        pass
                return success
            return False
            
        except Exception as e:
            print(f"{Fore.RED}[ERROR] Sign-up Process failed: {e}{Style.RESET_ALL}")
            return False
        finally:
            if browser_tab:
                try:
                    browser_tab.quit()
                except:
                    pass
                
    def _get_account_info(self):
        try:
            settings_url = "https://www.cursor.com/settings"
            self.signup_tab.get(settings_url)
            time.sleep(2)
            
            print(f"{Fore.CYAN}[WAIT] Extracting Session Token...{Style.RESET_ALL}")
            max_attempts = 30
            for i in range(max_attempts):
                try:
                    cookies = self.signup_tab.cookies()
                    for cookie in cookies:
                        if cookie.get("name") == "WorkosCursorSessionToken":
                            token = cookie["value"].split("%3A%3A")[1]
                            print(f"{Fore.GREEN}[SUCCESS] Token Acquired!{Style.RESET_ALL}")
                            self._save_account_info(token)
                            return True
                    time.sleep(2)
                except Exception:
                    time.sleep(2)

            print(f"{Fore.RED}[ERROR] Timed out waiting for token.{Style.RESET_ALL}")
            return False

        except Exception as e:
            print(f"{Fore.RED}[ERROR] Account extract failed: {e}{Style.RESET_ALL}")
            return False

    def _save_account_info(self, token):
        try:
            print(f"{Fore.CYAN}[KEY] Injecting Token into Cursor Auth...{Style.RESET_ALL}")
            auth_manager = CursorAuth(translator=translator)
            if auth_manager.update_auth(email=self.email_address, access_token=token, refresh_token=token):
                print(f"{Fore.GREEN}[SUCCESS] Token Injected Successfully.{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}[ERROR] Token Injection Failed.{Style.RESET_ALL}")

            print(f"{Fore.CYAN}[UPDATE] Triggering Machine ID Reset...{Style.RESET_ALL}")
            resetter = IDResetter()
            resetter.reset_all()
            
            acc_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'cursor_accounts.txt')
            with open(acc_file, 'a', encoding='utf-8') as f:
                f.write(f"\n{'='*50}\n")
                f.write(f"Email: {self.email_address}\n")
                f.write(f"Password: {self.password}\n")
                f.write(f"Token: {token}\n")
                f.write(f"Date: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"{'='*50}\n")
                
            print(f"{Fore.GREEN}[SUCCESS] Account Registration Complete! Credentials saved to cursor_accounts.txt{Style.RESET_ALL}")
            return True
            
        except Exception as e:
            print(f"{Fore.RED}[ERROR] Failed to save/inject account: {e}{Style.RESET_ALL}")
            return False

    def start(self):
        try:
            if self.setup_email():
                self.register_cursor()
        finally:
            if hasattr(self, 'temp_email'):
                try:
                    self.temp_email.close()
                except:
                    pass

def run_auto_register():
    print(f"\n{Fore.GREEN}{'='*50}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}[START] Cursor Pro Auto-Register Sequence{Style.RESET_ALL}")
    print(f"{Fore.GREEN}{'='*50}{Style.RESET_ALL}")

    registration = CursorRegistration()
    registration.start()

if __name__ == "__main__":
    run_auto_register()
