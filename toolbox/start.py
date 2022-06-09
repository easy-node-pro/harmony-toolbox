import os
import time
from wsgiref.validate import validator
import dotenv
from os import environ
from dotenv import load_dotenv
from utils.config import validatorToolbox
from utils.installer import firstSetup, printStars, recheckVars, passphraseStatus, recoverWallet
from utils.shared import loaderIntro, new_wallet_recovery, setWalletEnv, askYesNo, loadVarFile
from utils.toolbox import runRegularNode, runFullNode

load_dotenv("~/.easynode.env")

if __name__ == "__main__":
    os.system("clear")
    loaderIntro()
    if not os.path.exists(validatorToolbox.dotenv_file):
        firstSetup()
    loadVarFile()
    if not os.getenv("VALIDATOR_WALLET"):
        new_wallet_recovery()
        if not os.getenv("VALIDATOR_WALLET"):
            print(
                "* You don't currently have a validator wallet address loaded in your .env file, please edit ~/.easynode.env and add a line with the following info:\n "
                + "* VALIDATOR_WALLET='validatorONEaddress' "
            )
            input("* Press any key to exit.")
            raise SystemExit(0)
    print("* Configuration file detected, loading the validatortoolbox menu application.")
    printStars()
    if validatorToolbox.easyVersion != os.environ("EASY_VERSION"):
        os.environ = validatorToolbox.easyVersion
    if os.environ("SETUP_STATUS") != "2":
        recheckVars()
        passphraseStatus()
    if os.environ("NODE_TYPE") == "regular":
        if not os.environ("VALIDATOR_WALLET"):
            setWalletEnv()
        runRegularNode()
    if os.environ("NODE_TYPE") == "full":
        runFullNode()
    print("Uh oh, you broke me! Contact Easy Node")
    raise SystemExit(0)