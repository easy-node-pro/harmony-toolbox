import os
import socket
import urllib.request

def get_url() -> None:
    try:
        result = urllib.request.urlopen("https://ident.me").read().decode("utf8")
    except Exception as x:
        print(type(x),x)
        result = '0.0.0.0'
        pass
    return result

class easy_env:
    easy_version = "1.8.4"
    server_host_name = socket.gethostname()
    user_home_dir = os.path.expanduser("~")
    dotenv_file = f"{user_home_dir}/.easynode.env"
    active_user = os.path.split(user_home_dir)[-1]
    harmony_folder_name = f'harmony'
    harmony_dir = os.path.join(user_home_dir, "harmony")
    harmony_app = os.path.join(harmony_dir, "harmony")
    bls_key_file = os.path.join(harmony_dir, "blskey.pass")
    hmy_app = os.path.join(harmony_dir, "hmy")
    harmony_conf = os.path.join(harmony_dir, "harmony.conf")
    bls_key_dir = os.path.join(hmy_app, ".hmy", "blskeys")
    hmy_wallet_store = os.path.join(user_home_dir, ".hmy_cli", "account-keys", active_user)
    toolbox_location = os.path.join(user_home_dir, "validatortoolbox")
    validator_data = os.path.join(toolbox_location, "metadata", "validator.json")
    password_path = os.path.join(harmony_dir, "passphrase.txt")
    external_ip = get_url()
    main_menu_regular = os.path.join(toolbox_location, "src", "messages", "regularmenu.txt")
    main_menu_full = os.path.join(toolbox_location, "src", "messages", "fullmenu.txt")
    rpc_endpoints = ['https://api.s0.t.hmny.io', 'https://api.harmony.one', 'https://harmony-0-rpc.gateway.pokt.network']
    rpc_endpoints_test = ['https://rpc.s0.b.hmny.io', 'https://api.s0.pops.one']
    rpc_endpoints_max_connection_retries = 10
    hmy_tmp_path = '/tmp/hmy'
    harmony_tmp_path = '/tmp/harmony'
