import os
import sys
from colorama import Fore, Style, init

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'core'))

from core.id_resetter import IDResetter
from core.auto_register import run_auto_register

init()

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
    banner = f"""
{Fore.GREEN}
   ██████╗ ██╗   ██╗██████╗ ███████╗ ██████╗ ██████╗ 
  ██╔════╝ ██║   ██║██╔══██╗██╔════╝██╔═══██╗██╔══██╗
  ██║      ██║   ██║██████╔╝███████╗██║   ██║██████╔╝
  ██║      ██║   ██║██╔══██╗╚════██║██║   ██║██╔══██╗
  ╚██████╗ ╚██████╔╝██║  ██║███████║╚██████╔╝██║  ██║
   ╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═╝  ╚═╝
{Fore.CYAN}       --- PRO AUTO TOOL (100% OFFLINE / SAFE) ---
{Style.RESET_ALL}
    """
    print(banner)

def main_menu():
    while True:
        clear_screen()
        print_banner()
        print(f"{Fore.YELLOW}  [1]{Style.RESET_ALL} Reset Machine ID (Fast & Offline)")
        print(f"{Fore.YELLOW}  [2]{Style.RESET_ALL} Auto Sign-up & Reset (Browser Automation)")
        print(f"{Fore.YELLOW}  [3]{Style.RESET_ALL} Exit")
        print(f"\n{Fore.CYAN}  Please select an option: {Style.RESET_ALL}", end="")
        
        choice = input().strip()
        
        if choice == '1':
            print(f"\n{Fore.CYAN}[*] Starting Machine ID Reset...{Style.RESET_ALL}")
            resetter = IDResetter()
            resetter.reset_all()
            input(f"\n{Fore.GREEN}Press Enter to return to menu...{Style.RESET_ALL}")
            
        elif choice == '2':
            print(f"\n{Fore.CYAN}[*] Starting Auto Registration...{Style.RESET_ALL}")
            run_auto_register()
            input(f"\n{Fore.GREEN}Press Enter to return to menu...{Style.RESET_ALL}")
            
        elif choice == '3' or choice.lower() == 'q':
            print(f"\n{Fore.CYAN}Goodbye!{Style.RESET_ALL}")
            sys.exit(0)
            
        else:
            print(f"\n{Fore.RED}Invalid option. Please try again.{Style.RESET_ALL}")
            import time
            time.sleep(1)

if __name__ == "__main__":
    if not (sys.platform.startswith("win")):
        print(f"{Fore.RED}This tool is currently optimized for Windows.{Style.RESET_ALL}")
    main_menu()
