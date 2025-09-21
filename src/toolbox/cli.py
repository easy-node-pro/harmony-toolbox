import argparse
from toolbox.utils import (
    finish_node,
    set_var,
    load_var_file,
    get_folders,
    ask_yes_no,
)
from toolbox.toolbox import (
    update_harmony_app,
    run_multistats,
    rewards_collector,
    first_setup,
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
        "-u",
        "--upgrade",
        action="store_true",
        help="Upgrade your Harmony binary if an upgrade is available.",
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
        "-r",
        "--refresh",
        action="store_true",
        help="Enable auto-refresh mode with 10s interval",
    )

    args = parser.parse_args()

    if args.install:
        if get_folders():
            question = ask_yes_no("* It appears you already have Harmony installed. Would you like to install a 2nd service? (YES/NO)")
            if question:
                print("* To install a 2nd service, please contact us via our Discord on https://EasyNodePro.com/links by sending in a help ticket for assistance.")
            finish_node()
        else:
            first_setup()

    if args.install_second:
        if get_folders():
            print("* To install a 2nd service, please contact us via our Discord on https://EasyNodePro.com/links by sending in a help ticket for assistance.")
        else:
            print("* It appears you do not have Harmony installed. Please run the install command without the -is flag to install your first Harmony service.")
        finish_node()

    if args.upgrade:
        update_harmony_app()

    if args.stats:
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
        rewards_collector(config.working_rpc_endpoint)
        finish_node()

    if args.collect_send:
        rewards_collector(config.working_rpc_endpoint, True)
        finish_node()

    if args.refresh:
        set_var(config.dotenv_file, "REFRESH_OPTION", "True")
        set_var(config.dotenv_file, "REFRESH_TIME", "10")
        load_var_file(config.dotenv_file)
