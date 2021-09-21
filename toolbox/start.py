import os
import time
from os import environ
from utils.installer import *
from utils.shared import loaderIntro, loadVarFile, isFirstRun
from utils.toolbox import runRegularNode, runFullNode


if __name__ == "__main__":
    os.system("clear")
    loaderIntro()
    loadVarFile()
    if environ.get('FIRST_RUN') == "1":
        #first run stuff
        print("* This is the first time you've launched start.py, loading config menus.")
        printStars()
        time.sleep(1)
        dotenv.set_key(dotenv_file, "SETUP_STATUS", "2")
        if environ.get("EASY_VERSION"):
            dotenv.unset_key(dotenv_file, "EASY_VERSION")
        dotenv.set_key(dotenv_file, "EASY_VERSION", easyVersion)
        isFirstRun(dotenv_file)
        loadVarFile()
        if environ.get('SETUP_STATUS') == "0":
            getShardMenu(dotenv_file)
            getNodeType(dotenv_file)
            setMainOrTest(dotenv_file)
            getExpressStatus(dotenv_file)
            loadVarFile()
            checkForInstall()
            setAPIPaths(dotenv_file)
            dotenv.unset_key(dotenv_file, "FIRST_RUN")
            printStars()
            passphraseStatus()
            # load installer
    if environ.get('SETUP_STATUS') == "1":
        #not first run stuff
        print("* Configuration file detected, loading the validatortoolbox menu application.")
        printStars()
        dotenv.unset_key(dotenv_file, "EASY_VERSION")
        dotenv.set_key(dotenv_file, "EASY_VERSION", easyVersion)
        time.sleep(1)
        getShardMenu(dotenv_file)
        getNodeType(dotenv_file)
        setMainOrTest(dotenv_file)
        loadVarFile()
        setAPIPaths(dotenv_file)
        passphraseStatus()
        nodeType = environ.get("NODE_TYPE")
        if nodeType == "regular":
            if environ.get("VALIDATOR_WALLET") is None:
                setWalletEnv(dotenv_file)
            runRegularNode()
        if nodeType == "full":
            runFullNode()
    dotenv.unset_key(dotenv_file, "FIRST_RUN")
    print("Big problem, contact Easy Node")
    raise SystemExit(0)