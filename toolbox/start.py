import os
import pathlib
import time
from os import environ
from utils.installer import *
from utils.shared import loaderIntro, getValidatorInfo


if __name__ == "__main__":
    if os.path.isfile('~/.easynode.one') == False:
        os.system('touch ~/.easynode.env')
    envFile = pathlib.Path('~/.easynode.env')
    os.system("clear")
    loaderIntro()
    try:
        with envFile.open() as f:
            setupStatus = environ.get("SETUP_STATUS")
        print("* Configuration file detected, loading the validator-toolbox menu application.")
        printStars()
        load_dotenv(dotenv_file)
        setupStatus = environ.get("SETUP_STATUS")
        dotenv.set_key(dotenv_file, "EASY_VERSION", easyVersion)
        time.sleep(1)
    except OSError:
        print("* This is the first time you've launched start.py, loading config menus.")
        printStars()
        dotenv.set_key(dotenv_file, "SETUP_STATUS", "2")
        dotenv.set_key(dotenv_file, "EASY_VERSION", easyVersion)
        time.sleep(1)
    setupStatus = environ.get("SETUP_STATUS")
    checkEnvStatus(setupStatus)
    if setupStatus == "1":
        nodeType = environ.get("NODE_TYPE")
        if nodeType == "regular":
            if environ.get("VALIDATOR_WALLET") is None:
                setWalletEnv(dotenv_file, hmyAppPath, activeUserName)
            runRegularNode()
        if nodeType == "full":
            runFullNode()      
    printStars()
    print("* Initial run completed, ~/.easynode.env built.\n* Re-run python3 ~/validator-toolbox/toolbox/start.py to load management menu.")
    printStars()
