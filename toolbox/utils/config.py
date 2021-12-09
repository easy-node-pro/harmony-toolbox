import os
import socket
import urllib.request

class validatorToolbox:
    easyVersion = "1.2.7"
    serverHostName = socket.gethostname()
    userHomeDir = os.path.expanduser("~")
    dotenv_file = f"{userHomeDir}/.easynode.env"
    activeUserName = os.path.split(userHomeDir)[-1]
    harmonyDirPath = os.path.join(userHomeDir, "harmony")
    harmonyAppPath = os.path.join(harmonyDirPath, "harmony")
    blsKeyFile = os.path.join(harmonyDirPath, "blskey.pass")
    hmyAppPath = os.path.join(harmonyDirPath, "hmy")
    harmonyConfPath = os.path.join(harmonyDirPath, "harmony.conf")
    blskeyDirPath = os.path.join(hmyAppPath, ".hmy", "blskeys")
    hmyWalletStorePath = os.path.join(userHomeDir, ".hmy_cli", "account-keys", activeUserName)
    toolboxLocation = os.path.join(userHomeDir, "validatortoolbox")
    validatorData = os.path.join(toolboxLocation, "toolbox", "metadata", "validator.json")
    passwordPath = os.path.join(harmonyDirPath, "passphrase.txt")
    toolboxLocation = os.path.join(userHomeDir, "validatortoolbox")
    ourExternalIPAddress = urllib.request.urlopen("https://ident.me").read().decode("utf8")
    mainMenuRegular = os.path.join(toolboxLocation, "toolbox", "messages", "regularmenu.txt")
    mainMenuFull = os.path.join(toolboxLocation, "toolbox", "messages", "fullmenu.txt")
    rpc_endpoints = ['https://rpc.s0.t.hmny.io', 'https://api.harmony.one']
    rpc_endpoints_test = ['https://rpc.s0.b.hmny.io', 'https://api.s0.pops.one']
    rpc_endpoints_max_connection_retries = 10