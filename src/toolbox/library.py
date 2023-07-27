import psutil, platform, dotenv, os, subprocess, requests, pyhmy, shutil, hashlib, re, json, subprocess, getpass
from os import environ
from dotenv import load_dotenv
from simple_term_menu import TerminalMenu
from colorama import Fore, Style, Back
from pathlib import Path
from pyhmy import account, staking, validator, numbers
from json import load, dump
from toolbox.config import EnvironmentVariables
from collections import namedtuple
from datetime import datetime
from subprocess import PIPE, run

load_dotenv(EnvironmentVariables.dotenv_file)


class print_stuff:
    def __init__(self, reset: int = 0):
        self.reset = reset
        self.print_stars = "*" * 93
        self.reset_stars = self.print_stars + Style.RESET_ALL + Fore.GREEN

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
    print(Fore.GREEN)
    print_stars()
    p = f"""
                    ____ ____ ____ ____ _________ ____ ____ ____ ____           
                    ||E |||a |||s |||y |||       |||N |||o |||d |||e ||          
                    ||__|||__|||__|||__|||_______|||__|||__|||__|||__||          
                    |/__\|/__\|/__\|/__\|/_______\|/__\|/__\|/__\|/__\|          
                ____ ____ ____ ____ ____ ____ ____ _________ ____ ____ ____ 
                ||H |||a |||r |||m |||o |||n |||y |||       |||O |||N |||E ||
                ||__|||__|||__|||__|||__|||__|||__|||_______|||__|||__|||__||
                |/__\|/__\|/__\|/__\|/__\|/__\|/__\|/_______\|/__\|/__\|/__\|
                        ____ ____ ____ ____ ____ ____ ____ ____ ____                
                        ||V |||a |||l |||i |||d |||a |||t |||o |||r ||               
                        ||__|||__|||__|||__|||__|||__|||__|||__|||__||               
                        |/__\|/__\|/__\|/__\|/__\|/__\|/__\|/__\|/__\|               
                            ____ ____ ____ ____ ____ ____ ____                          
                            ||T |||o |||o |||l |||b |||o |||x ||                         
                            ||__|||__|||__|||__|||__|||__|||__||                         
                            |/__\|/__\|/__\|/__\|/__\|/__\|/__\|   
    """
    print(p)


def old_toolbox_check():
    if os.path.exists(f"{EnvironmentVariables.user_home_dir}/validatortoolbox"):
        print_stars()
        print(
            Fore.GREEN
            + "*\n* Old folder found, Exiting toolbox.\n*\n* Please renmae your ~/validatortoolbox folder to ~/harmony-toolbox and update your command paths!\n*\n* Run: cd ~/ && mv ~/validatortoolbox ~/harmony-toolbox\n*\n* After you run the move command, relaunch with: python3 ~/harmony-toolbox/src/menu.py\n*"
        )
        print_stars()
        raise SystemExit(0)


# Install Harmony ONE
def install_hmy():
    os.chdir(f"{os.environ.get('HARMONY_DIR')}")
    os.system(f"curl -LO https://harmony.one/hmycli && mv hmycli hmy && chmod +x hmy")
    print_stars()
    print("* hmy application installed.")


# Code to update the harmony.conf after an upgrade and other text files.
def update_text_file(fileName, originalText, newText):
    with open(fileName, "r") as f:
        filedata = f.read()

    newdata = filedata.replace(originalText, newText)

    with open(fileName, "w") as f:
        f.write(newdata)


# Setup a wallet, ask if they need to import one (not required but no toolbox menu without a wallet)
def recover_wallet():
    print_stars()
    print("* Wallet Configuration                                                                      *")
    print_stars()
    question = ask_yes_no(
        f"* If you would like to import a wallet for manual wallet actions, and for using our claim and send functions, answer yes.\n* If you only want to load your validator address for stats answer no.\n* Would you like to add your wallet to this server? (YES/NO) "
    )
    # if yes, find recovery type
    if question:
        recovery_type()
        load_var_file(EnvironmentVariables.dotenv_file)
        print(
            f'\n* Verify the address above matches the address below:\n* Detected Wallet: {Fore.YELLOW}{environ.get("VALIDATOR_WALLET")}{Fore.GREEN}\n* If a different wallet is showing you can remove it and retry it after installation.\n*\n* .{environ.get("HARMONY_DIR")}/hmy keys remove {EnvironmentVariables.active_user}\n*\n* To restore a wallet once again, run the following:\n*\n* .{environ.get("HARMONY_DIR")}/hmy keys recover-from-mnemonic {EnvironmentVariables.active_user} {environ.get("PASS_SWITCH")}\n*'
        )
        print_stars()
        input("* Verify your wallet information above.\n* Press ENTER to continue Installation.")
    else:
        while True:
            wallet = input(
                f"* If you'd like to use the management menu, we need a one1 or 0x address, please input your address now: "
            )
            if wallet.startswith("one1") or wallet.startswith("0x"):
                # Re-enter the wallet to verify
                verify_wallet = input(f"* Please re-enter your wallet address for verification: ")
                if wallet == verify_wallet:
                    set_var(EnvironmentVariables.dotenv_file, "VALIDATOR_WALLET", wallet)
                    break
                else:
                    print("The entered wallets do not match. Please try again.")
            else:
                print("Invalid wallet address. It should start with one1 or 0x. Please try again.")
    return


