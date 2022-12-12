import os
import requests
import time
import json
import subprocess
from subprocess import Popen, PIPE, run
from ast import literal_eval
from toolbox.config import easy_env
from os import environ
from datetime import datetime
from colorama import Fore, Back, Style
from pyhmy import blockchain, transaction
from requests.exceptions import HTTPError
from toolbox.library import (
    process_command,
    print_stars,
    print_stars,
    print_whitespace,
    ask_yes_no,
    return_txt,
    install_harmony,
    install_hmy,
    get_sign_pct,
    load_var_file,
    get_wallet_balance,
    get_rewards_balance,
    string_stars,
    set_var,
    free_space_check,
    server_drive_check,
    all_sys_info,
    coming_soon,
    menu_ubuntu_updates,
    menu_error,
    menu_reboot_server,
    finish_node
)

def collect_rewards(networkCall):
    os.system(
        f"{networkCall} staking collect-rewards --delegator-addr {environ.get('VALIDATOR_WALLET')} --gas-price 100 {environ.get('PASS_SWITCH')}"
    )

def send_rewards(networkCall, sendAmount, rewards_wallet):
    os.system(
        f"{networkCall} transfer --amount {sendAmount} --from {environ.get('VALIDATOR_WALLET')} --from-shard 0 --to {rewards_wallet} --to-shard 0 --gas-price 100 {environ.get('PASS_SWITCH')}"
    )

def rewards_collector(rewards_wallet, validator_wallet, rpc) -> None:
    print("* Harmony ONE Rewards Collection")
    print_stars()
    question = ask_yes_no(
        f"*\n* For your validator wallet {validator_wallet}\n* You have {get_rewards_balance(rpc, validator_wallet)} $ONE pending.\n* Would you like to collect your rewards on the Harmony mainnet? (YES/NO) "
    )
    if question:
        collect_rewards(environ.get('NETWORK_0_CALL'))
        print_stars()
        print(
            Fore.GREEN
            + f"* mainnet rewards for {validator_wallet} have been collected."
            + Style.RESET_ALL
        )
        print_stars()
    else:
        return
    wallet_balance, wallet_balance_test = get_wallet_balance(environ.get("VALIDATOR_WALLET"))
    suggested_send = wallet_balance - int(environ.get("GAS_RESERVE"))
    print("*\n*\n")
    print_stars()
    print("\n* Send your Harmony ONE Rewards?")
    print_stars()
    if suggested_send >= 1:
        question = ask_yes_no(
            f"* You have {wallet_balance} $ONE available to send. We suggest sending {suggested_send} $ONE using your reservation settings.\n* Would you like to send {suggested_send} $ONE to {rewards_wallet} now? (YES/NO)"
        )
        if question:
            send_rewards(environ.get("NETWORK_0_CALL"), suggested_send, rewards_wallet)
        return

