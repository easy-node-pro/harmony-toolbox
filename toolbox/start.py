import os
import time
import dotenv
from os import environ
from dotenv import load_dotenv
from utils.config import validatorToolbox
from utils.installer import firstSetup, printStars, recheckVars, passphraseStatus, recoverWallet
from utils.shared import loaderIntro, setWalletEnv, askYesNo, loadVarFile
from utils.toolbox import runRegularNode, runFullNode

# load_dotenv("~/.easynode.env")

if __name__ == "__main__":
    os.system("clear")
    loaderIntro()
    if not os.path.exists(validatorToolbox.dotenv_file):
        firstSetup()
    loadVarFile()
    if not environ.get("VALIDATOR_WALLET"):
        print(
            "* You don't currently have a validator wallet address loaded in your .env file."
            + "* If you have a wallet installed, press a key to continue and choose option 0 on the next menu to load your wallet (Yeah, it says Mnemonic Recovery but if it's loaded properly it won't ask)."
            + "* If you don't want to load a wallet but still want to use the menu, please edit ~/.easynode.env and add a line with the following info:"
            + "* VALIDATOR_WALLET='one1typevalidatorONEaddress' "
        )
        input("* Press any key to import or load a wallet.")
        recoverWallet()
        if not environ.get("VALIDATOR_WALLET"):
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
        runRegularNode()
    if environ.get("NODE_TYPE") == "full":
        runFullNode()
    print("Uh oh, you broke me! Contact Easy Node")
    raise SystemExit(0)