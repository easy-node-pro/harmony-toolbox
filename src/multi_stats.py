import os
import json
import subprocess
from os import environ
from ast import literal_eval
from toolbox.config import EnvironmentVariables
from toolbox.library import load_var_file, get_sign_pct, get_wallet_balance, print_stars, set_var, loader_intro, ask_yes_no, version_checks, get_folders, stats_output_regular
from toolbox.toolbox import free_space_check, get_rewards_balance, get_db_size, refresh_stats
from subprocess import PIPE, run
from colorama import Fore, Back, Style
from simple_term_menu import TerminalMenu

load_var_file(EnvironmentVariables.dotenv_file)

if not environ.get("VALIDATOR_WALLET"):
    # ask for wallet, save to env.
    address = input(f'No Harmony $ONE address found, please input a one1 or 0x address: ')
    address_2 = input(f'Please re-enter your address to verify: ')
    if address == address_2:
        set_var(EnvironmentVariables.dotenv_file, "VALIDATOR_WALLET", address_2)

if not environ.get("NETWORK_SWITCH"):
    # ask for mainnet or testnet
    subprocess.run("clear")
    print_stars()
    print("* Setup config not found, which blockchain does this node run on?                           *")
    print_stars()
    print("* [0] - Mainnet                                                                             *")
    print("* [1] - Testnet                                                                             *")
    print_stars()
    menu_options = [
        "[0] Mainnet",
        "[1] Testnet",
    ]
    terminal_menu = TerminalMenu(menu_options, title="Mainnet or Testnet")
    results = terminal_menu.show()
    if results == 0:
        set_var(EnvironmentVariables.dotenv_file, "NETWORK", "mainnet")
        set_var(EnvironmentVariables.dotenv_file, "NETWORK_SWITCH", "t")
        set_var(EnvironmentVariables.dotenv_file, "RPC_NET", "https://rpc.s0.t.hmny.io")
    if results == 1:
        set_var(EnvironmentVariables.dotenv_file, "NETWORK", "testnet")
        set_var(EnvironmentVariables.dotenv_file, "NETWORK_SWITCH", "b")
        set_var(EnvironmentVariables.dotenv_file, "RPC_NET", "https://rpc.s0.b.hmny.io")
    subprocess.run("clear")

def run_multistats():
    loader_intro()
    refresh_stats(1)
    folders = get_folders()
    stats_output_regular(folders)

if __name__ == "__main__":
    run_multistats()