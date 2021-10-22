import os
import dotenv
import subprocess
import requests
import pyhmy
from utils.config import validatorToolbox
from os import environ
from dotenv import load_dotenv
from simple_term_menu import TerminalMenu
from colorama import Style
from pathlib import Path
from pyhmy import validator, account, staking, numbers


def loaderIntro():
    printStars()
    print(" ____ ____ ____ ____ _________ ____ ____ ____ ____           ")
    print("||E |||a |||s |||y |||       |||N |||o |||d |||e ||          ")
    print("||__|||__|||__|||__|||_______|||__|||__|||__|||__||          ")
    print("|/__\|/__\|/__\|/__\|/_______\|/__\|/__\|/__\|/__\|          ")
    print(" ____ ____ ____ ____ ____ ____ ____ _________ ____ ____ ____ ")
    print("||H |||a |||r |||m |||o |||n |||y |||       |||O |||N |||E ||")
    print("||__|||__|||__|||__|||__|||__|||__|||_______|||__|||__|||__||")
    print("|/__\|/__\|/__\|/__\|/__\|/__\|/__\|/_______\|/__\|/__\|/__\|")
    print(" ____ ____ ____ ____ ____ ____ ____ ____ ____                ")
    print("||v |||a |||l |||i |||d |||a |||t |||o |||r ||               ")
    print("||__|||__|||__|||__|||__|||__|||__|||__|||__||               ")
    print("|/__\|/__\|/__\|/__\|/__\|/__\|/__\|/__\|/__\|               ")
    print(" ____ ____ ____ ____ ____ ____ ____                          ")
    print("||T |||o |||o |||l |||b |||o |||x ||                         ")
    print("||__|||__|||__|||__|||__|||__|||__||                         ")
    print("|/__\|/__\|/__\|/__\|/__\|/__\|/__\|                         ")
    printStars()


def installHmyApp(harmonyDirPath):
    os.chdir(f"{harmonyDirPath}")
    os.system("curl -LO https://harmony.one/hmycli && mv hmycli hmy && chmod +x hmy")
    printStars()
    print("* hmy application installed.")


def updateHarmonyConf(fileName, originalText, newText):
    f = open(fileName,'r')
    filedata = f.read()
    f.close()

    newdata = filedata.replace(originalText, newText)

    f = open(fileName,'w')
    f.write(newdata)
    f.close()
    return


def installHarmonyApp(harmonyDirPath, blsKeyFile):
    os.chdir(f"{harmonyDirPath}")
    if environ.get("NETWORK") == "testnet":
        os.system("curl -LO https://harmony.one/binary_testnet && mv binary_testnet harmony && chmod +x harmony")
        os.system("./harmony config dump --network testnet harmony.conf")
        updateHarmonyConf(validatorToolbox.harmonyConfPath, "MaxKeys = 10", "MaxKeys = 30")
    if environ.get("NETWORK") == "mainnet":
        os.system("curl -LO https://harmony.one/binary && mv binary harmony && chmod +x harmony")
        os.system("./harmony config dump harmony.conf")
        updateHarmonyConf(validatorToolbox.harmonyConfPath, "MaxKeys = 10", "MaxKeys = 30")
    printStars()
    print("* harmony.conf MaxKeys modified to 30")
    # when we setup rasppi as an option, this is the install command for harmony
    if environ.get("ARC") == "arm64":
        if environ.get("NETWORK") == "testnet":
            # no current testnet know for arm64, break for now
            print("No known testnet for R Pi at this time, try mainnet")
            raise SystemExit(0)
        else:
            os.system("curl -LO https://harmony.one/binary-arm64 && mv binary-arm64 harmony && chmod +x harmony")
            os.system("./harmony config dump harmony.conf")
    if os.path.exists(blsKeyFile):
        updateHarmonyConf(validatorToolbox.harmonyConfPath, "PassFile = \"\"", f"PassFile = \"blskey.pass\"")
        print("* blskey.pass found, updated harmony.conf")
    printStars()
    print(f"* Harmony {environ.get('NETWORK')} application installed & ~/harmony/harmony.conf created.")


def setWalletEnv():
    if environ.get("NODE_WALLET") == "true":
        if not environ.get("VALIDATOR_WALLET"):
            output = subprocess.getoutput(f"{validatorToolbox.hmyAppPath} keys list | grep {validatorToolbox.activeUserName}")
            outputStripped = output.lstrip(validatorToolbox.activeUserName)
            outputStripped = outputStripped.strip()
            dotenv.unset_key(validatorToolbox.dotenv_file, "VALIDATOR_WALLET")
            dotenv.set_key(validatorToolbox.dotenv_file, "VALIDATOR_WALLET", outputStripped)
            return outputStripped
        else:
            loadVarFile()
            validatorWallet = environ.get("VALIDATOR_WALLET")
            return validatorWallet


