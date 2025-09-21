import sys
if '-h' in sys.argv or '--help' in sys.argv:
    print("Harmony Validator Toolbox - Help Menu by EasyNodePro.com")
    print()
    print("options:")
    print("  -h, --help           show this help message and exit")
    print("  -s, --stats          Run your stats if Harmony is installed and running.")
    print("  -u, --upgrade        Upgrade your Harmony binary if an upgrade is available.")
    print("  -c, --collect        Collect your rewards to your validator wallet")
    print("  -cs, --collect-send  Collect your rewards to your validator wallet and send them to your rewards wallet")
    print("  -i, --install        Install Harmony ONE and hmy CLI if not installed.")
    print("  -r, --refresh        Enable auto-refresh mode with 10s interval")
    sys.exit(0)

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
    # Check for old toolbox first
    old_toolbox_check()
    # passed .env check, let's load it!
    first_env_check(config.dotenv_file)
    # This section is for hard coding new settings for current users.
    safety_defaults()
    # Check harmony.sh
    check_harmony_sh()
    # Run parser if flags added
    parser = argparse.ArgumentParser(
        description="Harmony Validator Toolbox - Help Menu by EasyNodePro.com"
    )
    parse_flags(parser)
    # Clear screen, show logo
    loader_intro()
    # Run regular validator node
    run_regular_node()


if __name__ == "__main__":
    # load environment variables
    load_var_file(config.dotenv_file)
    app()
