import psutil
import platform
import dotenv
import time
import os
import subprocess
import requests
import pyhmy
import shutil
import docker
from toolbox.config import easy_env
from os import environ
from dotenv import load_dotenv
from simple_term_menu import TerminalMenu
from colorama import Fore, Style
from pathlib import Path
from pyhmy import validator, account, staking, numbers
from json import load, dump
from toolbox.config import easy_env
from collections import namedtuple
from datetime import datetime

load_dotenv(easy_env.dotenv_file)

class print_stuff:
    def __init__(self, reset: int = 0):
        self.reset = reset
        self.print_stars = "*" * 93
        self.reset_stars = self.print_stars + Style.RESET_ALL

    def printStars(self) -> None:
        p = self.print_stars
        if self.reset:
            p = self.reset_stars
        print(p)

    def stringStars(self) -> str:
        p = self.print_stars
        if self.reset:
            p = self.reset_stars
        return p

    @classmethod
    def printWhitespace(self) -> None:
        print("\n" * 8)

print_whitespace = print_stuff.printWhitespace
print_stars = print_stuff().printStars
string_stars = print_stuff().stringStars
print_stars_reset = print_stuff(reset=1).printStars
string_stars_reset = print_stuff(reset=1).stringStars

# check if a var exists in your .env file, unset and reset if exists to avoid bad stuff
def set_var(env_file, key_name, update_name):
    if environ.get(key_name):
        dotenv.unset_key(env_file, key_name)
    dotenv.set_key(env_file, key_name, update_name)
    load_var_file(env_file)
    return

# loader intro splash screen
def loader_intro():
    subprocess.run("clear")
    p = f"""
                    ____ ____ ____ ____ _________ ____ ____ ____ ____           
                    ||E |||a |||s |||y |||       |||N |||o |||d |||e ||          
                    ||__|||__|||__|||__|||_______|||__|||__|||__|||__||          
                    |/__\|/__\|/__\|/__\|/_______\|/__\|/__\|/__\|/__\|          
                        ____ ____ ____ ____ ____ ____ ____ ____ ____                
                        ||v |||a |||l |||i |||d |||a |||t |||o |||r ||               
                        ||__|||__|||__|||__|||__|||__|||__|||__|||__||               
                        |/__\|/__\|/__\|/__\|/__\|/__\|/__\|/__\|/__\|               
                            ____ ____ ____ ____ ____ ____ ____                          
                            ||T |||o |||o |||l |||b |||o |||x ||                         
                            ||__|||__|||__|||__|||__|||__|||__||                         
                            |/__\|/__\|/__\|/__\|/__\|/__\|/__\|   
                                            
    """
    print_stars()
    print(p)
    return

# Install Harmony ONE
def install_hmy():
    os.chdir(f"{easy_env.harmony_dir}")
    os.system("curl -LO https://harmony.one/hmycli && mv hmycli hmy && chmod +x hmy")
    print_stars()
    print("* hmy application installed.")
    return

# Code to update the harmony.conf after an upgrade and other text files.
def update_text_file(fileName, originalText, newText):
    with open(fileName, "r") as f:
        filedata = f.read()

    newdata = filedata.replace(originalText, newText)

    with open(fileName, "w") as f:
        f.write(newdata)

# Setup a wallet, ask if they need to import one (not required but no toolbox menu without a wallet)
def recover_wallet():
    question = ask_yes_no(f"* Would you like to import a wallet? (YES/NO) ")
    # if yes, find recovery type
    if question:
        recovery_type()
        load_var_file(easy_env.dotenv_file)
        print(
            f'\n* Verify the address above matches the address below:\n* Detected Wallet: {Fore.GREEN}{environ.get("VALIDATOR_WALLET")}{Style.RESET_ALL}\n* If a different wallet is showing you can remove it and retry it after installation.\n*\n* .{easy_env.hmy_app} keys remove {easy_env.active_user}\n*\n* To restore a wallet once again, run the following:\n*\n* .{easy_env.hmy_app} keys recover-from-mnemonic {easy_env.active_user} {environ.get("PASS_SWITCH")}\n*'
        )
        print_stars()
        input("* Verify your wallet information above.\n* Press ENTER to continue Installation.")
    else:
        wallet = input(
            f"* If you'd like to use the management menu, we need a one1 address, please input your address now: "
        )
        set_var(easy_env.dotenv_file, "VALIDATOR_WALLET", wallet)
        return

def install_harmony():
    os.chdir(f"{easy_env.harmony_dir}")
    if environ.get("NETWORK") == "testnet":
        os.system("curl -LO https://harmony.one/binary_testnet && mv binary_testnet harmony && chmod +x harmony")
        os.system("./harmony config dump --network testnet harmony.conf")
        update_text_file(easy_env.harmony_conf, "MaxKeys = 10", "MaxKeys = 13")
    if environ.get("NETWORK") == "mainnet":
        os.system("curl -LO https://harmony.one/binary && mv binary harmony && chmod +x harmony")
        os.system("./harmony config dump harmony.conf")
        update_text_file(easy_env.harmony_conf, "MaxKeys = 10", "MaxKeys = 13")
    print_stars()
    print("* harmony.conf MaxKeys modified to 13")
    if os.path.exists(easy_env.bls_key_file):
        update_text_file(easy_env.harmony_conf, 'PassFile = ""', f'PassFile = "blskey.pass"')
        print("* blskey.pass found, updated harmony.conf")
    print_stars()
    print(f"* Harmony {environ.get('NETWORK')} application installed & ~/harmony/harmony.conf created.")
    return

