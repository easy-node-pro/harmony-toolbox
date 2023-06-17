import os
import socket
import urllib.request
from os import environ
from concurrent.futures import ThreadPoolExecutor, TimeoutError

def get_url(timeout=5) -> str:
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(urllib.request.urlopen, "https://ident.me")
        try:
            response = future.result(timeout)
            result = response.read().decode("utf8")
        except TimeoutError:
            print("Request timed out.")
            result = '0.0.0.0'
        except Exception as x:
            print(type(x), x)
            result = '0.0.0.0'
    return result

class EnvironmentVariables:
    easy_version = "1.0.6"
    server_host_name = socket.gethostname()
    user_home_dir = os.path.expanduser("~")
    dotenv_file = f"{user_home_dir}/.easynode.env"
    active_user = os.path.split(user_home_dir)[-1]
    harmony_dir = environ.get("HARMONY_DIR") or os.path.join(user_home_dir, "harmony")
    harmony_app = os.path.join(harmony_dir, "harmony")
    bls_key_file = os.path.join(harmony_dir, "blskey.pass")
    hmy_app = os.path.join(harmony_dir, "hmy")
    harmony_conf = os.path.join(harmony_dir, "harmony.conf")
    bls_key_dir = os.path.join(hmy_app, ".hmy", "blskeys")
    hmy_wallet_store = os.path.join(user_home_dir, ".hmy_cli", "account-keys", active_user)
    toolbox_location = os.path.join(user_home_dir, "harmony-toolbox")
    validator_data = os.path.join(toolbox_location, "metadata", "validator.json")
    password_path = os.path.join(harmony_dir, "passphrase.txt")
    external_ip = get_url()
    main_menu_regular = os.path.join(toolbox_location, "src", "messages", "regularmenu.txt")
    main_menu_full = os.path.join(toolbox_location, "src", "messages", "fullmenu.txt")
    rpc_endpoints = ['https://api.s0.t.hmny.io', 'https://api.harmony.one', 'https://rpc.ankr.com/harmony']
    rpc_endpoints_test = ['https://rpc.s0.b.hmny.io', 'https://api.s0.pops.one']
    rpc_endpoints_max_connection_retries = 10
    hmy_tmp_path = '/tmp/hmy'
    harmony_tmp_path = '/tmp/harmony'