def menu_topper_regular() -> None:
    # Get stats & balances
    load_1, load_5, load_15 = os.getloadavg()
    sign_percentage = get_sign_pct()
    total_balance, total_balance_test = get_wallet_balance(environ.get("VALIDATOR_WALLET"))
    remote_data_shard_0, local_data_shard, remote_data_shard = menu_validator_stats()
    subprocess.run("clear")
    # Print Menu
    print_stars()
    print(f'{Style.RESET_ALL}* {Fore.GREEN}validator-toolbox for Harmony ONE Validators by Easy Node   v{easy_env.easy_version}{Style.RESET_ALL}   https://easynode.pro *')
    print_stars()
    print(f'* Your validator wallet address is: {Fore.RED}{str(environ.get("VALIDATOR_WALLET"))}{Style.RESET_ALL}\n* Your $ONE balance is:             {Fore.GREEN}{str(round(total_balance, 2))}{Style.RESET_ALL}\n* Your pending $ONE rewards are:    {Fore.GREEN}{str(round(get_rewards_balance(easy_env.rpc_endpoints, environ.get("VALIDATOR_WALLET")), 2))}{Style.RESET_ALL}\n* Server Hostname & IP:             {easy_env.server_host_name}{Style.RESET_ALL} - {Fore.YELLOW}{easy_env.external_ip}{Style.RESET_ALL}')
    harmony_service_status()
    print(f'* Epoch Signing Percentage:         {Style.BRIGHT}{Fore.GREEN}{Back.BLUE}{sign_percentage} %{Style.RESET_ALL}\n* Current disk space free: {Fore.CYAN}{free_space_check(easy_env.harmony_dir): >6}{Style.RESET_ALL}\n* Current harmony version: {Fore.YELLOW}{environ.get("HARMONY_VERSION")}{Style.RESET_ALL}, has upgrade available: {environ.get("HARMONY_UPGRADE_AVAILABLE")}\n* Current hmy version: {Fore.YELLOW}{environ.get("HMY_VERSION")}{Style.RESET_ALL}, has upgrade available: {environ.get("HMY_UPGRADE_AVAILABLE")}')
    print_stars()
    if environ.get("SHARD") != "0":
        print(f"\n* Note: Running on shard {environ.get('SHARD')}, Shard 0 is no longer needed locally and should be under 200MB\n* Remote Shard 0 Epoch: {remote_data_shard_0['result']['shard-chain-header']['epoch']}, Current Block: {literal_eval(remote_data_shard_0['result']['shard-chain-header']['number'])}, Local Shard 0 Size: {get_db_size('0')}")
        print(f"* Remote Shard {environ.get('SHARD')} Epoch: {remote_data_shard['result']['shard-chain-header']['epoch']}, Current Block: {literal_eval(remote_data_shard['result']['shard-chain-header']['number'])}")
        print(f"*  Local Shard {environ.get('SHARD')} Epoch: {local_data_shard['result']['shard-chain-header']['epoch']}, Current Block: {literal_eval(local_data_shard['result']['shard-chain-header']['number'])}, Local Shard {environ.get('SHARD')} Size: {get_db_size(environ.get('SHARD'))}")
    if environ.get("SHARD") == "0":
        print(f"* Remote Shard {environ.get('SHARD')} Epoch: {remote_data_shard_0['result']['shard-chain-header']['epoch']}, Current Block: {literal_eval(remote_data_shard_0['result']['shard-chain-header']['number'])}")
        print(f"*  Local Shard {environ.get('SHARD')} Epoch: {local_data_shard['result']['shard-chain-header']['epoch']}, Current Block: {literal_eval(local_data_shard['result']['shard-chain-header']['number'])}")
    print(f"* CPU Load Averages: {round(load_1, 2)} over 1 min, {round(load_5, 2)} over 5 min, {round(load_15, 2)} over 15 min")
    print_stars()

def menu_topper_full() -> None:
    load_1, load_5, load_15 = os.getloadavg()
    remote_data_shard_0, local_data_shard, remote_data_shard = menu_validator_stats()
    subprocess.run("clear")
    # Print Menu
    print_stars()
    print(f'{Style.RESET_ALL}* {Fore.GREEN}validator-toolbox for Harmony ONE Validators by Easy Node   v{str(environ.get("EASY_VERSION"))}{Style.RESET_ALL}   https://easynode.one *')
    print_stars()
    print(f'* Server Hostname & IP:             {easy_env.server_host_name}{Style.RESET_ALL} - {Fore.YELLOW}{easy_env.external_ip}{Style.RESET_ALL}')
    harmony_service_status()
    print(f'* Current disk space free: {Fore.CYAN}{free_space_check(easy_env.harmony_dir): >6}{Style.RESET_ALL}{Style.RESET_ALL}\n* Current harmony version: {Fore.YELLOW}{environ.get("HARMONY_VERSION")}{Style.RESET_ALL}, has upgrade available: {environ.get("HARMONY_UPGRADE_AVAILABLE")}\n* Current hmy version: {Fore.YELLOW}{environ.get("HMY_VERSION")}{Style.RESET_ALL}, has upgrade available: {environ.get("HMY_UPGRADE_AVAILABLE")}')
    print(f"* Remote Shard {environ.get('SHARD')} Epoch: {remote_data_shard_0['result']['shard-chain-header']['epoch']}, Current Block: {literal_eval(remote_data_shard_0['result']['shard-chain-header']['number'])}")
    print(f"*  Local Shard {environ.get('SHARD')} Epoch: {local_data_shard['result']['shard-chain-header']['epoch']}, Current Block: {literal_eval(local_data_shard['result']['shard-chain-header']['number'])}")
    print(f"* CPU Load Averages: {round(load_1, 2)} over 1 min, {round(load_5, 2)} over 5 min, {round(load_15, 2)} over 15 min")
    print_stars()

