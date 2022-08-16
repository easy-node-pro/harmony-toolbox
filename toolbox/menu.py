import os
from os import environ
from utils.config import validatorToolbox
from utils.installer import printStars, recheckVars, recoverWallet
from utils.shared import loaderIntro, setWalletEnv, askYesNo, loadVarFile, passphraseStatus
from utils.toolbox import runRegularNode, setReserveTotal

if __name__ == "__main__":
    os.system("clear")
    loaderIntro()
    if not os.path.exists(validatorToolbox.dotenv_file):
        print("Install Harmony First!!!\nRun python3 ~/validatortoolbox/toolbox/install.py")
        raise SystemExit(0)
    loadVarFile()
    if environ.get("REWARDS_RESERVE") is None:
        setReserveTotal("5")
    if environ.get("VALIDATOR_WALLET") is None:
        recoverWallet()
        if environ.get("VALIDATOR_WALLET") is None:
            print(
                "* You don't currently have a validator wallet address loaded in your .env file, please edit ~/.easynode.env and add a line with the following info:\n "
                + "* VALIDATOR_WALLET='validatorONEaddress' "
            )
            input("* Press any key to exit.")
            raise SystemExit(0)
    if environ.get("SETUP_STATUS") != "2":
        recheckVars()
        passphraseStatus()
    if environ.get("NODE_TYPE") == "regular":
        if environ.get("VALIDATOR_WALLET") is None:
            setWalletEnv()
        runRegularNode()
    print("Uh oh, you broke me! Contact Easy Node")
    raise SystemExit(0)