def set_wallet_env():
    if environ.get("NODE_WALLET") == "true":
        if not environ.get("VALIDATOR_WALLET"):
            output = subprocess.getoutput(
                f"{easy_env.hmy_app} keys list | grep {easy_env.active_user}"
            )
            output_stripped = output.lstrip(easy_env.active_user)
            output_stripped = output_stripped.strip()
            set_var(easy_env.dotenv_file, "VALIDATOR_WALLET", output_stripped)
            return output_stripped
        else:
            load_var_file(easy_env.dotenv_file)
            validator_wallet = environ.get("VALIDATOR_WALLET")
            return validator_wallet

def recovery_type():
    subprocess.run("clear")
    set_var(easy_env.dotenv_file, "NODE_WALLET", "true")
    passphrase_status()
    passphrase_switch = environ.get("PASS_SWITCH")
    print_stars()
    print("* Wallet Recovery Type!                                                                     *")
    print_stars()
    print("* [0] = Mnemonic phrase recovery (aka seed phrase)                                          *")
    print("* [1] = Private Key recovery                                                                *")
    print_stars()
    menu_options = [
        "[0] - Mnemonic Phrase Recovery",
        "[1] - Private Key Recovery",
    ]
    terminal_menu = TerminalMenu(
        menu_options, title="* Which type of restore method would you like to use for your validator wallet?"
    )
    results = terminal_menu.show()
    if results == 0:
        # Mnemonic Recovery Here
        os.system(
            f"{easy_env.hmy_app} keys recover-from-mnemonic {easy_env.active_user} {passphrase_switch}"
        )
        print_stars()
        set_wallet_env()
    elif results == 1:
        # Private Key Recovery Here
        print("* Private key recovery requires your private information in the command itself.")
        private = input("* Please enter your private key to restore your wallet: ")
        os.system(
            f"{easy_env.hmy_app} keys import-private-key {private} {easy_env.active_user} --passphrase"
        )
        print_stars()
        set_wallet_env()

def passphrase_status():
    load_var_file(easy_env.dotenv_file)
    if environ.get("NODE_WALLET") == "true":
        passphrase_set()
        set_var(
            easy_env.dotenv_file,
            "PASS_SWITCH",
            f"--passphrase-file {easy_env.harmony_dir}/passphrase.txt",
        )
    if environ.get("NODE_WALLET") == "false":
        set_var(easy_env.dotenv_file, "PASS_SWITCH", "--passphrase")

def passphrase_set():
    if os.path.exists(easy_env.password_path):
        return
    import getpass
    
    print("* Setup ~/harmony/passphrase.txt file for use with autobidder & validatortoolbox.")
    print_stars()
    # take input
    while True:
        print("* ")
        password_1 = getpass.getpass(
            prompt="* Please set a wallet password for this node\n* Enter your password now: ", stream=None
        )
        password_2 = getpass.getpass(prompt="* Re-enter your password: ", stream=None)
        if not password_1 == password_2:
            print("* Passwords do NOT match, Please try again..")
        else:
            print("* Passwords Match!")
            break
    # Save file, we won't encrypt because if someone has access to the file, they will also have the salt and decrypt code at their disposal.
    save_text(easy_env.password_path, password_1)
    load_var_file(easy_env.dotenv_file)
    passphrase_status()

def process_command(command: str) -> None:
    process = subprocess.Popen(command, shell=True)
    output, error = process.communicate()

def ask_yes_no(question: str) -> bool:
    yes_no_answer = ""
    while not yes_no_answer.startswith(("Y", "N")):
        yes_no_answer = input(f"{question}: ").upper()
    if yes_no_answer.startswith("Y"):
        return True
    return False

def save_text(fn: str, to_write: str) -> bool:
    try:
        with open(fn, "w") as f:
            f.write(to_write)
            return True
    except Exception as e:
        print(f"Error writing file  ::  {e}")
        return False

def return_txt(fn: str) -> list:
    try:
        with open(fn, "r") as f:
            return f.readlines()
    except FileNotFoundError as e:
        print(f"File not Found  ::  {e}")
        return []

def load_var_file(var_file):
    if os.path.exists(var_file):
        load_dotenv(var_file, override=True)
    else:
        subprocess.run(["touch", var_file])

def get_shard_menu() -> None:
    if not environ.get("SHARD"):
        subprocess.run("clear")
        print_stars()
        print("* First Boot - Gathering more information about your server                                 *")
        print_stars()
        print("* Which shard do you want this node run on?                                                 *")
        print_stars()
        menu_options = [
            "[0] - Shard 0",
            "[1] - Shard 1",
            "[2] - Shard 2",
            "[3] - Shard 3",
        ]
        terminal_menu = TerminalMenu(menu_options, title="* Which Shard will this node operate on? ")
        our_shard = str(terminal_menu.show())
        set_var(easy_env.dotenv_file, "SHARD", our_shard)
        return our_shard

