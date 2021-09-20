import os
import pathlib
import time
from os import environ
from utils.installer import *
from utils.shared import loaderIntro, getValidatorInfo


if __name__ == "__main__":
    envFile = pathlib.Path(dotenv_file)
    os.system("clear")
    loaderIntro()
    load_dotenv(dotenv_file)
    if environ.get('FIRST_RUN') == "1":
        #first run stuff
        print("* This is the first time you've launched start.py, loading config menus.")
        printStars()
        time.sleep(1)
        dotenv.set_key(dotenv_file, "SETUP_STATUS", "2")
        dotenv.set_key(dotenv_file, "EASY_VERSION", easyVersion)
        checkEnvStatus(environ.get('SETUP_STATUS'))
    if environ.get('SETUP_STATUS') == "1":
        #not first run stuff
        print("* Configuration file detected, loading the validator-toolbox menu application.")
        printStars()
        dotenv.unset_key(dotenv_file, "EASY_VERSION")
        dotenv.set_key(dotenv_file, "EASY_VERSION", easyVersion)
        time.sleep(1)
        checkEnvStatus(environ.get('SETUP_STATUS'))
        nodeType = environ.get("NODE_TYPE")
        if nodeType == "regular":
            if environ.get("VALIDATOR_WALLET") is None:
                setWalletEnv(dotenv_file)
            runRegularNode()
        if nodeType == "full":
            runFullNode()