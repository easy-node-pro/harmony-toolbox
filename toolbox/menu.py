import os
from os import environ
from utils.config import validatorToolbox
from utils.library import loaderIntro, setWalletEnv, loadVarFile, passphraseStatus, setVar, versionChecks, recheckVars, recoverWallet
from utils.toolbox import runRegularNode, runFullNode, refreshStats

if __name__ == "__main__":
    # clear screen, show logo
    os.system("clear")
    loaderIntro()
    # check for .env file, if none we have a first timer.
    if os.path.exists(validatorToolbox.dotenv_file) is None:
        # they should run the installer, goodbye!
        print("Install Harmony First!!!\nRun python3 ~/validatortoolbox/toolbox/install.py")
        raise SystemExit(0)
    # passed .env check, let's load it!
    loadVarFile()
    # This section is for hard coding new settings for current users.
    if environ.get("GAS_RESERVE") is None:
        setVar(validatorToolbox.dotenv_file, "GAS_RESERVE", "5")
    # Make sure they have a wallet or wallet address in the .env file, if none, get one.
    if environ.get("VALIDATOR_WALLET") is None:
        recoverWallet()
        if environ.get("VALIDATOR_WALLET") is None:
            print(
                "* You don't currently have a validator wallet address loaded in your .env file, please edit ~/.easynode.env and add a line with the following info:\n "
                + "* VALIDATOR_WALLET='validatorONEaddress' "
            )
            input("* Press any key to exit.")
            raise SystemExit(0)
    # Check online versions of harmony & hmy and compare to our local copy.
    refreshStats(1)
    versionChecks()
    # Last check on setup status, if it never finished it will try again here.
    if environ.get("SETUP_STATUS") != "2":
        recheckVars()
        passphraseStatus()
    # Run regular validator node
    if environ.get("NODE_TYPE") == "regular":
        if environ.get("VALIDATOR_WALLET") is None:
            setWalletEnv()
        runRegularNode()
    # Run full node
    if environ.get("NODE_TYPE") == "full":
        runFullNode()
    print("Uh oh, you broke me! Contact Easy Node")
    raise SystemExit(0)