def get_node_type() -> None:
    if not os.path.exists(easy_env.hmy_wallet_store):
        if environ.get("NODE_TYPE") == None:
            subprocess.run("clear")
            print_stars()
            print("* Which type of node would you like to run on this server?                                  *")
            print_stars()
            print("* [0] - Standard w/ Wallet - Harmony Validator Signing Node with Wallet                     *")
            print("* [1] - Standard No Wallet - Harmony Validator Signing Node no Wallet                       *")
            print("* [2] - Full Node Dev/RPC - Non Validating Harmony Node                                     *")
            print_stars()
            menu_options = [
                "[0] Signing Node w/ Wallet",
                "[1] Signing Node No Wallet",
                "[2] Full Node Non Validating Dev/RPC",
            ]
            terminal_menu = TerminalMenu(menu_options, title="Regular or Full Node Server")
            results = terminal_menu.show()
            if results == 0:
                set_var(easy_env.dotenv_file, "NODE_TYPE", "regular")
                set_var(easy_env.dotenv_file, "NODE_WALLET", "true")
            if results == 1:
                set_var(easy_env.dotenv_file, "NODE_TYPE", "regular")
                set_var(easy_env.dotenv_file, "NODE_WALLET", "false")
            if results == 2:
                set_var(easy_env.dotenv_file, "NODE_TYPE", "full")
            subprocess.run("clear")
            return
        set_wallet_env()
    if not environ.get("NODE_TYPE"):
        set_var(easy_env.dotenv_file, "NODE_TYPE", "regular")
    if not environ.get("NODE_WALLET"):
        set_var(easy_env.dotenv_file, "NODE_WALLET", "true")

def set_main_or_test() -> None:
    if not environ.get("NETWORK"):
        subprocess.run("clear")
        print_stars()
        print("* Setup config not found, which blockchain does this node run on?                           *")
        print_stars()
        print("* [0] - Mainnet                                                                             *")
        print("* [1] - Testnet                                                                             *")
        print_stars()
        menu_options = [
            "[0] Mainnet",
            "[1] Testnet",
        ]
        terminal_menu = TerminalMenu(menu_options, title="Mainnet or Testnet")
        results = terminal_menu.show()
        if results == 0:
            set_var(easy_env.dotenv_file, "NETWORK", "mainnet")
            set_var(easy_env.dotenv_file, "NETWORK_SWITCH", "t")
            set_var(easy_env.dotenv_file, "RPC_NET", "https://rpc.s0.t.hmny.io")
            set_var(easy_env.dotenv_file, "RPC_NET_SHARD", f"https://rpc.s{environ.get('SHARD')}.t.hmny.io")
        if results == 1:
            set_var(easy_env.dotenv_file, "NETWORK", "testnet")
            set_var(easy_env.dotenv_file, "NETWORK_SWITCH", "b")
            set_var(easy_env.dotenv_file, "RPC_NET", "https://rpc.s0.b.hmny.io")
            set_var(easy_env.dotenv_file, "RPC_NET_SHARD", f"https://rpc.s{environ.get('SHARD')}.b.hmny.io")
        subprocess.run("clear")
    return

def get_express_status() -> None:
    if environ.get("SETUP_STATUS") == "0":
        subprocess.run("clear")
        print_stars()
        print("* Express or Manual Setup?                                                                  *")
        print_stars()
        print("* Would you like the turbo express setup or Manual approval of each step?                   *")
        print_stars()
        menu_options = [
            "[0] - Express Install",
            "[1] - Manual Approval",
        ]
        terminal_menu = TerminalMenu(menu_options, title="* Express Or Manual Setup")
        set_var(easy_env.dotenv_file, "EXPRESS", str(terminal_menu.show()))


def get_wallet_address():
    print("* Signing Node, No Wallet!                                                                  *")
    print("* You are attempting to launch the menu but no wallet has been loaded, as you chose         *")
    print("* If you would like to use the menu on the server, complete the following:                  *")
    print_stars()
    print("* Edit ~/.easynode.env and add your wallet address on a new line like this example:         *")
    print("* VALIDATOR_WALLET='one1thisisjustanexamplewalletreplaceme'                                 *")
    print_stars()
    raise SystemExit(0)

def set_api_paths():
    if not environ.get("NETWORK_0_CALL"):
        set_var(
            easy_env.dotenv_file,
            "NETWORK_0_CALL",
            f"{easy_env.hmy_app} --node='https://api.s0.{environ.get('NETWORK_SWITCH')}.hmny.io' ",
        )
        set_var(
            easy_env.dotenv_file,
            "NETWORK_S_CALL",
            f"{easy_env.hmy_app} --node='https://api.s{environ.get('SHARD')}.{environ.get('NETWORK_SWITCH')}.hmny.io' ",
        )

def get_validator_info():
    if environ.get("NETWORK") == "mainnet":
        endpoint = len(easy_env.rpc_endpoints)
    if environ.get("NETWORK") == "testnet":
        endpoint = len(easy_env.rpc_endpoints_test)
    current = 0
    max_tries = easy_env.rpc_endpoints_max_connection_retries
    validator_data = -1

    while current < max_tries:
        try:
            validator_data = staking.get_validator_information(environ.get("VALIDATOR_WALLET"), endpoint)
            return validator_data
        except Exception:
            current += 1
            continue

    return validator_data

