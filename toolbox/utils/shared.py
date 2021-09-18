import os
import dotenv
import subprocess
from os import environ
from dotenv import load_dotenv
from simple_term_menu import TerminalMenu
from colorama import Fore, Back, Style


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


def installHarmonyApp(harmonyDirPath, testOrMain):
    os.chdir(f"{harmonyDirPath}")
    if testOrMain == "testnet":
        os.system("curl -LO https://harmony.one/binary_testnet && mv binary_testnet harmony && chmod +x harmony")
        os.system("./harmony config dump --network testnet harmony.conf")
    if testOrMain == "mainnet":
        os.system("curl -LO https://harmony.one/binary && mv binary harmony && chmod +x harmony")
        os.system("./harmony config dump harmony.conf")
    # when we setup rasppi as an option, this is the install command for harmony
    if testOrMain == "rasppi_main":
        os.system("curl -LO https://harmony.one/binary-arm64 && mv binary-arm64 harmony && chmod +x harmony")
        os.system("./harmony config dump harmony.conf")
    printStars()
    print("* Harmony application installed & ~/harmony/harmony.conf created.")


def setWalletEnv(dotenv_file, hmyAppPath, activeUserName):
    output = subprocess.getoutput(f"{hmyAppPath} keys list | grep {activeUserName}")
    outputStripped = output.lstrip(activeUserName)
    outputStripped = outputStripped.strip()
    # verify strip matches file if this isn't a first run, if first run set it
    dotenv.set_key(dotenv_file, "VALIDATOR_WALLET", outputStripped)
    return str(outputStripped)


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
    """
    Opens a file and returns the whole file as a list
    Args:
        fn (str): File name to open
    Returns:
        list: return whole file as a list
    """
    try:
        with open(fn, "r") as f:
            return f.readlines()
    except FileNotFoundError as e:
        print(f"File not Found  ::  {e}")
        return []


def firstRun(dotenv_file, setupStatus):
    if setupStatus not in {"0", "1"}:
        os.system("clear")
        print("*********************************************************************************************")
        print("* First run detected!                                                                       *")
        print("*********************************************************************************************")
        print("* [0] = Start new harmony validator node server install")
        print("* [1] = Harmony Node already loaded on this server, just run the menu! ")
        print()
        menuOptions = ["[0] - Start Validator Server Node Installer", "[1] - Start Validator Toolbox Menu", ]
        terminal_menu = TerminalMenu(menuOptions, title="* Brand New Server Node or Already Running Server Node")
        setupStatus = str(terminal_menu.show())
        dotenv.set_key(dotenv_file, "SETUP_STATUS", setupStatus)
        return setupStatus
    return setupStatus


def getExpressStatus(dotenv_file) -> None:
    if environ.get("EXPRESS") is None:
        os.system("clear")
        print("*********************************************************************************************")
        print("* Express or Manual Setup?                                                                  *")
        print("*********************************************************************************************")
        print("* Would you like the turbo express setup or Manual approval of each step?                   *")
        print("*********************************************************************************************")
        menuOptions = ["[0] - Express Install", "[1] - Manual Approval", ]
        terminal_menu = TerminalMenu(menuOptions, title="* Express Or Manual Setup")
        expressStatus = str(terminal_menu.show())
        dotenv.set_key(dotenv_file, "EXPRESS", expressStatus)
        return


def getShardMenu(dotenv_file) -> None:
    if environ.get("SHARD") is None:
        os.system("clear")
        print("*********************************************************************************************")
        print("* Shard not found, building ~/.easynode.env file                                            *")
        print("*********************************************************************************************")
        print("* Which shard does this node run on?                                                        *")
        print("*********************************************************************************************")
        menuOptions = ["[0] - Shard 0", "[1] - Shard 1", "[2] - Shard 2", "[3] - Shard 3", ]
        terminal_menu = TerminalMenu(menuOptions, title="* Shard Choice")
        ourShard = str(terminal_menu.show())
        dotenv.set_key(dotenv_file, "SHARD", ourShard)
        return 


def setMainOrTest(dotenv_file) -> None:
    if environ.get("NETWORK") is None:
        os.system("clear")
        print("*********************************************************************************************")
        print("* Setup config not found, which blockchain does this node run on?                           *")
        print("*********************************************************************************************")
        print("* [0] - Mainnet                                                                             *")
        print("* [1] - Testnet                                                                             *")
        print("* [2] - Raspberry Pi Mainnet                                                                *")
        print("*********************************************************************************************")
        menuOptions = ["[0] Mainnet", "[1] Testnet", "[2] Raspberry Pi Mainnet", ]
        terminal_menu = TerminalMenu(menuOptions, title="Mainnet or Testnet")
        results = terminal_menu.show()
        if results == 0:
            dotenv.set_key(dotenv_file, "NETWORK", "mainnet")
        if results == 1:
            dotenv.set_key(dotenv_file, "NETWORK", "testnet")
        if results == 1:
            dotenv.set_key(dotenv_file, "NETWORK", "rasppi_main")
        os.system("clear")
        return 


def getNodeType(dotenv_file) -> None:
    if environ.get("NODE_TYPE") is None:        
        os.system("clear")
        print("*********************************************************************************************")
        print("* Which type of node would you like to run on this server?                                  *")
        print("*********************************************************************************************")
        print("* [0] - Regular Validating Harmony Node                                                     *")
        print("* [1] - Full Node - Non Validating Harmony Node                                             *")
        print("*********************************************************************************************")
        menuOptions = ["[0] Regular Harmony Validating Node", "[1] Full Node Non Validating", ]
        terminal_menu = TerminalMenu(menuOptions, title="Regular or Full Node Server")
        results = terminal_menu.show()
        if results == 0:
            dotenv.set_key(dotenv_file, "NODE_TYPE", "regular")
        if results == 1:
            dotenv.set_key(dotenv_file, "NODE_TYPE", "full")
        os.system("clear")
        return


def setAPIPaths(hmyAppPath, ourShard, dotenv_file):
    networkType = environ.get("NETWORK")
    ourShard = environ.get("SHARD")
    if networkType == "mainnet" or "rasppi_main":
        networkZeroCall = f"{hmyAppPath} --node='https://api.s0.t.hmny.io'"
        networkNumCall = f"{hmyAppPath} --node='https://api.s{ourShard}.t.hmny.io'"
        networkTestCall = f"{hmyAppPath} --node='https://api.s0.b.hmny.io'"
        dotenv.set_key(dotenv_file, "TESTNET_CALL", networkTestCall)
        dotenv.set_key(dotenv_file, "NETWORK_0_CALL", networkZeroCall)
        dotenv.set_key(dotenv_file, "NETWORK_S_CALL", networkNumCall)
        return 
    if networkType == "testnet":
        networkZeroCall = f"{hmyAppPath} --node='https://api.s0.b.hmny.io'"
        networkNumCall = f"{hmyAppPath} --node='https://api.s{ourShard}.b.hmny.io'"
        dotenv.set_key(dotenv_file, "NETWORK_0_CALL", networkZeroCall)
        dotenv.set_key(dotenv_file, "NETWORK_S_CALL", networkNumCall)
        # same as regular 0 on testnet, set anyways
        dotenv.set_key(dotenv_file, "TESTNET_CALL", networkZeroCall)
        return
    return