def recoveryType():
    loadVarFile()
    os.system("clear")
    dotenv.set_key(validatorToolbox.dotenv_file, "NODE_WALLET", "true")
    passphraseStatus()
    passphraseSwitch = environ.get("PASS_SWITCH")
    printStars()
    print("* Wallet Recovery Type!                                                                     *")
    printStars()
    print("* [0] = Mnemonic phrase recovery (aka seed phrase)                                          *")
    print("* [1] = Private Key recovery                                                                *")
    printStars()
    menuOptions = ["[0] - Mnemonic Phrase Recovery", "[1] - Private Key Recovery", ]
    terminal_menu = TerminalMenu(menuOptions, title="* Which type of restore method would you like to use for your validator wallet?")
    results = terminal_menu.show()
    if results == 0:
        # Mnemonic Recovery Here
        os.system(f"{validatorToolbox.hmyAppPath} keys recover-from-mnemonic {validatorToolbox.activeUserName} {passphraseSwitch}")
        printStars()
        setWalletEnv()
        return
    if results == 1:
        # Private Key Recovery Here
        print("* Private key recovery requires your private information in the command itself.")
        private = input("* Please enter your private key to restore your wallet: ")
        os.system(f"{validatorToolbox.hmyAppPath} keys import-private-key {private} {validatorToolbox.activeUserName} --passphrase")
        printStars()
        setWalletEnv()
        return


def passphraseStatus():
    loadVarFile()
    if environ.get("NODE_WALLET") == "true":
        passphraseSet()
        dotenv.unset_key(validatorToolbox.dotenv_file, "PASS_SWITCH")
        dotenv.set_key(validatorToolbox.dotenv_file, "PASS_SWITCH",
                       f"--passphrase-file {validatorToolbox.harmonyDirPath}/passphrase.txt")
    if environ.get("NODE_WALLET") == "false":
        dotenv.unset_key(validatorToolbox.dotenv_file, "PASS_SWITCH")
        dotenv.set_key(validatorToolbox.dotenv_file, "PASS_SWITCH", "--passphrase")
    loadVarFile()
    return


def passphraseSet():
    if os.path.exists(validatorToolbox.passwordPath):
        return
    import getpass
    os.system("clear")
    printStars()
    print("* Setup ~/harmony/passphrase.txt file for use with autobidder & validatortoolbox.")
    printStars()
    # take input
    while True:
        print("* ")
        password1 = getpass.getpass(
            prompt="* Please set a wallet password for this node\n* Enter your password now: ", stream=None)
        password2 = getpass.getpass(
            prompt="* Re-enter your password: ", stream=None
        )
        if not password1 == password2:
            print("* Passwords do NOT match, Please try again..")
        else:
            print("* Passwords Match!")
            break
    # Save file, we won't encrypt because if someone has access to the file, they will also have the salt and decrypt code at their disposal.
    save_text(validatorToolbox.passwordPath, password1)
    loadVarFile()
    passphraseStatus()
    return


def process_command(command: str) -> None:
    process = subprocess.Popen(command, shell=True)
    output, error = process.communicate()


def printStars() -> str:
    print(
        "*********************************************************************************************"
    )
    return


def printStarsReset() -> str:
    print(
        "*********************************************************************************************"
        + Style.RESET_ALL
    )
    return


def printWhiteSpace() -> str:
    print()
    print()
    print()
    print()
    print()
    print()
    print()
    print()


def askYesNo(question: str) -> bool:
    YesNoAnswer = ""
    while not YesNoAnswer.startswith(("Y", "N")):
        YesNoAnswer = input(f"{question}: ").upper()
    if YesNoAnswer.startswith("Y"):
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


def loadVarFile():
    if os.path.exists(validatorToolbox.dotenv_file) == True:
        load_dotenv(validatorToolbox.dotenv_file)
        return