def pull_harmony_update(harmony_dir, harmony_conf):
    arch = os.uname().machine
    os.chdir(f"{harmony_dir}")
    if environ.get("NETWORK") == "testnet":
        os.system("curl -LO https://harmony.one/binary_testnet && mv binary_testnet harmony && chmod +x harmony")
        os.system("./harmony config dump --network testnet harmony.conf")
    if environ.get("NETWORK") == "mainnet":
        if arch.startswith("arm"):
            os.system("curl -LO https://harmony.one/binary-arm64 && mv binary-arm64 harmony && chmod +x harmony")
        if arch == "x86_64":
            os.system("curl -LO https://harmony.one/binary && mv binary harmony && chmod +x harmony")
        os.system("./harmony config dump harmony.conf")
    update_text_file(harmony_conf, "MaxKeys = 10", "MaxKeys = 13")
    update_text_file(harmony_conf, " DisablePrivateIPScan = false", " DisablePrivateIPScan = true")
    print_stars()
    print("* harmony.conf MaxKeys modified to 13 & DisablePrivateIPScan set to true.")
    if os.path.isfile(f"{os.environ.get('HARMONY_DIR')}/blskey.pass"):
        update_text_file(harmony_conf, 'PassFile = ""', f'PassFile = "blskey.pass"')
        print("* blskey.pass found, updated harmony.conf")
    print_stars()
    print(f"* Harmony {environ.get('NETWORK')} application installed & ~/harmony/harmony.conf created. ")
    return


# Search harmony.conf for the proper port to hit
def find_port(folder):
    with open(f"{folder}/harmony.conf") as f:
        data_file = f.readlines()
    count = 0
    for line in data_file:
        line = line.rstrip()
        if "Port =" in line:
            if count == 3:
                return line[9:]
            count += 1


# build list of installs
def get_folders():
    folders = {}
    if os.path.isfile(f"{EnvironmentVariables.user_home_dir}/harmony/harmony.conf"):
        port = find_port(f"{EnvironmentVariables.user_home_dir}/harmony")
        folders["harmony"] = port
        print(f"* Found ~/harmony folder, on port {port}")
    if os.path.isfile(f"{EnvironmentVariables.user_home_dir}/harmony0/harmony.conf"):
        port = find_port(f"{EnvironmentVariables.user_home_dir}/harmony0")
        folders["harmony0"] = port
        print(f"* Found ~/harmony1 folder, on port {port}")
    if os.path.isfile(f"{EnvironmentVariables.user_home_dir}/harmony1/harmony.conf"):
        port = find_port(f"{EnvironmentVariables.user_home_dir}/harmony1")
        folders["harmony1"] = port
        print(f"* Found ~/harmony1 folder, on port {port}")
    if os.path.isfile(f"{EnvironmentVariables.user_home_dir}/harmony2/harmony.conf"):
        port = find_port(f"{EnvironmentVariables.user_home_dir}/harmony2")
        folders["harmony2"] = port
        print(f"* Found ~/harmony2 folder, on port {port}")
    if os.path.isfile(f"{EnvironmentVariables.user_home_dir}/harmony3/harmony.conf"):
        port = find_port(f"{EnvironmentVariables.user_home_dir}/harmony3")
        folders["harmony3"] = port
        print(f"* Found ~/harmony3 folder, on port {port}")
    print_stars()
    return folders


