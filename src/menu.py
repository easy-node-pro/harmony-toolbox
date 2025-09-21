import sys
import argparse
import os
import hashlib
import shutil
from toolbox.config import config
from toolbox.utils import (
    loader_intro,
    first_env_check,
    load_var_file,
    old_toolbox_check,
    check_harmony_sh,
)
from toolbox.toolbox import safety_defaults, run_regular_node
from toolbox.cli import parse_flags


def app():
    # Run parser first to handle help and flags
    parser = argparse.ArgumentParser(
        description="Harmony Validator Toolbox - Help Menu by EasyNodePro.com"
    )
    parse_flags(parser)
    # Check for old toolbox first
    old_toolbox_check()
    # passed .env check, let's load it!
    first_env_check(config.dotenv_file)
    # This section is for hard coding new settings for current users.
    safety_defaults()
    # Check harmony.sh
    check_harmony_sh()
    # Clear screen, show logo
    loader_intro()
    # Run regular validator node
    run_regular_node()


if __name__ == "__main__":
    # load environment variables
    load_var_file(config.dotenv_file)
    app()