def menu_regular() -> None:
    menu_topper_regular()
    for x in return_txt(easy_env.main_menu_regular):
        x = x.strip()
        try:
            x = eval(x)
        except SyntaxError:
            pass
        if x:
            print(x)

def menu_full() -> None:
    menu_topper_full()
    for x in return_txt(easy_env.main_menu_full):
        x = x.strip()
        try:
            x = eval(x)
        except SyntaxError:
            pass
        if x:
            print(x)

def get_wallet_json(wallet: str) -> str:
    test_or_main = environ.get("NETWORK")
    try:
        response = requests.get(f"https://api.stake.hmny.io/networks/{test_or_main}/validators/{wallet}")
        response.raise_for_status()
        # access JSOn content
        json_response = response.json()
    #        print("Entire JSON response")
    #        print(json_response)
    except HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        print(
            f'* You have not created your validator yet, try again after you add one!\n* cd ~/harmony\n* ./hmy keys recover-from-mnemonic {easy_env.active_user} {environ.get("PASS_SWITCH")}'
        )
        input("Press ENTER to return to the main menu.")
        return
    except Exception as err:
        print(f"Other error occurred: {err}")
        input("Press ENTER to return to the main menu.")
        return
    return json_response

def tmi_server_info() -> None:
    validator_wallet = environ.get("VALIDATOR_WALLET")
    json_response = get_wallet_json(validator_wallet)
    for key, value in json_response.items():
        print(key, ":", value)
    print_stars()
    input("Press ENTER to return to the main menu.")

def set_rewards_wallet() -> None:
    rewards_wallet = environ.get("REWARDS_WALLET")
    gas_reserve = environ.get("GAS_RESERVE")
    if rewards_wallet is None:
        question = ask_yes_no("* Would you like to add an address to send your rewards too? (YES/NO)")
        if question:
            rewards_wallet = input(f"* Input your one1 address to send rewards into, please input your address now: ")
            if rewards_wallet.startswith("one1"):
                set_var(easy_env.dotenv_file, "REWARDS_WALLET", rewards_wallet)
            else:
                print("* Wallet does not start with one1, please try again.")
                return
        return
    else:
        question = ask_yes_no(
            f"* Your current saved rewards wallet address is {rewards_wallet}\n* Would you like to update the address you send your rewards too? (YES/NO)"
        )
        if question:
            rewards_wallet = input(f"* Input your one1 address to send rewards into, please input your address now: ")
            if rewards_wallet.startswith("one1"):
                set_var(easy_env.dotenv_file, "REWARDS_WALLET", rewards_wallet)
            else:
                print("* Wallet does not start with one1, please try again.")
                return
            set_gas_reserve()
            return
        else:
            question = ask_yes_no(
                f"* Your current wallet gas reservation is {gas_reserve} $ONE\n* Would you like to update your reservation total? (YES/NO)"
            )
            if question:
                set_gas_reserve()
                return
    return

def set_gas_reserve() -> None:
    gas_reserve = environ.get("GAS_RESERVE")
    question = ask_yes_no(
        f"* Your current total of $ONE to reserve for fees is {gas_reserve}\n* Would you like to update the reserve total? (YES/NO)"
    )
    if question:
        ask_reserve_total()
    return

