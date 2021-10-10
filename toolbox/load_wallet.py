from os import environ
from utils.config import validatorToolbox
from utils.installer import firstSetup, printStars, recheckVars, passphraseStatus
from utils.shared import loaderIntro, setWalletEnv
from utils.toolbox import runRegularNode, runFullNode

if __name__ == "__main__":
    printStars()
    print(
        "* Harmony ONE Validator Wallet Import"
    )
    printStars()
    question = askYesNo(
            "\n* You will directly utilize the harmony application interface"
            + "\n* We do not store any pass phrases  or data inside of our application"
            + "\n* Respond yes to recover your validator wallet via Mnemonic phrase now or say NO to create a new wallet post-install"
            + "\n* Restore an existing wallet now? (YES/NO) "
        )
    if question:
        passphraseStatus()
        recoverWallet()