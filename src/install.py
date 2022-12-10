import os
from os import environ
from toolbox.config import easy_env
from toolbox.library import loader_intro, load_var_file, first_setup, recover_wallet

if __name__ == "__main__":
    os.system("clear")
    loader_intro()
    if not os.path.exists(easy_env.dotenv_file):
        first_setup()
    load_var_file()
    if not environ.get("VALIDATOR_WALLET"):
        recover_wallet()
        if not environ.get("VALIDATOR_WALLET"):
            print(
                "* You don't currently have a validator wallet address loaded in your .env file, please edit ~/.easynode.env and add a line with the following info:\n "
                + "* VALIDATOR_WALLET='validatorONEaddress' "
            )
            input("* Press any key to exit.")
            raise SystemExit(0)
    exec(open(f"{easy_env.toolbox_location}menu.py").read())
