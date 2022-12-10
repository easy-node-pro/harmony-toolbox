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
    print_stars_reset,
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
    server_drive_check
)
from toolbox.allsysinfo import allSysInfo


def collectRewards(networkCall):
    os.system(
        f"{networkCall} staking collect-rewards --delegator-addr {environ.get('VALIDATOR_WALLET')} --gas-price 100 {environ.get('PASS_SWITCH')}"
    )


def sendRewards(networkCall, sendAmount, rewardsWallet):
    os.system(
        f"{networkCall} transfer --amount {sendAmount} --from {environ.get('VALIDATOR_WALLET')} --from-shard 0 --to {rewardsWallet} --to-shard 0 --gas-price 100 {environ.get('PASS_SWITCH')}"
    )


def rewardsCollector() -> None:
    rewardsWallet = environ.get("REWARDS_WALLET")
    print_stars()
    print("* Harmony ONE Rewards Collection")
    print_stars()
    question = ask_yes_no(
        f"*\n* For your validator wallet {environ.get('VALIDATOR_WALLET')}\n* You have {get_rewards_balance(easy_env.rpc_endpoints, environ.get('VALIDATOR_WALLET'))} $ONE pending.\n* Would you like to collect your rewards on the Harmony mainnet? (YES/NO) "
    )
    if question:
        collectRewards(f"{environ.get('NETWORK_0_CALL')}")
        print_stars()
        print(
            Fore.GREEN
            + f"* mainnet rewards for {environ.get('VALIDATOR_WALLET')} have been collected."
            + Style.RESET_ALL
        )
        print_stars()
    else:
        return
    if rewardsWallet:
        wallet_balance, wallet_balance_test = get_wallet_balance(environ.get("VALIDATOR_WALLET"))
        suggestedSend = wallet_balance - int(environ.get("GAS_RESERVE"))
        print("*\n*\n")
        print_stars()
        print("\n* Send your Harmony ONE Rewards?")
        print_stars()
        if suggestedSend >= 1:
            question = ask_yes_no(
                f"* You have {wallet_balance} $ONE available to send. We suggest sending {suggestedSend} $ONE using your reservation settings.\n* Would you like to send {suggestedSend} $ONE to {rewardsWallet} now? (YES/NO)"
            )
            if question:
                sendRewards(environ.get("NETWORK_0_CALL"), suggestedSend, rewardsWallet)
            return
    return


def menuTopperRegular() -> None:
    # Get stats & balances
    Load1, Load5, Load15 = os.getloadavg()
    sign_percentage = get_sign_pct()
    total_balance, total_balance_test = get_wallet_balance(environ.get("VALIDATOR_WALLET"))
    remote_data_shard_0, local_data_shard, remote_data_shard = menuValidatorStats()
    os.system("clear")
    # Print Menu
    print_stars()
    print(f'{Style.RESET_ALL}* {Fore.GREEN}validator-toolbox for Harmony ONE Validators by Easy Node   v{easy_env.easy_version}{Style.RESET_ALL}   https://easynode.pro *')
    print_stars()
    print(f'* Your validator wallet address is: {Fore.RED}{str(environ.get("VALIDATOR_WALLET"))}{Style.RESET_ALL}\n* Your $ONE balance is:             {Fore.GREEN}{str(total_balance)}{Style.RESET_ALL}\n* Your pending $ONE rewards are:    {Fore.GREEN}{str(get_rewards_balance(easy_env.rpc_endpoints, environ.get("VALIDATOR_WALLET")))}{Style.RESET_ALL}\n* Server Hostname & IP:             {easy_env.server_host_name}{Style.RESET_ALL} - {Fore.YELLOW}{easy_env.external_ip}{Style.RESET_ALL}')
    harmonyServiceStatus()
    print(f'* Epoch Signing Percentage:         {Style.BRIGHT}{Fore.GREEN}{Back.BLUE}{sign_percentage} %{Style.RESET_ALL}\n* Current disk space free: {Fore.CYAN}{free_space_check(easy_env.harmony_dir): >6}{Style.RESET_ALL}\n* Current harmony version: {Fore.YELLOW}{environ.get("HARMONY_VERSION")}{Style.RESET_ALL}, has upgrade available: {environ.get("HARMONY_UPGRADE_AVAILABLE")}\n* Current hmy version: {Fore.YELLOW}{environ.get("HMY_VERSION")}{Style.RESET_ALL}, has upgrade available: {environ.get("HMY_UPGRADE_AVAILABLE")}')
    print_stars()
    if environ.get("SHARD") != "0":
        print(f"\n* Note: Running on shard {environ.get('SHARD')}, Shard 0 is no longer needed locally and should be under 200MB\n* Remote Shard 0 Epoch: {remote_data_shard_0['result']['shard-chain-header']['epoch']}, Current Block: {literal_eval(remote_data_shard_0['result']['shard-chain-header']['number'])}, Local Shard 0 Size: {getDBSize('0')}")
        print(f"* Remote Shard {environ.get('SHARD')} Epoch: {remote_data_shard['result']['shard-chain-header']['epoch']}, Current Block: {literal_eval(remote_data_shard['result']['shard-chain-header']['number'])}")
        print(f"*  Local Shard {environ.get('SHARD')} Epoch: {local_data_shard['result']['shard-chain-header']['epoch']}, Current Block: {literal_eval(local_data_shard['result']['shard-chain-header']['number'])}, Local Shard {environ.get('SHARD')} Size: {getDBSize(environ.get('SHARD'))}")
    if environ.get("SHARD") == "0":
        print(f"* Remote Shard {environ.get('SHARD')} Epoch: {remote_data_shard_0['result']['shard-chain-header']['epoch']}, Current Block: {literal_eval(remote_data_shard_0['result']['shard-chain-header']['number'])}")
        print(f"*  Local Shard {environ.get('SHARD')} Epoch: {local_data_shard['result']['shard-chain-header']['epoch']}, Current Block: {literal_eval(local_data_shard['result']['shard-chain-header']['number'])}")
    print(f"* CPU Load Averages: {round(Load1, 2)} over 1 min, {round(Load5, 2)} over 5 min, {round(Load15, 2)} over 15 min")
    print_stars()