def ask_reserve_total() -> None:
    reserve_total = input("* How much $ONE would you like to keep reserved for fees? ")
    set_reserve_total(reserve_total)
    return

def set_reserve_total(reserve_total):
    set_var(easy_env.dotenv_file, "GAS_RESERVE", reserve_total)

def drive_check() -> None:
    server_drive_check(easy_env.dotenv_file, easy_env.harmony_dir)
    return

def run_check_balance() -> None:
    menu_check_balance(easy_env.rpc_endpoints, environ.get("VALIDATOR_WALLET"))

def run_full_node() -> None:
    menu_options = {
        # 0: finish_node,
        1: refresh_stats,
        2: coming_soon,
        3: coming_soon,
        4: coming_soon,
        5: coming_soon,
        6: coming_soon,
        7: set_rewards_wallet,
        8: menu_service_stop_start,
        9: menu_service_restart,
        10: menu_binary_updates,
        11: hmy_cli_upgrade,
        12: menu_ubuntu_updates,
        13: drive_check,
        14: coming_soon,
        15: all_sys_info,
        999: menu_reboot_server,
    }
    while True:
        load_var_file(easy_env.dotenv_file)
        menu_full()
        if environ.get("HARMONY_UPGRADE_AVAILABLE") == "True":
            print(
                f"* The harmony binary has an update available, Option #10 will upgrade you but you may miss a block while it restarts.\n"
            )
            print_stars()
        if environ.get("HMY_UPGRADE_AVAILABLE") == "True":
            print(
                f"* The hmy binary has an update available, Option #11 will upgrade you but you may miss a block while it restarts.\n"
            )
            print_stars()
        try:
            option = int(input("Enter your option: "))
        except ValueError:
            menu_error()
            run_full_node(environ.get("NODE_TYPE"))
        if option == 0:
            return finish_node()
        subprocess.run("clear")
        menu_options[option]()

def bingo_checker():
    os.system("grep BINGO ~/harmony/latest/zerolog-harmony.log | tail -10")
    print_stars()
    print("* Press enter to return to the main menu.")
    print_stars()
    input()

def run_rewards_collector() -> None:
    rewards_collector(environ.get("REWARDS_WALLET"), environ.get('VALIDATOR_WALLET'), easy_env.rpc_endpoints)
    return

def run_regular_node(software_versions) -> None:
    menu_options = {
        0: finish_node,
        1: refresh_stats,
        2: menu_active_bls,
        3: coming_soon,
        4: run_rewards_collector,
        5: bingo_checker,
        6: coming_soon,
        7: set_rewards_wallet,
        8: menu_service_stop_start,
        9: menu_service_restart,
        10: menu_binary_updates,
        11: hmy_cli_upgrade,
        12: menu_ubuntu_updates,
        13: drive_check,
        14: tmi_server_info,
        15: all_sys_info,
        999: menu_reboot_server,
    }
    while True:
        load_var_file(easy_env.dotenv_file)
        menu_regular()
        if software_versions["harmony_upgrade"] == "True":
            print(
                f'* The harmony binary has an update available to version {software_versions["online_harmony_version"]}\n* Option #10 will upgrade you, but you may miss a block while it upgrades & restarts.\n* Currently installed version {software_versions["harmony_version"]}'
            )
            print_stars()
        if software_versions["hmy_upgrade"] == "True":
            print(
                f'* The hmy binary has an update available to version {software_versions["online_hmy_version"]}\n* Option #11 will upgrade you.\n* Currently installed version {software_versions["hmy_version"]}'
            )
            print_stars()
        try:
            option = int(input("Enter your option: "))
        except ValueError:
            menu_error()
            break
        subprocess.run("clear")
        print_stars()
        menu_options[option]()
        if option != 1:
            refresh_stats(1)

