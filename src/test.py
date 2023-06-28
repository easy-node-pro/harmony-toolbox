import psutil, platform, dotenv, time, os, subprocess, requests, pyhmy, shutil, hashlib, re
from os import environ
from dotenv import load_dotenv
from simple_term_menu import TerminalMenu
from colorama import Fore, Style
from pathlib import Path
from pyhmy import validator, account, staking, numbers
from json import load, dump
from toolbox.config import EnvironmentVariables
from collections import namedtuple
from datetime import datetime

load_dotenv(EnvironmentVariables.dotenv_file)


class print_stuff:
    def __init__(self, reset: int = 0):
        self.reset = reset
        self.print_stars = "*" * 93
        self.reset_stars = self.print_stars + Style.RESET_ALL + Fore.GREEN

    def printStars(self) -> None:
        p = self.print_stars
        if self.reset:
            p = self.reset_stars
        print(p)

    def stringStars(self) -> str:
        p = self.print_stars
        if self.reset:
            p = self.reset_stars
        return p

    @classmethod
    def printWhitespace(self) -> None:
        print("\n" * 8)


print_whitespace = print_stuff.printWhitespace
print_stars = print_stuff().printStars
string_stars = print_stuff().stringStars
print_stars_reset = print_stuff(reset=1).printStars
string_stars_reset = print_stuff(reset=1).stringStars

def get_sign_pct() -> str:
    rpc_endpoint = EnvironmentVariables.working_rpc_endpoint
    hmy_external_rpc = f"{EnvironmentVariables.hmy_app} --node='{rpc_endpoint}'"
    print(hmy_external_rpc)
    output = subprocess.getoutput(
        f"{hmy_external_rpc} blockchain validator information {environ.get('VALIDATOR_WALLET')} | grep signing-percentage"
    )
    print(output)
    output_stripped = output.lstrip('        "current-epoch-signing-percentage": "').rstrip('",')
    try:
        math = float(output_stripped)
        signPerc = math * 100
        roundSignPerc = round(signPerc, 6)
        return str(roundSignPerc)
    except (OSError, ValueError):
        output_stripped = "0"
        return str(output_stripped)
    
get_sign_pct()