def validator_stats_output(folders) -> None:
    # Get server stats & wallet balances
    load_1, load_5, load_15 = os.getloadavg()
    sign_percentage = get_sign_pct()
    total_balance = get_wallet_balance(environ.get("VALIDATOR_WALLET"))
    # Print Menu
    print_stars()
    print(
        f"{Fore.GREEN}* harmony-toolbox for {Fore.CYAN}Harmony ONE{Fore.GREEN} Validators by Easy Node   v{EnvironmentVariables.easy_version}{Style.RESET_ALL}{Fore.WHITE}   https://easynode.pro {Fore.GREEN}*"
    )
    print_stars()
    print(
        f'* Your validator wallet address is: {Fore.RED}{str(environ.get("VALIDATOR_WALLET"))}{Fore.GREEN}\n* Your $ONE balance is:             {Fore.CYAN}{str(round(total_balance, 2))}{Fore.GREEN}\n* Your pending $ONE rewards are:    {Fore.CYAN}{str(round(get_rewards_balance(EnvironmentVariables.rpc_endpoints, environ.get("VALIDATOR_WALLET")), 2))}{Fore.GREEN}\n* Server Hostname & IP:             {EnvironmentVariables.server_host_name} - {Fore.YELLOW}{EnvironmentVariables.external_ip}{Fore.GREEN}'
    )
    for folder in folders:
        harmony_service_status(folder)
    print(
        f"* Epoch Signing Percentage:         {Style.BRIGHT}{Fore.GREEN}{Back.BLUE}{sign_percentage} %{Style.RESET_ALL}{Fore.GREEN}\n* Current user home dir free space: {Fore.CYAN}{free_space_check(EnvironmentVariables.user_home_dir): >6}{Fore.GREEN}"
    )
    print(
        f"* CPU Load Averages: {round(load_1, 2)} over 1 min, {round(load_5, 2)} over 5 min, {round(load_15, 2)} over 15 min"
    )
    print_stars()
    remote_shard_0 = [
        f"{EnvironmentVariables.user_home_dir}/{list(folders.items())[0][0]}/hmy",
        "utility",
        "metadata",
        f"--node=https://api.s0.t.hmny.io",
    ]
    result_shard_0 = run(remote_shard_0, stdout=PIPE, stderr=PIPE, universal_newlines=True)
    remote_0_data = json.loads(result_shard_0.stdout)
    print(
        f"* Remote Shard 0 Epoch: {remote_0_data['result']['current-epoch']}, Current Block: {remote_0_data['result']['current-block-number']}"
    )
    print_stars()
    for folder in folders:
        current_full_path = f"{EnvironmentVariables.user_home_dir}/{folder}"
        software_versions = version_checks(current_full_path)
        print(
            f'* Results for the current folder: {current_full_path}\n* Current harmony version: {Fore.YELLOW}{software_versions["harmony_version"]}{Fore.GREEN}, has upgrade available: {software_versions["harmony_upgrade"]}\n* Current hmy version: {Fore.YELLOW}{software_versions["hmy_version"]}{Fore.GREEN}, has upgrade available: {software_versions["hmy_upgrade"]}'
        )
        local_server = [
            f"{EnvironmentVariables.user_home_dir}/{folder}/hmy",
            "utility",
            "metadata",
            f"--node=http://localhost:{folders[folder]}",
        ]
        result_local_server = run(local_server, stdout=PIPE, stderr=PIPE, universal_newlines=True)
        try:
            local_data = json.loads(result_local_server.stdout)
            remote_server = [
                f"{EnvironmentVariables.user_home_dir}/{folder}/hmy",
                "utility",
                "metadata",
                f"--node=https://api.s{local_data['result']['shard-id']}.t.hmny.io",
            ]
            result_remote_server = run(remote_server, stdout=PIPE, stderr=PIPE, universal_newlines=True)
            remote_data = json.loads(result_remote_server.stdout)
            print(
                f"* Remote Shard {local_data['result']['shard-id']} Epoch: {remote_data['result']['current-epoch']}, Current Block: {remote_data['result']['current-block-number']}"
            )
            if local_data["result"]["shard-id"] == 0:
                print(
                    f"*  Local Shard {local_data['result']['shard-id']} Epoch: {local_data['result']['current-epoch']}, Current Block: {(local_data['result']['current-block-number'])}"
                    + f"\n*   Local Shard {local_data['result']['shard-id']} Size: {get_db_size(f'{current_full_path}', local_data['result']['shard-id'])}"
                )
            else:
                print(
                    f"*  Local Shard {local_data['result']['shard-id']} Epoch: {local_data['result']['current-epoch']}, Current Block: {(local_data['result']['current-block-number'])}"
                    + f"\n*   Local Shard 0 Size: {get_db_size(f'{current_full_path}', '0')}\n*   Local Shard {local_data['result']['shard-id']} Size: {get_db_size(f'{current_full_path}', local_data['result']['shard-id'])}"
                )

            print_stars()
        except Exception as e:
            print(f"* Error, Service Offline or Unresponsive: {e}")
            print_stars()


def harmony_service_status(service="harmony") -> None:
    status = subprocess.call(["systemctl", "is-active", "--quiet", service])
    if status == 0:
        if service == "harmony":
            print(
                f"* {service} Service is:               "
                + Fore.BLACK
                + Back.GREEN
                + "   Online  "
                + Style.RESET_ALL
                + Fore.GREEN
            )
        else:
            print(
                f"* {service} Service is:              "
                + Fore.BLACK
                + Back.GREEN
                + "   Online  "
                + Style.RESET_ALL
                + Fore.GREEN
            )
    else:
        print(
            f"* {service} Service is:               "
            + Fore.WHITE
            + Back.RED
            + "  *** Offline *** "
            + Style.RESET_ALL
            + Fore.GREEN
        )


