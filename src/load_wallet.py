import os
import dotenv
from os import environ
from toolbox.config import easy_env
from toolbox.library import loader_intro, set_wallet_env, ask_yes_no, printStars, recover_wallet

if __name__ == "__main__":
    os.system("clear")
    loader_intro()
    print(
        "* Harmony ONE Validator Wallet Import"
    )
    printStars()
    question = ask_yes_no(
            "\n* You will directly utilize the harmony application interface"
            + "\n* We do not store any pass phrases  or data inside of our application"
            + "\n* Respond yes to recover your validator wallet via Mnemonic phrase now or say NO to create a new wallet post-install"
            + "\n* Restore an existing wallet now? (YES/NO) "
        )
    if question:
        dotenv.unset_key(easy_env.dotenv_file, "VALIDATOR_WALLET")
        dotenv.unset_key(easy_env.dotenv_file, "PASS_SWITCH")
        dotenv.unset_key(easy_env.dotenv_file, "NODE_WALLET")
        recover_wallet()
        set_wallet_env()