def current_price():
    try:
        response = requests.get(easy_env.onePriceURL, timeout=5)
    except (ValueError, KeyError, TypeError):
        response = "0.0000"
        return response
    data_dict = response.json()
    type(data_dict)
    data_dict.keys()
    return data_dict["lastPrice"][:-4]

def get_wallet_balance(wallet_addr):
    endpoints_count = len(easy_env.rpc_endpoints)

    for i in range(endpoints_count):
        wallet_balance = get_wallet_balance_by_endpoint(easy_env.rpc_endpoints[i], wallet_addr)
        wallet_balance_test = get_wallet_balance_by_endpoint(easy_env.rpc_endpoints_test[i], wallet_addr)

        if wallet_balance >= 0 and wallet_balance_test >= 0:
            return wallet_balance, wallet_balance_test

    raise ConnectionError("Couldn't fetch RPC data for current epoch.")

def get_wallet_balance_by_endpoint(endpoint, wallet_addr):
    current = 0
    max_tries = easy_env.rpc_endpoints_max_connection_retries
    get_balance = 0

    while current < max_tries:
        try:
            get_balance = pyhmy.numbers.convert_atto_to_one(account.get_balance(wallet_addr, endpoint))
            return get_balance
        except Exception:
            current += 1
            continue

    return get_balance

def get_rewards_balance(endpoint, wallet_addr):
    endpoints_count = len(endpoint)

    for i in range(endpoints_count):
        wallet_balance = get_rewards_balance_by_endpoint(endpoint[i], wallet_addr)

        if wallet_balance >= 0:
            return wallet_balance

    raise ConnectionError("Couldn't fetch RPC data for current epoch.")

def get_rewards_balance_by_endpoint(endpoint, wallet_addr):
    current = 0
    max_tries = easy_env.rpc_endpoints_max_connection_retries
    totalRewards = 0

    try:
        validator_rewards = staking.get_delegations_by_delegator(wallet_addr, endpoint)
    except Exception:
        return totalRewards

    for i in validator_rewards:
        totalRewards = totalRewards + i["reward"]
    totalRewards = pyhmy.numbers.convert_atto_to_one(totalRewards)
    return totalRewards

def save_json(fn: str, data: dict) -> dict:
    with open(fn, "w") as j:
        dump(data, j, indent=4)

def return_json(fn: str, single_key: str = None) -> dict:
    try:
        with open(fn, "r", encoding="utf-8") as j:
            data = load(j)
            if single_key:
                return data.get(single_key)
            return data
    except FileNotFoundError as e:
        # print(f"File not Found  ::  {e}")
        return {}

def wallet_pending_rewards(wallet):
    res, walletBalance = get_rewards_balance(wallet, save_data=True, display=False)
    totalRewards = 0
    for i in walletBalance["result"]:
        totalRewards = totalRewards + i["reward"]
    totalRewards = "{:,}".format(round(totalRewards * 0.000000000000000001, 2))
    return totalRewards

def get_sign_pct() -> str:
    output = subprocess.getoutput(
        f"{environ.get('NETWORK_0_CALL')} blockchain validator information {environ.get('VALIDATOR_WALLET')} | grep signing-percentage"
    )
    output_stripped = output.lstrip('        "current-epoch-signing-percentage": "').rstrip('",')
    try:
        math = float(output_stripped)
        signPerc = math * 100
        roundSignPerc = round(signPerc, 6)
        return str(roundSignPerc)
    except (OSError, ValueError):
        output_stripped = "0"
        return str(output_stripped)

def get_local_version(folder):
    harmony_version = subprocess.getoutput(f"{folder}/harmony -V")
    hmy_version = subprocess.getoutput(f"{folder}/hmy version")
    return harmony_version[35:-35], hmy_version[62:-15]

def set_mod_x(file):
    subprocess.run(["chmod", "+x", file])

def check_online_version():
    subprocess.check_output(
        ["wget", "https://harmony.one/binary", "-O", easy_env.hmy_tmp_path], stderr=subprocess.STDOUT
    )
    set_mod_x(easy_env.hmy_tmp_path)
    subprocess.check_output([easy_env.hmy_tmp_path, "config", "dump", "harmony.conf"], stderr=subprocess.STDOUT)
    harmony_ver = subprocess.getoutput(f"{easy_env.hmy_tmp_path} -V")
    subprocess.check_output(
        ["wget", "https://harmony.one/hmycli", "-O", easy_env.hmy_tmp_path], stderr=subprocess.STDOUT
    )
    set_mod_x(easy_env.hmy_tmp_path)
    hmy_ver = subprocess.getoutput(f"{easy_env.hmy_tmp_path} version")
    return harmony_ver[35:-35], hmy_ver[62:-15]

def first_env_check(env_file, home_dir) -> None:
    if os.path.exists(env_file):
        load_var_file(env_file)
    else:
        os.system(f"touch {home_dir}/.easynode.env")
        load_var_file(env_file)