def set_wallet_env():
    load_var_file(EnvironmentVariables.dotenv_file)
    if os.path.exists(EnvironmentVariables.hmy_wallet_store):
        output = subprocess.getoutput(
            f"{environ.get('HARMONY_DIR')}/hmy keys list | grep {EnvironmentVariables.active_user}"
        )
        output_stripped = output.lstrip(EnvironmentVariables.active_user)
        output_stripped = output_stripped.strip()
        set_var(EnvironmentVariables.dotenv_file, "VALIDATOR_WALLET", output_stripped)
        return output_stripped
    else:
        validator_wallet = environ.get("VALIDATOR_WALLET")
        return validator_wallet


def get_db_size(harmony_dir, our_shard) -> str:
    harmony_db_size = subprocess.getoutput(f"du -h {harmony_dir}/harmony_db_{our_shard}")
    harmony_db_size = harmony_db_size.rstrip("\t")
    countTrim = len(os.environ.get("HARMONY_DIR")) + 13
    return harmony_db_size[:-countTrim]


def recovery_type():
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
    passphrase_set()
    if results == 0:
        # Mnemonic Recovery Here
        os.system(
            f"{environ.get('HARMONY_DIR')}/hmy keys recover-from-mnemonic {EnvironmentVariables.active_user} --passphrase-file passphrase.txt"
        )
        print_stars()
        set_wallet_env()
    elif results == 1:
        # Private Key Recovery Here
        print("* Private key recovery requires your private information in the command itself.")
        private = input("* Please enter your private key to restore your wallet: ")
        os.system(
            f"{environ.get('HARMONY_DIR')}/hmy keys import-private-key {private} {EnvironmentVariables.active_user} --passphrase-file passphrase.txt"
        )
        print_stars()
        set_wallet_env()


def passphrase_status():
    load_var_file(EnvironmentVariables.dotenv_file)
    if os.path.exists(EnvironmentVariables.hmy_wallet_store):
        passphrase_set()
        set_var(
            EnvironmentVariables.dotenv_file,
            "PASS_SWITCH",
            f"--passphrase-file {os.environ.get('HARMONY_DIR')}/passphrase.txt",
        )
    else:
        set_var(EnvironmentVariables.dotenv_file, "PASS_SWITCH", "--passphrase")
    load_var_file(EnvironmentVariables.dotenv_file)


def passphrase_set():
    if os.path.exists(f"{environ.get('HARMONY_DIR')}/passphrase.txt"):
        return
    import getpass

    print(f"* Setup {os.environ.get('HARMONY_DIR')}/passphrase.txt file for use with autobidder & harmony-toolbox.")
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
    save_text(f"{environ.get('HARMONY_DIR')}/passphrase.txt", password_1)
    load_var_file(EnvironmentVariables.dotenv_file)
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
        return False
    else:
        subprocess.run(["touch", var_file])
        return True


def get_shard_menu() -> None:
    if not environ.get("SHARD"):
        print_stars()
        print("* Gathering more information about your server.                                             *")
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
        set_var(EnvironmentVariables.dotenv_file, "SHARD", our_shard)
        return our_shard


def set_main_or_test() -> None:
    if not environ.get("NETWORK"):
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
            set_var(EnvironmentVariables.dotenv_file, "NETWORK", "mainnet")
            set_var(EnvironmentVariables.dotenv_file, "NETWORK_SWITCH", "t")
            set_var(EnvironmentVariables.dotenv_file, "RPC_NET", "https://rpc.s0.t.hmny.io")
            set_var(EnvironmentVariables.dotenv_file, "RPC_NET_SHARD", f"https://rpc.s{environ.get('SHARD')}.t.hmny.io")
        if results == 1:
            set_var(EnvironmentVariables.dotenv_file, "NETWORK", "testnet")
            set_var(EnvironmentVariables.dotenv_file, "NETWORK_SWITCH", "b")
            set_var(EnvironmentVariables.dotenv_file, "RPC_NET", "https://rpc.s0.b.hmny.io")
            set_var(EnvironmentVariables.dotenv_file, "RPC_NET_SHARD", f"https://rpc.s{environ.get('SHARD')}.b.hmny.io")
    return


def get_wallet_address():
    print("* Signing Node, No Wallet!                                                                  *")
    print("* You are attempting to launch the menu but no wallet has been loaded, as you chose         *")
    print("* If you would like to use the menu on the server, complete the following:                  *")
    print_stars()
    print("* Edit ~/.easynode.env and add your wallet address on a new line like this example:         *")
    print("* VALIDATOR_WALLET='one1thisisjustanexamplewalletreplaceme'                                 *")
    print_stars()
    raise SystemExit(0)