def firstRunMenu():
    os.system("clear")
    printStars()
    print("* First run detected!                                                                       *")
    printStars()
    print("* [0] = Install Harmony Validator Software - For Brand NEW SERVERS ONLY                     *")
    print("* [1] = Load Validator Toolbox Menu App    - For servers already running harmony validator  *")
    printStars()
    menuOptions = ["[0] - Install Harmony Validator Software", "[1] - Load Validator Toolbox Menu Setup", ]
    terminal_menu = TerminalMenu(menuOptions, title="* Is this a new server or an already existing harmony node?")
    setupStatus = str(terminal_menu.show())
    dotenv.unset_key(validatorToolbox.dotenv_file, "SETUP_STATUS", setupStatus)
    dotenv.set_key(validatorToolbox.dotenv_file, "SETUP_STATUS", setupStatus)
    return



def getShardMenu(dotenv_file) -> None:
    if environ.get("SHARD") is None:
        os.system("clear")
        printStars()
        print("* First Boot - Gathering more information about your server                                 *")
        printStars()
        print("* Which shard do you want this node run on?                                                 *")
        printStars()
        menuOptions = ["[0] - Shard 0", "[1] - Shard 1", "[2] - Shard 2", "[3] - Shard 3", ]
        terminal_menu = TerminalMenu(menuOptions, title="* Which Shard will this node operate on? ")
        ourShard = str(terminal_menu.show())
        dotenv.set_key(dotenv_file, "SHARD", ourShard)
        return ourShard


def getNodeType(dotenv_file) -> None:
    if not os.path.exists(validatorToolbox.hmyWalletStorePath):
        if environ.get("NODE_TYPE") == None:
            os.system("clear")
            printStars()
            print("* Which type of node would you like to run on this server?                                  *")
            printStars()
            print("* [0] - Standard w/ Wallet - Harmony Validator Signing Node with Wallet                     *")
            print("* [1] - Standard No Wallet - Harmony Validator Signing Node no Wallet                       *")
            print("* [2] - Full Node Dev/RPC - Non Validating Harmony Node                                     *")
            printStars()
            menuOptions = ["[0] Signing Node w/ Wallet", "[1] Signing Node No Wallet", "[2] Full Node Non Validating Dev/RPC", ]
            terminal_menu = TerminalMenu(menuOptions, title="Regular or Full Node Server")
            results = terminal_menu.show()
            if results == 0:
                dotenv.set_key(dotenv_file, "NODE_TYPE", "regular")
                dotenv.set_key(dotenv_file, "NODE_WALLET", "true")
            if results == 1:
                dotenv.set_key(dotenv_file, "NODE_TYPE", "regular")
                dotenv.set_key(dotenv_file, "NODE_WALLET", "false")
            if results == 2:
                dotenv.set_key(dotenv_file, "NODE_TYPE", "full")
            os.system("clear")
            return
        setWalletEnv()
    if not environ.get("NODE_TYPE"):
        dotenv.set_key(dotenv_file, "NODE_TYPE", "regular")
    if not environ.get("NODE_WALLET"):
        dotenv.set_key(dotenv_file, "NODE_WALLET", "true")
    return


def setMainOrTest(dotenv_file) -> None:
    if environ.get("NETWORK") is None:
        os.system("clear")
        printStars()
        print("* Setup config not found, which blockchain does this node run on?                           *")
        printStars()
        print("* [0] - Mainnet                                                                             *")
        print("* [1] - Testnet                                                                             *")
        printStars()
        menuOptions = ["[0] Mainnet", "[1] Testnet", ]
        terminal_menu = TerminalMenu(menuOptions, title="Mainnet or Testnet")
        results = terminal_menu.show()
        if results == 0:
            dotenv.set_key(dotenv_file, "NETWORK", "mainnet")
            dotenv.set_key(dotenv_file, "NETWORK_SWITCH", "t")
            dotenv.set_key(dotenv_file, "RPC_NET", "https://rpc.s0.t.hmny.io")
        if results == 1:
            dotenv.set_key(dotenv_file, "NETWORK", "testnet")
            dotenv.set_key(dotenv_file, "NETWORK_SWITCH", "b")
            dotenv.set_key(dotenv_file, "RPC_NET", "https://rpc.s0.b.hmny.io")
        os.system("clear")
        loadVarFile()
        return 


def getExpressStatus(dotenv_file) -> None:
    if environ.get("SETUP_STATUS") == "0":
        os.system("clear")
        printStars()
        print("* Express or Manual Setup?                                                                  *")
        printStars()
        print("* Would you like the turbo express setup or Manual approval of each step?                   *")
        printStars()
        menuOptions = ["[0] - Express Install", "[1] - Manual Approval", ]
        terminal_menu = TerminalMenu(menuOptions, title="* Express Or Manual Setup")
        dotenv.set_key(dotenv_file, "EXPRESS", str(terminal_menu.show()))
    return


