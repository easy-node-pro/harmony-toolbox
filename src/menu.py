import os, subprocess
from os import environ
from colorama import Fore
from toolbox.config import easy_env
from toolbox.library import loader_intro, set_wallet_env, load_var_file, passphrase_status, set_var, version_checks, recheck_vars, recover_wallet, update_text_file, first_env_check, print_stars
from toolbox.toolbox import run_regular_node, run_full_node, refresh_stats, safety_defaults, start_regular_node

if __name__ == "__main__":
    if os.path.exists(f'{easy_env.user_home_dir}/validatortoolbox'):
        subprocess.run('clear') 
        print_stars()
        print('*\n* Old folder found, Exiting\n*\n* Please renmae your ~/validatortoolbox folder to ~/harmony-toolbox and update your command paths!\n*\n* Run: cd ~/ && mv ~/validatortoolbox ~/harmony-toolbox\n*\n* After you run the move command, relaunch with: python3 ~/harmony-toolbox/src/menu.py\n*')
        print_stars()
        raise SystemExit(0)
    # clear screen, show logo
    loader_intro()
    # check for .env file, if none we have a first timer.
    if os.path.exists(easy_env.dotenv_file) is None:
        # they should run the installer, goodbye!
        print("Install Harmony First!!!\nRun python3 ~/harmony-toolbox/install.py")
        raise SystemExit(0)
    # passed .env check, let's load it!
    first_env_check(easy_env.dotenv_file, easy_env.user_home_dir)
    # This section is for hard coding new settings for current users.
    safety_defaults()
    # always set conf to 13 keys, shard max
    if os.path.exists(easy_env.harmony_conf): update_text_file(easy_env.harmony_conf, "MaxKeys = 10", "MaxKeys = 13")
    # Make sure they have a wallet or wallet address in the .env file, if none, get one.
    if environ.get("VALIDATOR_WALLET") is None:
        recover_wallet()
        if environ.get("VALIDATOR_WALLET") is None:
            print(
                "* You don't currently have a validator wallet address loaded in your .env file, please edit ~/.easynode.env and add a line with the following info:\n "
                + "* VALIDATOR_WALLET='validatorONEaddress' "
            )
            input("* Press any key to exit.")
            raise SystemExit(0)
    # Last check on setup status, if it never finished it will try again here.
    if environ.get("SETUP_STATUS") != "2":
        recheck_vars()
        passphrase_status()
    # Run regular validator node
    if environ.get("NODE_TYPE") == "regular":
        if environ.get("VALIDATOR_WALLET") is None:
            set_wallet_env()
        start_regular_node()
    # Run full node
    if environ.get("NODE_TYPE") == "full":
        run_full_node()
    print("Uh oh, you broke me! Contact Easy Node")
    raise SystemExit(0)