def version_checks(folder = f'harmony'):
    software_versions = {}
    software_versions["harmony_version"], software_versions["hmy_version"] = get_local_version(f'{easy_env.user_home_dir}/{folder}')
    software_versions["online_harmony_version"], software_versions["online_hmy_version"] = check_online_version()
    # Check versions, if matching False (No Upgrade Required), non-match True (Upgrade Required)
    if software_versions["harmony_version"] == software_versions["online_harmony_version"]:
        software_versions["harmony_upgrade"] = "False"
    else:
        software_versions["harmony_upgrade"] = "True"
    if software_versions["hmy_version"] == software_versions["online_hmy_version"]:
        software_versions["hmy_upgrade"] = "False"
    else:
        software_versions["hmy_upgrade"] = "True"
    return software_versions

def first_setup():
    first_env_check(easy_env.dotenv_file, easy_env.user_home_dir)
    # first run stuff
    time.sleep(2)
    # Update version if newer from conf file to .easynode.env
    if environ.get("EASY_VERSION"):
        set_var(easy_env.dotenv_file, "EASY_VERSION", easy_env.easy_version)
    # Find Shard #
    get_shard_menu()
    # Express - no prompts for each step, Manual - prompts for each step
    get_express_status()
    # Get Regular validator with/without wallet or Full RPC Node
    get_node_type()
    # Get Mainnet or Testnet
    set_main_or_test()
    # Set the API for previous choices
    set_api_paths()
    # Setup status done
    set_var(easy_env.dotenv_file, "SETUP_STATUS", "0")
    # Look for a harmony install or install.
    check_for_install()
    print_stars()
    return

def recheck_vars():
    # recheck some stuff just in case the .easynode.env isn't proper
    load_var_file(easy_env.dotenv_file)
    get_shard_menu()
    get_node_type()
    set_main_or_test()
    set_api_paths()
    return

# looks for ~/harmony or installs it if it's not there. Asks to overwrite if it finds it, run at your own risk.
def check_for_install() -> str:
    load_var_file(easy_env.dotenv_file)
    if not os.path.exists(easy_env.harmony_dir):
        print(f"* You selected Shard: {environ.get('SHARD')}. ")
        install_harmony()
        if environ.get("NODE_WALLET") == "true":
            restore_wallet()
        print_stars()
        print("* All harmony files now installed. Database download starting now...")
        print_stars()
        clone_shards()
        finish_node_install()
    else:
        question = ask_yes_no(
            "* You already have a harmony folder on this system, would you like to re-run installation and rclone? (YES/NO)"
        )
        if question:
            install_harmony()
            if environ.get("NODE_WALLET") == "true":
                restore_wallet()
            print_stars()
            print("* All harmony files now installed. Database download starting now...")
            print_stars()
            clone_shards()
            finish_node_install()

# Installer Module
def install_harmony() -> None:
    # check disk space, find mounted disks
    mntCount = 0
    if os.path.isdir("/dev/disk/by-id/"):
        testMnt = "/mnt"
        for subdir, dirs, files in os.walk(testMnt):
            for dir in dirs:
                tester = os.path.join(subdir, dir)
                if os.path.ismount(tester):
                    myVolumePath = tester
                    mntCount = mntCount + 1

        # if you have more than one, we'll have to find a way to list them and let people choose
        if mntCount > 1:
            print("* You have multiple mounts in /mnt - Review mounts, only 1 allowed for our installer at this time!")
            raise SystemExit(0)
        # Checks Passed at this point, only 1 folder in /mnt and it's probably our volume (can scope this down further later)
        if environ.get("SHARD") == "0":
            if mntCount == 1:
                myLongHmyPath = myVolumePath + "/harmony"
                dotenv.set_key(easy_env.dotenv_file, "MOUNT_POINT", myLongHmyPath)
                print("* Creating all Harmony Files & Folders")
                os.system(f"sudo chown {easy_env.active_user} {myVolumePath}")
                os.system(f"mkdir -p {myLongHmyPath}/.hmy/blskeys")
                os.system(f"ln -s {myLongHmyPath} {easy_env.harmony_dir}")
            # Let's make sure your volume is mounted
            if mntCount == 0:
                question = ask_yes_no(
                    "* You have a volume but it is not mounted.\n* Would you like to install Harmony in ~/harmony on your main disk instead of your volume? (Yes/No) "
                )
                if question:
                    dotenv.set_key(easy_env.dotenv_file, "MOUNT_POINT", easy_env.harmony_dir)
                else:
                    raise SystemExit(0)
    # Setup folders now that symlink exists or we know we're using ~/harmony
    if not os.path.isdir(f"{easy_env.user_home_dir}/.hmy_cli/account-keys/"):
        os.system(f"mkdir -p {easy_env.user_home_dir}/.hmy_cli/account-keys/")
    if not os.path.isdir(f"{easy_env.harmony_dir}/.hmy/blskeys"):
        print("* Creating all Harmony Files & Folders")
        os.system(f"mkdir -p {easy_env.harmony_dir}/.hmy/blskeys")
    # Change to ~/harmony folder
    os.chdir(f"{easy_env.harmony_dir}")
    print_stars()
    # Install hmy
    install_hmy()
    print_stars()
    # Install harmony
    install_harmony()
    # install hmy files
    print("* Installing rclone application & rclone configuration files")
    print_stars()
    # check for working rclone site and download
    try:
        os.system("curl https://rclone.org/install.sh | sudo bash")
    except (ValueError, KeyError, TypeError):
        result = ask_yes_no(
            "* rclone site is offline, we can install rclone from the Ubuntu repo as a workaround, do you want to continue? (Y/N): "
        )
        if result:
            # If rclone curl is down, install rclone with apt instead
            subprocess.run('sudo apt install rclone -y')

    os.system(
        f"mkdir -p {easy_env.user_home_dir}/.config/rclone && cp {easy_env.toolbox_location}/src/bin/rclone.conf {easy_env.user_home_dir}/.config/rclone/"
    )
    print_stars()
    # Setup the harmony service file
    print("* Customizing, Moving & Enabling your harmony.service systemd file")
    if easy_env.active_user == "root":
        os.system(
            f"sudo cp {easy_env.toolbox_location}/src/bin/harmony.service . && sed -i 's/home\/serviceharmony/{easy_env.active_user}/g' 'harmony.service' && sed -i 's/serviceharmony/{easy_env.active_user}/g' 'harmony.service' && sudo mv harmony.service /etc/systemd/system/harmony.service && sudo chmod a-x /etc/systemd/system/harmony.service && sudo systemctl enable harmony.service"
        )
    else:
        os.system(
            f"sudo cp {easy_env.toolbox_location}/src/bin/harmony.service . && sed -i 's/serviceharmony/{easy_env.active_user}/g' 'harmony.service' && sudo mv harmony.service /etc/systemd/system/harmony.service && sudo chmod a-x /etc/systemd/system/harmony.service && sudo systemctl enable harmony.service"
        )