def get_validator_info():
    if environ.get("NETWORK") == "mainnet":
        endpoint = len(EnvironmentVariables.rpc_endpoints)
    if environ.get("NETWORK") == "testnet":
        endpoint = len(EnvironmentVariables.rpc_endpoints_test)
    current = 0
    max_tries = EnvironmentVariables.rpc_endpoints_max_connection_retries
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
        response = requests.get(EnvironmentVariables.onePriceURL, timeout=5)
    except (ValueError, KeyError, TypeError):
        response = "0.0000"
        return response
    data_dict = response.json()
    type(data_dict)
    data_dict.keys()
    return data_dict["lastPrice"][:-4]


def get_wallet_balance(wallet_addr):
    config = EnvironmentVariables()
    rpc_endpoint = config.working_rpc_endpoint
    wallet_balance = get_wallet_balance_by_endpoint(rpc_endpoint, wallet_addr)
    if wallet_balance is not None:
        return wallet_balance


def get_wallet_balance_by_endpoint(endpoint, wallet_addr):
    current = 0
    max_tries = EnvironmentVariables.rpc_endpoints_max_connection_retries
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
    max_tries = EnvironmentVariables.rpc_endpoints_max_connection_retries
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
    config = EnvironmentVariables()
    hmy_external_rpc = f"{environ.get('HARMONY_DIR')}/hmy --node='{config.working_rpc_endpoint}'"
    output = subprocess.getoutput(
        f"{hmy_external_rpc} blockchain validator information {environ.get('VALIDATOR_WALLET')} | grep signing-percentage"
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
    output_harmony_version = re.search(r"version (v\d+-v\d+\.\d+\.\d+-\d+-g[0-9a-f]+ )\(", harmony_version)
    hmy_version = subprocess.getoutput(f"{folder}/hmy version")
    return output_harmony_version.group(1)[:-2], hmy_version[62:-15]


def set_mod_x(file):
    subprocess.run(["chmod", "+x", file])


def check_online_version():
    try:
        subprocess.check_output(
            ["wget", "https://harmony.one/binary", "-O", EnvironmentVariables.harmony_tmp_path],
            stderr=subprocess.STDOUT,
        )
        set_mod_x(EnvironmentVariables.harmony_tmp_path)
        harmony_ver = subprocess.getoutput(f"{EnvironmentVariables.harmony_tmp_path} -V")
        output_harmony_version = re.search(r"version (v\d+-v\d+\.\d+\.\d+-\d+-g[0-9a-f]+ )\(", harmony_ver)
    except subprocess.CalledProcessError:
        print(f"* Error - Website for harmony upgrade is offline, setting to offline.")
        harmony_ver = "Offline"
    try:
        subprocess.check_output(
            ["wget", "https://harmony.one/hmycli", "-O", EnvironmentVariables.hmy_tmp_path], stderr=subprocess.STDOUT
        )
        set_mod_x(EnvironmentVariables.hmy_tmp_path)
        hmy_ver = subprocess.getoutput(f"{EnvironmentVariables.hmy_tmp_path} version")
        hmy_ver = hmy_ver[62:-15]
    except subprocess.CalledProcessError:
        print(f"* Error - Website for hmy upgrade is offline, setting to offline.")
        hmy_ver = "Offline"
    return output_harmony_version.group(1)[:-2], hmy_ver


def first_env_check(env_file) -> None:
    first_time = load_var_file(env_file)
    return first_time


def version_checks(harmony_folder):
    software_versions = {}
    software_versions["harmony_version"], software_versions["hmy_version"] = get_local_version(f"{harmony_folder}")
    software_versions["online_harmony_version"], software_versions["online_hmy_version"] = check_online_version()
    # Check versions, if matching False (No Upgrade Required), non-match True (Upgrade Required)
    if (
        software_versions["harmony_version"] == software_versions["online_harmony_version"]
        or software_versions["online_harmony_version"] == "Offline"
    ):
        software_versions["harmony_upgrade"] = "False"
    else:
        software_versions["harmony_upgrade"] = "True"
    if (
        software_versions["hmy_version"] == software_versions["online_hmy_version"]
        or software_versions["online_hmy_version"] == "Offline"
    ):
        software_versions["hmy_upgrade"] = "False"
    else:
        software_versions["hmy_upgrade"] = "True"
    return software_versions


def first_setup():
    # Find Shard #
    get_shard_menu()
    # Get Mainnet or Testnet
    set_main_or_test()
    # Look for a harmony install or install.
    check_for_install()
    print_stars()
    return


# looks for ~/harmony or installs it if it's not there. Asks to overwrite if it finds it, run at your own risk.
def check_for_install() -> str:
    if os.path.exists(f"{EnvironmentVariables.user_home_dir}/harmony"):
        question = ask_yes_no(
            "* You already have a harmony folder on this system, would you like to re-run installation and rclone on this server? (YES/NO)"
        )
        if question:
            install_harmony()
            print_stars()
            # Wallet Setup
            recover_wallet()
            print_stars()
            # Check passphrase if wallet is added
            passphrase_status()
            print_stars()
            print("* All harmony files now installed. Database download starting now...")
            print_stars()
            clone_shards()
            finish_node_install()
        else:
            if os.path.isdir(f"{EnvironmentVariables.user_home_dir}/harmony"):
                print(
                    "* Exiting Harmony Validator Toolbox\n* You already have a folder at ~/harmony.\n* Contact Easy Node for help setting up if this is an existing Harmony server."
                )
            if os.path.isfile(f"{EnvironmentVariables.user_home_dir}/harmony"):
                print(
                    "* Exiting Harmony Validator Toolbox\n* You already have a file at ~/harmony.\n* Contact Easy Node for help setting up if this is an existing Harmony server with a custom configuration."
                )
            raise SystemExit(0)
    else:
        print(f"* You selected Shard: {environ.get('SHARD')}. ")
        install_harmony()
        print_stars()
        # Wallet Setup
        recover_wallet()
        print_stars()
        # Check passphrase if wallet is added
        passphrase_status()
        print_stars()
        print("* All harmony files now installed. Database download starting now...")
        print_stars()
        clone_shards()
        finish_node_install()
    return


# Installer Module
def install_harmony() -> None:
    # Checks Passed at this point, only 1 folder in /mnt and it's probably our volume (can scope this down further later)
    print_stars()
    print("* Install Location")
    print_stars()
    question = ask_yes_no(
        f"* Answer yes if you'd like to setup harmony in the default location\n* {EnvironmentVariables.user_home_dir}/harmony\n* Or answer no to choose a custom folder (for a volume or 2nd disk setup): (YES/NO) "
    )
    if question:
        set_var(EnvironmentVariables.dotenv_file, "HARMONY_DIR", f"{EnvironmentVariables.user_home_dir}/harmony")
    else:
        answer = input(
            "\n* Please enter the full path to a location you'd like to install harmony into.\n* The folder should not exist yet for best results (example: /mnt/volume1/harmony): "
        )
        if not os.path.exists(answer):
            question = ask_yes_no(
                f"* That path {answer} doesn't exist yet.\n* Do you want to create the folder {answer} and install the harmony files here? (YES/NO) "
            )
            if question:
                set_var(EnvironmentVariables.dotenv_file, "HARMONY_DIR", f"{answer}")
            else:
                install_harmony()
        else:
            question = ask_yes_no(
                f"* Are you sure you want to isntall into the already existing folder {answer}? (YES/NO) "
            )
            if question:
                set_var(EnvironmentVariables.dotenv_file, "HARMONY_DIR", f"{answer}")
            else:
                install_harmony()
        set_var(EnvironmentVariables.dotenv_file, "HARMONY_DIR", f"{answer}")
        os.system(f"sudo mkdir -p {os.environ.get('HARMONY_DIR')}")
        os.system(f"sudo chown {EnvironmentVariables.active_user} {os.environ.get('HARMONY_DIR')}")
    print_stars()
    print("* Creating all Harmony Files & Folders")
    os.system(f"mkdir -p {os.environ.get('HARMONY_DIR')}/.hmy/blskeys")

    # Setup folders now that symlink exists or we know we're using ~/harmony
    if not os.path.isdir(f"{EnvironmentVariables.user_home_dir}/.hmy_cli/account-keys/"):
        os.system(f"mkdir -p {EnvironmentVariables.user_home_dir}/.hmy_cli/account-keys/")
    if not os.path.isdir(f"{os.environ.get('HARMONY_DIR')}/.hmy/blskeys"):
        print("* Creating all Harmony Files & Folders")
        os.system(f"mkdir -p {os.environ.get('HARMONY_DIR')}/.hmy/blskeys")
    # Change to ~/harmony folder
    os.chdir(f"{os.environ.get('HARMONY_DIR')}")
    print_stars()
    # Install hmy
    install_hmy()
    print_stars()
    # Install harmony
    pull_harmony_update(os.environ.get("HARMONY_DIR"), f"{os.environ.get('HARMONY_DIR')}/harmony.conf")
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
            subprocess.run("sudo apt install rclone -y")

    os.system(
        f"mkdir -p {EnvironmentVariables.user_home_dir}/.config/rclone && cp {EnvironmentVariables.toolbox_location}/src/bin/rclone.conf {EnvironmentVariables.user_home_dir}/.config/rclone/"
    )
    print_stars()
    # Setup the harmony service file
    print("* Customizing, Moving & Enabling your harmony.service systemd file")
    service_file_path = f"{EnvironmentVariables.toolbox_location}/src/bin/harmony.service"
    
    # Read the service file
    with open(service_file_path, 'r') as file:
        filedata = file.read()

    # Replace the paths with the value of HARMONY_DIR
    harmony_dir = os.environ.get("HARMONY_DIR")
    if harmony_dir:
        filedata = filedata.replace('WorkingDirectory=/home/serviceharmony/harmony', f'WorkingDirectory={harmony_dir}')
        filedata = filedata.replace('ExecStart=/home/serviceharmony/harmony/harmony -c harmony.conf', f'ExecStart={harmony_dir}/harmony -c harmony.conf')

    # Write the file out again
    with open('harmony.service', 'w') as file:
        file.write(filedata)

    # Move the modified service file into place, change the permissions and enable the service
    subprocess.run(['sudo', 'mv', 'harmony.service', '/etc/systemd/system/harmony.service'], check=True)
    subprocess.run(['sudo', 'chmod', 'a-x', '/etc/systemd/system/harmony.service'], check=True)
    subprocess.run(['sudo', 'systemctl', 'enable', 'harmony.service'], check=True)


# Database Downloader
def clone_shards():
    # Move to ~/harmony
    os.chdir(f"{os.environ.get('HARMONY_DIR')}")

    if environ.get("SHARD") != "0":
        # If we're not on shard 0, download the numbered shard DB here.
        print(f"* Now cloning shard {environ.get('SHARD')}")
        print_stars()
        os.system(
            f"rclone -P sync release:pub.harmony.one/{environ.get('NETWORK')}.min/harmony_db_{environ.get('SHARD')} {os.environ.get('HARMONY_DIR')}/harmony_db_{environ.get('SHARD')} --multi-thread-streams 4 --transfers=32"
        )
        print_stars()
        print(f"* Shard {environ.get('SHARD')} completed.\n* Shard 0 will be created when you start your service.")
        print_stars()
    else:
        # If we're on shard 0, grab the snap DB here.
        print("* Now cloning Shard 0, kick back and relax for awhile...")
        print_stars()
        os.system(
            f"rclone -P -L --checksum sync release:pub.harmony.one/{environ.get('NETWORK')}.snap/harmony_db_0 {os.environ.get('HARMONY_DIR')}/harmony_db_0 --multi-thread-streams 4 --transfers=32"
        )


# is this used?
def set_mounted_point():
    # First let's make sure your volume is mounted
    totalDir = len(os.listdir("/mnt"))
    if totalDir > 0:
        volumeMountPath = os.listdir("/mnt")
        myVolumePath = "/mnt/" + str(volumeMountPath[0])
        myLongHmyPath = myVolumePath + "/harmony"
    else:
        myVolumePath = os.environ.get("HARMONY_DIR")
    if totalDir == 1:
        dotenv.set_key(EnvironmentVariables.dotenv_file, "HARMONY_DIR", myLongHmyPath)
    else:
        dotenv.set_key(EnvironmentVariables.dotenv_file, "HARMONY_DIR", f"{os.environ.get('HARMONY_DIR')}")


def finish_node_install():
    load_var_file(EnvironmentVariables.dotenv_file)
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
            + f"\n* python3 ~/harmony-toolboxload_wallet.py"
            + "\n*"
            + "\n* To create BLS keys run:"
            + f'\n* ./hmy keys generate-bls-keys --count 1 --shard {environ.get("SHARD")} --passphrase'
            + "\n*"
        )
    else:
        print(
            "* Post installation quick tips:"
            + "\n* To recover your wallet again, run:"
            + f"\n* python3 ~/harmony-toolboxload_wallet.py"
            + "\n*"
            + "\n* To create BLS keys run:"
            + f'\n* ./hmy keys generate-bls-keys --count 1 --shard {environ.get("SHARD")} {environ.get("PASS_SWITCH")}'
            + "\n*"
        )
    print_stars()
    print("* Thanks for using Easy Node - Validator Node Server Software Installer!")
    print_stars()
    raise SystemExit(0)