def menuTopperFull() -> None:
    Load1, Load5, Load15 = os.getloadavg()
    remote_data_shard_0, local_data_shard, remote_data_shard = menuValidatorStats()
    os.system("clear")
    # Print Menu
    print_stars()
    print(f'{Style.RESET_ALL}* {Fore.GREEN}validator-toolbox for Harmony ONE Validators by Easy Node   v{str(environ.get("EASY_VERSION"))}{Style.RESET_ALL}   https://easynode.one *')
    print_stars()
    print(f'* Server Hostname & IP:             {easy_env.server_host_name}{Style.RESET_ALL} - {Fore.YELLOW}{easy_env.external_ip}{Style.RESET_ALL}')
    harmonyServiceStatus()
    print(f'* Current disk space free: {Fore.CYAN}{free_space_check(easy_env.harmony_dir): >6}{Style.RESET_ALL}{Style.RESET_ALL}\n* Current harmony version: {Fore.YELLOW}{environ.get("HARMONY_VERSION")}{Style.RESET_ALL}, has upgrade available: {environ.get("HARMONY_UPGRADE_AVAILABLE")}\n* Current hmy version: {Fore.YELLOW}{environ.get("HMY_VERSION")}{Style.RESET_ALL}, has upgrade available: {environ.get("HMY_UPGRADE_AVAILABLE")}')
    print(f"* Remote Shard {environ.get('SHARD')} Epoch: {remote_data_shard_0['result']['shard-chain-header']['epoch']}, Current Block: {literal_eval(remote_data_shard_0['result']['shard-chain-header']['number'])}")
    print(f"*  Local Shard {environ.get('SHARD')} Epoch: {local_data_shard['result']['shard-chain-header']['epoch']}, Current Block: {literal_eval(local_data_shard['result']['shard-chain-header']['number'])}")
    print(f"* CPU Load Averages: {round(Load1, 2)} over 1 min, {round(Load5, 2)} over 5 min, {round(Load15, 2)} over 15 min")
    print_stars_reset()


def menuRegular() -> None:
    menuTopperRegular()
    for x in return_txt(easy_env.main_menu_regular):
        x = x.strip()
        try:
            x = eval(x)
        except SyntaxError:
            pass
        if x:
            print(x)


def menuFull() -> None:
    menuTopperFull()
    for x in return_txt(easy_env.main_menu_full):
        x = x.strip()
        try:
            x = eval(x)
        except SyntaxError:
            pass
        if x:
            print(x)


def getWalletJSON(wallet: str) -> str:
    testOrMain = environ.get("NETWORK")
    try:
        response = requests.get(f"https://api.stake.hmny.io/networks/{testOrMain}/validators/{wallet}")
        response.raise_for_status()
        # access JSOn content
        jsonResponse = response.json()
    #        print("Entire JSON response")
    #        print(jsonResponse)
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
    return jsonResponse