# Database Downloader
def clone_shards():
    # Move to ~/harmony
    os.chdir(f"{easy_env.harmony_dir}")
    
    if environ.get("SHARD") != "0":
        # If we're not on shard 0, download the numbered shard DB here.
        print(f"* Now cloning shard {environ.get('SHARD')}")
        print_stars()
        os.system(
            f"rclone -P sync release:pub.harmony.one/{environ.get('NETWORK')}.min/harmony_db_{environ.get('SHARD')} {easy_env.harmony_dir}/harmony_db_{environ.get('SHARD')} --multi-thread-streams 4 --transfers=32"
        )
        print_stars()
        print(f"Shard {environ.get('SHARD')} completed.")
        print_stars()
    else:
        # If we're on shard 0, grab the snap DB here.
        print("* Now cloning Shard 0, kick back and relax for awhile...")
        print_stars()
        os.system(
            f"rclone -P -L --checksum sync release:pub.harmony.one/{environ.get('NETWORK')}.snap/harmony_db_0 {easy_env.harmony_dir}/harmony_db_0 --multi-thread-streams 4 --transfers=32"
        )

# Code to restore a wallet
def restore_wallet() -> str:
    if environ.get("NODE_WALLET") == "true":
        if not os.path.exists(easy_env.hmy_wallet_store):
            subprocess.run("clear")
            print_stars()
            print("* Harmony ONE Validator Wallet Import")
            print_stars()
            if environ.get("EXPRESS") == "1":
                question = ask_yes_no(
                    "\n* You will directly utilize the harmony application interface"
                    + "\n* We do not store any pass phrases  or data inside of our application"
                    + "\n* Respond yes to recover your validator wallet via Mnemonic phrase now or say NO to create a new wallet post-install"
                    + "\n* Restore an existing wallet now? (YES/NO) "
                )
                if question:
                    passphrase_status()
                    recover_wallet()
                print_stars()
                return
            passphrase_status()
            recover_wallet()
            return
        print_stars()
        print("* Wallet already setup for this user account")

# is this used?
def set_mounted_point():
    # First let's make sure your volume is mounted
    totalDir = len(os.listdir("/mnt"))
    if totalDir > 0:
        volumeMountPath = os.listdir("/mnt")
        myVolumePath = "/mnt/" + str(volumeMountPath[0])
        myLongHmyPath = myVolumePath + "/harmony"
    else:
        myVolumePath = easy_env.harmony_dir
    if totalDir == 1:
        dotenv.set_key(easy_env.dotenv_file, "MOUNT_POINT", myLongHmyPath)
    else:
        dotenv.set_key(easy_env.dotenv_file, "MOUNT_POINT", f"{easy_env.harmony_dir}")

def finish_node_install():
    load_var_file(easy_env.dotenv_file)
    print_stars()
    print(
        "* Installation is completed"
        + "\n* Create a new wallet or recover your existing wallet into ./hmy"
        + "\n* Create or upload your bls key & pass files into ~/harmony/.hmy/blskeys"
        + "\n* Finally, reboot to start synchronization."
    )
    print_stars()
    if environ.get("NODE_WALLET") == "false":
        print(
            "* Post installation quick tips:"
            + "\n* To recover your wallet on this server run:"
            + f"\n* python3 ~/validatortoolboxload_wallet.py"
            + "\n*"
            + "\n* To create BLS keys run:"
            + f'\n* ./hmy keys generate-bls-keys --count 1 --shard {environ.get("SHARD")} --passphrase'
            + "\n*"
        )
    else:
        print(
            "* Post installation quick tips:"
            + "\n* To recover your wallet again, run:"
            + f"\n* python3 ~/validatortoolboxload_wallet.py"
            + "\n*"
            + "\n* To create BLS keys run:"
            + f'\n* ./hmy keys generate-bls-keys --count 1 --shard {environ.get("SHARD")} {environ.get("PASS_SWITCH")}'
            + "\n*"
        )
    print_stars()
    print("* Thanks for using Easy Node - Validator Node Server Software Installer!")
    print_stars()
    set_var(easy_env.dotenv_file, "SETUP_STATUS", "1")
    raise SystemExit(0)