def free_space_check(mount) -> str:
    ourDiskMount = get_HARMONY_DIR(mount)
    _, _, free = shutil.disk_usage(ourDiskMount)
    freeConverted = str(converted_unit(free))
    return freeConverted


def server_drive_check(dot_env, directory) -> None:
    if environ.get("HARMONY_DIR") is not None:
        ourDiskMount = environ.get("HARMONY_DIR")
    else:
        dotenv.set_key(dot_env, "HARMONY_DIR", directory)
        load_var_file(dot_env)
        ourDiskMount = environ.get("HARMONY_DIR")
    print_stars()
    print("Here are all of your mount points: ")
    for part in disk_partitions():
        print(part)
    print_stars()
    total, used, free = shutil.disk_usage(ourDiskMount)
    total = str(converted_unit(total))
    used = str(converted_unit(used))
    print(
        "Disk: "
        + str(ourDiskMount)
        + "\n"
        + free_space_check(directory)
        + " Free\n"
        + used
        + " Used\n"
        + total
        + " Total"
    )
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


def get_HARMONY_DIR(pathname):
    pathname = os.path.normcase(os.path.realpath(pathname))
    parent_device = path_device = os.stat(pathname).st_dev
    while parent_device == path_device:
        HARMONY_DIR = pathname
        pathname = os.path.dirname(pathname)
        if pathname == HARMONY_DIR:
            break
        parent_device = os.stat(pathname).st_dev
    return HARMONY_DIR


