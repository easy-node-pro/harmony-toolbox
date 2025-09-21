import os, requests, time, json, subprocess, pytz
from pytimedinput import timedInteger
from subprocess import PIPE, run
from ast import literal_eval
from toolbox.config import config
from os import environ
from datetime import datetime
from simple_term_menu import TerminalMenu
from colorama import Fore, Back, Style
from pyhmy import blockchain, numbers
from requests.exceptions import HTTPError
from toolbox.utils import (
    process_command,
    print_stars,
    ask_yes_no,
    check_online_version,
    return_txt,
    find_port,
    update_hmy_binary,
    get_sign_pct,
    load_var_file,
    get_wallet_balance,
    get_rewards_balance,
    string_stars,
    set_var,
    free_space_check,
    server_drive_check,
    all_sys_info,
    get_vote_choice,
    get_validator_wallet_name,
    governance_member_voting,
    proposal_choices_option,
    menu_ubuntu_updates,
    menu_reboot_server,
    finish_node,
    update_harmony_binary,
    version_checks,
    harmony_service_status,
    run_command,
    validator_stats_output,
    get_db_size,
    update_text_file,
    recover_wallet,
    refreshing_stats_message,
    passphrase_status,
    clear_temp_files,
    set_network,
    install_harmony,
    clone_shards,
    finish_node_install,
)


def first_setup():
    # Find Shard #
    shard = get_shard_menu()
    # Set mainnet
    set_network("t")
    # Look for a harmony install or install.
    check_for_install(shard)
    return


# looks for ~/harmony or installs it if it's not there. Asks to overwrite if it finds it, run at your own risk.
def check_for_install(shard) -> str:
    if os.path.exists(f"{config.user_home_dir}/harmony"):
        question = ask_yes_no(
            "* You already have a harmony folder on this system, would you like to re-run installation and rclone on this server? (YES/NO)"
        )
        if question:
            install_harmony()
            # Wallet Setup
            recover_wallet()
            # Check passphrase if wallet is added
            passphrase_status()
            print(
                f"* All harmony files now installed. Database download starting now...\n{string_stars()}"
            )
            clone_shards()
            finish_node_install()
        else:
            if os.path.isdir(f"{config.user_home_dir}/harmony"):
                print(
                    "* You have a harmony folder already, skipping install. Returning to menu..."
                )
                return
    else:
        print(f"{Fore.GREEN}* You selected Shard: {environ.get('SHARD')}. ")
        install_harmony()
        # Wallet Setup
        recover_wallet()
        # Check passphrase if wallet is added
        passphrase_status()
        print(
            f"* All harmony files now installed. Database download starting now...\n{string_stars()}"
        )
        clone_shards()
        finish_node_install()
    return


