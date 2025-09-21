import socket
import requests
from os import environ, path
from dotenv import load_dotenv
import configparser
import random


class Config:
    def __init__(self):       
        # Read version from setup.cfg
        config_parser = configparser.ConfigParser()
        setup_cfg_path = path.join(path.dirname(__file__), '..', '..', 'setup.cfg')
        config_parser.read(setup_cfg_path)
        self.easy_version = config_parser.get('metadata', 'version')
        
        # Set constants
        self.server_host_name = socket.gethostname()
        self.user_home_dir = path.expanduser("~")
        self.dotenv_file = f"{self.user_home_dir}/.easynode.env"
        # Load env file
        load_dotenv(self.dotenv_file)
        self.active_user = path.split(self.user_home_dir)[-1]
        self.harmony_dir = environ.get("HARMONY_DIR") or f"{self.user_home_dir}/harmony"
        self.bls_key_file = path.join(self.harmony_dir, "blskey.pass")
        self.hmy_app = path.join(self.harmony_dir, "hmy")
        self.harmony_conf = path.join(self.harmony_dir, "harmony.conf")
        self.bls_key_dir = path.join(self.harmony_dir, ".hmy", "blskeys")
        self.hmy_wallet_store = path.join(self.user_home_dir, ".hmy_cli", "account-keys", self.active_user)
        self.toolbox_location = path.join(self.user_home_dir, "harmony-toolbox")
        self.validator_data = path.join(self.toolbox_location, "metadata", "validator.json")
        self.password_path = path.join(self.harmony_dir, "passphrase.txt")
        self.external_ip = self.get_url()
        self.main_menu_regular = path.join(self.toolbox_location, "src", "messages", "regularmenu.txt")
        self.shard_0_rpc_endpoints = ["https://1rpc.io/one", "https://api.s0.t.hmny.io", "https://api.harmony.one", "https://rpc.ankr.com/harmony", "https://hmyone-pokt.nodies.app"]
        self.shard_1_rpc_endpoints = ["https://api.s1.t.hmny.io"] 
        self.rpc_endpoints_max_connection_retries = 10
        self.hmy_tmp_path = "/tmp/hmy"
        self.harmony_tmp_path = "/tmp/harmony"
        self.folder_checks = ["harmony", "harmony0", "harmony1", "harmony2", "harmony3", "harmony4"]
        self.shard = environ.get("SHARD") or "4"

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
        working = []
        for endpoint in endpoints:
            try:
                response = requests.get(endpoint, timeout=5)
                if response.status_code == 200:
                    working.append(endpoint)
            except requests.exceptions.RequestException:
                pass
        if working:
            return random.choice(working)
        return None

    @property
    def working_rpc_endpoint(self):
        if self.shard == "0":
            return self.get_working_endpoint(self.shard_0_rpc_endpoints)
        elif self.shard == "1":
            return self.get_working_endpoint(self.shard_1_rpc_endpoints)
        else:
            # For other shards, default to shard 0 endpoints
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
            "server_host_name",
            "user_home_dir",
            "dotenv_file",
            "active_user",
            "harmony_dir",
            "bls_key_file",
            "hmy_app",
            "harmony_conf",
            "bls_key_dir",
            "hmy_wallet_store",
            "toolbox_location",
            "validator_data",
            "password_path",
            "external_ip",
            "main_menu_regular",
            "shard_0_rpc_endpoints",
            "shard_1_rpc_endpoints",
            "rpc_endpoints_max_connection_retries",
            "hmy_tmp_path",
            "harmony_tmp_path",
            "folder_checks",
            "shard",
        ]
        for var in essential_vars:
            if not getattr(self, var):
                raise Exception(f"Config variable {var} is not set!")

# Usage
config = Config()
config.validate()  # Ensure essential configurations are set