def refreshing_stats_message() -> str:
    print(Fore.GREEN)
    print_stars()
    print(f"* Getting the latest local & blockchain information now, one moment while we load...")
    print_stars()
    return


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
    print("=" * 40, "System Information", "=" * 40)
    uname = platform.uname()
    print(f"System: {uname.system}")
    print(f"Node Name: {uname.node}")
    print(f"Release: {uname.release}")
    print(f"Version: {uname.version}")
    print(f"Machine: {uname.machine}")
    print(f"Processor: {uname.processor}")

    # Boot Time
    print("=" * 40, "Boot Time", "=" * 40)
    boot_time_timestamp = psutil.boot_time()
    bt = datetime.fromtimestamp(boot_time_timestamp)
    print(f"Boot Time: {bt.year}/{bt.month}/{bt.day} {bt.hour}:{bt.minute}:{bt.second}")

    # let's print CPU information
    print("=" * 40, "CPU Info", "=" * 40)
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
    print("=" * 40, "Memory Information", "=" * 40)
    # get the memory details
    svmem = psutil.virtual_memory()
    print(f"Total: {get_size(svmem.total)}")
    print(f"Available: {get_size(svmem.available)}")
    print(f"Used: {get_size(svmem.used)}")
    print(f"Percentage: {svmem.percent}%")
    print("=" * 20, "SWAP", "=" * 20)
    # get the swap memory details (if exists)
    swap = psutil.swap_memory()
    print(f"Total: {get_size(swap.total)}")
    print(f"Free: {get_size(swap.free)}")
    print(f"Used: {get_size(swap.used)}")
    print(f"Percentage: {swap.percent}%")

    # Disk Information
    print("=" * 40, "Disk Information", "=" * 40)
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
    print("=" * 40, "Network Information", "=" * 40)
    # get all network interfaces (virtual and physical)
    if_addrs = psutil.net_if_addrs()
    for interface_name, interface_addresses in if_addrs.items():
        for address in interface_addresses:
            print(f"=== Interface: {interface_name} ===")
            if str(address.family) == "AddressFamily.AF_INET":
                print(f"  IP Address: {address.address}")
                print(f"  Netmask: {address.netmask}")
                print(f"  Broadcast IP: {address.broadcast}")
            elif str(address.family) == "AddressFamily.AF_PACKET":
                print(f"  MAC Address: {address.address}")
                print(f"  Netmask: {address.netmask}")
                print(f"  Broadcast MAC: {address.broadcast}")
    # get IO statistics since boot
    net_io = psutil.net_io_counters()
    print(f"Total Bytes Sent: {get_size(net_io.bytes_sent)}")
    print(f"Total Bytes Received: {get_size(net_io.bytes_recv)}")
    input("Press ENTER to return to the main menu.")
    return


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
    question = ask_yes_no(f"* Are you sure you would like to proceed with Linux apt Upgrades? (Y/N) ")
    if question:
        run_ubuntu_updater()
        input("* OS Updates completed, press ENTER to return to the main menu. ")