def install_rclone():
    # Fetch the content of the script
    url = "https://rclone.org/install.sh"
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code != 200:
        print("* Failed to download the script.")
        return False

    script_content = response.text

    # Execute the fetched content
    try:
        process = subprocess.Popen(
            ["sudo", "bash"],
            stdin=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        process.communicate(input=script_content.encode())
        if process.returncode != 0:
            return False
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False


def get_folder_choice() -> str:
    print(
        Fore.GREEN
        + f"* Which folder would you like to install harmony in?                              *\n{string_stars()}"
    )
    menu_options = [
        "[1] - harmony",
        "[2] - harmony0",
        "[3] - harmony1",
        "[4] - harmony2",
        "[5] - harmony3",
    ]
    terminal_menu = TerminalMenu(
        menu_options, title="* Please choose your installation folder option. "
    )
    vote_choice_index = terminal_menu.show()
    if vote_choice_index == 6:  # The index of the "Quit" option
        return None, "Quit"
    vote_choice_text = menu_options[vote_choice_index].split(" - ")[1]
    return vote_choice_text


def run_multistats():
    refreshing_stats_message()
    validator_stats_output()
    return


def collect_rewards(
    pending_rewards_balance, validator_wallet, networkCall=config.hmy_app
):
    print(
        f"*\n* Collecting {pending_rewards_balance} $ONE Rewards, awaiting confirmation..."
    )
    command = f"{networkCall} staking collect-rewards --delegator-addr {environ.get('VALIDATOR_WALLET')} --gas-price 100 {environ.get('PASS_SWITCH')}"
    result = run_command(command, print_output=True)
    if result:
        print("*\n*\n* Rewards collection Finished.")
        print_stars()
        print(
            Fore.GREEN
            + f"* mainnet rewards for {validator_wallet} have been collected."
            + Style.RESET_ALL
            + Fore.GREEN
        )
        print_stars()
    else:
        print("*\n*\n* Rewards collection Failed.\n")


def send_rewards(networkCall, sendAmount, rewards_wallet):
    command = f"{networkCall} transfer --amount {sendAmount} --from {environ.get('VALIDATOR_WALLET')} --from-shard 0 --to {rewards_wallet} --to-shard 0 --gas-price 100 {environ.get('PASS_SWITCH')}"
    result = run_command(command, print_output=True)
    if result:
        print("*\n* Rewards sending Finished.")
    else:
        print("*\n* Rewards sending Failed.")


def send_rewards_func(
    suggested_send,
    validator_wallet_balance,
    rewards_wallet,
    validator_wallet,
    bypass=False,
):
    print(
        f"*\n*\n* Sending {suggested_send} $ONE Rewards to {rewards_wallet}, awaiting confirmation..."
    )
    send_rewards(config.hmy_app, suggested_send, rewards_wallet)
    validator_wallet_balance = get_wallet_balance(validator_wallet)
    rewards_wallet_balance = get_wallet_balance(rewards_wallet)
    print(f"*\n* Current Validator Wallet Balance: {validator_wallet_balance} $ONE")
    print(f"* Current Rewards Wallet Balance: {rewards_wallet_balance} $ONE\n*")
    return


def get_shard_menu() -> None:
    if not environ.get("SHARD"):
        print(
            f"{string_stars()}\n* Gathering more information about your server.\n{string_stars()}"
        )
        print(
            f"* Which shard do you want this node to sign blocks on?\n{string_stars()}"
        )
        menu_options = [
            "[0] - Shard 0",
            "[1] - Shard 1",
        ]
        terminal_menu = TerminalMenu(
            menu_options, title="* Which Shard will this node sign blocks on? "
        )
        our_shard = int(terminal_menu.show())

        set_var(config.dotenv_file, "SHARD", str(our_shard))
        return our_shard
    else:
        print(f"* Shard already set to {environ.get('SHARD')}")
        return int(environ.get("SHARD"))


def rewards_sender(
    rewards_wallet=environ.get("REWARDS_WALLET"),
    validator_wallet=environ.get("VALIDATOR_WALLET"),
) -> None:
    validator_wallet_balance = get_wallet_balance(validator_wallet)
    suggested_send = validator_wallet_balance - int(environ.get("GAS_RESERVE"))
    if suggested_send >= 1:
        question = ask_yes_no(
            f"* You have {validator_wallet_balance} $ONE available to send. We suggest sending {suggested_send} $ONE using your reservation settings.\n* Would you like to send {suggested_send} $ONE to {rewards_wallet} now? (YES/NO)"
        )
        if question:
            send_rewards_func(
                suggested_send,
                validator_wallet_balance,
                rewards_wallet,
                validator_wallet,
            )
        else:
            print("*\n* Skipping sending of rewards.")
    else:
        print(
            "*\n* Wallet balance is less than your gas reservation, please try again later."
        )
    validator_wallet_balance = get_wallet_balance(validator_wallet)
    rewards_wallet_balance = get_wallet_balance(rewards_wallet)
    print(
        f"*\n* Current Validator Wallet Balance: {validator_wallet_balance} $ONE\n* Current Rewards Wallet Balance: {rewards_wallet_balance}\n*"
    )
    return


def rewards_collector(
    rpc,
    bypass=False,
    rewards_wallet=environ.get("REWARDS_WALLET"),
    validator_wallet=environ.get("VALIDATOR_WALLET"),
) -> None:
    pending_rewards_balance = get_rewards_balance(rpc, validator_wallet)

    print(
        f"{Fore.GREEN}{string_stars()}\n* Harmony ONE Rewards Collection\n{string_stars()}"
    )

    if bypass or ask_yes_no(
        f"*\n* For your validator wallet {validator_wallet}\n* You have {pending_rewards_balance} $ONE pending.\n* Would you like to collect your rewards on the Harmony {environ.get('NETWORK')}? (YES/NO) "
    ):
        collect_rewards(pending_rewards_balance, validator_wallet)
    else:
        print("*\n* Skipping collection of rewards.")

    validator_wallet_balance = get_wallet_balance(validator_wallet)
    suggested_send = validator_wallet_balance - int(environ.get("GAS_RESERVE"))

    if suggested_send >= 1:
        if bypass or ask_yes_no(
            f"* You have {validator_wallet_balance} $ONE available to send. We suggest sending {suggested_send} $ONE using your reservation settings.\n* Would you like to send {suggested_send} $ONE to {rewards_wallet} now? (YES/NO)"
        ):
            send_rewards_func(
                suggested_send,
                validator_wallet_balance,
                rewards_wallet,
                validator_wallet,
                bypass,
            )
        else:
            print("*\n* Skipping sending of rewards.")
    else:
        rewards_wallet_balance = get_wallet_balance(rewards_wallet)
        print("*\n* Balance too low to send to rewards wallet")
        print(
            f"*\n* Current Validator Wallet Balance: {validator_wallet_balance} $ONE*"
        )
        print(f"* Current Rewards Wallet Balance: {rewards_wallet_balance} $ONE\n*")

    return


def get_shard_menu() -> None:
    if not environ.get("SHARD"):
        print(
            f"{string_stars()}\n* Gathering more information about your server.\n{string_stars()}"
        )
        print(
            f"* Which shard do you want this node to sign blocks on?\n{string_stars()}"
        )
        menu_options = [
            "[0] - Shard 0",
            "[1] - Shard 1",
        ]
        terminal_menu = TerminalMenu(
            menu_options, title="* Which Shard will this node sign blocks on? "
        )
        our_shard = int(terminal_menu.show())

        set_var(config.dotenv_file, "SHARD", str(our_shard))
        return our_shard
    else:
        print(f"* Shard already set to {environ.get('SHARD')}")
        return int(environ.get("SHARD"))


def governance_member_voting():
    options = [
        "AffinityShard",
        "BoxedCloud",
        "Buttheadus",
        "Crypt0Tech",
        "ENTER Group",
        "GGA",
        "Hank The Crank",
        "Kratos",
        "Legion",
        "MetaONE",
        "Nick Vasilich",
        "Octeka.One",
        "One1000Lakes",
        "ONECelestial",
        "PeaceLoveHarmony",
        "PiStake",
        "Quick.One",
        "TEC Viva",
        "Tr4ck3r",
        "Quit",
    ]

    selected_indexes = []
    selected_names = []

    for _ in range(7):
        print(
            Fore.GREEN
            + "* Highlight an option and hit enter to add it to your list.\n* (pick up to 7, 'Quit' to finish if less than 7 selections):"
        )
        terminal_menu = TerminalMenu(options, title="Choose a governance member:")
        choice_index = terminal_menu.show()

        # Check if the "Quit" option was selected
        if choice_index == len(options) - 1:
            print("Quitting the selection process.")
            break

        # Check if the same option was not selected previously
        if choice_index not in selected_indexes:
            selected_indexes.append(choice_index)
            selected_names.append(options[choice_index])
            print(f"You have selected: {options[choice_index]}")
        else:
            print(
                f"You have already selected {options[choice_index]}. Please choose another option."
            )

    # Return selected indexes and names as a string
    selected_indexes_str = (
        "[" + ", ".join(map(str, [index + 1 for index in selected_indexes])) + "]"
    )
    selected_names_str = "[" + ", ".join(selected_names) + "]"
    return selected_indexes_str, selected_names_str


def proposal_choices_option() -> None:
    options = ["HIP-30v2", "Governance for Harmony Recovery Wallet", "Quit"]

    print("* Current proposals:\n*\n*")

    terminal_menu = TerminalMenu(options, title="Choose a proposal to vote on:")
    choice_index = terminal_menu.show()

    # Check if the "Quit" option was selected
    if choice_index == len(options) - 1:
        print("Quitting the voting process.")
        return False, None

    # Ask for a vote on the selected proposal
    selected_proposal = options[choice_index]
    question = ask_yes_no(
        f"* Would you like to vote on {selected_proposal}? (YES/NO): "
    )
    if question:
        return question, selected_proposal
    else:
        return question, None


def get_vote_choice() -> (int, str):
    print(
        Fore.GREEN
        + f"* How would you like to vote on this proposal?                                                 *\n{string_stars()}"
    )
    menu_options = [
        "[1] - Yes",
        "[2] - No",
        "[3] - Abstain",
        "[4] - Quit",
    ]
    terminal_menu = TerminalMenu(
        menu_options, title="* Please choose your voting option. "
    )
    vote_choice_index = terminal_menu.show()
    if vote_choice_index == 3:  # The index of the "Quit" option
        return None, "Quit"
    vote_choice_num = vote_choice_index + 1
    vote_choice_text = menu_options[vote_choice_index].split(" - ")[1]
    return vote_choice_num, vote_choice_text


# Database Downloader
def clone_shards():
    our_shard = environ.get("SHARD")
    load_dotenv(config.dotenv_file)
    # Move to ~/harmony
    os.chdir(f"{environ.get('HARMONY_DIR')}")

    if our_shard != "0":
        # If we're not on shard 0, download the numbered shard DB here.
        print(f"* Now cloning shard {our_shard}\n{string_stars()}")
        run_command(
            f"rclone -P -L --webdav-url 'http://fulldb.s{our_shard}.t.hmny.io/webdav' --checksum sync snap: harmony_db_{our_shard} --multi-thread-streams 4 --transfers=32"
        )
        print(
            f"{string_stars()}\n* Shard {our_shard} completed.\n* Shard 0 will be created when you start your service.\n{string_stars()}"
        )
    if our_shard == "0":
        # If we're on shard 0, grab the snap DB here.
        print(
            f"* Now cloning Shard 0, kick back and relax for awhile...\n{string_stars()}"
        )
        run_command(
            f"rclone -P -L --webdav-url 'http://snapdb.s0.t.hmny.io/webdav' --checksum sync snap: harmony_db_0 --multi-thread-streams 4 --transfers=32"
        )


def finish_node_install():
    load_var_file(config.dotenv_file)
    our_shard = config.shard
    print(
        f"{string_stars()}\n* Installation is completed"
        + "\n* Create a new wallet or recover your existing wallet into ./hmy"
        + "\n* Create or upload your bls key & pass files into ~/harmony/.hmy/blskeys"
        + f"\n* Finally, reboot to start synchronization.\n{string_stars()}"
    )
    if environ.get("NODE_WALLET") == "false":
        print(
            "* Post installation quick tips:"
            + "\n* To recover your wallet on this server run:"
            + "\n* python3 ~/harmony-toolbox/load_wallet.py"
            + "\n*"
            + "\n* To create BLS keys run:"
            + f'\n* {environ.get("HARMONY_DIR")}/hmy keys generate-bls-keys --count 1 --shard {our_shard} --passphrase'
            + f"\n*\n{string_stars()}"
        )
    else:
        print(
            "* Post installation quick tips:"
            + "\n* To recover your wallet again, run:"
            + "\n* python3 ~/harmony-toolbox/load_wallet.py"
            + "\n*"
            + "\n* To create BLS keys run:"
            + f'\n* {environ.get("HARMONY_DIR")}/hmy keys generate-bls-keys --count 1 --shard {our_shard} {environ.get("PASS_SWITCH")}'
            + f"\n*\n{string_stars()}"
        )
    print(
        f"* Thanks for using Easy Node - Validator Node Server Software Installer!\n{string_stars()}"
    )
    raise SystemExit(0)


def menu_topper_regular(software_versions) -> None:
    our_shard = config.shard

    try:
        load_1, load_5, load_15 = os.getloadavg()
        sign_percentage = get_sign_pct()
        validator_wallet_balance = get_wallet_balance(environ.get("VALIDATOR_WALLET"))

        # Not getting remote shard 0 epoch here, investigate.
        remote_data_shard_0, local_data_shard, remote_data_shard = (
            menu_validator_stats()
        )

        # Ensure dictionaries are initialized correctly
        remote_data_shard_0 = (
            remote_data_shard_0 if remote_data_shard_0 is not None else {}
        )
        local_data_shard = local_data_shard if local_data_shard is not None else {}
        remote_data_shard = remote_data_shard if remote_data_shard is not None else {}

        # Safely access epoch information from remote_data_shard_0
        result_0 = remote_data_shard_0.get("result", {})
        current_remote_epoch = result_0.get("shard-chain-header", {}).get("epoch", 0)

        # Safely access block number from remote_data_shard
        result_remote = remote_data_shard.get("result", {})
        shard_header_remote = result_remote.get("shard-chain-header", {})
        remote_shard_block = literal_eval(shard_header_remote.get("number", 0))

        # Safely access block number from local_data_shard
        result_local = local_data_shard.get("result", {})
        shard_header_local = result_local.get("shard-chain-header", {})
        local_shard_block = literal_eval(shard_header_local.get("number", 0))

        # Calculate shard difference
        shard_difference = remote_shard_block - local_shard_block

    except (ValueError, KeyError, TypeError) as e:
        print(f"* Error fetching data: {e}")
        current_remote_epoch = 0
        remote_shard_block = 0
        local_shard_block = 0
        shard_difference = 0

    # Print Menu
    print(
        f"{Fore.GREEN}{string_stars()}\n* Validator Toolbox for {Fore.CYAN}Harmony ONE{Fore.GREEN} Validators by Easy Node   v{config.easy_version}{Fore.WHITE}   https://EasyNodePro.com {Fore.GREEN}\n{string_stars()}"
    )
    print(
        f'* Your validator wallet address is: {Fore.RED}{str(environ.get("VALIDATOR_WALLET"))}{Fore.GREEN}\n* Your $ONE balance is:             {Fore.CYAN}{str(round(validator_wallet_balance, 2))}{Fore.GREEN}\n* Your pending $ONE rewards are:    {Fore.CYAN}{str(round(get_rewards_balance(config.working_rpc_endpoint, environ.get("VALIDATOR_WALLET")), 2))}{Fore.GREEN}\n* Server Hostname & IP:             {Fore.BLUE}{config.server_host_name}{Fore.GREEN} - {Fore.YELLOW}{config.external_ip}{Fore.GREEN}'
    )
    harmony_service_status(environ.get("SERVICE_NAME", "harmony"))
    print(
        f'* Epoch Signing Percentage:         {Style.BRIGHT}{Fore.GREEN}{Back.BLUE}{sign_percentage} %{Style.RESET_ALL}{Fore.GREEN}\n* Current disk space: {Fore.CYAN}{free_space_check(config.harmony_dir): >6}{Fore.GREEN}\n* Current harmony version: {Fore.YELLOW}{software_versions["harmony_version"]}{Fore.GREEN}, has upgrade available: {software_versions["harmony_upgrade"]}\n* Current hmy version: {Fore.YELLOW}{software_versions["hmy_version"]}{Fore.GREEN}, has upgrade available: {software_versions["hmy_upgrade"]}\n{string_stars()}'
    )

    shard_stats_title = f"* Shard {environ.get('SHARD')} Stats:\n{string_stars()}"
    remote_shard_info = f"* Remote Shard {environ.get('SHARD')} Epoch: {current_remote_epoch}, Current Block: {remote_shard_block}"
    local_shard_diff = f"(Diff: {shard_difference})" if shard_difference != 0 else ""
    if our_shard == "0":
        print(
            f"{shard_stats_title}\n{remote_shard_info}{local_shard_diff}, Local Shard 0 Size: {get_db_size(config.harmony_dir, '0')}"
        )
    else:
        print(
            f"{shard_stats_title}\n{remote_shard_info}{local_shard_diff}, Local Shard {environ.get('SHARD')} Size: {get_db_size(config.harmony_dir, environ.get('SHARD'))}"
        )
    print(
        f"* CPU Load Averages: {round(load_1, 2)} over 1 min, {round(load_5, 2)} over 5 min, {round(load_15, 2)} over 15 min\n{string_stars()}"
    )


def menu_regular(software_versions) -> None:
    run_multistats()
    for x in return_txt(config.main_menu_regular):
        x = x.strip()
        try:
            x = eval(x)
        except SyntaxError:
            pass
        if x:
            print(x)


def get_wallet_json(wallet: str) -> str:
    try:
        response = requests.get(
            f"https://api.stake.hmny.io/networks/{environ.get('NETWORK')}/validators/{wallet}"
        )
        response.raise_for_status()
        # access JSOn content
        json_response = response.json()
    #        print("Entire JSON response")
    #        print(json_response)
    except HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        print(
            f'* You have not created your validator yet, try again after you add one!\n* cd ~/harmony\n* ./hmy keys recover-from-mnemonic {config.active_user} {environ.get("PASS_SWITCH")}'
        )
        input("Press ENTER to return to the main menu.")
        return
    except Exception as err:
        print(f"Other error occurred: {err}")
        input("Press ENTER to return to the main menu.")
        return
    return json_response


def tmi_server_info() -> None:
    validator_wallet = environ.get("VALIDATOR_WALLET")
    json_response = get_wallet_json(validator_wallet)
    for key, value in json_response.items():
        print(key, ":", value)
    input(f"{string_stars()}\nPress ENTER to return to the main menu.")


def set_rewards_wallet() -> None:
    rewards_wallet = environ.get("REWARDS_WALLET")
    gas_reserve = environ.get("GAS_RESERVE")
    if rewards_wallet is None:
        question = ask_yes_no(
            "* Would you like to add an address to send your rewards too? (YES/NO)"
        )
        if question:
            rewards_wallet = input(
                "* Input your one1 address to send rewards into, please input your address now: "
            )
            if rewards_wallet.startswith("one1"):
                set_var(config.dotenv_file, "REWARDS_WALLET", rewards_wallet)
            else:
                print("* Wallet does not start with one1, please try again.")
                return
        return
    else:
        question = ask_yes_no(
            f"* Your current saved rewards wallet address is {rewards_wallet}\n* Would you like to update the address you send your rewards too? (YES/NO)"
        )
        if question:
            rewards_wallet = input(
                f"* Input your one1 address to send rewards into, please input your address now: "
            )
            if rewards_wallet.startswith("one1"):
                set_var(config.dotenv_file, "REWARDS_WALLET", rewards_wallet)
            else:
                print("* Wallet does not start with one1, please try again.")
                return
            set_gas_reserve()
            return
        else:
            question = ask_yes_no(
                f"* Your current wallet gas reservation is {gas_reserve} $ONE\n* Would you like to update your reservation total? (YES/NO)"
            )
            if question:
                set_gas_reserve()
                return
    return


def set_gas_reserve() -> None:
    gas_reserve = environ.get("GAS_RESERVE")
    question = ask_yes_no(
        f"* Your current total of $ONE to reserve for fees is {gas_reserve}\n* Would you like to update the reserve total? (YES/NO)"
    )
    if question:
        ask_reserve_total()
    return


def ask_reserve_total() -> None:
    reserve_total = input("* How much $ONE would you like to keep reserved for fees? ")
    set_reserve_total(reserve_total)
    return


def set_reserve_total(reserve_total):
    set_var(config.dotenv_file, "GAS_RESERVE", reserve_total)


def drive_check() -> None:
    server_drive_check(config.dotenv_file, config.harmony_dir)
    return


def bingo_checker():
    command = f"grep BINGO {config.harmony_dir}/latest/zerolog-harmony.log | tail -10"
    process_command(command, shell=True, print_output=True)
    print(
        f"{string_stars()}\n* Press enter to return to the main menu.\n{string_stars()}"
    )
    input()


def run_rewards_collector() -> None:
    rewards_collector(config.working_rpc_endpoint)
    return


def safety_defaults() -> None:
    # clean files
    clear_temp_files()
    check_online_version()
    # Set default ENV settings if they don't exist
    set_var(config.dotenv_file, "EASY_VERSION", config.easy_version)
    if environ.get("GAS_RESERVE") is None:
        set_var(config.dotenv_file, "GAS_RESERVE", "5")
    if environ.get("REFRESH_TIME") is None:
        set_var(config.dotenv_file, "REFRESH_TIME", "30")
    if environ.get("REFRESH_OPTION") is None:
        set_var(config.dotenv_file, "REFRESH_OPTION", "True")
    if environ.get("HARMONY_DIR") is None:
        if os.path.isdir(f"{config.user_home_dir}/harmony"):
            set_var(
                config.dotenv_file, "HARMONY_DIR", f"{config.user_home_dir}/harmony"
            )
            set_var(config.dotenv_file, "SERVICE_NAME", "harmony")
            return
        elif os.path.isfile(f"{config.user_home_dir}/harmony"):
            print(
                f"* It appears your don't have harmony binary in a folder. We're exiting as we're not compatible. Install harmony on a fresh server with toolbox to become compatible or read our docs.\n* Error: {e}"
            )
            raise SystemExit(0)
        else:
            first_setup()
    if environ.get("SERVICE_NAME") is None:
        set_var(config.dotenv_file, "SERVICE_NAME", "harmony")
    # set blskey.pass file if it exists
    if os.path.isfile(f"{config.harmony_dir}/blskey.pass"):
        update_text_file(
            config.harmony_conf, 'PassFile = ""', 'PassFile = "blskey.pass"'
        )
    passphrase_status()
    get_shard_menu()
    # Set mainnet
    set_network("t")
    if environ.get("VALIDATOR_WALLET") is None:
        # Recover wallet or have them add address
        recover_wallet()
    # Any more pre-gather info here?
    return


def refresh_toggle() -> None:
    if environ.get("REFRESH_OPTION") == "True":
        answer = ask_yes_no(
            f"* Refresh is currently enabled. Would you like to disable it? (Y/N) "
        )
        if answer:
            set_var(config.dotenv_file, "REFRESH_OPTION", "False")
        else:
            answer = ask_yes_no(
                f'* Your current refresh time is {str(environ.get("REFRESH_TIME"))} seconds. Would you like to change the delay? (Y/N) '
            )
            if answer:
                delay_time = timedInteger(
                    "* Enter the number of seconds to wait before auto-refreshing: ",
                    timeout=-1,
                    resetOnInput=True,
                    allowNegative=False,
                )
                set_var(config.dotenv_file, "REFRESH_TIME", str(delay_time[0]))
    else:
        answer = ask_yes_no(
            f"* Refresh is currently disabled. Would you like to enable it? (Y/N) "
        )
        if answer:
            set_var(config.dotenv_file, "REFRESH_OPTION", "True")
        answer = ask_yes_no(
            f'* Your current refresh time is {str(environ.get("REFRESH_TIME"))} seconds. Would you like to change the delay? (Y/N) '
        )
        if answer:
            delay_time = timedInteger(
                "* Enter the number of seconds to wait before auto-refreshing: ",
                timeout=-1,
                resetOnInput=True,
                allowNegative=False,
            )
            set_var(config.dotenv_file, "REFRESH_TIME", str(delay_time[0]))
    load_var_file(config.dotenv_file)
    return


def update_stats_option() -> None:
    if environ.get("REFRESH_OPTION") == "True":
        print(
            f"*  20 - Disable auto-update       - Disable Refresh or Change Delay Timer: {str(environ.get('REFRESH_TIME'))} seconds"
        )
    else:
        print(f"*  20 - Enable Auto update        - Enable Update Timer")


def harmony_voting() -> None:
    # Specify the deadline in UTC
    utc = pytz.utc
    # Deadline to go inactive, currently passed
    deadline = utc.localize(datetime(2023, 8, 9, 20, 59))

    # Get the current time in UTC
    current_time = datetime.now(utc)

    # Check if the current time is before or after the deadline
    active_vote = current_time < deadline

    if active_vote:
        print(f"{string_stars()}\n* Harmony Voting\n{string_stars()}")
        question, proposal = proposal_choices_option()
        if proposal == "Quit" or question == False:
            return
        validator_wallet_name = get_validator_wallet_name(
            environ.get("VALIDATOR_WALLET")
        )
        if proposal == "HIP-30v2":
            vote_choice_option, vote_choice_text = get_vote_choice()
            if vote_choice_text == "Quit":
                return
            print(
                f"* Voting for {vote_choice_option} - {vote_choice_text} on proposal {proposal}\n* Please enter your validator wallet password now: \n"
            )
            command = f"{environ.get('HARMONY_DIR')}/hmy governance vote-proposal --space harmony-mainnet.eth --proposal 0xce5f516c683170e4164a06e42dcd487681f46f42606b639955eb7c0fa3b13b96 --proposal-type single-choice --choice {vote_choice_option} --key {validator_wallet_name} --passphrase"
            process_command(
                command,
                True,
                True,
            )
        if proposal == "Governance for Harmony Recovery Wallet":
            vote_choice_option, vote_choice_names_list = governance_member_voting()
            vote_choice_names = "\n* ".join(
                vote_choice_names_list[1:-1].split(", ")
            )  # Extracting the names and formatting them
            question = ask_yes_no(
                f"* You have selected\n*\n* {vote_choice_names}\n*\n* Are you sure you want to vote for this list?  (Yes/No) "
            )
            if question:
                print(
                    f"* Voting for {vote_choice_option} - {vote_choice_names_list} on proposal {proposal}\n* Please enter your validator wallet password now: \n"
                )
                command = f"{environ.get('HARMONY_DIR')}/hmy governance vote-proposal --space harmony-mainnet.eth --proposal 0x80b87627254aa71870407a3c95742aa30c0e5ccdc81da23a1a54dcf0108778ae --proposal-type approval --choice \"{vote_choice_option}\" --key {validator_wallet_name} --passphrase"
                process_command(
                    command,
                    True,
                    True,
                )
            else:
                print("*\n* Returning to menu...")
    else:
        print(f"* Voting is currently closed, please try again later.")
    return


def run_regular_node() -> None:
    menu_options = {
        0: finish_node,
        1: refreshing_stats_message,
        2: menu_active_bls,
        3: bingo_checker,
        4: run_rewards_collector,
        5: rewards_sender,
        6: set_rewards_wallet,
        7: harmony_voting,
        8: menu_service_stop_start,
        9: menu_service_restart,
        10: harmony_binary_upgrade,
        11: hmy_cli_upgrade,
        12: menu_ubuntu_updates,
        13: drive_check,
        14: tmi_server_info,
        15: all_sys_info,
        20: refresh_toggle,
        999: menu_reboot_server,
    }
    while True:
        load_var_file(config.dotenv_file)
        software_versions = version_checks(environ.get("HARMONY_DIR"))
        menu_regular(software_versions)
        if environ.get("REFRESH_OPTION") == "True":
            try:
                # run timed input
                option, timedOut = timedInteger(
                    f"* Auto refresh enabled, Enter your menu choice: ",
                    timeout=int(environ.get("REFRESH_TIME")),
                    resetOnInput=True,
                    allowNegative=False,
                )
                if timedOut:
                    run_regular_node()
                else:
                    print_stars()
                    menu_options[option]()
                    if option != 1:
                        run_regular_node()
            except KeyError:
                print("* Bad option, try again. Press enter to continue.")
                print_stars()
                input()
                run_regular_node()
        else:
            try:
                option, timedOut = timedInteger(
                    "* Auto refresh disabled, Enter your menu choice: ",
                    timeout=-1,
                    resetOnInput=True,
                    allowNegative=False,
                )
                print_stars()
                menu_options[option]()
                if option != 1:
                    run_regular_node()
            except KeyError:
                print(f"* Bad option, try again. Press enter to continue.")
                print_stars()
                input()
                run_regular_node()


def service_menu_option() -> None:
    status = process_command(
        f"systemctl is-active --quiet {environ.get('SERVICE_NAME')}", True, False
    )
    if status:
        print(
            f"*   8 - {Fore.RED}Stop Harmony Service      {Fore.GREEN}- {Fore.YELLOW}{Back.RED}WARNING: You will miss blocks while stopped!   {Style.RESET_ALL}{Fore.GREEN}"
        )
        print(
            f"*   9 - Restart Harmony Service   - {Back.RED}{Fore.YELLOW}WARNING: You will miss blocks during a restart!{Style.RESET_ALL}{Fore.GREEN}"
        )
    else:
        print("*   8 - Start Harmony Service")
    return


def update_menu_option(software_versions) -> None:
    if software_versions["harmony_upgrade"] == "True":
        print(
            f"*  10 - Update Harmony App Binary - For New Harmony Releases ONLY, {Fore.YELLOW}{Back.RED}WARNING: You will miss blocks during upgrade.{Style.RESET_ALL}{Fore.GREEN}"
        )
    if software_versions["hmy_upgrade"] == "True":
        print(
            "*  11 - Update hmy CLI App        - Update harmony binary file, run anytime!"
        )


def hip_voting_option() -> None:
    # Specify the deadline in UTC
    utc = pytz.utc
    # Deadline to go inactive, currently passed
    deadline = utc.localize(datetime(2023, 8, 9, 20, 59))

    # Get the current time in UTC
    current_time = datetime.now(utc)

    # Check if the current time is before or after the deadline
    active_vote = current_time < deadline

    if active_vote:
        print("*   7 - Harmony Governance Voting - Cast your vote for HIP-30v2")
    else:
        print("*   7 - Harmony Governance Voting - No votes currently active.")


def rewards_sender_option() -> None:
    if environ.get("REWARDS_WALLET"):
        print(
            "*   5 - Send Wallet Balance       - Send your wallet balance - saved gas to rewards wallet"
        )
        print(
            "*   6 - Set Rewards Wallet        - Update your saved wallet or gas reserve"
        )
    else:
        print(
            "*   6 - Set Rewards Wallet        - Set up a one1 wallet address to send rewards when using option #4"
        )
    return


def make_backup_dir() -> str:
    folder_name = (
        f'{config.harmony_dir}/harmony_backup/{datetime.now().strftime("%Y%m%d%H%M")}'
    )
    process_command(f"mkdir -p {folder_name}")
    return folder_name


def hmy_cli_upgrade():
    question = ask_yes_no(
        "* Are you sure you would like to proceed with updating the Harmony CLI file?\n\nType 'Yes' or 'No' to continue"
    )

    if not question:
        print("* Update canceled.")
        return

    try:
        # Backup the current version of hmy CLI
        folder_name = make_backup_dir()
        process_command(f"cp {environ.get('HARMONY_DIR')}/hmy {folder_name}")
        print_stars()

        # Install the new version
        software_versions = update_hmy_binary()
        print_stars()

        # Print the updated version
        print(f"Harmony cli has been updated to: {software_versions['hmy_version']}")
        print_stars()

        # Update the environment variable
        set_var(config.dotenv_file, "HMY_UPGRADE_AVAILABLE", "False")

    except (
        Exception
    ) as e:  # Catch generic errors, though you might want to catch more specific exceptions
        print(
            f"{string_stars()}\n* An error occurred during the update: {e}\n{string_stars()}"
        )
        # Handle the error or possibly re-raise it depending on your requirements
        return

    input("* Update completed, press ENTER to return to the main menu. ")


def update_harmony_app():
    our_shard = config.shard
    os.chdir(f"{config.harmony_dir}")
    print(f"{string_stars()}\nCurrently installed version: ")
    process_command("./harmony -V")
    folder_name = make_backup_dir()
    process_command(
        f"cp {config.harmony_dir}/harmony {config.harmony_dir}/harmony.conf {folder_name}"
    )
    update_harmony_binary()
    print(f"{string_stars()}\nUpdated version: ")
    process_command("./harmony -V")
    if our_shard != "0":
        size = 0
        for path, dirs, files in os.walk(f"{config.harmony_dir}/harmony_db_0"):
            for f in files:
                fp = os.path.join(path, f)
                size += os.path.getsize(fp)
            if size >= 500000000:
                question = ask_yes_no(
                    Fore.WHITE
                    + "* Are you sure you would like to proceed with upgrading and trimming database 0?\n\nType 'Yes' or 'No' to continue"
                )
                if question:
                    process_command(f"sudo service {environ.get('SERVICE_NAME')} stop")
                    process_command(
                        f"mv {config.harmony_dir}/harmony_db_0 {config.harmony_dir}/harmony_db_0_old"
                    )
                    process_command(f"sudo service {environ.get('SERVICE_NAME')} start")
                    process_command(f"rm -r {config.harmony_dir}/harmony_db_0_old")
                else:
                    print(
                        "Skipping removal of 0, but it's no longer required, get your space back next time by running this prune, fyi!"
                    )
            else:
                print("Your database 0 is already trimmed, enjoy!")
    process_command(f"sudo service {environ.get('SERVICE_NAME')} restart")
    print(
        f"{string_stars()}\nHarmony Service is restarting, waiting 10 seconds for processing to resume..."
    )
    set_var(config.dotenv_file, "HARMONY_UPGRADE_AVAILABLE", "False")
    time.sleep(10)


def menu_validator_stats():
    load_var_file(config.dotenv_file)
    our_shard = config.shard
    api_endpoint = config.working_rpc_endpoint
    remote_shard_0 = [
        f"{config.hmy_app}",
        "blockchain",
        "latest-headers",
        f"--node={api_endpoint}",
    ]
    try:
        result_remote_shard_0 = run(
            remote_shard_0, stdout=PIPE, stderr=PIPE, universal_newlines=True
        )
        remote_data_shard_0 = json.loads(result_remote_shard_0.stdout)

        # Check if the remote data is empty or None
        if not remote_data_shard_0:
            raise ValueError("Empty or None data")
    except (ValueError, KeyError, TypeError) as e:
        print(f"* Remote Shard 0 Offline, Please try again later.\n* Error {e}")
        finish_node()
    try:
        http_port = find_port(environ.get("HARMONY_DIR"))
        local_shard = [
            f"{environ.get('HARMONY_DIR')}/hmy",
            "blockchain",
            "latest-headers",
            "--node",
            f"http://localhost:{http_port}",
        ]
        result_local_shard = run(
            local_shard, stdout=PIPE, stderr=PIPE, universal_newlines=True
        )
        local_data_shard = json.loads(result_local_shard.stdout)

        # Check if the local data is empty or None
        if not local_data_shard:
            raise ValueError("Empty or None data")
    except (ValueError, KeyError, TypeError) as e:
        print(
            f"* Local Server Offline\n*\n* Run troubleshooting, See our documents site for info on how to manually troubleshoot:\n* https://docs.EasyNodePro.com/harmony/post#validator-toolbox-troubleshooting\n{string_stars()}"
        )
        finish_node()

    if our_shard != "0":
        remote_shard = [
            f"{config.hmy_app}",
            "blockchain",
            "latest-headers",
            f"--node=https://api.s1.t.hmny.io",
        ]
        try:
            result_remote_shard = run(
                remote_shard, stdout=PIPE, stderr=PIPE, universal_newlines=True
            )
            remote_data_shard = json.loads(result_remote_shard.stdout)

            # Check if the remote data is empty or None
            if not remote_data_shard:
                raise ValueError("Empty or None data")

            return remote_data_shard_0, local_data_shard, remote_data_shard
        except (ValueError, KeyError, TypeError):
            return

    return remote_data_shard_0, local_data_shard, None


def shard_stats(our_shard) -> str:
    our_uptime = subprocess.getoutput("uptime")
    db_0_size = get_db_size(config.harmony_dir, "0")
    if our_shard == "0":
        print(
            f"""
    * Uptime :: {our_uptime}\n\n Harmony DB 0 Size  ::  {db_0_size}
    {string_stars()}
        """
        )
    else:
        print(
            f"""
    * Uptime :: {our_uptime}
    *
    * Harmony DB 0 Size  ::  {db_0_size}
    * Harmony DB {our_shard} Size  ::   {get_db_size(config.harmony_dir, str(our_shard))}
    *
    *
    {string_stars()}
        """
        )


def harmony_binary_upgrade():
    our_shard = config.shard
    if our_shard == "0" or our_shard == "1":
        question = ask_yes_no(
            Fore.RED
            + "* WARNING: YOU WILL MISS BLOCKS WHILE YOU UPGRADE THE HARMONY SERVICE.\n\n"
            + Fore.WHITE
            + "* Are you sure you would like to proceed?\n\nType 'Yes' or 'No' to continue"
        )
        if question:
            update_harmony_app()
    else:
        print(
            "* We do not support upgrading shards 2/3 any longer, please upgrade manually if you'd like to update for now.\n* See the harmony discord here for more details on upgrading: https://discord.com/channels/532383335348043777/616699767594156045/1164484026413895742"
        )


def menu_service_stop_start():
    menu_service_stop_start_trigger(environ.get("HARMONY_SERVICE"))


def menu_service_stop_start_trigger(service) -> str:
    status = process_command(f"systemctl is-active --quiet {service}")
    if status != 0:
        process_command(f"sudo service {environ.get('SERVICE_NAME')} start")
        print()
        print("* Harmony Service Has Been Started.")
        print()
        input("* Press ENTER to return to the main menu.")
    else:
        question = ask_yes_no(
            "*********\n"
            + Fore.RED
            + "* WARNING: YOU WILL MISS BLOCKS IF YOU STOP THE HARMONY SERVICE.\n\n"
            + Fore.WHITE
            + "* Are you sure you would like to proceed?\n\nType 'Yes' or 'No' to continue"
        )
        if question:
            process_command(f"sudo service {environ.get('SERVICE_NAME')} stop")
            print()
            print(
                "* Harmony Service Has Been Stopped. "
                + Fore.RED
                + "YOU ARE MISSING BLOCKS ON THIS NODE."
                + Style.RESET_ALL
                + Fore.GREEN
            )
            print()
            input("* Press ENTER to return to the main menu.")


def menu_service_restart() -> str:
    question = ask_yes_no(
        "*********\n"
        + Fore.RED
        + "WARNING: YOU WILL MISS BLOCKS UNTIL RESTART IS COMPLETED & SYNC CATCHES UP!\n\n"
        + Fore.WHITE
        + "Are you sure you would like to proceed?\n\nType 'Yes' or 'No' to continue"
    )
    if question:
        process_command(f"sudo service {environ.get('SERVICE_NAME')} restart")
        print()
        print("* The Harmony Service Has Been Restarted")
        input("* Press ENTER to return to the main menu.")


def menu_active_bls() -> str:
    validator_wallet = environ.get("VALIDATOR_WALLET")
    json_response = get_wallet_json(validator_wallet)
    print("* This is a list of your BLS Keys that are active for the next election.")
    for i, x in enumerate(json_response["bls-public-keys"]):
        print(f"BLS Key {i+1} {x}")
    print(
        f"{string_stars()}\n* Press ENTER to return to the main menu.\n{string_stars()}"
    )
    input()
