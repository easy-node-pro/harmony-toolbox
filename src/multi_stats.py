import os
import json
import subprocess
from os import environ
from ast import literal_eval
from toolbox.config import easy_env
from toolbox.library import load_var_file, get_sign_pct, get_wallet_balance, print_stars, set_var, loader_intro, ask_yes_no, version_checks
from toolbox.toolbox import free_space_check, harmony_service_status, get_rewards_balance, get_db_size, refresh_stats
from subprocess import PIPE, run
from colorama import Fore, Back, Style
from simple_term_menu import TerminalMenu

load_var_file(easy_env.dotenv_file)

user_home = f'{os.path.expanduser("~")}'

if not environ.get("VALIDATOR_WALLET"):
    # ask for wallet, save to env.
    address = input(f'No Harmony $ONE address found, please input a one1 or 0x address: ')
    address_2 = input(f'Please re-enter your address to verify: ')
    if address == address_2:
        set_var(easy_env.dotenv_file, "VALIDATOR_WALLET", address_2)

if not environ.get("NETWORK_SWITCH"):
    # ask for mainnet or testnet
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
    if results == 1:
        set_var(easy_env.dotenv_file, "NETWORK", "testnet")
        set_var(easy_env.dotenv_file, "NETWORK_SWITCH", "b")
        set_var(easy_env.dotenv_file, "RPC_NET", "https://rpc.s0.b.hmny.io")
    subprocess.run("clear")

# Search harmony.conf for the proper port to hit
def find_port(folder):
    with open(f'{user_home}/{folder}/harmony.conf') as f:
        data_file = f.readlines()
    count = 0
    for line in data_file:
        line = line.rstrip()
        if 'Port =' in line:
            if count == 3:
                return line[9:]
            count += 1

# build list of installs
def get_folders():
    folders = {}
    if os.path.exists(f"{user_home}/harmony/harmony.conf"):
        port = find_port(f'harmony')
        folders['harmony'] = port
        print(f'* Found ~/harmony folder, on port {port}')
        print_stars()
    if os.path.exists(f"{user_home}/harmony0/harmony.conf"):
        port = find_port(f'harmony0')
        folders['harmony0'] = port
        print(f'* Found ~/harmony1 folder, on port {port}')
        print_stars()
    if os.path.exists(f"{user_home}/harmony1/harmony.conf"):
        port = find_port(f'harmony1')
        folders['harmony1'] = port
        print(f'* Found ~/harmony1 folder, on port {port}')
        print_stars()
    if os.path.exists(f"{user_home}/harmony2/harmony.conf"):
        port = find_port(f'harmony2')
        folders['harmony2'] = port
        print(f'* Found ~/harmony2 folder, on port {port}')
        print_stars()
    if os.path.exists(f"{user_home}/harmony3/harmony.conf"):
        port = find_port(f'harmony3')
        folders['harmony3'] = port
        print(f'* Found ~/harmony3 folder, on port {port}')
        print_stars()
    return folders

def stats_output_regular(folders) -> None:
    # Get server stats & wallet balances
    load_1, load_5, load_15 = os.getloadavg()
    sign_percentage = get_sign_pct()
    total_balance, total_balance_test = get_wallet_balance(environ.get("VALIDATOR_WALLET"))
    subprocess.run("clear")
    # Print Menu
    print_stars()
    print(f'{Style.RESET_ALL}* {Fore.GREEN}validator-toolbox for Harmony ONE Validators by Easy Node   v{easy_env.easy_version}{Style.RESET_ALL}   https://easynode.one *')
    print_stars()
    print(f'* Your validator wallet address is: {Fore.RED}{str(environ.get("VALIDATOR_WALLET"))}{Style.RESET_ALL}\n* Your $ONE balance is:             {Fore.GREEN}{str(round(total_balance, 2))}{Style.RESET_ALL}\n* Your pending $ONE rewards are:    {Fore.GREEN}{str(round(get_rewards_balance(easy_env.rpc_endpoints, environ.get("VALIDATOR_WALLET")), 2))}{Style.RESET_ALL}\n* Server Hostname & IP:             {easy_env.server_host_name}{Style.RESET_ALL} - {Fore.YELLOW}{easy_env.external_ip}{Style.RESET_ALL}')
    harmony_service_status()
    print(f'* Epoch Signing Percentage:         {Style.BRIGHT}{Fore.GREEN}{Back.BLUE}{sign_percentage} %{Style.RESET_ALL}\n* Current user home dir free space: {Fore.CYAN}{free_space_check(easy_env.user_home_dir): >6}{Style.RESET_ALL}')
    print(f"* CPU Load Averages: {round(load_1, 2)} over 1 min, {round(load_5, 2)} over 5 min, {round(load_15, 2)} over 15 min")
    print_stars()
    remote_shard_0 = [f"{user_home}/{list(folders.items())[0][0]}/hmy", "utility", "metadata", f"--node=https://api.s0.t.hmny.io"]
    result_shard_0 = run(remote_shard_0, stdout=PIPE, stderr=PIPE, universal_newlines=True)
    remote_0_data = json.loads(result_shard_0.stdout)
    print(f"* Remote Shard 0 Epoch: {remote_0_data['result']['current-epoch']}, Current Block: {remote_0_data['result']['current-block-number']}")
    print_stars()
    for folder in folders:
        software_versions = version_checks(folder)
        print(f'* Results for the current folder: {easy_env.user_home_dir}/{folder}\n* Current harmony version: {Fore.YELLOW}{software_versions["harmony_version"]}{Style.RESET_ALL}, has upgrade available: {software_versions["harmony_upgrade"]}\n* Current hmy version: {Fore.YELLOW}{software_versions["hmy_version"]}{Style.RESET_ALL}, has upgrade available: {software_versions["hmy_upgrade"]}')
        local_server = [f"{user_home}/{folder}/hmy", "utility", "metadata", f"--node=http://localhost:{folders[folder]}"]
        result_local_server = run(local_server, stdout=PIPE, stderr=PIPE, universal_newlines=True)
        local_data = json.loads(result_local_server.stdout)
        remote_server = [f"{user_home}/{folder}/hmy", "utility", "metadata", f"--node=https://api.s{local_data['result']['shard-id']}.t.hmny.io"]
        result_remote_server = run(remote_server, stdout=PIPE, stderr=PIPE, universal_newlines=True)
        remote_data = json.loads(result_remote_server.stdout)
        print(f"* Remote Shard {local_data['result']['shard-id']} Epoch: {remote_data['result']['current-epoch']}, Current Block: {remote_data['result']['current-block-number']}")
        print(f"*  Local Shard {local_data['result']['shard-id']} Epoch: {local_data['result']['current-epoch']}, Current Block: {(local_data['result']['current-block-number'])}\n*   Local Shard 0 Size: {get_db_size(f'{user_home}/{folder}', '0')}\n*   Local Shard {local_data['result']['shard-id']} Size: {get_db_size(f'{user_home}/{folder}', local_data['result']['shard-id'])}")
        print_stars()

if __name__ == "__main__":
    loader_intro()
    refresh_stats(1)
    folders = get_folders()
    stats_output_regular(folders)