def menu_reboot_server() -> str:
    question = ask_yes_no(
        Fore.RED
        + "WARNING: YOU WILL MISS BLOCKS WHILE YOU REBOOT YOUR ENTIRE SERVER.\n\n"
        + "Reconnect after a few moments & Run the Validator Toolbox Menu again with: python3 ~/harmony-toolbox/start.py\n"
        + Fore.WHITE
        + "Are you sure you would like to proceed with rebooting your server?\n\nType 'Yes' or 'No' to continue"
    )
    if question:
        os.system("sudo reboot")
    else:
        print("Invalid option.")


def finish_node():
    print(
        "* Thanks for using Easy Node Toolbox - Making everything Easy Mode!"
        + "\n*\n* We serve up free tools and guides for validators every day."
        + "\n*\n* Check our guides out at https://docs.easynode.pro\n*\n"
        + "* Please consider joining our discord & supporting us one time or monthly\n* for our"
        + " tools and guides at https://bit.ly/easynodediscord today!\n*\n* Goodbye!"
    )
    print_stars()
    raise SystemExit(0)


def compare_two_files(input1, input2) -> None:
    # open the files
    file1 = open(input1, "rb")
    file2 = open(input2, "rb")

    # generate their hashes
    hash1 = hashlib.md5(file1.read()).hexdigest()
    hash2 = hashlib.md5(file2.read()).hexdigest()

    # compare the hashes
    if hash1 == hash2:
        return True
    else:
        return False
