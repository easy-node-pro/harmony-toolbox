import os
import urllib.request
from requests import get, post
from json import load, dump, loads, load

# List of methods
# https://docs.harmony.one/home/developers/api``


# TODO: Will move this to setup.py when we utilize
curVersion = "v0.1.6"

rpc_url = "https://api.harmony.one"

# the shard this node should run on - 0,1,2,3:
nodeShard = 2

# File Locations
PASSWORD_FILE = os.path.join(
    "metadata", "passphrase.txt"
)  # extension is needed for autobidder plz :D
METADATA_FILE = os.path.join("metadata", "metadata.json")
RPC_DATA = os.path.join("metadata", "rpc_data.json")
BLSKEYS_FILE = os.path.join("metadata", "blskeys.json")

# Fill in this section of config.py before running the application:
# your validator wallet address in place of oneXXXXXXXX
validatorWallet = 'one18julyys26h67r4vq3zexzpfmvt9vpn0g75phmu'


# Pull current user to build paths
userHomeDir = os.path.expanduser("~")
# Set active linux user name
activeUserName = os.path.split(userHomeDir)[-1]

# Set paths dynamically
harmonyDirPath = os.path.join(userHomeDir, "harmony")
hmyAppPath = os.path.join(os.path.normpath(harmonyDirPath), "hmy")
easyNodeDirPath = os.path.join(userHomeDir, "ez-node")
harmonyAppPath = os.path.join(os.path.normpath(harmonyDirPath), "harmony")
blskeyDirPath = os.path.join(hmyAppPath, ".hmy", "blskeys")

# Password locations
passphraseFile = os.path.join(harmonyDirPath, PASSWORD_FILE)
passphraseIsFile = os.path.isfile(passphraseFile)

mainnetShardCall = f'{hmyAppPath} --node="https://api.s0.t.hmny.io" '
testnetShardCall = f'{hmyAppPath} --node="https://api.s0.b.hmny.io" '

dirCheckSH = os.path.isdir(harmonyDirPath)

# Init var items for scoreboard
ourExternalIPAddress = urllib.request.urlopen("https://ident.me").read().decode("utf8")


def get_validator_info(
    one_address: str, save_data: bool = False, display: bool = False
) -> dict:

    d = {
        "jsonrpc": "2.0",
        "method": "hmy_getValidatorInformation",
        "params": [one_address],
        "id": 1,
    }
    try:
        response = post(rpc_url, json=d)
    except Exception as e:
        print("ERROR: <get_validator_info> Something went wrong with the RPC API.")
        return False, {"Error": response.text}

    if response.status_code == 200:
        data = response.json()

        if save_data:
            save_json(RPC_DATA, data)

        if display:
            print(dumps(data, indent=4))

    else:
        data = False, {f"Error [{response.status_code}]": response.text}

    return True, data


def save_text(fn: str, to_write: str) -> bool:
    try:
        with open(fn, "w") as f:
            f.write(to_write)
            return True
    except Exception as e:
        print(f"Error writing file  ::  {e}")
        return False


def return_txt(fn: str) -> list:
    """Opens a file and returns the whole file as a list
    Args:
        fn (str): File name to open
    Returns:
        list: return whole file as a list
    """
    try:
        with open(fn, "r") as f:
            return f.readlines()
    except FileNotFoundError as e:
        # print(f"File not Found  ::  {e}")
        return []


def save_json(fn: str, data: dict) -> dict:
    with open(fn, "w") as j:
        dump(data, j, indent=4)


def return_json(fn: str, single_key: str = None) -> dict:
    try:
        with open(fn, "r", encoding="utf-8") as j:
            data = load(j)
            if single_key:
                return data.get(single_key)
            return data
    except FileNotFoundError as e:
        # print(f"File not Found  ::  {e}")
        return {}


if __name__ == "__main__":

    # Example Usage (See json saved for full structure)
    one_address = "one18julyys26h67r4vq3zexzpfmvt9vpn0g75phmu"

    res, validator_data = get_validator_info(one_address, save_data=True, display=False)

    if not res:
        print("there was a problem")
    else:
        validatorName = validator_data["result"]["validator"]["name"]
        validatorDetails = validator_data["result"]["validator"]["details"]
        validatorRate = float(validator_data["result"]["validator"]["rate"])
        validatorRate = validatorRate * 100
        validatorWebsite = validator_data["result"]["validator"]["website"]
        email = validator_data["result"]["validator"]["security-contact"]
        bls_keys = validator_data["result"]["validator"]["bls-public-keys"]
        validatorSign = float(validator_data["result"]["current-epoch-performance"]["current-epoch-signing-percent"]["current-epoch-signing-percentage"])
        validatorSign = validatorSign * 100
        lifetimeAPR = float(validator_data["result"]["lifetime"]["apr"])
        lifetimeAPR = lifetimeAPR * 100
        electedStatus = validator_data["result"]["epos-status"]
        print(f"{validatorName} is {electedStatus}. {validatorWebsite}")
        print(f"{validatorDetails}")
        print(f"Current commission: {validatorRate}%")
        print(f"Security Contact: {email}")
        print()
        print("Active BLS Keys:\n")
        a=0
        if len(bls_keys) <= 0:
            print("oh no, I cannot find the keys")
        else:
            for x in bls_keys:
                print(f"Key {a + 1}: {bls_keys[a]}")
                a=a+1
        print()
        print(f"Current Epoch Signing  %: {validatorSign}")
        print(f"Validator Lifetime APR %: {lifetimeAPR}")

