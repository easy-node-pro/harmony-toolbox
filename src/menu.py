import argparse
from toolbox.config import config
from toolbox.library import loader_intro, first_env_check, load_var_file, old_toolbox_check
from toolbox.toolbox import safety_defaults, run_regular_node, parse_flags

def app():
    # Check for old toolbox first
    old_toolbox_check()
    # passed .env check, let's load it!
    first_env_check(config.dotenv_file)
    # This section is for hard coding new settings for current users.
    safety_defaults()
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