def harmony_service_status() -> None:
    status = subprocess.call(["systemctl", "is-active", "--quiet", "harmony"])
    if status == 0:
        print("* Harmony Service is:               " + Fore.BLACK + Back.GREEN + "   Online  " + Style.RESET_ALL)
    else:
        print("* Harmony Service is:               " + Fore.WHITE + Back.RED + "  *** Offline *** " + Style.RESET_ALL)

def service_menu_option() -> None:
    status = os.system("systemctl is-active --quiet harmony")
    if status == 0:
        print(f'*   8 - {Fore.RED}Stop Harmony Service      {Fore.GREEN}- {Fore.YELLOW}{Back.RED}WARNING: You will miss blocks while stopped!   {Style.RESET_ALL}')
        print(f'*   9 - Restart Harmony Service   - {Back.RED}{Fore.YELLOW}WARNING: You will miss blocks during a restart!{Style.RESET_ALL}')
    else:
        print(f'*   8 - {Fore.GREEN}Start Harmony Service{Style.RESET_ALL}')

def make_backup_dir() -> str:
    if not os.path.isdir(f"{easy_env.harmony_dir}/harmony_backup"):
        print_stars()
        print("Backup directory not found, creating folder")
        os.system(f"mkdir -p {easy_env.harmony_dir}/harmony_backup")

def hmy_cli_upgrade():
    question = ask_yes_no(
        "Are you sure you would like to proceed with updating the Harmony CLI file?\n\nType 'Yes' or 'No' to continue"
    )
    if question:
        os.chdir(f"{easy_env.harmony_dir}")
        make_backup_dir()
        os.system(f"cp {easy_env.hmy_app} {easy_env.harmony_dir}/harmony_backup")
        print_stars()
        install_hmy(easy_env.harmony_dir)
        print_stars()
        print("Harmony cli has been updated to: ")
        os.system(f"{easy_env.hmy_app} version")
        print_stars()
        set_var(easy_env.dotenv_file, "HMY_UPGRADE_AVAILABLE", "False")
        input("Update completed, press ENTER to return to the main menu. ")

def update_harmony_app(test_or_main):
    os.chdir(f"{easy_env.harmony_dir}")
    print_stars()
    print("Currently installed version: ")
    os.system("./harmony -V")
    make_backup_dir()
    os.system(f"cp {easy_env.harmony_dir}/harmony {easy_env.harmony_dir}/harmony_backup")
    print_stars()
    print("Downloading current harmony binary file from harmony.one: ")
    print_stars()
    install_harmony(easy_env.harmony_dir, easy_env.bls_key_file)
    print_stars()
    print("Updated version: ")
    os.system("./harmony -V")
    if environ.get("SHARD") != "0":
        size = 0
        for path, dirs, files in os.walk(f"{easy_env.harmony_dir}/harmony_db_0"):
            for f in files:
                fp = os.path.join(path, f)
                size += os.path.getsize(fp)
            if size >= 200000000:
                question = ask_yes_no(
                    Fore.WHITE
                    + "Are you sure you would like to proceed with upgrading and trimming database 0?\n\nType 'Yes' or 'No' to continue"
                )
                if question:
                    os.system("sudo service harmony stop")
                    os.system(
                        f"mv {easy_env.harmony_dir}/harmony_db_0 {easy_env.harmony_dir}/harmony_db_0_old"
                    )
                    os.system("sudo service harmony start")
                    os.system(f"rm -r {easy_env.harmony_dir}/harmony_db_0_old")
                else:
                    print("Skipping removal of 0, but it's no longer required, fyi!")
            else:
                print("Your database 0 is already trimmed, enjoy!")
    else:
        os.system("sudo service harmony restart")
    print_stars()
    print("Harmony Service is restarting, waiting 10 seconds for restart.")
    set_var(easy_env.dotenv_file, "HARMONY_UPGRADE_AVAILABLE", "False")
    time.sleep(10)

