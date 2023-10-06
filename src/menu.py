import argparse
from toolbox.config import EnvironmentVariables
from toolbox.library import loader_intro, first_env_check, load_var_file, old_toolbox_check, update_rclone_conf
from toolbox.toolbox import safety_defaults, start_regular_node, parse_flags

def app():
    # Check for old toolbox first
    old_toolbox_check()
    # passed .env check, let's load it!
    check_status = first_env_check(EnvironmentVariables.dotenv_file)
    if check_status == False:
        update_rclone_conf()
    # This section is for hard coding new settings for current users.
    safety_defaults()
    # Run parser if flags added
    parser = argparse.ArgumentParser(description="Harmony Validator Toolbox - Help Menu by EasyNode.pro")
    parse_flags(parser)
    # Run regular validator node
    start_regular_node()

if __name__ == "__main__":
    # load environment variables
    load_var_file(EnvironmentVariables.dotenv_file)
    # Clear screen, show logo
    loader_intro()
    app()