def getWalletAddress():
    os.system("clear")
    printStars()
    print("* Signing Node, No Wallet!                                                                  *")
    print("* You are attempting to launch the menu but no wallet has been loaded, as you chose         *")
    print("* If you would like to use the menu on the server, complete the following:                  *")
    printStars()
    print("* Edit ~/.easynode.env and add your wallet address on a new line like this example:         *")
    print("* VALIDATOR_WALLET='one1thisisjustanexamplewalletreplaceme'                                 *")
    printStars()
    raise SystemExit(0)


def setAPIPaths(dotenv_file):
    if environ.get("NETWORK_0_CALL") is None:
        dotenv.set_key(dotenv_file, "NETWORK_0_CALL", f"{validatorToolbox.hmyAppPath} --node='https://api.s0.{environ.get('NETWORK_SWITCH')}.hmny.io' ")
        dotenv.set_key(dotenv_file, "NETWORK_S_CALL", f"{validatorToolbox.hmyAppPath} --node='https://api.s{environ.get('SHARD')}.{environ.get('NETWORK_SWITCH')}.hmny.io' ")
    return 


def getValidatorInfo():
    if environ.get("NETWORK") == "mainnet":
        endpoint = len(validatorToolbox.rpc_endpoints)
    if environ.get("NETWORK") == "testnet":
        endpoint = len(validatorToolbox.rpc_endpoints_test)
    current = 0
    max_tries = validatorToolbox.rpc_endpoints_max_connection_retries
    validator_data = -1

    while current < max_tries:
        try:
            validator_data = staking.get_validator_information(environ.get("VALIDATOR_WALLET"), endpoint)
            return validator_data
        except Exception:
            current += 1
            continue

    return validator_data


def currentPrice():
    try:
        response = requests.get(validatorToolbox.onePriceURL, timeout=5)
    except (ValueError, KeyError, TypeError):
        response = "0.0000"
        return response
    data_dict = response.json()
    type(data_dict)
    data_dict.keys()
    return (data_dict['lastPrice'][:-4])


def getWalletBalance(wallet_addr):
    endpoints_count = len(validatorToolbox.rpc_endpoints)

    for i in range(endpoints_count):
        wallet_balance = getWalletBalanceByEndpoint(validatorToolbox.rpc_endpoints[i], wallet_addr)
        wallet_balance_test = getWalletBalanceByEndpoint(validatorToolbox.rpc_endpoints_test[i], wallet_addr)

        if wallet_balance >= 0 and wallet_balance_test >= 0:
            return wallet_balance, wallet_balance_test

    raise ConnectionError("Couldn't fetch RPC data for current epoch.")


def getWalletBalanceByEndpoint(endpoint, wallet_addr):
    current = 0
    max_tries = validatorToolbox.rpc_endpoints_max_connection_retries
    get_balance = 0

    while current < max_tries:
        try:
            get_balance = pyhmy.numbers.convert_atto_to_one(account.get_balance(wallet_addr, endpoint))
            return get_balance
        except Exception:
            current += 1
            continue

    return get_balance


def getRewardsBalance(endpoint, wallet_addr):
    endpoints_count = len(endpoint)
    
    for i in range(endpoints_count):
        wallet_balance = getRewardsBalanceByEndpoint(endpoint[i], wallet_addr)

        if wallet_balance >= 0:
            return wallet_balance

    raise ConnectionError("Couldn't fetch RPC data for current epoch.")


def getRewardsBalanceByEndpoint(endpoint, wallet_addr):
    current = 0
    max_tries = validatorToolbox.rpc_endpoints_max_connection_retries
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


def walletPendingRewards(wallet):
    res, walletBalance = getRewardsBalance(wallet, save_data=True, display=False)
    totalRewards = 0
    for i in walletBalance["result"]:
        totalRewards = totalRewards + i["reward"]
    totalRewards = "{:,}".format(round(totalRewards * 0.000000000000000001, 2))
    return totalRewards


def getSignPercent() -> str:
    output = subprocess.getoutput(
        f"{environ.get('NETWORK_0_CALL')} blockchain validator information {environ.get('VALIDATOR_WALLET')} | grep signing-percentage"
    )
    outputStripped = output.lstrip(
        '        "current-epoch-signing-percentage": "'
    ).rstrip('",')
    try:
        math = float(outputStripped)
        signPerc = math * 100
        roundSignPerc = round(signPerc, 6)
        return str(roundSignPerc)
    except (OSError, ValueError):
        outputStripped = "0"
        return str(outputStripped)