def free_space_check(mount) -> str:
    ourDiskMount = get_mount_point(mount)
    _, _, free = shutil.disk_usage(ourDiskMount)
    freeConverted = str(converted_unit(free))
    return freeConverted

def server_drive_check(dot_env, directory) -> None:
    if environ.get("MOUNT_POINT") is not None:
        ourDiskMount = environ.get("MOUNT_POINT")
    else:
        dotenv.set_key(dot_env, "MOUNT_POINT", directory)
        load_var_file(dot_env)
        ourDiskMount = environ.get("MOUNT_POINT")
    print_stars()
    print("Here are all of your mount points: ")
    for part in disk_partitions():
        print(part)
    print_stars()
    total, used, free = shutil.disk_usage(ourDiskMount)
    total = str(converted_unit(total))
    used = str(converted_unit(used))
    print("Disk: " + str(ourDiskMount) + "\n" + free_space_check(directory) + " Free\n" + used + " Used\n" + total + " Total")
    print_stars()
    input("Disk check complete, press ENTER to return to the main menu. ")

def disk_partitions(all=False):
    disk_ntuple = namedtuple("partition", "device mountpoint fstype")
    # Return all mounted partitions as a nameduple.
    # If all == False return physical partitions only.
    phydevs = []
    with open("/proc/filesystems", "r") as f:
        for line in f:
            if not line.startswith("nodev"):
                phydevs.append(line.strip())

    retlist = []
    with open("/etc/mtab", "r") as f:
        for line in f:
            if not all and line.startswith("none"):
                continue
            fields = line.split()
            device = fields[0]
            mountpoint = fields[1]
            fstype = fields[2]
            if not all and fstype not in phydevs:
                continue
            if device == "none":
                device = ""
            ntuple = disk_ntuple(device, mountpoint, fstype)
            retlist.append(ntuple)
    return retlist

def get_mount_point(pathname):
    pathname = os.path.normcase(os.path.realpath(pathname))
    parent_device = path_device = os.stat(pathname).st_dev
    while parent_device == path_device:
        mount_point = pathname
        pathname = os.path.dirname(pathname)
        if pathname == mount_point:
            break
        parent_device = os.stat(pathname).st_dev
    return mount_point

def converted_unit(n):
    symbols = ("K", "M", "G", "T", "P", "E", "Z", "Y")
    prefix = {}
    for i, s in enumerate(symbols):
        prefix[s] = 1 << (i + 1) * 10
    for s in reversed(symbols):
        if n >= prefix[s]:
            value = float(n) / prefix[s]
            return "%.1f%s" % (value, s)
    return "%sB" % n

def get_size(bytes, suffix="B"):
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < factor:
            return f"{bytes:.2f}{unit}{suffix}"
        bytes /= factor

