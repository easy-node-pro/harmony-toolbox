from utils.config import validatorToolbox
from os import environ
from dotenv import load_dotenv
from simple_term_menu import TerminalMenu
from colorama import Fore, Style
from pathlib import Path
from pyhmy import validator, account, staking, numbers
from json import load, dump
from utils.config import validatorToolbox
import dotenv
import time
import os
import subprocess
import requests
import pyhmy

load_dotenv(validatorToolbox.dotenv_file)


class PrintStuff:
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
    def printWhiteSpace(self) -> None:
        print("\n" * 8)


printWhiteSpace = PrintStuff.printWhiteSpace
printStars = PrintStuff().printStars
stringStars = PrintStuff().stringStars
printStarsReset = PrintStuff(reset=1).printStars
stringStarsReset = PrintStuff(reset=1).stringStars

# check if a var exists in your .env file, unset and reset if exists to avoid bad stuff
def setVar(fileName, keyName, updateName):
    if environ.get(keyName):
        dotenv.unset_key(fileName, keyName)
    dotenv.set_key(fileName, keyName, updateName)
    loadVarFile()
    return


# loader intro splash screen
def loaderIntro():
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
    printStars()
    print(p)
    return


# Install Harmony ONE
def installHmyApp():
    os.chdir(f"{validatorToolbox.harmonyDirPath}")
    os.system("curl -LO https://harmony.one/hmycli && mv hmycli hmy && chmod +x hmy")
    printStars()
    print("* hmy application installed.")
    return


# Code to update the harmony.conf after an upgrade and other text files.
def updateTextFile(fileName, originalText, newText):

    with open(fileName, "r") as f:
        filedata = f.read()

    newdata = filedata.replace(originalText, newText)

    with open(fileName, "w") as f:
        f.write(newdata)


# Setup a wallet, ask if they need to import one (not required but no toolbox menu without a wallet)
def recoverWallet():
    question = askYesNo(f"* Would you like to import a wallet? (YES/NO) ")
    # if yes, find recovery type
    if question:
        recoveryType()
        loadVarFile()
        print(
            f'\n* Verify the address above matches the address below:\n* Detected Wallet: {Fore.GREEN}{environ.get("VALIDATOR_WALLET")}{Style.RESET_ALL}\n* If a different wallet is showing you can remove it and retry it after installation.\n*\n* .{validatorToolbox.hmyAppPath} keys remove {validatorToolbox.activeUserName}\n*\n* To restore a wallet once again, run the following:\n*\n* .{validatorToolbox.hmyAppPath} keys recover-from-mnemonic {validatorToolbox.activeUserName} {environ.get("PASS_SWITCH")}\n*'
        )
        printStars()
        input("* Verify your wallet information above.\n* Press ENTER to continue Installation.")
    else:
        wallet = input(
            f"* If you'd like to use the management menu, we need a one1 address, please input your address now: "
        )
        setVar(validatorToolbox.dotenv_file, "VALIDATOR_WALLET", wallet)
        return


def installHarmonyApp():
    os.chdir(f"{validatorToolbox.harmonyDirPath}")
    if environ.get("NETWORK") == "testnet":
        os.system("curl -LO https://harmony.one/binary_testnet && mv binary_testnet harmony && chmod +x harmony")
        os.system("./harmony config dump --network testnet harmony.conf")
        updateTextFile(validatorToolbox.harmonyConfPath, "MaxKeys = 10", "MaxKeys = 13")
    if environ.get("NETWORK") == "mainnet":
        os.system("curl -LO https://harmony.one/binary && mv binary harmony && chmod +x harmony")
        os.system("./harmony config dump harmony.conf")
        updateTextFile(validatorToolbox.harmonyConfPath, "MaxKeys = 10", "MaxKeys = 13")
    printStars()
    print("* harmony.conf MaxKeys modified to 13")
    if os.path.exists(validatorToolbox.blsKeyFile):
        updateTextFile(validatorToolbox.harmonyConfPath, 'PassFile = ""', f'PassFile = "blskey.pass"')
        print("* blskey.pass found, updated harmony.conf")
    printStars()
    print(f"* Harmony {environ.get('NETWORK')} application installed & ~/harmony/harmony.conf created.")
    return


