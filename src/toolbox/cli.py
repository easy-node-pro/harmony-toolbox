import argparse
import os
from toolbox.utils import (
    finish_node,
    set_var,
    load_var_file,
    get_folders,
    ask_yes_no,
    first_env_check,
)
from toolbox.toolbox import (
    harmony_binary_upgrade,
    update_harmony_app,
    run_multistats,
    rewards_collector,
    first_setup,
    multi_setup,
)
from toolbox.config import config


def parse_flags(parser):
    # Add the arguments
    parser.add_argument(
        "-s",
        "--stats",
        action="store_true",
        help="Run your stats if Harmony is installed and running.",
    )

    parser.add_argument(
        "-r",
        "--refresh",
        action="store_true",
        help="Refresh stats continuously every 10 seconds.",
    )

    parser.add_argument(
        "-uh",
        "--upgrade-harmony",
        action="store_true",
        help="Upgrade your harmony file if an upgrade is available.",
    )

    parser.add_argument(
        "-uhmy",
        "--upgrade-hmy",
        action="store_true",
        help="Upgrade your hmy file if an upgrade is available.",
    )

    parser.add_argument(
        "-c",
        "--collect",
        action="store_true",
        help="Collect your rewards to your validator wallet",
    )

    parser.add_argument(
        "-cs",
        "--collect-send",
        action="store_true",
        help="Collect your rewards to your validator wallet and send them to your rewards wallet",
    )

    parser.add_argument(
        "-i",
        "--install",
        action="store_true",
        help="Install Harmony ONE and hmy CLI if not installed.",
    )

    parser.add_argument(
        "-is",
        "--install-second",
        action="store_true",
        # help="Install a second Harmony ONE service if you already have one installed.",
    )

    parser.add_argument(
        "-f",
        "--folder",
        help="Specify the harmony folder to use (e.g., harmony0).",
    )

    parser.add_argument(
        "--default-folder",
        action="store_true",
        help="Set a new default folder.",
    )

    args = parser.parse_args()

    if args.folder:
        os.environ["SELECTED_FOLDER"] = args.folder

    if args.default_folder:
        load_var_file(config.dotenv_file)
        folders = get_folders()
        if not folders:
            print("* No harmony folders found.")
            finish_node()
        print("* Select a folder to set as default:")
        for i, f in enumerate(folders.keys()):
            print(f"  {i+1}. {f}")
        while True:
            try:
                choice = int(input("* Select folder number: ")) - 1
                if 0 <= choice < len(folders):
                    folder_name = list(folders.keys())[choice]
                    set_var(config.dotenv_file, "HARMONY_DIR", f"{config.user_home_dir}/{folder_name}")
                    print(f"* Default folder set to: {folder_name}")
                    finish_node()
                else:
                    print("* Invalid choice.")
            except ValueError:
                print("* Please enter a number.")

    if args.install:
        if get_folders():
            question = ask_yes_no("* It appears you already have Harmony installed. Would you like to install another service? (YES/NO)")
            if question:
                print("* To install another service, please contact us via our Discord on https://EasyNodePro.com/links by sending in a help ticket for assistance.")
            finish_node()
        else:
            first_setup()

    if args.install_second:
        if get_folders():
            question = ask_yes_no("* It appears you already have Harmony installed. Would you like to install another service? (YES/NO)")
            if question:
                multi_setup()
            finish_node()
        else:
            first_setup()

    if args.upgrade:
        first_env_check(config.dotenv_file)
        update_harmony_app()

    if args.upgrade_hmy:
        first_env_check(config.dotenv_file)
        harmony_binary_upgrade()

    if args.stats:
        first_env_check(config.dotenv_file)
        if args.refresh:
            import time

            try:
                while True:
                    run_multistats()
                    time.sleep(10)
            except KeyboardInterrupt:
                print("\n* Exiting watch mode.")
                finish_node()
        else:
            run_multistats()
            finish_node()

    if args.collect:
        first_env_check(config.dotenv_file)
        rewards_collector(config.working_rpc_endpoint)
        finish_node()

    if args.collect_send:
        first_env_check(config.dotenv_file)
        rewards_collector(config.working_rpc_endpoint, True)
        finish_node()

    if args.refresh:
        settings_file = os.path.join(config.toolbox_location, "settings.txt")
        with open(settings_file, "w") as f:
            f.write("REFRESH_OPTION=True\nREFRESH_TIME=10\n")
