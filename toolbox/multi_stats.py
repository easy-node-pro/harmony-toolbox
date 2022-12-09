import os
from os import environ
from utils.config import validatorToolbox
from utils.library import loadVarFile, getSignPercent, getWalletBalance, printStars, setVar
from utils.toolbox import menuTopperRegular, freeSpaceCheck
from subprocess import PIPE, run

loadVarFile()

if not environ.get("VALIDATOR_WALLET"):
    # ask for wallet, save to env.
    address = input(f'No Harmony $ONE address found, please input a one1 or 0x address: ')
    address2 = input(f'Please re-enter your address to verify: ')
    if address == address2:
        setVar(validatorToolbox.dot_env, "VALIDATOR_WALLET", address2)

def menuTopperRegular() -> None:
    # Get stats & balances
    Load1, Load5, Load15 = os.getloadavg()
    sign_percentage = getSignPercent()
    total_balance, total_balance_test = getWalletBalance(environ.get("VALIDATOR_WALLET"))
    remote_data_shard_0, local_data_shard, remote_data_shard = menuValidatorStats()
    os.system("clear")
    # Print Menu
    printStars()
    print(f'{Style.RESET_ALL}* {Fore.GREEN}validator-toolbox for Harmony ONE Validators by Easy Node   v{validatorToolbox.easyVersion}{Style.RESET_ALL}   https://easynode.one *')
    printStars()
    print(f'* Your validator wallet address is: {Fore.RED}{str(environ.get("VALIDATOR_WALLET"))}{Style.RESET_ALL}\n* Your $ONE balance is:             {Fore.GREEN}{str(total_balance)}{Style.RESET_ALL}\n* Your pending $ONE rewards are:    {Fore.GREEN}{str(getRewardsBalance(validatorToolbox.rpc_endpoints, environ.get("VALIDATOR_WALLET")))}{Style.RESET_ALL}\n* Server Hostname & IP:             {validatorToolbox.serverHostName}{Style.RESET_ALL} - {Fore.YELLOW}{validatorToolbox.ourExternalIPAddress}{Style.RESET_ALL}')
    harmonyServiceStatus()
    print(f'* Epoch Signing Percentage:         {Style.BRIGHT}{Fore.GREEN}{Back.BLUE}{sign_percentage} %{Style.RESET_ALL}\n* Current disk space free: {Fore.CYAN}{freeSpaceCheck(): >6}{Style.RESET_ALL}\n* Current harmony version: {Fore.YELLOW}{environ.get("HARMONY_VERSION")}{Style.RESET_ALL}, has upgrade available: {environ.get("HARMONY_UPGRADE_AVAILABLE")}\n* Current hmy version: {Fore.YELLOW}{environ.get("HMY_VERSION")}{Style.RESET_ALL}, has upgrade available: {environ.get("HMY_UPGRADE_AVAILABLE")}')
    printStars()
    if environ.get("SHARD") != "0":
        print(f"\n* Note: Running on shard {environ.get('SHARD')}, Shard 0 is no longer needed locally and should be under 200MB\n* Remote Shard 0 Epoch: {remote_data_shard_0['result']['shard-chain-header']['epoch']}, Current Block: {literal_eval(remote_data_shard_0['result']['shard-chain-header']['number'])}, Local Shard 0 Size: {getDBSize('0')}")
        print(f"* Remote Shard {environ.get('SHARD')} Epoch: {remote_data_shard['result']['shard-chain-header']['epoch']}, Current Block: {literal_eval(remote_data_shard['result']['shard-chain-header']['number'])}")
        print(f"*  Local Shard {environ.get('SHARD')} Epoch: {local_data_shard['result']['shard-chain-header']['epoch']}, Current Block: {literal_eval(local_data_shard['result']['shard-chain-header']['number'])}, Local Shard {environ.get('SHARD')} Size: {getDBSize(environ.get('SHARD'))}")
    if environ.get("SHARD") == "0":
        print(f"* Remote Shard {environ.get('SHARD')} Epoch: {remote_data_shard_0['result']['shard-chain-header']['epoch']}, Current Block: {literal_eval(remote_data_shard_0['result']['shard-chain-header']['number'])}")
        print(f"*  Local Shard {environ.get('SHARD')} Epoch: {local_data_shard['result']['shard-chain-header']['epoch']}, Current Block: {literal_eval(local_data_shard['result']['shard-chain-header']['number'])}")
    print(f"* CPU Load Averages: {round(Load1, 2)} over 1 min, {round(Load5, 2)} over 5 min, {round(Load15, 2)} over 15 min")
    printStars()

    def menuValidatorStats():
    loadVarFile()
    remote_shard_0 = [
        f"{validatorToolbox.hmyAppPath}",
        "blockchain",
        "latest-headers",
        f'--node=https://api.s0.{environ.get("NETWORK_SWITCH")}.hmny.io',
    ]
    result_remote_shard_0 = run(remote_shard_0, stdout=PIPE, stderr=PIPE, universal_newlines=True)
    remote_data_shard_0 = json.loads(result_remote_shard_0.stdout)
    local_shard = [f"{validatorToolbox.hmyAppPath}", "blockchain", "latest-headers"]
    result_local_shard = run(local_shard, stdout=PIPE, stderr=PIPE, universal_newlines=True)
    local_data_shard = json.loads(result_local_shard.stdout)
            
    if environ.get("SHARD") != "0":
        remote_shard = [
            f"{validatorToolbox.hmyAppPath}",
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

if __name__ == "__main__":
    menuValidatorStats()
    