def setWalletEnv():
    if environ.get("NODE_WALLET") == "true":
        if not environ.get("VALIDATOR_WALLET"):
            output = subprocess.getoutput(
                f"{validatorToolbox.hmyAppPath} keys list | grep {validatorToolbox.activeUserName}"
            )
            outputStripped = output.lstrip(validatorToolbox.activeUserName)
            outputStripped = outputStripped.strip()
            setVar(validatorToolbox.dotenv_file, "VALIDATOR_WALLET", outputStripped)
            return outputStripped
        else:
            loadVarFile()
            validatorWallet = environ.get("VALIDATOR_WALLET")
            return validatorWallet


def recoveryType():
    os.system("clear")
    setVar(validatorToolbox.dotenv_file, "NODE_WALLET", "true")
    passphraseStatus()
    passphraseSwitch = environ.get("PASS_SWITCH")
    printStars()
    print("* Wallet Recovery Type!                                                                     *")
    printStars()
    print("* [0] = Mnemonic phrase recovery (aka seed phrase)                                          *")
    print("* [1] = Private Key recovery                                                                *")
    printStars()
    menuOptions = [
        "[0] - Mnemonic Phrase Recovery",
        "[1] - Private Key Recovery",
    ]
    terminal_menu = TerminalMenu(
        menuOptions, title="* Which type of restore method would you like to use for your validator wallet?"
    )
    results = terminal_menu.show()
    if results == 0:
        # Mnemonic Recovery Here
        os.system(
            f"{validatorToolbox.hmyAppPath} keys recover-from-mnemonic {validatorToolbox.activeUserName} {passphraseSwitch}"
        )
        printStars()
        setWalletEnv()
    elif results == 1:
        # Private Key Recovery Here
        print("* Private key recovery requires your private information in the command itself.")
        private = input("* Please enter your private key to restore your wallet: ")
        os.system(
            f"{validatorToolbox.hmyAppPath} keys import-private-key {private} {validatorToolbox.activeUserName} --passphrase"
        )
        printStars()
        setWalletEnv()


def passphraseStatus():
    loadVarFile()
    if environ.get("NODE_WALLET") == "true":
        passphraseSet()
        setVar(
            validatorToolbox.dotenv_file,
            "PASS_SWITCH",
            f"--passphrase-file {validatorToolbox.harmonyDirPath}/passphrase.txt",
        )
    if environ.get("NODE_WALLET") == "false":
        setVar(validatorToolbox.dotenv_file, "PASS_SWITCH", "--passphrase")


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
            prompt="* Please set a wallet password for this node\n* Enter your password now: ", stream=None
        )
        password2 = getpass.getpass(prompt="* Re-enter your password: ", stream=None)
        if not password1 == password2:
            print("* Passwords do NOT match, Please try again..")
        else:
            print("* Passwords Match!")
            break
    # Save file, we won't encrypt because if someone has access to the file, they will also have the salt and decrypt code at their disposal.
    save_text(validatorToolbox.passwordPath, password1)
    loadVarFile()
    passphraseStatus()


def process_command(command: str) -> None:
    process = subprocess.Popen(command, shell=True)
    output, error = process.communicate()


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
    if os.path.exists(validatorToolbox.dotenv_file):
        load_dotenv(validatorToolbox.dotenv_file, override=True)


def getShardMenu() -> None:
    if not environ.get("SHARD"):
        os.system("clear")
        printStars()
        print("* First Boot - Gathering more information about your server                                 *")
        printStars()
        print("* Which shard do you want this node run on?                                                 *")
        printStars()
        menuOptions = [
            "[0] - Shard 0",
            "[1] - Shard 1",
            "[2] - Shard 2",
            "[3] - Shard 3",
        ]
        terminal_menu = TerminalMenu(menuOptions, title="* Which Shard will this node operate on? ")
        ourShard = str(terminal_menu.show())
        setVar(validatorToolbox.dotenv_file, "SHARD", ourShard)
        return ourShard


