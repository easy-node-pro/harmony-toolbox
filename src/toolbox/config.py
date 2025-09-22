import socket
import requests
import os
import configparser
import random
import subprocess
from os import environ, path
from dotenv import load_dotenv


class Config:
    def __init__(self):
        # Read version from setup.cfg
        config_parser = configparser.ConfigParser()
        setup_cfg_path = path.join(path.dirname(__file__), '..', '..', 'setup.cfg')
        config_parser.read(setup_cfg_path)
        self.easy_version = config_parser.get('metadata', 'version')

        # Host and user information
        self.user_home_dir = path.expanduser("~")
        self.server_host_name = socket.gethostname()
        self.active_user = path.split(self.user_home_dir)[-1]

        # Environment file setup
        self.dotenv_file = f"{self.user_home_dir}/.easynode.env"
        if os.path.exists(self.dotenv_file):
            load_dotenv(self.dotenv_file, override=True)
        else:
            subprocess.run(["touch", self.dotenv_file])

        # Harmony directories and files
        self.harmony_dir = environ.get("HARMONY_DIR") or f"{self.user_home_dir}/harmony"
        self.bls_key_file = path.join(self.harmony_dir, "blskey.pass")
        self.hmy_app = path.join(self.harmony_dir, "hmy")
        self.harmony_conf = path.join(self.harmony_dir, "harmony.conf")
        self.bls_key_dir = path.join(self.harmony_dir, ".hmy", "blskeys")
        self.hmy_wallet_store = path.join(self.user_home_dir, ".hmy_cli", "account-keys", self.active_user)
        self.toolbox_location = path.join(self.user_home_dir, "harmony-toolbox")
        self.validator_data = path.join(self.toolbox_location, "metadata", "validator.json")
        self.password_path = path.join(self.harmony_dir, "passphrase.txt")

        # Wallets and addresses
        self.validator_wallet = environ.get("VALIDATOR_WALLET") or "0xInvalidAddress"
        self.rewards_wallet = environ.get("REWARDS_WALLET") or "0xInvalidAddress"

        # Network and external info
        self.external_ip = self.get_url()
        self.main_menu_regular = path.join(self.toolbox_location, "src", "messages", "regularmenu.txt")

        # RPC endpoints
        self.shard_0_rpc_endpoints = [
            "https://1rpc.io/one",
            "https://api.s0.t.hmny.io",
            "https://api.harmony.one",
            "https://rpc.ankr.com/harmony",
            "https://hmyone-pokt.nodies.app"
        ]
        self.rpc_endpoints_max_connection_retries = 10

        # Temporary paths
        self.hmy_tmp_path = "/tmp/hmy"
        self.harmony_tmp_path = "/tmp/harmony"

        # Folder checks and service defaults
        self.folder_checks = ["harmony", "harmony0", "harmony1", "harmony2", "harmony3", "harmony4"]
        self.shard = environ.get("SHARD") or "4"
        self.harmony_service = environ.get("HARMONY_SERVICE") or "harmony"
        self.pass_switch = environ.get("PASS_SWITCH") or "--passphrase"
        self.gas_reserve = environ.get("GAS_RESERVE") or "5"
        self.refresh_time = environ.get("REFRESH_TIME") or "30"
        self.refresh_option = environ.get("REFRESH_OPTION") or "False"
        self.run_count = environ.get("RUN_COUNT") or 0
        self.print_menu_count = 50  # Number of runs before printing the menu again
        
        

    @staticmethod
    def get_url(timeout=5) -> str:
        try:
            response = requests.get("https://api.ipify.org?format=json", timeout=timeout)
            response.raise_for_status()
            ip_data = response.json()
            return ip_data["ip"]
        except requests.exceptions.RequestException:
            try:
                response = requests.get("https://ident.me", timeout=timeout)
                response.raise_for_status()
                return response.text
            except requests.exceptions.RequestException as x:
                return "0.0.0.0"

    @staticmethod
    def get_working_endpoint(endpoints):
        for endpoint in endpoints:
            try:
                response = requests.get(endpoint, timeout=5)
                if response.status_code == 200:
                    return endpoint
            except requests.exceptions.RequestException:
                pass
        return None

    @property
    def working_rpc_endpoint(self):
        return self.get_working_endpoint(self.shard_0_rpc_endpoints)
        
    @property
    def harmony_sh_home_path(self):
        return path.join(self.user_home_dir, "harmony.sh")

    @property
    def harmony_sh_toolbox_path(self):
        return path.join(self.toolbox_location, "src", "bin", "harmony.sh")

    def validate(self):
        """Validate that essential configurations are set."""
        essential_vars = [
            "easy_version",
            "user_home_dir",
            "server_host_name",
            "active_user",
            "dotenv_file",
            "harmony_dir",
            "bls_key_file",
            "hmy_app",
            "harmony_conf",
            "bls_key_dir",
            "hmy_wallet_store",
            "toolbox_location",
            "validator_data",
            "password_path",
            "validator_wallet",
            "rewards_wallet",
            "external_ip",
            "main_menu_regular",
            "shard_0_rpc_endpoints",
            "rpc_endpoints_max_connection_retries",
            "hmy_tmp_path",
            "harmony_tmp_path",
            "folder_checks",
            "shard",
            "service_name",
            "pass_switch",
            "gas_reserve",
            "refresh_time",
            "refresh_option",
            "run_count",
        ]
        for var in essential_vars:
            if not getattr(self, var):
                raise Exception(f"Config variable {var} is not set!")

# Usage
config = Config()
config.validate()  # Ensure essential configurations are set