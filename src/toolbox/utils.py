import psutil, platform, dotenv, os, subprocess, requests, pyhmy, shutil, hashlib, re, json, subprocess, getpass, time, sys
from os import environ
from dotenv import load_dotenv
from simple_term_menu import TerminalMenu
from colorama import Fore, Style, Back
from pyhmy import account, staking, numbers
from json import load, dump
from collections import namedtuple
from datetime import datetime
from subprocess import PIPE, run
from concurrent.futures import ThreadPoolExecutor
from typing import Tuple
from toolbox.config import config


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
def set_var(env_file: str, key_name: str, update_name: str):
    if environ.get(key_name):
        dotenv.unset_key(env_file, key_name)
    dotenv.set_key(env_file, key_name, update_name)
    load_var_file(env_file)
    return


# loader intro splash screen
def loader_intro():
    print(Fore.GREEN + string_stars())
    p = """
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


def initialization_process():
    update_rclone_conf()
    old_toolbox_check()


def update_rclone_conf():
    if os.path.exists(f"{config.toolbox_location}/src/bin/rclone.conf"):
        comparison = compare_two_files(
            f"{config.toolbox_location}/src/bin/rclone.conf",
            f"{config.user_home_dir}/.config/rclone/rclone.conf",
        )
        if comparison == False:
            process_command(
                f"cp {config.toolbox_location}/src/bin/rclone.conf {config.user_home_dir}/.config/rclone/"
            )


def old_toolbox_check():
    if os.path.exists(f"{config.user_home_dir}/validatortoolbox"):
        print(
            Fore.GREEN
            + f"{string_stars()}\n* Old folder found, renaming and restarting...\n*\n* Please wait..."
        )
        try:
            subprocess.run(
                [
                    "mv",
                    f"{config.user_home_dir}/validatortoolbox",
                    f"{config.user_home_dir}/harmony-toolbox",
                ],
                check=True,
            )
            print(Fore.GREEN + f"* Renamed successfully. Restarting...\n*")
            subprocess.run(
                ["python3", f"{config.user_home_dir}/harmony-toolbox/src/menu.py"]
            )
            sys.exit(0)
        except subprocess.CalledProcessError as e:
            print(Fore.RED + f"* Error renaming folder: {e}")
            raise SystemExit(1)


# Install Harmony ONE
def update_hmy_binary():
    load_dotenv(config.dotenv_file)
    hmy_dir = environ.get("HARMONY_DIR")
    download_url = "https://harmony.one/hmycli"
    destination_path = f"{hmy_dir}/hmy"

    if os.path.isfile(config.hmy_tmp_path):
        process_command(f"cp {config.hmy_tmp_path} {destination_path}")
    else:
        try:
            # Download the hmycli
            response = requests.get(download_url, stream=True)
            response.raise_for_status()

            # Save the downloaded content to the destination path
            with open(destination_path, "wb") as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)

            # Set execute permissions
            os.chmod(destination_path, 0o755)
        except requests.RequestException as e:
            print(f"* Error while downloading hmy using requests: {e}")

        except OSError as e:
            print(f"* Error while saving or setting permissions for hmy: {e}")

    # Get version string
    software_versions = version_checks(hmy_dir)

    if software_versions:
        print(f"* hmy application installed.")
        return software_versions
    else:
        print(f"* Version Check Failed.")
        return None


# Code to update the harmony.conf after an upgrade and other text files.
def update_text_file(fileName, originalText, newText):
    with open(fileName, "r") as f:
        filedata = f.read()

    newdata = filedata.replace(originalText, newText)

    with open(fileName, "w") as f:
        f.write(newdata)


# Setup a wallet, ask if they need to import one (not required but no toolbox menu without a wallet)
def recover_wallet():
    print(
        f"{string_stars()}\n* Wallet Configuration                                                                      *\n{string_stars()}\n"
    )
    question = ask_yes_no(
        "* If you would like to import a wallet for manual wallet actions, and for using our claim and send functions, answer yes.\n* If you only want to load your validator address for stats answer no.\n* Would you like to add your wallet to this server? (YES/NO) "
    )
    # if yes, find recovery type
    if question:
        recovery_type()
        load_var_file(config.dotenv_file)
        print(
            f'\n* Verify the address above matches the address below:\n* Detected Wallet: {Fore.YELLOW}{environ.get("VALIDATOR_WALLET")}{Fore.GREEN}\n* If a different wallet is showing you can remove it and retry it after installation.\n*\n* .{environ.get("HARMONY_DIR")}/hmy keys remove {config.active_user}\n*\n* To restore a wallet once again, run the following:\n*\n* .{environ.get("HARMONY_DIR")}/hmy keys recover-from-mnemonic {config.active_user} {environ.get("PASS_SWITCH")}\n{string_stars()}'
        )
        input(
            "* Verify your wallet information above.\n* Press ENTER to continue Installation."
        )
    else:
        while True:
            wallet = input(
                "* If you'd like to use the management menu, we need a one1 or 0x address, please input your address now: "
            )
            if wallet.startswith("one1") or wallet.startswith("0x"):
                # Re-enter the wallet to verify
                verify_wallet = input(
                    "* Please re-enter your wallet address for verification: "
                )
                if wallet == verify_wallet:
                    set_var(config.dotenv_file, "VALIDATOR_WALLET", wallet)
                    break
                else:
                    print("The entered wallets do not match. Please try again.")
            else:
                print(
                    "Invalid wallet address. It should start with one1 or 0x. Please try again."
                )
    return


def update_harmony_binary():
    harmony_dir = environ.get("HARMONY_DIR")
    os.chdir(f"{harmony_dir}")
    if os.path.isfile(f"{config.harmony_tmp_path}/harmony"):
        process_command(f"cp /tmp/harmony {harmony_dir}")
    else:
        process_command(
            "curl -LO https://harmony.one/binary && mv binary harmony && chmod +x harmony"
        )
    process_command("./harmony config dump harmony.conf")
    update_text_file(
        f"{harmony_dir}/harmony.conf",
        " DisablePrivateIPScan = false",
        " DisablePrivateIPScan = true",
    )
    # Update to 11 keys for HIP-32 expansion to 396 slots
    update_text_file(f"{harmony_dir}/harmony.conf", " MaxKeys = 10", " MaxKeys = 11")
    if os.path.isfile(f"{harmony_dir}/blskey.pass"):
        update_text_file(
            f"{harmony_dir}/harmony.conf", 'PassFile = ""', 'PassFile = "blskey.pass"'
        )
        print(
            f"* Harmony binary installed, 11 keys max, {harmony_dir}/harmony.conf created and modified: blskey.pass file, disabled private ip scan. "
        )
    else:
        print(
            f"* Harmony binary installed, 11 keys max, {harmony_dir}/harmony.conf created and modified: disabled private ip scan. "
        )
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
    for f in config.folder_checks:
        if os.path.isfile(f"{config.user_home_dir}/{f}/harmony.conf"):
            port = find_port(f"{config.user_home_dir}/{f}")
            folders[f"{f}"] = port
    return folders


def process_folder(folder, port, max_retries=3, retry_delay=3):
    if folder == "None":
        return None
    current_full_path = f"{config.user_home_dir}/{folder}"
    software_versions = version_checks(current_full_path)
    retry_count = 0
    while retry_count <= max_retries:
        try:
            local_server = [
                f"{current_full_path}/hmy",
                "utility",
                "metadata",
                f"--node=http://localhost:{port}",
            ]
            result_local_server = run(
                local_server, stdout=PIPE, stderr=PIPE, universal_newlines=True
            )
            local_data = json.loads(result_local_server.stdout)
            shard_id = local_data["result"]["shard-id"]
            remote_server = [
                f"{current_full_path}/hmy",
                "utility",
                "metadata",
                f"--node=https://api.s{shard_id}.t.hmny.io",
            ]
            result_remote_server = run(
                remote_server, stdout=PIPE, stderr=PIPE, universal_newlines=True
            )
            remote_data = json.loads(result_remote_server.stdout)
            db_size_0 = get_db_size(f"{current_full_path}", "0")
            db_size_shard = get_db_size(f"{current_full_path}", str(shard_id))
            free_space_0 = (
                free_space_check(f"{current_full_path}/harmony_db_0")
                if os.path.exists(f"{current_full_path}/harmony_db_0")
                else "N/A"
            )
            free_space_shard = (
                free_space_check(f"{current_full_path}/harmony_db_{shard_id}")
                if os.path.exists(f"{current_full_path}/harmony_db_{shard_id}")
                else "N/A"
            )
            return {
                "folder": folder,
                "path": current_full_path,
                "shard_id": shard_id,
                "local_epoch": local_data["result"]["current-epoch"],
                "remote_epoch": remote_data["result"]["current-epoch"],
                "local_block": local_data["result"]["current-block-number"],
                "remote_block": remote_data["result"]["current-block-number"],
                "db_size_0": db_size_0,
                "db_size_shard": db_size_shard,
                "free_space_0": free_space_0,
                "free_space_shard": free_space_shard,
                "versions": software_versions,
            }
        except Exception as e:
            retry_count += 1
            if retry_count <= max_retries:
                time.sleep(retry_delay)
            else:
                return {"folder": folder, "error": f"Offline or error: {e}"}


def validator_stats_output() -> None:
    # Get all folders for multi-stats run
    folders = get_folders()
    # Get server stats & wallet balances
    load_1, load_5, load_15 = os.getloadavg()
    sign_percentage = get_sign_pct()
    validator_wallet_balance = get_wallet_balance(environ.get("VALIDATOR_WALLET"))
    short_address = f"{environ.get('VALIDATOR_WALLET')[:4]}...{environ.get('VALIDATOR_WALLET')[-4:]}"
    # Print Menu
    print(
        f"{Fore.GREEN}{string_stars()}\n* harmony-toolbox for {Fore.CYAN}Harmony ONE{Fore.GREEN} Validators by Easy Node{' '*8}{Style.RESET_ALL}{Fore.WHITE}   https://EasyNodePro.com {Fore.GREEN}*"
    )
    print(
        f"{string_stars()}\n* Address: {Fore.RED}{short_address}{Fore.GREEN} Balance: {Fore.CYAN}{str(round(validator_wallet_balance, 2))}{Fore.GREEN} Pending Rewards: {Fore.CYAN}{str(round(get_rewards_balance(config.working_rpc_endpoint, environ.get('VALIDATOR_WALLET')), 2))}{Fore.GREEN}\n* Hostname: {Fore.CYAN}{config.server_host_name}{Fore.GREEN} IP: {Fore.YELLOW}{config.external_ip}{Fore.GREEN}"
    )
    service_statuses = [harmony_service_status(folder) for folder in folders]
    print(f"* Service Status: {' '.join(service_statuses)}")
    print(
        f"* Current Signing %: {Style.BRIGHT}{Fore.GREEN}{Back.BLUE}{sign_percentage} %{Style.RESET_ALL}{Fore.GREEN}"
    )
    print(
        f"* CPU Load Averages: {round(load_1, 2)} over 1 min, {round(load_5, 2)} over 5 min, {round(load_15, 2)} over 15 min\n{string_stars()}"
    )
    # get api here
    api_endpoint = config.working_rpc_endpoint
    remote_shard_0 = [
        f"{config.user_home_dir}/{list(folders.items())[0][0]}/hmy",
        "utility",
        "metadata",
        f"--node={api_endpoint}",
    ]
    remote_shard_1 = [
        f"{config.user_home_dir}/{list(folders.items())[0][0]}/hmy",
        "utility",
        "metadata",
        f"--node=https://api.s1.t.hmny.io",
    ]
    result_shard_0 = run(
        remote_shard_0, stdout=PIPE, stderr=PIPE, universal_newlines=True
    )
    result_shard_1 = run(
        remote_shard_1, stdout=PIPE, stderr=PIPE, universal_newlines=True
    )
    remote_0_data = json.loads(result_shard_0.stdout)
    remote_1_data = json.loads(result_shard_1.stdout)
    print(
        f"* Remote Shard 0 Epoch: {remote_0_data['result']['current-epoch']}, Current Block: {remote_0_data['result']['current-block-number']}\n" +
        f"* Remote Shard 1 Epoch: {remote_1_data['result']['current-epoch']}, Current Block: {remote_1_data['result']['current-block-number']}\n{string_stars()}"
    )

    # Concurrently process each folder
    with ThreadPoolExecutor(max_workers=10) as executor:
        folder_results = list(
            executor.map(process_folder, folders.keys(), folders.values())
        )

    # Collect version info (assume same for all)
    versions = None
    for result in folder_results:
        if result and "versions" in result:
            versions = result["versions"]
            break

    if versions:
        print(
            f"* Toolbox Version: {Fore.CYAN}v{config.easy_version}{Fore.GREEN}\n* Harmony Version: {Fore.YELLOW}{versions['harmony_version']}{Fore.GREEN} Upgrade Available: {versions['harmony_upgrade']}"
        )
        print(
            f"* HMY Version: {' '*4}{Fore.YELLOW}{versions['hmy_version']}{Fore.GREEN}{' '*17} Upgrade Available: {versions['hmy_upgrade']}"
        )

    print(f"{string_stars()}")
    print(f"* Service Status & Sync:")
    print(
        f"* {'Folder':<10} {'S':<2} {'Sync':<5} {'DB 0':<6} {'Free 0':<6} {'DB 1':<6} {'Free 1':<6} {'Local Block':<12}"
    )
    print(f"* {'-'*10} {'-'*2} {'-'*5} {'-'*6} {'-'*6} {'-'*6} {'-'*6} {'-'*12}")

    # Now print results for each folder
    for result in folder_results:
        if result:
            if "error" in result:
                print(f"* {result['folder']:<10} ERROR: {result['error']}")
            else:
                sync_status = (
                    "OK"
                    if result["local_epoch"] == result["remote_epoch"]
                    and abs(result["local_block"] - result["remote_block"]) <= 2
                    else "SYNC"
                )
                db_size_shard = (
                    result["db_size_shard"] if result["shard_id"] != 0 else "N/A"
                )
                free_space_shard = (
                    result["free_space_shard"] if result["shard_id"] != 0 else "N/A"
                )
                print(
                    f"* {result['folder']:<10} {result['shard_id']:<2} {sync_status:<5} {colorize_size(result['db_size_0']):<6} {colorize_size(result['free_space_0']):<6} {colorize_size(db_size_shard):<6} {colorize_size(free_space_shard):<6} {result['local_block']:<12}"
                )

    print(f"{string_stars()}")


def harmony_service_status(service="harmony") -> str:
    status = subprocess.call(["systemctl", "is-active", "--quiet", service])
    if status == 0:
        return f"{service} {Back.GREEN}{Fore.BLACK}Online{Back.RESET}{Fore.GREEN}"
    else:
        return f"{service} {Fore.RED}Offline{Fore.GREEN}"


def set_wallet_env():
    load_var_file(config.dotenv_file)
    if os.path.exists(config.hmy_wallet_store):
        output = subprocess.getoutput(
            f"{environ.get('HARMONY_DIR')}/hmy keys list | grep {config.active_user}"
        )
        output_stripped = output.lstrip(config.active_user)
        output_stripped = output_stripped.strip()
        set_var(config.dotenv_file, "VALIDATOR_WALLET", output_stripped)
        return output_stripped
    else:
        validator_wallet = environ.get("VALIDATOR_WALLET")
        return validator_wallet


def get_db_size(harmony_dir, our_shard) -> str:
    harmony_db_size = subprocess.getoutput(
        f"du -h {harmony_dir}/harmony_db_{our_shard}"
    )
    harmony_db_size = harmony_db_size.rstrip("\t")
    countTrim = len(environ.get("HARMONY_DIR")) + 13
    return harmony_db_size[:-countTrim].strip()


def recovery_type():
    print_stars()
    print(
        f"{string_stars()}\n* Wallet Recovery Type!                                                                     *\n{string_stars()}"
    )
    print(
        "* [0] = Mnemonic phrase recovery (aka seed phrase)                                          *"
    )
    print(
        f"* [1] = Private Key recovery                                                                *\n{string_stars()}"
    )
    menu_options = [
        "[0] - Mnemonic Phrase Recovery",
        "[1] - Private Key Recovery",
    ]
    terminal_menu = TerminalMenu(
        menu_options,
        title="* Which type of restore method would you like to use for your validator wallet?",
    )
    results = terminal_menu.show()
    passphrase_set()
    if results == 0:
        # Mnemonic Recovery Here
        # --passphrase-file passphrase.txt not working atm on ./hmy keys
        run_command(
            f"{environ.get('HARMONY_DIR')}/hmy keys recover-from-mnemonic {config.active_user} --passphrase"
        )
        set_wallet_env()
    elif results == 1:
        # Private Key Recovery Here
        print(
            "* Private key recovery requires your private information in the command itself."
        )
        private = getpass.getpass(
            "* Please enter your private key to restore your wallet: "
        )
        # --passphrase-file passphrase.txt not working atm on ./hmy keys
        run_command(
            f"{environ.get('HARMONY_DIR')}/hmy keys import-private-key {private} {config.active_user} --passphrase"
        )
        set_wallet_env()


def passphrase_status():
    if os.path.exists(config.hmy_wallet_store):
        passphrase_set()
        set_var(
            config.dotenv_file,
            "PASS_SWITCH",
            f"--passphrase-file {environ.get('HARMONY_DIR')}/passphrase.txt",
        )
    else:
        set_var(config.dotenv_file, "PASS_SWITCH", "--passphrase")
    load_var_file(config.dotenv_file)


def passphrase_set():
    if os.path.exists(f"{environ.get('HARMONY_DIR')}/passphrase.txt"):
        return

    print(
        f"{Fore.GREEN}* Setup {environ.get('HARMONY_DIR')}/passphrase.txt file for use with autobidder & harmony-toolbox.\n{string_stars()}"
    )
    # take input
    while True:
        print("* ")
        password_1 = getpass.getpass(
            prompt="* Please set a wallet password for this node\n* Enter your password now: ",
            stream=None,
        )
        password_2 = getpass.getpass(prompt="* Re-enter your password: ", stream=None)
        if not password_1 == password_2:
            print("* Passwords do NOT match, Please try again..")
        else:
            print("* Passwords Match!")
            break
    # Save file, we won't encrypt because if someone has access to the file, they will also have the salt and decrypt code at their disposal.
    save_text(f"{environ.get('HARMONY_DIR')}/passphrase.txt", password_1)
    load_var_file(config.dotenv_file)
    passphrase_status()


def process_command(command: str, shell=True, print_output=True) -> Tuple[bool, str]:
    result = subprocess.run(
        command, shell=shell, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )

    # Command was successful
    if result.returncode == 0:
        if print_output and result.stdout:
            print(result.stdout)
        return True, result.stdout

    # Command failed
    if print_output:
        print(f"Error executing command: {result.stderr}")
    return False, result.stderr


def run_command(command: str, shell=True, print_output=True) -> bool:
    try:
        if print_output:
            subprocess.run(command, shell=shell, check=True)
        else:
            # Suppress the output if print_output is set to False
            with open(os.devnull, "w") as fnull:
                subprocess.run(
                    command, shell=shell, check=True, stdout=fnull, stderr=fnull
                )
        return True
    except subprocess.CalledProcessError as e:
        if print_output:
            print(f"Error executing command: {e}")
        return False


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
    # load .env file or create it if it doesn't exist
    if os.path.exists(var_file):
        load_dotenv(var_file, override=True)
        return True
    else:
        subprocess.run(["touch", var_file])
        return False


def get_validator_wallet_name(wallet_id):
    command = f"{environ.get('HARMONY_DIR')}/hmy keys list"
    result = subprocess.run(
        command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )

    if result.returncode != 0:
        print(f"Error executing command: {result.stderr}")
        return None

    lines = result.stdout.strip().split("\n")
    for line in lines[2:]:  # Skip the header line & blank
        name, address = line.strip().split(None, 1)  # Split by whitespace, max 1 split
        if address == wallet_id:
            return name

    print(f"Wallet ID {wallet_id} not found in the output.")
    return None


def governance_member_voting():
    options = [
        "AffinityShard",
        "BoxedCloud",
        "Buttheadus",
        "Crypt0Tech",
        "ENTER Group",
        "GGA",
        "Hank The Crank",
        "Kratos",
        "Legion",
        "MetaONE",
        "Nick Vasilich",
        "Octeka.One",
        "One1000Lakes",
        "ONECelestial",
        "PeaceLoveHarmony",
        "PiStake",
        "Quick.One",
        "TEC Viva",
        "Tr4ck3r",
        "Quit",
    ]

    selected_indexes = []
    selected_names = []

    for _ in range(7):
        print(
            Fore.GREEN
            + "* Highlight an option and hit enter to add it to your list.\n* (pick up to 7, 'Quit' to finish if less than 7 selections):"
        )
        terminal_menu = TerminalMenu(options, title="Choose a governance member:")
        choice_index = terminal_menu.show()

        # Check if the "Quit" option was selected
        if choice_index == len(options) - 1:
            print("Quitting the selection process.")
            break

        # Check if the same option was not selected previously
        if choice_index not in selected_indexes:
            selected_indexes.append(choice_index)
            selected_names.append(options[choice_index])
            print(f"You have selected: {options[choice_index]}")
        else:
            print(
                f"You have already selected {options[choice_index]}. Please choose another option."
            )

    # Return selected indexes and names as a string
    selected_indexes_str = (
        "[" + ", ".join(map(str, [index + 1 for index in selected_indexes])) + "]"
    )
    selected_names_str = "[" + ", ".join(selected_names) + "]"
    return selected_indexes_str, selected_names_str


def proposal_choices_option() -> None:
    options = ["HIP-30v2", "Governance for Harmony Recovery Wallet", "Quit"]

    print("* Current proposals:\n*\n*")

    terminal_menu = TerminalMenu(options, title="Choose a proposal to vote on:")
    choice_index = terminal_menu.show()

    # Check if the "Quit" option was selected
    if choice_index == len(options) - 1:
        print("Quitting the voting process.")
        return False, None

    # Ask for a vote on the selected proposal
    selected_proposal = options[choice_index]
    question = ask_yes_no(
        f"* Would you like to vote on {selected_proposal}? (YES/NO): "
    )
    if question:
        return question, selected_proposal
    else:
        return question, None


def get_vote_choice() -> tuple[int, str]:
    print(
        Fore.GREEN
        + f"* How would you like to vote on this proposal?                                                 *\n{string_stars()}"
    )
    menu_options = [
        "[1] - Yes",
        "[2] - No",
        "[3] - Abstain",
        "[4] - Quit",
    ]
    terminal_menu = TerminalMenu(
        menu_options, title="* Please choose your voting option. "
    )
    vote_choice_index = terminal_menu.show()
    if vote_choice_index == 3:  # The index of the "Quit" option
        return None, "Quit"
    vote_choice_num = vote_choice_index + 1
    vote_choice_text = menu_options[vote_choice_index].split(" - ")[1]
    return vote_choice_num, vote_choice_text


def get_available_space(directory: str) -> int:
    """Returns available space in given directory in GB."""
    statvfs = os.statvfs(directory)
    return (statvfs.f_frsize * statvfs.f_bavail) / (1024**3)


def check_space_requirements(shard: int, directory: str) -> bool:
    available_space = get_available_space(directory)
    if shard == 0 and available_space < 400:
        if not os.listdir(directory):
            shutil.rmtree(f"{directory}")
        os.remove(f"{config.user_home_dir}/.easynode.env")
        input(
            f"* Warning: There is not enough space to load shard 0 into {directory}.\n* Restart the toolbox and select a volume with more free space when prompted on the install location.\n* Press ENTER to quit."
        )
        raise SystemExit(0)
    elif shard in [1, 2, 3] and available_space < 50:
        if not os.listdir(directory):
            shutil.rmtree(f"{directory}")
        os.remove(f"{config.user_home_dir}/.easynode.env")
        input(
            f"* Warning: There is not enough space to load shard {shard} into {directory}.\n* Restart the toolbox and select a volume with more free space when prompted on the install location.\n* Press ENTER to quit."
        )
        raise SystemExit(0)
    return True


def check_harmony_sh():
    if os.path.exists(config.harmony_sh_home_path):
        # Check if executable
        if not os.access(config.harmony_sh_home_path, os.X_OK):
            print("* ~/harmony.sh is not executable, fixing permissions...")
            os.chmod(config.harmony_sh_home_path, 0o755)

        # Check MD5
        with open(config.harmony_sh_home_path, "rb") as f:
            home_md5 = hashlib.md5(f.read()).hexdigest()
        with open(config.harmony_sh_toolbox_path, "rb") as f:
            toolbox_md5 = hashlib.md5(f.read()).hexdigest()

        if home_md5 != toolbox_md5:
            print("* ~/harmony.sh is outdated, updating...")
            shutil.copy2(config.harmony_sh_toolbox_path, config.harmony_sh_home_path)
            os.chmod(config.harmony_sh_home_path, 0o755)
            print(
                "* Updated ~/harmony.sh. Please re-run the script for the latest version."
            )
            finish_node()
    else:
        print(
            "* ~/harmony.sh not found. If you want to use the launcher script, copy it from the toolbox."
        )


def get_wallet_address():
    print(
        "* Signing Node, No Wallet!                                                                  *"
    )
    print(
        "* You are attempting to launch the menu but no wallet has been loaded, as you chose         *"
    )
    print(
        f"* If you would like to use the menu on the server, complete the following:                  *\n{string_stars()}"
    )
    print(
        "* Edit ~/.easynode.env and add your wallet address on a new line like this example:         *"
    )
    print(
        f"* VALIDATOR_WALLET='one1thisisjustanexamplewalletreplaceme'                                 *\n{string_stars()}"
    )
    raise SystemExit(0)


def get_validator_info():
    validator_data = -1
    try:
        validator_data = staking.get_validator_information(
            environ.get("VALIDATOR_WALLET"), config.working_rpc_endpoint
        )
        return validator_data
    except Exception:
        return validator_data


def current_price():
    try:
        response = requests.get(config.onePriceURL, timeout=5)
    except (ValueError, KeyError, TypeError):
        response = "0.0000"
        return response
    data_dict = response.json()
    type(data_dict)
    data_dict.keys()
    return data_dict["lastPrice"][:-4]


def get_wallet_balance(wallet_addr):
    rpc_endpoint = config.working_rpc_endpoint
    wallet_balance = get_wallet_balance_by_endpoint(rpc_endpoint, wallet_addr)
    if wallet_balance is not None:
        return wallet_balance


def get_wallet_balance_by_endpoint(endpoint, wallet_addr):
    get_balance = 0

    try:
        get_balance = pyhmy.numbers.convert_atto_to_one(
            account.get_balance(wallet_addr, endpoint)
        )
        return get_balance
    except Exception:
        return get_balance


def get_rewards_balance(endpoint, wallet_addr):
    totalRewards = 0
    try:
        validator_rewards = staking.get_delegations_by_delegator(wallet_addr, endpoint)
    except (Exception, ConnectionError):
        return totalRewards

    for i in validator_rewards:
        totalRewards = totalRewards + i["reward"]
    totalRewards = pyhmy.numbers.convert_atto_to_one(totalRewards)

    if totalRewards >= 0:
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
        print(f"File not Found  ::  {e}")
        return {}


def get_sign_pct() -> str:
    hmy_external_rpc = (
        f"{environ.get('HARMONY_DIR')}/hmy --node='{config.working_rpc_endpoint}'"
    )
    output = subprocess.getoutput(
        f"{hmy_external_rpc} blockchain validator information {environ.get('VALIDATOR_WALLET')} | grep signing-percentage"
    )
    output_stripped = output.lstrip(
        '        "current-epoch-signing-percentage": "'
    ).rstrip('",')
    try:
        math = float(output_stripped)
        signPerc = math * 100
        roundSignPerc = round(signPerc, 6)
        return str(roundSignPerc)
    except (OSError, ValueError):
        output_stripped = "0"
        return str(output_stripped)


def get_local_version(folder):
    harmony_version = None
    hmy_version = None

    if os.path.isfile(f"{folder}/harmony"):
        harmony_version = subprocess.getoutput(f"{folder}/harmony -V")
        match = re.search(
            r"version (v\d+-v\d+\.\d+\.\d+-\d+-g[0-9a-f]+ )\(", harmony_version
        )
        if match:
            harmony_version = match.group(1)[:-2]

    if os.path.isfile(f"{folder}/hmy"):
        hmy_version_raw = subprocess.getoutput(f"{folder}/hmy version")
        hmy_version = hmy_version_raw[62:-15]

    if not harmony_version or not hmy_version:
        return None

    return harmony_version, hmy_version


def set_mod_x(file):
    subprocess.run(["chmod", "+x", file])


def clear_temp_files() -> None:
    # check and clear previous versions in /tmp
    tmp_files = [config.harmony_tmp_path, config.hmy_tmp_path]

    for tmp_file in tmp_files:
        try:
            os.remove(tmp_file)
        except FileNotFoundError:
            pass  # Silently ignore if file doesn't exist
        except Exception as e:
            # You can still log or handle other exceptions if desired
            pass


def check_online_version(harmony_version_str="Offline", hmy_ver="Offline") -> None:
    print(Fore.GREEN + string_stars())
    print("* Checking online version of harmony & hmy...")
    try:
        # Check if the harmony binary exists before downloading
        if not os.path.exists(config.harmony_tmp_path):
            with open(os.devnull, "wb") as devnull:
                subprocess.call(
                    [
                        "wget",
                        "https://harmony.one/binary",
                        "-O",
                        config.harmony_tmp_path,
                    ],
                    stdout=devnull,
                    stderr=devnull,
                )
                set_mod_x(config.harmony_tmp_path)

        # Get harmony version
        harmony_ver = subprocess.getoutput(f"{config.harmony_tmp_path} -V")
        output_harmony_version = re.search(
            r"version (v\d+-v\d+\.\d+\.\d+-\d+-g[0-9a-f]+ )\(", harmony_ver
        )
        harmony_version_str = output_harmony_version.group(1)[:-2]
        set_var(config.dotenv_file, "ONLINE_HARMONY_VERSION", harmony_version_str)

        # Check if the hmycli binary exists before downloading
        if not os.path.exists(config.hmy_tmp_path):
            with open(os.devnull, "wb") as devnull:
                subprocess.call(
                    ["wget", "https://harmony.one/hmycli", "-O", config.hmy_tmp_path],
                    stdout=devnull,
                    stderr=devnull,
                )
                set_mod_x(config.hmy_tmp_path)

        # Get hmy version
        hmy_ver = subprocess.getoutput(f"{config.hmy_tmp_path} version")
        hmy_ver = hmy_ver[62:-15]
        set_var(config.dotenv_file, "ONLINE_HMY_VERSION", hmy_ver)

        return
    except (AttributeError, subprocess.CalledProcessError):
        # print("* Error - Website for hmy upgrade is offline, setting to offline.")
        return


def first_env_check(env_file) -> None:
    # Load our easynode.env file
    load_var_file(env_file)
    # Update run count for menus
    current_run_count = int(os.environ.get("RUN_COUNT", default=0)) + 1
    if current_run_count >= config.print_menu_count:
        current_run_count = 0
    set_var(config.dotenv_file, "RUN_COUNT", str(current_run_count))
    return


def version_checks(harmony_folder):
    software_versions = {}
    local_versions = get_local_version(f"{harmony_folder}")

    # Check if the local versions exist. If not, set to a default value.
    software_versions["harmony_version"] = (
        local_versions[0] if local_versions else "Offline"
    )
    software_versions["hmy_version"] = (
        local_versions[1] if local_versions else "Offline"
    )

    # Check if the online versions exist. If not, set to a default value.
    software_versions["online_harmony_version"] = (
        environ.get("ONLINE_HARMONY_VERSION")
        if environ.get("ONLINE_HARMONY_VERSION")
        else "Offline"
    )
    software_versions["online_hmy_version"] = (
        environ.get("ONLINE_HMY_VERSION")
        if environ.get("ONLINE_HMY_VERSION")
        else "Offline"
    )

    # Check versions, if matching False (No Upgrade Required), non-match True (Upgrade Required)
    if (
        software_versions["harmony_version"]
        == software_versions["online_harmony_version"]
        or software_versions["online_harmony_version"] == "Offline"
        or software_versions["harmony_version"] == "Offline"
    ):
        software_versions["harmony_upgrade"] = "False"
    else:
        software_versions["harmony_upgrade"] = "True"

    if (
        software_versions["hmy_version"] == software_versions["online_hmy_version"]
        or software_versions["online_hmy_version"] == "Offline"
        or software_versions["hmy_version"] == "Offline"
    ):
        software_versions["hmy_upgrade"] = "False"
    else:
        software_versions["hmy_upgrade"] = "True"

    return software_versions


# looks for ~/harmony or installs it if it's not there. Asks to overwrite if it finds it, run at your own risk.
def check_for_install(shard) -> str:
    if os.path.exists(f"{config.user_home_dir}/harmony"):
        question = ask_yes_no(
            "* You already have a harmony folder on this system, would you like to re-run installation and rclone on this server? (YES/NO)"
        )
        if question:
            install_harmony()
            # Wallet Setup
            recover_wallet()
            # Check passphrase if wallet is added
            passphrase_status()
            print(
                f"* All harmony files now installed. Database download starting now...\n{string_stars()}"
            )
            clone_shards()
            finish_node_install()
        else:
            if os.path.isdir(f"{config.user_home_dir}/harmony"):
                print(
                    "* You have a harmony folder already, skipping install. Returning to menu..."
                )
                return
    else:
        print(f"{Fore.GREEN}* You selected Shard: {environ.get('SHARD')}. ")
        install_harmony()
        # Wallet Setup
        recover_wallet()
        # Check passphrase if wallet is added
        passphrase_status()
        print(
            f"* All harmony files now installed. Database download starting now...\n{string_stars()}"
        )
        clone_shards()
        finish_node_install()
    return


def install_rclone():
    # Fetch the content of the script
    url = "https://rclone.org/install.sh"
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code != 200:
        print("* Failed to download the script.")
        return False

    script_content = response.text

    # Execute the fetched content
    try:
        process = subprocess.Popen(
            ["sudo", "bash"],
            stdin=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        process.communicate(input=script_content.encode())
        if process.returncode != 0:
            return False
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False


def get_folder_choice() -> str:
    print(
        Fore.GREEN
        + f"* Which folder would you like to install harmony in?                              *\n{string_stars()}"
    )
    menu_options = [
        "[1] - harmony",
        "[2] - harmony0",
        "[3] - harmony1",
        "[4] - harmony2",
        "[5] - harmony3",
    ]
    terminal_menu = TerminalMenu(
        menu_options, title="* Please choose your installation folder option. "
    )
    vote_choice_index = terminal_menu.show()
    if vote_choice_index == 6:  # The index of the "Quit" option
        return None, "Quit"
    vote_choice_text = menu_options[vote_choice_index].split(" - ")[1]
    return vote_choice_text


# Installer Module
def install_harmony() -> None:
    while True:
        print(f"{string_stars()}\n* Install Location\n{string_stars()}")
        folder_path = get_folder_choice()
        harmony_dir = f"{config.user_home_dir}/{folder_path}"
        set_var(config.dotenv_file, "HARMONY_DIR", f"{harmony_dir}")
        if os.path.exists(harmony_dir):
            question = ask_yes_no(
                f"* The folder {harmony_dir} already exists.\n* Are you sure you want to re-install into this existing folder? (YES/NO) "
            )
            if question:
                install_path = harmony_dir
                service_name = os.path.basename(harmony_dir)
                break
        else:
            question = ask_yes_no(
                f"* The path {harmony_dir} doesn't exist yet.\n* Do you want to create it and install the harmony files here? (YES/NO) "
            )
            if question:
                install_path = harmony_dir
                service_name = os.path.basename(harmony_dir)
                break

    # Save envs
    set_var(config.dotenv_file, "HARMONY_DIR", install_path)
    set_var(config.dotenv_file, "SERVICE_NAME", service_name)

    # Create the directory if not exists, and set ownership
    process_command(f"sudo mkdir -p {install_path}")
    process_command(f"sudo chown {config.active_user} {install_path}")

    # Check space requirements for the selected shard
    shard_value = int(environ.get("SHARD"))
    answer = ask_yes_no(
        f"* Last chance to verify, you want to install shard {shard_value} into {install_path}? (Y/N): "
    )
    if answer:
        check_space_requirements(shard_value, install_path)
    else:
        print("* We will exit out of the installation process.")
        finish_node()

    print(f"{string_stars()}\n* Creating all Harmony Files & Folders")
    process_command(f"mkdir -p {install_path}/.hmy/blskeys")

    # Setup folders now that symlink exists or we know we're using ~/harmony
    if not os.path.isdir(f"{config.user_home_dir}/.hmy_cli/account-keys/"):
        process_command(f"mkdir -p {config.user_home_dir}/.hmy_cli/account-keys/")
    if not os.path.isdir(f"{environ.get('HARMONY_DIR')}/.hmy/blskeys"):
        process_command(f"mkdir -p {environ.get('HARMONY_DIR')}/.hmy/blskeys")
    # Change to ~/harmony folder
    os.chdir(f"{environ.get('HARMONY_DIR')}")
    # Install hmy
    update_hmy_binary()
    # Install harmony
    update_harmony_binary()
    # install hmy files
    print(f"* Installing rclone application & rclone configuration files")
    # check for working rclone site and download
    try:
        install_rclone()
    except (ValueError, KeyError, TypeError):
        result = ask_yes_no(
            "* rclone site is offline, we can install rclone from the Ubuntu repo as a workaround, do you want to continue? (Y/N): "
        )
        if result:
            # If rclone curl is down, install rclone with apt instead
            subprocess.run("sudo apt install rclone -y")
        else:
            finish_node()

    process_command(
        f"mkdir -p {config.user_home_dir}/.config/rclone && cp {config.toolbox_location}/src/bin/rclone.conf {config.user_home_dir}/.config/rclone/"
    )
    # Setup the harmony service file
    print(f"* Customizing, Moving & Enabling your {service_name}.service systemd file")

    # Set initial file for customization
    service_file_path = f"{config.toolbox_location}/src/bin/harmony.service"

    # Read the service file
    with open(service_file_path, "r") as file:
        filedata = file.read()

    # Replace the paths with the value of HARMONY_DIR
    filedata = filedata.replace("User=serviceharmony", f"User={config.active_user}")
    filedata = filedata.replace(
        "WorkingDirectory=/home/serviceharmony/harmony",
        f"WorkingDirectory={install_path}",
    )
    filedata = filedata.replace(
        "ExecStart=/home/serviceharmony/harmony/harmony -c harmony.conf",
        f"ExecStart={install_path}/harmony -c harmony.conf",
    )

    # Write the file out again
    with open(f"{service_name}.service", "w") as file:
        file.write(filedata)

    # Move the modified service file into place, change the permissions and enable the service
    subprocess.run(
        [
            "sudo",
            "mv",
            f"{service_name}.service",
            f"/etc/systemd/system/{service_name}.service",
        ],
        check=True,
    )
    subprocess.run(
        ["sudo", "chmod", "a-x", f"/etc/systemd/system/{service_name}.service"],
        check=True,
    )
    subprocess.run(
        ["sudo", "systemctl", "enable", f"{service_name}.service"], check=True
    )


# Database Downloader
def clone_shards():
    our_shard = environ.get("SHARD")
    load_dotenv(config.dotenv_file)
    # Move to ~/harmony
    os.chdir(f"{environ.get('HARMONY_DIR')}")

    if our_shard != "0":
        # If we're not on shard 0, download the numbered shard DB here.
        print(f"* Now cloning shard {our_shard}\n{string_stars()}")
        run_command(
            f"rclone -P -L --webdav-url 'http://fulldb.s{our_shard}.t.hmny.io/webdav' --checksum sync snap: harmony_db_{our_shard} --multi-thread-streams 4 --transfers=32"
        )
        print(
            f"{string_stars()}\n* Shard {our_shard} completed.\n* Shard 0 will be created when you start your service.\n{string_stars()}"
        )
    if our_shard == "0":
        # If we're on shard 0, grab the snap DB here.
        print(
            f"* Now cloning Shard 0, kick back and relax for awhile...\n{string_stars()}"
        )
        run_command(
            f"rclone -P -L --webdav-url 'http://snapdb.s0.t.hmny.io/webdav' --checksum sync snap: harmony_db_0 --multi-thread-streams 4 --transfers=32"
        )


def finish_node_install():
    load_var_file(config.dotenv_file)
    our_shard = config.shard
    print(
        f"{string_stars()}\n* Installation is completed"
        + "\n* Create a new wallet or recover your existing wallet into ./hmy"
        + "\n* Create or upload your bls key & pass files into ~/harmony/.hmy/blskeys"
        + f"\n* Finally, reboot to start synchronization.\n{string_stars()}"
    )
    if environ.get("NODE_WALLET") == "false":
        print(
            "* Post installation quick tips:"
            + "\n* To recover your wallet on this server run:"
            + "\n* python3 ~/harmony-toolbox/load_wallet.py"
            + "\n*"
            + "\n* To create BLS keys run:"
            + f'\n* {environ.get("HARMONY_DIR")}/hmy keys generate-bls-keys --count 1 --shard {our_shard} --passphrase'
            + f"\n*\n{string_stars()}"
        )
    else:
        print(
            "* Post installation quick tips:"
            + "\n* To recover your wallet again, run:"
            + "\n* python3 ~/harmony-toolbox/load_wallet.py"
            + "\n*"
            + "\n* To create BLS keys run:"
            + f'\n* {environ.get("HARMONY_DIR")}/hmy keys generate-bls-keys --count 1 --shard {our_shard} {environ.get("PASS_SWITCH")}'
            + f"\n*\n{string_stars()}"
        )
    print(
        f"* Thanks for using Easy Node - Validator Node Server Software Installer!\n{string_stars()}"
    )
    if int(os.environ.get("RUN_COUNT", default=0)) == 0:
        print(
            "* Thanks for using Easy Node Toolbox - Making everything Easy Mode!"
            + "\n*\n* We serve up free tools and guides for validators every day."
            + "\n*\n* Check our guides out at https://docs.EasyNodePro.com\n*\n"
            + "* Please consider joining our discord & supporting us one time or monthly\n* for our"
            + f" tools and guides at https://bit.ly/easynodediscord today!\n*\n* Goodbye!\n{string_stars()}"
        )
    else:
        print(f"* EasyNodePro.com - https://EasyNodePro.com\n{string_stars()}")
    raise SystemExit(0)


def free_space_check(mount) -> str:
    ourDiskMount = get_harmony_dir_from_path(mount)
    _, _, free = shutil.disk_usage(ourDiskMount)
    freeConverted = str(converted_unit(free)).strip()
    return freeConverted


def free_space_size(mount) -> str:
    ourDiskMount = get_harmony_dir_from_path(mount)
    _, _, free = shutil.disk_usage(ourDiskMount)
    return free


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
    input(
        f"{string_stars()}\nDisk check complete, press ENTER to return to the main menu. "
    )


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


def get_harmony_dir_from_path(pathname):
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
    print(
        f"{Fore.GREEN}* Getting the latest local & blockchain information now, one moment while we load..."
    )
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
    print(f"* This option isn't available on your system, yet!\n{string_stars()}")
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
    for x in upgrades:
        print_stars()
        process_command(x)
        print_stars()


def set_network(network):
    set_var(config.dotenv_file, "NETWORK", "mainnet")
    set_var(config.dotenv_file, "NETWORK_SWITCH", network)
    set_var(config.dotenv_file, "RPC_NET", f"https://rpc.s0.{network}.hmny.io")
    if config.shard != "0":
        set_var(
            config.dotenv_file,
            "RPC_NET_SHARD",
            f"https://rpc.s{environ.get('SHARD')}.t.hmny.io",
        )
    return


def menu_ubuntu_updates() -> str:
    question = ask_yes_no(
        "* Are you sure you would like to proceed with Linux apt Upgrades? (Y/N) "
    )
    if question:
        run_ubuntu_updater()
        input("* OS Updates completed, press ENTER to return to the main menu. ")


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def menu_reboot_server() -> str:
    question = ask_yes_no(
        Fore.RED
        + "WARNING: YOU WILL MISS BLOCKS WHILE YOU REBOOT YOUR ENTIRE SERVER.\n\n"
        + "Reconnect after a few moments & Run the Validator Toolbox Menu again with: python3 ~/harmony-toolbox/start.py\n"
        + Fore.WHITE
        + "Are you sure you would like to proceed with rebooting your server?\n\nType 'Yes' or 'No' to continue"
    )
    if question:
        process_command("sudo reboot")
    else:
        print("Invalid option.")


def finish_node():
    if int(os.environ.get("RUN_COUNT", default=0)) == 0:
        print(
            "* Thanks for using Easy Node Toolbox - Making everything Easy Mode!"
            + "\n*\n* We serve up free tools and guides for validators every day."
            + "\n*\n* Check our guides out at https://docs.EasyNodePro.com\n*\n"
            + "* Please consider joining our discord & supporting us one time or monthly\n* for our"
            + f" tools and guides at https://bit.ly/easynodediscord today!\n*\n* Goodbye!\n{string_stars()}"
        )
    else:
        print(f"* EasyNodePro.com - https://EasyNodePro.com\n{string_stars()}")
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


def colorize_size(size_str, threshold_gb=50.0):
    if size_str.endswith("G"):
        try:
            gb = float(size_str[:-1])
            if gb < threshold_gb:
                return f"{Fore.RED}{Back.YELLOW}{size_str}{Style.RESET_ALL}{Fore.GREEN}"
        except ValueError:
            pass
    return size_str
