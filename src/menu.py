import argparse, os, subprocess
from os import environ
from colorama import Fore
from toolbox.config import EnvironmentVariables
from toolbox.library import loader_intro, first_env_check, print_stars, load_var_file
from toolbox.toolbox import safety_defaults, start_regular_node, parse_flags

def app():
    load_var_file(EnvironmentVariables.dotenv_file)
    if os.path.exists(f"{EnvironmentVariables.user_home_dir}/validatortoolbox"):
        subprocess.run("clear")
        print_stars()
        print(
            Fore.GREEN
            + "*\n* Old folder found, Exiting toolbox.\n*\n* Please renmae your ~/validatortoolbox folder to ~/harmony-toolbox and update your command paths!\n*\n* Run: cd ~/ && mv ~/validatortoolbox ~/harmony-toolbox\n*\n* After you run the move command, relaunch with: python3 ~/harmony-toolbox/src/menu.py\n*"
        )
        print_stars()
        raise SystemExit(0)
    # Run parser if flags added
    parser = argparse.ArgumentParser(description="Findora Validator Toolbox - Help Menu")
    parse_flags(parser)
    # passed .env check, let's load it!
    fec_result = first_env_check(EnvironmentVariables.dotenv_file, EnvironmentVariables.user_home_dir)
    # This section is for hard coding new settings for current users.
    safety_defaults()
    # Run regular validator node
    start_regular_node()

if __name__ == "__main__":
    # Clear screen, show logo
    loader_intro()
    app()
