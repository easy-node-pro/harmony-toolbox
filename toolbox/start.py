import os
import time
import dotenv
from os import environ
from utils.config import validatorToolbox
from utils.installer import firstSetup, printStars, recheckVars, setAPIPaths, passphraseStatus, setWalletEnv
from utils.shared import loaderIntro, loadVarFile
from utils.toolbox import runRegularNode, runFullNode


if __name__ == "__main__":
    os.system("clear")
    loaderIntro()
    loadVarFile()
    if os.path.exists(validatorToolbox.dotenv_file) == False:
        firstSetup()
    if environ.get("FIRST_RUN") != "0":
        dotenv.unset_key(validatorToolbox.dotenv_file, "FIRST_RUN")
        dotenv.set_key(validatorToolbox.dotenv_file, "FIRST_RUN", "0")
    print("* Configuration file detected, loading the validatortoolbox menu application.")
    printStars()
    if validatorToolbox.easyVersion != environ.get("EASY_VERSION"):
        dotenv.unset_key(validatorToolbox.dotenv_file, "EASY_VERSION")
        dotenv.set_key(validatorToolbox.dotenv_file, "EASY_VERSION", validatorToolbox.easyVersion)
    time.sleep(1)
    recheckVars()
    setAPIPaths(validatorToolbox.dotenv_file)
    passphraseStatus()
    nodeType = environ.get("NODE_TYPE")
    if nodeType == "regular":
        if environ.get("VALIDATOR_WALLET") is None:
            setWalletEnv(validatorToolbox.dotenv_file)
        runRegularNode()
    if nodeType == "full":
        runFullNode()
    if environ.get("FIRST_RUN"):
        dotenv.unset_key(validatorToolbox.dotenv_file, "FIRST_RUN")
    print("Big problem, contact Easy Node")
    raise SystemExit(0)