def tmiServerInfo() -> None:
    validator_wallet = environ.get("VALIDATOR_WALLET")
    jsonResponse = getWalletJSON(validator_wallet)
    for key, value in jsonResponse.items():
        print(key, ":", value)
    print_stars_reset()
    input("Press ENTER to return to the main menu.")


def setRewardsWallet() -> None:
    rewardsWallet = environ.get("REWARDS_WALLET")
    gasReserve = environ.get("GAS_RESERVE")
    if rewardsWallet is None:
        question = ask_yes_no("* Would you like to add an address to send your rewards too? (YES/NO)")
        if question:
            rewardsWallet = input(f"* Input your one1 address to send rewards into, please input your address now: ")
            if rewardsWallet.startswith("one1"):
                set_var(easy_env.dotenv_file, "REWARDS_WALLET", rewardsWallet)
            else:
                print("* Wallet does not start with one1, please try again.")
                return
        return
    else:
        question = ask_yes_no(
            f"* Your current saved rewards wallet address is {rewardsWallet}\n* Would you like to update the address you send your rewards too? (YES/NO)"
        )
        if question:
            rewardsWallet = input(f"* Input your one1 address to send rewards into, please input your address now: ")
            if rewardsWallet.startswith("one1"):
                set_var(easy_env.dotenv_file, "REWARDS_WALLET", rewardsWallet)
            else:
                print("* Wallet does not start with one1, please try again.")
                return
            setGasReserve()
            return
        else:
            question = ask_yes_no(
                f"* Your current wallet gas reservation is {gasReserve} $ONE\n* Would you like to update your reservation total? (YES/NO)"
            )
            if question:
                setGasReserve()
                return
    return


def setGasReserve() -> None:
    gasReserve = environ.get("GAS_RESERVE")
    question = ask_yes_no(
        f"* Your current total of $ONE to reserve for fees is {gasReserve}\n* Would you like to update the reserve total? (YES/NO)"
    )
    if question:
        askReserveTotal()
    return


def askReserveTotal() -> None:
    reserveTotal = input("* How much $ONE would you like to keep reserved for fees? ")
    setReserveTotal(reserveTotal)
    return


def setReserveTotal(reserveTotal):
    set_var(easy_env.dotenv_file, "GAS_RESERVE", reserveTotal)


def runFullNode() -> None:
    menu_options = {
        # 0: finish_node,
        1: refreshStats,
        2: menuCheckBalance,
        3: comingSoon,
        4: comingSoon,
        5: comingSoon,
        6: comingSoon,
        7: setRewardsWallet,
        8: menuServiceStopStart,
        9: menuServiceRestart,
        10: menuBinaryUpdates,
        11: hmyCLIUpgrade,
        12: menuUbuntuUpdates,
        13: server_drive_check,
        14: comingSoon,
        15: allSysInfo,
        999: menuRebootServer,
    }
    while True:
        load_var_file()
        menuFull()
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
            menuError()
            runFullNode(environ.get("NODE_TYPE"))
        if option == 0:
            return finish_node()
        os.system("clear")
        menu_options[option]()


def bingoChecker():
    os.system("grep BINGO ~/harmony/latest/zerolog-harmony.log | tail -10")
    input("* Press enter to return to the main menu.")


def comingSoon():
    os.system("clear")
    print_whitespace()
    print_stars()
    print("* This option isn't available on your system, yet!")
    print_stars()
    input("* Press enter to return to the main menu.")


def runRegularNode() -> None:
    menu_options = {
        # 0: finish_node,
        1: refreshStats,
        2: menuActiveBLS,
        3: menuCheckBalance,
        4: rewardsCollector,
        5: bingoChecker,
        6: comingSoon,
        7: setRewardsWallet,
        8: menuServiceStopStart,
        9: menuServiceRestart,
        10: menuBinaryUpdates,
        11: hmyCLIUpgrade,
        12: menuUbuntuUpdates,
        13: server_drive_check,
        14: tmiServerInfo,
        15: allSysInfo,
        999: menuRebootServer,
    }
    while True:
        load_var_file()
        menuRegular()
        if environ.get("HARMONY_UPGRADE_AVAILABLE") == "True":
            print(
                f'* The harmony binary has an update available to version {environ.get("ONLINE_HARMONY_VERSION")}\n* Option #10 will upgrade you, but you may miss a block while it upgrades & restarts.\n* Currently installed version {environ.get("HARMONY_VERSION")}\n'
            )
            print_stars()
        if environ.get("HMY_UPGRADE_AVAILABLE") == "True":
            print(
                f'* The hmy binary has an update available to version {environ.get("ONLINE_HMY_VERSION")}\n* Option #11 will upgrade you.\n* Currently installed version {environ.get("HMY_VERSION")}\n'
            )
            print_stars()
        try:
            option = int(input("Enter your option: "))
        except ValueError:
            menuError()
            refreshStats(1)
            runRegularNode()
        if option == 0:
            return finish_node()
        os.system("clear")
        menu_options[option]()