def menu_validator_stats():
    load_var_file(easy_env.dotenv_file)
    remote_shard_0 = [
        f"{easy_env.hmy_app}",
        "blockchain",
        "latest-headers",
        f'--node=https://api.s0.{environ.get("NETWORK_SWITCH")}.hmny.io',
    ]
    result_remote_shard_0 = run(remote_shard_0, stdout=PIPE, stderr=PIPE, universal_newlines=True)
    try:
        remote_data_shard_0 = json.loads(result_remote_shard_0.stdout)
    except:
        print(f'* Remote Shard 0 Offline')
    local_shard = [f"{easy_env.hmy_app}", "blockchain", "latest-headers"]
    result_local_shard = run(local_shard, stdout=PIPE, stderr=PIPE, universal_newlines=True)
    try:
        local_data_shard = json.loads(result_local_shard.stdout)
    except:
        print(f'* Local Server Offline, restart your service or troubleshoot the issue by running the following in your ~/harmony directory:\n* ./harmony -c harmony.conf')
            
    if environ.get("SHARD") != "0":
        remote_shard = [
            f"{easy_env.hmy_app}",
            "blockchain",
            "latest-headers",
            f'--node=https://api.s{environ.get("SHARD")}.{environ.get("NETWORK_SWITCH")}.hmny.io',
        ]
        try:
            result_remote_shard = run(remote_shard, stdout=PIPE, stderr=PIPE, universal_newlines=True)
            remote_data_shard = json.loads(result_remote_shard.stdout)
            return remote_data_shard_0, local_data_shard, remote_data_shard
        except (ValueError, KeyError, TypeError):
            return
        
    return remote_data_shard_0, local_data_shard, None

def refresh_stats(clear=0) -> str:
    if clear == 0:
        subprocess.run("clear")
    print_stars()
    print(f'* Getting the latest local & blockchain information now, one moment while we load...')
    print_stars()
    return

def get_db_size(our_shard) -> str:
    harmony_db_size = subprocess.getoutput(f"du -h {easy_env.harmony_dir}/harmony_db_{our_shard}")
    harmony_db_size = harmony_db_size.rstrip("\t")
    countTrim = len(easy_env.harmony_dir) + 13
    return harmony_db_size[:-countTrim]

def shard_stats(our_shard) -> str:
    our_uptime = subprocess.getoutput("uptime")
    our_ver = subprocess.getoutput(f"{easy_env.harmony_app} -V")
    db_0_size = get_db_size("0")
    if our_shard == "0":
        print(
            f"""
    * Uptime :: {our_uptime}\n\n Harmony DB 0 Size  ::  {db_0_size}
    * {our_ver}
    {string_stars()}
        """
        )
    else:
        print(
            f"""
    * Uptime :: {our_uptime}
    *
    * Harmony DB 0 Size  ::  {db_0_size}
    * Harmony DB {our_shard} Size  ::   {get_db_size(str(our_shard))}
    *
    * {our_ver}
    *
    {string_stars()}
        """
        )

def menu_binary_updates():
    test_or_main = environ.get("NETWORK")
    question = ask_yes_no(
        Fore.RED
        + "WARNING: YOU WILL MISS BLOCKS WHILE YOU UPGRADE THE HARMONY SERVICE.\n\n"
        + Fore.WHITE
        + "Are you sure you would like to proceed?\n\nType 'Yes' or 'No' to continue"
    )
    if question:
        update_harmony_app(test_or_main)

def menu_service_stop_start() -> str:
    status = os.system("systemctl is-active --quiet harmony")
    if status != 0:
        os.system("sudo service harmony start")
        print()
        print("Harmony Service Has Been Started.")
        print()
        input("Press ENTER to return to the main menu.")
    else:
        question = ask_yes_no(
            "*********\n"
            + Fore.RED
            + "WARNING: YOU WILL MISS BLOCKS IF YOU STOP THE HARMONY SERVICE.\n\n"
            + Fore.WHITE
            + "Are you sure you would like to proceed?\n\nType 'Yes' or 'No' to continue"
        )
        if question:
            os.system("sudo service harmony stop")
            print()
            print(
                "Harmony Service Has Been Stopped. "
                + Fore.RED
                + "YOU ARE MISSING BLOCKS ON THIS NODE."
                + Style.RESET_ALL
            )
            print()
            input("Press ENTER to return to the main menu.")

