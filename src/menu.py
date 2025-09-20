import argparse
import os
import hashlib
import shutil
from toolbox.config import config
from toolbox.utils import loader_intro, first_env_check, load_var_file, old_toolbox_check, finish_node
from toolbox.toolbox import safety_defaults, run_regular_node
from toolbox.cli import parse_flags

def check_harmony_sh():
    if os.path.exists(config.harmony_sh_home_path):
        # Check if executable
        if not os.access(config.harmony_sh_home_path, os.X_OK):
            print("* ~/harmony.sh is not executable, fixing permissions...")
            os.chmod(config.harmony_sh_home_path, 0o755)
        
        # Check MD5
        with open(config.harmony_sh_home_path, 'rb') as f:
            home_md5 = hashlib.md5(f.read()).hexdigest()
        with open(config.harmony_sh_toolbox_path, 'rb') as f:
            toolbox_md5 = hashlib.md5(f.read()).hexdigest()
        
        if home_md5 != toolbox_md5:
            print("* ~/harmony.sh is outdated, updating...")
            shutil.copy2(config.harmony_sh_toolbox_path, config.harmony_sh_home_path)
            os.chmod(config.harmony_sh_home_path, 0o755)
            print("* Updated ~/harmony.sh. Please re-run the script for the latest version.")
            finish_node()
    else:
        print("* ~/harmony.sh not found. If you want to use the launcher script, copy it from the toolbox.")

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
    parser = argparse.ArgumentParser(description="Harmony Validator Toolbox - Help Menu by EasyNode.pro")
    parse_flags(parser)
    # Clear screen, show logo
    loader_intro()
    # Run regular validator node
    run_regular_node()

if __name__ == "__main__":
    # load environment variables
    load_var_file(config.dotenv_file)
    app()