def getNodeType() -> None:
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
            menuOptions = [
                "[0] Signing Node w/ Wallet",
                "[1] Signing Node No Wallet",
                "[2] Full Node Non Validating Dev/RPC",
            ]
            terminal_menu = TerminalMenu(menuOptions, title="Regular or Full Node Server")
            results = terminal_menu.show()
            if results == 0:
                setVar(validatorToolbox.dotenv_file, "NODE_TYPE", "regular")
                setVar(validatorToolbox.dotenv_file, "NODE_WALLET", "true")
            if results == 1:
                setVar(validatorToolbox.dotenv_file, "NODE_TYPE", "regular")
                setVar(validatorToolbox.dotenv_file, "NODE_WALLET", "false")
            if results == 2:
                setVar(validatorToolbox.dotenv_file, "NODE_TYPE", "full")
            os.system("clear")
            return
        setWalletEnv()
    if not environ.get("NODE_TYPE"):
        setVar(validatorToolbox.dotenv_file, "NODE_TYPE", "regular")
    if not environ.get("NODE_WALLET"):
        setVar(validatorToolbox.dotenv_file, "NODE_WALLET", "true")

def setMainOrTest() -> None:
    if not environ.get("NETWORK"):
        os.system("clear")
        printStars()
        print("* Setup config not found, which blockchain does this node run on?                           *")
        printStars()
        print("* [0] - Mainnet                                                                             *")
        print("* [1] - Testnet                                                                             *")
        printStars()
        menuOptions = [
            "[0] Mainnet",
            "[1] Testnet",
        ]
        terminal_menu = TerminalMenu(menuOptions, title="Mainnet or Testnet")
        results = terminal_menu.show()
        if results == 0:
            setVar(validatorToolbox.dotenv_file, "NETWORK", "mainnet")
            setVar(validatorToolbox.dotenv_file, "NETWORK_SWITCH", "t")
            setVar(validatorToolbox.dotenv_file, "RPC_NET", "https://rpc.s0.t.hmny.io")
            setVar(validatorToolbox.dotenv_file, "RPC_NET_SHARD", f"https://rpc.s{environ.get('SHARD')}.t.hmny.io")
        if results == 1:
            setVar(validatorToolbox.dotenv_file, "NETWORK", "testnet")
            setVar(validatorToolbox.dotenv_file, "NETWORK_SWITCH", "b")
            setVar(validatorToolbox.dotenv_file, "RPC_NET", "https://rpc.s0.b.hmny.io")
            setVar(validatorToolbox.dotenv_file, "RPC_NET_SHARD", f"https://rpc.s{environ.get('SHARD')}.b.hmny.io")
        os.system("clear")
    return

def getExpressStatus() -> None:
    if environ.get("SETUP_STATUS") == "0":
        os.system("clear")
        printStars()
        print("* Express or Manual Setup?                                                                  *")
        printStars()
        print("* Would you like the turbo express setup or Manual approval of each step?                   *")
        printStars()
        menuOptions = [
            "[0] - Express Install",
            "[1] - Manual Approval",
        ]
        terminal_menu = TerminalMenu(menuOptions, title="* Express Or Manual Setup")
        setVar(validatorToolbox.dotenv_file, "EXPRESS", str(terminal_menu.show()))


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


def setAPIPaths():
    if not environ.get("NETWORK_0_CALL"):
        setVar(
            validatorToolbox.dotenv_file,
            "NETWORK_0_CALL",
            f"{validatorToolbox.hmyAppPath} --node='https://api.s0.{environ.get('NETWORK_SWITCH')}.hmny.io' ",
        )
        setVar(
            validatorToolbox.dotenv_file,
            "NETWORK_S_CALL",
            f"{validatorToolbox.hmyAppPath} --node='https://api.s{environ.get('SHARD')}.{environ.get('NETWORK_SWITCH')}.hmny.io' ",
        )


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
    return data_dict["lastPrice"][:-4]


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
    outputStripped = output.lstrip('        "current-epoch-signing-percentage": "').rstrip('",')
    try:
        math = float(outputStripped)
        signPerc = math * 100
        roundSignPerc = round(signPerc, 6)
        return str(roundSignPerc)
    except (OSError, ValueError):
        outputStripped = "0"
        return str(outputStripped)