def menu_service_restart() -> str:
    question = ask_yes_no(
        "*********\n"
        + Fore.RED
        + "WARNING: YOU WILL MISS BLOCKS UNTIL RESTART IS COMPLETED & SYNC CATCHES UP!\n\n"
        + Fore.WHITE
        + "Are you sure you would like to proceed?\n\nType 'Yes' or 'No' to continue"
    )
    if question:
        os.system("sudo service harmony restart")
        print()
        print("* The Harmony Service Has Been Restarted")
        input("* Press ENTER to return to the main menu.")

def menu_active_bls() -> str:
    validator_wallet = environ.get("VALIDATOR_WALLET")
    json_response = get_wallet_json(validator_wallet)
    print("* This is a list of your BLS Keys that are active for the next election.")
    for i, x in enumerate(json_response["bls-public-keys"]):
        print(f"BLS Key {i+1} {x}")
    print_stars()
    print("* Press ENTER to return to the main menu.")
    print_stars()
    input()

# is this used?
def is_float(value):
    try:
        float(value)
        return True
    except ValueError:
        return False

def menu_check_balance(rpc, validator_wallet) -> None:
    if environ.get("NODE_TYPE") == "regular":
        print("* Calling mainnet and testnet for balances...")
        print_stars()
        total_balance, total_balance_test = get_wallet_balance(validator_wallet)
        print(f"* Your Validator Wallet Balance on Mainnet is: {total_balance} Harmony ONE Coins")
        print(f"* Your Pending Validator Rewards are: {get_rewards_balance(rpc, validator_wallet)}")
        print(f"* Your Validator Wallet Balance on Testnet is: {total_balance_test} Harmony ONE Test Coins")
        print_stars()
        i = 0
        while i < 1:
            question = ask_yes_no("* Would you like to check another Harmony ONE Address? (YES/NO) ")
            if question:
                balanceCheckAny()
            else:
                i = 1
    else:
        i = 0
        while i < 1:
            question = ask_yes_no("* Would you like to check a Harmony ONE Address? (YES/NO) ")
            if question:
                balanceCheckAny()
            else:
                i = 1

def balanceCheckAny():
    check_wallet = input(
        "* Type the address of the Harmony ONE Wallet you would like to check.\n"
        + "* Only one wallets will work, no 0x addresses : "
    )
    print("* Calling mainnet and testnet for balances...")
    print_stars()
    total_balance, total_balance_test = get_wallet_balance(check_wallet)
    print(
        f"* The Mainnet Wallet Balance is: {total_balance} Harmony ONE Coins\n* The Testnet Wallet Balance is: {total_balance_test} Harmony ONE Test Coins"
    )
    print_stars()
    input("Press ENTER to continue.")

def get_current_epoch():
    if environ.get("NETWORK") == "mainnet":
        endpoints_count = len(easy_env.rpc_endpoints)
    if environ.get("NETWORK") == "testnet":
        endpoints_count = len(easy_env.rpc_endpoints_test)

    for i in range(endpoints_count):
        current_epoch = get_current_epochByEndpoint(easy_env.rpc_endpoints[i])

        if current_epoch != -1:
            return current_epoch
    current_epoch = 0
    return current_epoch

def get_current_epochByEndpoint(endpoint):
    current = 0
    max_tries = easy_env.rpc_endpoints_max_connection_retries
    current_epoch = -1

    while current < max_tries:
        try:
            current_epoch = blockchain.get_current_epoch(endpoint)
            return current_epoch
        except Exception:
            current += 1
            continue

    return current_epoch