def all_sys_info():
    print("="*40, "System Information", "="*40)
    uname = platform.uname()
    print(f"System: {uname.system}")
    print(f"Node Name: {uname.node}")
    print(f"Release: {uname.release}")
    print(f"Version: {uname.version}")
    print(f"Machine: {uname.machine}")
    print(f"Processor: {uname.processor}")

    # Boot Time
    print("="*40, "Boot Time", "="*40)
    boot_time_timestamp = psutil.boot_time()
    bt = datetime.fromtimestamp(boot_time_timestamp)
    print(f"Boot Time: {bt.year}/{bt.month}/{bt.day} {bt.hour}:{bt.minute}:{bt.second}")

    # let's print CPU information
    print("="*40, "CPU Info", "="*40)
    # number of cores
    print("Physical cores:", psutil.cpu_count(logical=False))
    print("Total cores:", psutil.cpu_count(logical=True))
    # CPU frequencies
    cpufreq = psutil.cpu_freq()
    print(f"Max Frequency: {cpufreq.max:.2f}Mhz")
    print(f"Min Frequency: {cpufreq.min:.2f}Mhz")
    print(f"Current Frequency: {cpufreq.current:.2f}Mhz")
    # CPU usage
    print("CPU Usage Per Core:")
    
    # TODO: Does a Core start from 0? or 1? enumerate starts from 0.. check if we need i+1 to align !
    for i, percentage in enumerate(psutil.cpu_percent(percpu=True, interval=1)):
        print(f"Core {i}: {percentage}%")
    print(f"Total CPU Usage: {psutil.cpu_percent()}%")

    # Memory Information
    print("="*40, "Memory Information", "="*40)
    # get the memory details
    svmem = psutil.virtual_memory()
    print(f"Total: {get_size(svmem.total)}")
    print(f"Available: {get_size(svmem.available)}")
    print(f"Used: {get_size(svmem.used)}")
    print(f"Percentage: {svmem.percent}%")
    print("="*20, "SWAP", "="*20)
    # get the swap memory details (if exists)
    swap = psutil.swap_memory()
    print(f"Total: {get_size(swap.total)}")
    print(f"Free: {get_size(swap.free)}")
    print(f"Used: {get_size(swap.used)}")
    print(f"Percentage: {swap.percent}%")

    # Disk Information
    print("="*40, "Disk Information", "="*40)
    print("Partitions and Usage:")
    # get all disk partitions
    partitions = psutil.disk_partitions()
    for partition in partitions:
        print(f"=== Device: {partition.device} ===")
        print(f"  Mountpoint: {partition.mountpoint}")
        print(f"  File system type: {partition.fstype}")
        try:
            partition_usage = psutil.disk_usage(partition.mountpoint)
        except PermissionError:
            # this can be catched due to the disk that
            # isn't ready
            continue
        print(f"  Total Size: {get_size(partition_usage.total)}")
        print(f"  Used: {get_size(partition_usage.used)}")
        print(f"  Free: {get_size(partition_usage.free)}")
        print(f"  Percentage: {partition_usage.percent}%")
    # get IO statistics since boot
    disk_io = psutil.disk_io_counters()
    print(f"Total read: {get_size(disk_io.read_bytes)}")
    print(f"Total write: {get_size(disk_io.write_bytes)}")

    # Network information
    print("="*40, "Network Information", "="*40)
    # get all network interfaces (virtual and physical)
    if_addrs = psutil.net_if_addrs()
    for interface_name, interface_addresses in if_addrs.items():
        for address in interface_addresses:
            print(f"=== Interface: {interface_name} ===")
            if str(address.family) == 'AddressFamily.AF_INET':
                print(f"  IP Address: {address.address}")
                print(f"  Netmask: {address.netmask}")
                print(f"  Broadcast IP: {address.broadcast}")
            elif str(address.family) == 'AddressFamily.AF_PACKET':
                print(f"  MAC Address: {address.address}")
                print(f"  Netmask: {address.netmask}")
                print(f"  Broadcast MAC: {address.broadcast}")
    # get IO statistics since boot
    net_io = psutil.net_io_counters()
    print(f"Total Bytes Sent: {get_size(net_io.bytes_sent)}")
    print(f"Total Bytes Received: {get_size(net_io.bytes_recv)}")
    input("Press ENTER to return to the main menu.")
    return

def docker_check():
    status = subprocess.call(["docker"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if status == 0:
        print("* Docker is available and working properly.\n* Loading management menu now...")
        print_stars()
        return 0
    else:
        print("* Docker is not installed and/or is not working properly.")
        print("* Install docker on this server and give the user access to continue.")
        print_stars()
        raise SystemExit(0)

def container_running(container_name) -> None:
    # create client object to connect
    client = docker.from_env()
    # Get a list of all containers
    containers = client.containers.list()
    # Search for the container by name
    container = next(filter(lambda c: c.name == container_name, containers), None)
    if container is not None and container.status == "running":
        return True
    else:
        return False

def coming_soon():    
    print("* This option isn't available on your system, yet!")
    print_stars()
    input("* Press enter to return to the main menu.")

def run_ubuntu_updater() -> None:
    os_upgrades()
    print()

def os_upgrades() -> None:
    upgrades = (
        "sudo apt update",
        "sudo apt upgrade -y",
        "sudo apt dist-upgrade -y",
        "sudo apt autoremove -y",
    )
    print_stars()
    for x in upgrades:
        process_command(x)
    print_stars()

def menu_ubuntu_updates() -> str:
    question = ask_yes_no(
        f"* Are you sure you would like to proceed with Linux apt Upgrades? (Y/N) "
    )
    if question:
        run_ubuntu_updater()
        input("* OS Updates completed, press ENTER to return to the main menu. ")

def menu_error() -> None:
    subprocess.run("clear")
    print_stars()
    print(
        "* "
        + Fore.RED
        + "WARNING"
        + Style.RESET_ALL
        + ": Only numbers are possible, please try your selection on the main menu once again.\n* Press enter to return to the menu."
    )
    print_stars()
    return

def menu_reboot_server() -> str:
    question = ask_yes_no(
        Fore.RED
        + "WARNING: YOU WILL MISS BLOCKS WHILE YOU REBOOT YOUR ENTIRE SERVER.\n\n"
        + "Reconnect after a few moments & Run the Validator Toolbox Menu again with: python3 ~/validator-toolboxstart.py\n"
        + Fore.WHITE
        + "Are you sure you would like to proceed with rebooting your server?\n\nType 'Yes' or 'No' to continue"
    )
    if question:
        os.system("sudo reboot")
    else:
        print("Invalid option.")

def finish_node():
    print("* Thanks for using Easy Node - EZ Mode!\n* We serve up free tools.\n* Please consider supporting us one time or monthly at https://github.com/sponsors/easy-node-pro today!\n*\n* Goodbye!")
    print_stars()
    raise SystemExit(0)