def getVersions():
    output = subprocess.getoutput(f"{validatorToolbox.harmonyAppPath} -V")
    output2 = subprocess.getoutput(f"{validatorToolbox.hmyAppPath} version")
    setVar(validatorToolbox.dotenv_file, "HARMONY_VERSION", output[35:-35])
    setVar(validatorToolbox.dotenv_file, "HMY_VERSION", output2[62:-15])
    return output[35:-35], output2[62:-15]


def setModX(file):
    subprocess.run(["chmod", "+x", file])


def checkForUpdates():
    subprocess.check_output(
        ["wget", "https://harmony.one/binary", "-O", validatorToolbox.hmyTmpPath], stderr=subprocess.STDOUT
    )
    setModX(validatorToolbox.hmyTmpPath)
    subprocess.check_output([validatorToolbox.hmyTmpPath, "config", "dump", "harmony.conf"], stderr=subprocess.STDOUT)
    output = subprocess.getoutput(f"{validatorToolbox.hmyTmpPath} -V")
    setVar(validatorToolbox.dotenv_file, "ONLINE_HARMONY_VERSION", output[35:-35])
    subprocess.check_output(
        ["wget", "https://harmony.one/hmycli", "-O", validatorToolbox.hmyTmpPath], stderr=subprocess.STDOUT
    )
    setModX(validatorToolbox.hmyTmpPath)
    output2 = subprocess.getoutput(f"{validatorToolbox.hmyTmpPath} version")
    setVar(validatorToolbox.dotenv_file, "ONLINE_HMY_VERSION", output2[62:-15])
    return output[35:-35], output2[62:-15]


def versionChecks():
    harmonyVersion, hmyVersion = getVersions()
    onlineVersion, onlineHmyVersion = checkForUpdates()
    if harmonyVersion != onlineVersion:
        # here we would set the upgrade harmony flag in env
        setVar(validatorToolbox.dotenv_file, "HARMONY_UPGRADE_AVAILABLE", "True")
    if harmonyVersion == onlineVersion:
        setVar(validatorToolbox.dotenv_file, "HARMONY_UPGRADE_AVAILABLE", "False")
    if hmyVersion != onlineHmyVersion:
        setVar(validatorToolbox.dotenv_file, "HMY_UPGRADE_AVAILABLE", "True")
    if hmyVersion == onlineHmyVersion:
        setVar(validatorToolbox.dotenv_file, "HMY_UPGRADE_AVAILABLE", "False")
    return


def firstSetup():
    os.system("touch ~/.easynode.env")
    # first run stuff
    time.sleep(2)
    # Update version if newer from conf file to .easynode.env
    if environ.get("EASY_VERSION"):
        setVar(validatorToolbox.dotenv_file, "EASY_VERSION", validatorToolbox.easyVersion)
    # Find Shard #
    getShardMenu()
    # Express - no prompts for each step, Manual - prompts for each step
    getExpressStatus()
    # Get Regular validator with/without wallet or Full RPC Node
    getNodeType()
    # Get Mainnet or Testnet
    setMainOrTest()
    # Set the API for previous choices
    setAPIPaths()
    # Setup status done
    setVar(validatorToolbox.dotenv_file, "SETUP_STATUS", "0")
    # Look for a harmony install or install.
    checkForInstall()
    printStars()
    return


def recheckVars():
    # recheck some stuff just in case the .easynode.env isn't proper
    loadVarFile()
    getShardMenu()
    getNodeType()
    setMainOrTest()
    setAPIPaths()
    return


# looks for ~/harmony or installs it if it's not there. Asks to overwrite if it finds it, run at your own risk.
def checkForInstall() -> str:
    loadVarFile()
    if not os.path.exists(validatorToolbox.harmonyDirPath):
        print(f"* You selected Shard: {environ.get('SHARD')}. ")
        installHarmony()
        if environ.get("NODE_WALLET") == "true":
            restoreWallet()
        printStars()
        print("* All harmony files now installed. Database download starting now...")
        printStars()
        cloneShards()
        finish_node_install()
    else:
        question = askYesNo(
            "* You already have a harmony folder on this system, would you like to re-run installation and rclone? (YES/NO)"
        )
        if question:
            installHarmony()
            if environ.get("NODE_WALLET") == "true":
                restoreWallet()
            printStars()
            print("* All harmony files now installed. Database download starting now...")
            printStars()
            cloneShards()
            finish_node_install()