def menuError() -> None:
    os.system("clear")
    print_stars_reset()
    print(
        "* "
        + Fore.RED
        + "WARNING"
        + Style.RESET_ALL
        + ": Only numbers are possible, please try your selection on the main menu once again."
    )
    return


def osUpgrades() -> None:
    print_stars()
    upgrades = (
        "sudo apt update",
        "sudo apt upgrade -y",
        "sudo apt dist-upgrade -y",
        "sudo apt autoremove -y",
    )
    for x in upgrades:
        process_command(x)
    print_stars()


def harmonyServiceStatus() -> None:
    status = subprocess.call(["systemctl", "is-active", "--quiet", "harmony"])
    if status == 0:
        print("* Harmony Service is:               " + Fore.BLACK + Back.GREEN + "   Online  " + Style.RESET_ALL)
    else:
        print("* Harmony Service is:               " + Fore.WHITE + Back.RED + "  *** Offline *** " + Style.RESET_ALL)


def serviceMenuOption() -> None:
    status = os.system("systemctl is-active --quiet harmony")
    if status == 0:
        print(f'*   8 - {Fore.RED}Stop Harmony Service      {Fore.GREEN}- {Fore.YELLOW}{Back.RED}WARNING: You will miss blocks while stopped!   {Style.RESET_ALL}')
        print(f'*   9 - Restart Harmony Service   - {Back.RED}{Fore.YELLOW}WARNING: You will miss blocks during a restart!{Style.RESET_ALL}')
    else:
        print(f'*   8 - {Fore.GREEN}Start Harmony Service{Style.RESET_ALL}')


def makeBackupDir() -> str:
    if not os.path.isdir(f"{easy_env.harmony_dir}/harmony_backup"):
        print_stars_reset()
        print("Backup directory not found, creating folder")
        os.system(f"mkdir -p {easy_env.harmony_dir}/harmony_backup")


def hmyCLIUpgrade():
    print_stars_reset()
    question = ask_yes_no(
        "Are you sure you would like to proceed with updating the Harmony CLI file?\n\nType 'Yes' or 'No' to continue"
    )
    if question:
        os.chdir(f"{easy_env.harmony_dir}")
        makeBackupDir()
        os.system(f"cp {easy_env.hmy_app} {easy_env.harmony_dir}/harmony_backup")
        print_stars()
        install_hmy(easy_env.harmony_dir)
        print_stars()
        print("Harmony cli has been updated to: ")
        os.system(f"{easy_env.hmy_app} version")
        print_stars()
        set_var(easy_env.dotenv_file, "HMY_UPGRADE_AVAILABLE", "False")
        input("Update completed, press ENTER to return to the main menu. ")


def upgradeHarmonyApp(testOrMain):
    os.chdir(f"{easy_env.harmony_dir}")
    print_stars_reset()
    print("Currently installed version: ")
    os.system("./harmony -V")
    makeBackupDir()
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

def menuValidatorStats():
    load_var_file()
    remote_shard_0 = [
        f"{easy_env.hmy_app}",
        "blockchain",
        "latest-headers",
        f'--node=https://api.s0.{environ.get("NETWORK_SWITCH")}.hmny.io',
    ]
    result_remote_shard_0 = run(remote_shard_0, stdout=PIPE, stderr=PIPE, universal_newlines=True)
    remote_data_shard_0 = json.loads(result_remote_shard_0.stdout)
    local_shard = [f"{easy_env.hmy_app}", "blockchain", "latest-headers"]
    result_local_shard = run(local_shard, stdout=PIPE, stderr=PIPE, universal_newlines=True)
    local_data_shard = json.loads(result_local_shard.stdout)
            
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


def refreshStats(clear=0) -> str:
    if clear == 0:
        os.system("clear")
    print_stars()
    print(f'* Getting the latest local & blockchain information now, one moment while we load...')
    print_stars()
    return


