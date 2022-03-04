import os
import time
import dotenv
from os import environ
from dotenv import load_dotenv
from utils.config import validatorToolbox
from utils.installer import firstSetup, printStars, recheckVars, passphraseStatus
from utils.shared import loaderIntro, setWalletEnv, askYesNo, loadVarFile
from utils.toolbox import runRegularNode, runFullNode


if __name__ == "__main__":
    os.system("clear")
    loaderIntro()
    if not os.path.exists(validatorToolbox.dotenv_file):
        firstSetup()
    loadVarFile()
    if not environ.get("VALIDATOR_WALLET"):
        print(
            "* You don't currently have a validator wallet address loaded in your .env file, please edit ~/.easynode.env and add a line with the following info:\n "
            + "* VALIDATOR_WALLET='validatorONEaddress' "
        )
        input("* Press any key to exit.")
        raise SystemExit(0)
    print("* Configuration file detected, loading the validatortoolbox menu application.")
    printStars()
    if validatorToolbox.easyVersion != environ.get("EASY_VERSION"):
        dotenv.unset_key(validatorToolbox.dotenv_file, "EASY_VERSION")
        dotenv.set_key(validatorToolbox.dotenv_file, "EASY_VERSION", validatorToolbox.easyVersion)
    if environ.get("SETUP_STATUS") != "2":
        recheckVars()
        passphraseStatus()
    if environ.get("NODE_TYPE") == "regular":
        if not environ.get("VALIDATOR_WALLET"):
            setWalletEnv()
        runRegularNode()
    if environ.get("NODE_TYPE") == "full":
        runFullNode()
    print("Uh oh, you broke me! Contact Easy Node")
    raise SystemExit(0)