# Installer Module
def installHarmony() -> None:
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
                dotenv.set_key(validatorToolbox.dotenv_file, "MOUNT_POINT", myLongHmyPath)
                print("* Creating all Harmony Files & Folders")
                os.system(f"sudo chown {validatorToolbox.activeUserName} {myVolumePath}")
                os.system(f"mkdir -p {myLongHmyPath}/.hmy/blskeys")
                os.system(f"ln -s {myLongHmyPath} {validatorToolbox.harmonyDirPath}")
            # Let's make sure your volume is mounted
            if mntCount == 0:
                question = askYesNo(
                    "* You have a volume but it is not mounted.\n* Would you like to install Harmony in ~/harmony on your main disk instead of your volume? (Yes/No) "
                )
                if question:
                    dotenv.set_key(validatorToolbox.dotenv_file, "MOUNT_POINT", validatorToolbox.harmonyDirPath)
                else:
                    raise SystemExit(0)
    # Setup folders now that symlink exists or we know we're using ~/harmony
    if not os.path.isdir(f"{validatorToolbox.userHomeDir}/.hmy_cli/account-keys/"):
        os.system(f"mkdir -p {validatorToolbox.userHomeDir}/.hmy_cli/account-keys/")
    if not os.path.isdir(f"{validatorToolbox.harmonyDirPath}/.hmy/blskeys"):
        print("* Creating all Harmony Files & Folders")
        os.system(f"mkdir -p {validatorToolbox.harmonyDirPath}/.hmy/blskeys")
    # Change to ~/harmony folder
    os.chdir(f"{validatorToolbox.harmonyDirPath}")
    printStars()
    # Install hmy
    installHmyApp()
    printStars()
    # Install harmony
    installHarmonyApp()
    # install hmy files
    print("* Installing rclone application & rclone configuration files")
    printStars()
    # check for working rclone site and download
    try:
        os.system("curl https://rclone.org/install.sh | sudo bash")
    except (ValueError, KeyError, TypeError):
        result = askYesNo(
            "* rclone site is offline, we can install rclone from the Ubuntu repo as a workaround, do you want to continue? (Y/N): "
        )
        if result:
            # If rclone curl is down, install rclone with apt instead
            subprocess.run('sudo apt install rclone -y')

    os.system(
        f"mkdir -p {validatorToolbox.userHomeDir}/.config/rclone && cp {validatorToolbox.toolboxLocation}/toolbox/bin/rclone.conf {validatorToolbox.userHomeDir}/.config/rclone/"
    )
    printStars()
    # Setup the harmony service file
    print("* Customizing, Moving & Enabling your harmony.service systemd file")
    if validatorToolbox.activeUserName == "root":
        os.system(
            f"sudo cp {validatorToolbox.toolboxLocation}/toolbox/bin/harmony.service . && sed -i 's/home\/serviceharmony/{validatorToolbox.activeUserName}/g' 'harmony.service' && sed -i 's/serviceharmony/{validatorToolbox.activeUserName}/g' 'harmony.service' && sudo mv harmony.service /etc/systemd/system/harmony.service && sudo chmod a-x /etc/systemd/system/harmony.service && sudo systemctl enable harmony.service"
        )
    else:
        os.system(
            f"sudo cp {validatorToolbox.toolboxLocation}/toolbox/bin/harmony.service . && sed -i 's/serviceharmony/{validatorToolbox.activeUserName}/g' 'harmony.service' && sudo mv harmony.service /etc/systemd/system/harmony.service && sudo chmod a-x /etc/systemd/system/harmony.service && sudo systemctl enable harmony.service"
        )