def getDBSize(ourShard) -> str:
    harmonyDBSize = subprocess.getoutput(f"du -h {easy_env.harmony_dir}/harmony_db_{ourShard}")
    harmonyDBSize = harmonyDBSize.rstrip("\t")
    countTrim = len(easy_env.harmony_dir) + 13
    return harmonyDBSize[:-countTrim]


def shardStats(ourShard) -> str:
    ourUptime = subprocess.getoutput("uptime")
    ourVersion = subprocess.getoutput(f"{easy_env.harmony_app} -V")
    dbZeroSize = getDBSize("0")
    if ourShard == "0":
        print(
            f"""
    * Uptime :: {ourUptime}\n\n Harmony DB 0 Size  ::  {dbZeroSize}
    * {ourVersion}
    {string_stars()}
        """
        )
    else:
        print(
            f"""
    * Uptime :: {ourUptime}
    *
    * Harmony DB 0 Size  ::  {dbZeroSize}
    * Harmony DB {ourShard} Size  ::   {getDBSize(str(ourShard))}
    *
    * {ourVersion}
    *
    {string_stars()}
        """
        )


def menuBinaryUpdates():
    testOrMain = environ.get("NETWORK")
    print_stars_reset()
    question = ask_yes_no(
        Fore.RED
        + "WARNING: YOU WILL MISS BLOCKS WHILE YOU UPGRADE THE HARMONY SERVICE.\n\n"
        + Fore.WHITE
        + "Are you sure you would like to proceed?\n\nType 'Yes' or 'No' to continue"
    )
    if question:
        upgradeHarmonyApp(testOrMain)


def menuUbuntuUpdates() -> str:
    print_stars_reset()
    question = ask_yes_no(
        Fore.WHITE + "Are you sure you would like to proceed with Linux apt Upgrades?\n\nType 'Yes' or 'No' to continue"
    )
    if question:
        osUpgrades()
        print()
        input("OS Updates completed, press ENTER to return to the main menu. ")


def menuRebootServer() -> str:
    print_stars_reset()
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


def menuServiceStopStart() -> str:
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


def menuServiceRestart() -> str:
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


def menuActiveBLS() -> str:
    validator_wallet = environ.get("VALIDATOR_WALLET")
    jsonResponse = getWalletJSON(validator_wallet)
    print_stars_reset()
    print("* This is a list of your BLS Keys that are active for the next election.")
    for i, x in enumerate(jsonResponse["bls-public-keys"]):
        print(f"BLS Key {i+1} {x}")
    print_stars()
    input("Press ENTER to return to the main menu.")


def isfloat(value):
    try:
        float(value)
        return True
    except ValueError:
        return False


def menuCheckBalance() -> None:
    validator_wallet = environ.get("VALIDATOR_WALLET")
    if environ.get("NODE_TYPE") == "regular":
        print_stars_reset()
        print("* Calling mainnet and testnet for balances...")
        print_stars()
        total_balance, total_balance_test = get_wallet_balance(validator_wallet)
        print(f"* Your Validator Wallet Balance on Mainnet is: {total_balance} Harmony ONE Coins")
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
    print_stars_reset()
    checkWallet = input(
        "* Type the address of the Harmony ONE Wallet you would like to check.\n"
        + "* Only one wallets will work, no 0x addresses : "
    )
    print("* Calling mainnet and testnet for balances...")
    print_stars_reset()
    total_balance, total_balance_test = get_wallet_balance(checkWallet)
    print(
        f"* The Mainnet Wallet Balance is: {total_balance} Harmony ONE Coins\n* The Testnet Wallet Balance is: {total_balance_test} Harmony ONE Test Coins"
    )
    print_stars()
    input("Press ENTER to continue.")


def getCurrentEpoch():
    if environ.get("NETWORK") == "mainnet":
        endpoints_count = len(easy_env.rpc_endpoints)
    if environ.get("NETWORK") == "testnet":
        endpoints_count = len(easy_env.rpc_endpoints_test)

    for i in range(endpoints_count):
        current_epoch = getCurrentEpochByEndpoint(easy_env.rpc_endpoints[i])

        if current_epoch != -1:
            return current_epoch
    current_epoch = 0
    return current_epoch


def getCurrentEpochByEndpoint(endpoint):
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


def finish_node():
    print_stars()
    print("* Thanks for using Easy Node - EZ Mode! Goodbye.")
    print_stars()
    raise SystemExit(0)
