import argparse
from toolbox.config import EnvironmentVariables
from toolbox.library import loader_intro, first_env_check, load_var_file, old_toolbox_check, first_setup
from toolbox.toolbox import safety_defaults, start_regular_node, parse_flags

load_var_file(EnvironmentVariables.dotenv_file)

def app():
    # Check for old toolbox first
    old_toolbox_check()
    # Run parser if flags added
    parser = argparse.ArgumentParser(description="Harmony Validator Toolbox - Help Menu by EasyNode.pro")
    parse_flags(parser)
    # passed .env check, let's load it!
    first_time = first_env_check(EnvironmentVariables.dotenv_file, EnvironmentVariables.user_home_dir)
    # If first time, run installer
    if first_time:
        first_setup()
    # This section is for hard coding new settings for current users.
    safety_defaults()
    # Run regular validator node
    start_regular_node()

if __name__ == "__main__":
    # Clear screen, show logo
    loader_intro()
    app()