# Database Downloader
def cloneShards():
    # Move to ~/harmony
    os.chdir(f"{validatorToolbox.harmonyDirPath}")
    os.system("clear")
    printStars()
    if environ.get("SHARD") != "0":
        # If we're not on shard 0, download the numbered shard DB here.
        print(f"* Now cloning shard {environ.get('SHARD')}")
        printStars()
        os.system(
            f"rclone -P sync release:pub.harmony.one/{environ.get('NETWORK')}.min/harmony_db_{environ.get('SHARD')} {validatorToolbox.harmonyDirPath}/harmony_db_{environ.get('SHARD')} --multi-thread-streams 4 --transfers=32"
        )
        printStars()
        print(f"Shard {environ.get('SHARD')} completed.")
        printStars()
    else:
        # If we're on shard 0, grab the snap DB here.
        print("* Now cloning Shard 0, kick back and relax for awhile...")
        printStars()
        os.system(
            f"rclone -P -L --checksum sync release:pub.harmony.one/{environ.get('NETWORK')}.snap/harmony_db_0 {validatorToolbox.harmonyDirPath}/harmony_db_0 --multi-thread-streams 4 --transfers=32"
        )

# Code to restore a wallet
def restoreWallet() -> str:
    if environ.get("NODE_WALLET") == "true":
        if not os.path.exists(validatorToolbox.hmyWalletStorePath):
            os.system("clear")
            printStars()
            print("* Harmony ONE Validator Wallet Import")
            printStars()
            if environ.get("EXPRESS") == "1":
                question = askYesNo(
                    "\n* You will directly utilize the harmony application interface"
                    + "\n* We do not store any pass phrases  or data inside of our application"
                    + "\n* Respond yes to recover your validator wallet via Mnemonic phrase now or say NO to create a new wallet post-install"
                    + "\n* Restore an existing wallet now? (YES/NO) "
                )
                if question:
                    passphraseStatus()
                    recoverWallet()
                printStars()
                return
            passphraseStatus()
            recoverWallet()
            return
        printStars()
        print("* Wallet already setup for this user account")


def setMountedPoint():
    # First let's make sure your volume is mounted
    totalDir = len(os.listdir("/mnt"))
    if totalDir > 0:
        volumeMountPath = os.listdir("/mnt")
        myVolumePath = "/mnt/" + str(volumeMountPath[0])
        myLongHmyPath = myVolumePath + "/harmony"
    else:
        myVolumePath = validatorToolbox.harmonyDirPath
    if totalDir == 1:
        dotenv.set_key(validatorToolbox.dotenv_file, "MOUNT_POINT", myLongHmyPath)
    else:
        dotenv.set_key(validatorToolbox.dotenv_file, "MOUNT_POINT", f"{validatorToolbox.harmonyDirPath}")


def finish_node_install():
    loadVarFile()
    printStars()
    print(
        "* Installation is completed"
        + "\n* Create a new wallet or recover your existing wallet into ./hmy"
        + "\n* Create or upload your bls key & pass files into ~/harmony/.hmy/blskeys"
        + "\n* Finally, reboot to start synchronization."
    )
    printStars()
    if environ.get("NODE_WALLET") == "false":
        print(
            "* Post installation quick tips:"
            + "\n* To recover your wallet on this server run:"
            + f"\n* python3 ~/validatortoolbox/toolbox/load_wallet.py"
            + "\n*"
            + "\n* To create BLS keys run:"
            + f'\n* ./hmy keys generate-bls-keys --count 1 --shard {environ.get("SHARD")} --passphrase'
            + "\n*"
        )
    else:
        print(
            "* Post installation quick tips:"
            + "\n* To recover your wallet again, run:"
            + f"\n* python3 ~/validatortoolbox/toolbox/load_wallet.py"
            + "\n*"
            + "\n* To create BLS keys run:"
            + f'\n* ./hmy keys generate-bls-keys --count 1 --shard {environ.get("SHARD")} {environ.get("PASS_SWITCH")}'
            + "\n*"
        )
    printStars()
    print("* Thanks for using Easy Node - Validator Node Server Software Installer!")
    printStars()
    setVar(validatorToolbox.dotenv_file, "SETUP_STATUS", "1")
    raise SystemExit(0)
