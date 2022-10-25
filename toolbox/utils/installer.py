import os
import dotenv
import time
from utils.shared import setVar
from utils.config import validatorToolbox
from os import environ
from colorama import Fore, Style
from utils.shared import setAPIPaths, getShardMenu, getNodeType, printStars, loadVarFile, askYesNo, save_text, installHarmonyApp, installHmyApp, recoveryType, passphraseStatus, passphraseSet, recoverWallet


def firstSetup():
    os.system("touch ~/.easynode.env")
    # first run stuff
    time.sleep(2)
    if environ.get("EASY_VERSION"):
        setVar(validatorToolbox.dotenv_file, "EASY_VERSION", validatorToolbox.easyVersion)
    loadVarFile()
    getShardMenu(validatorToolbox.dotenv_file)
    setVar(validatorToolbox.dotenv_file, "EXPRESS", "0")
    getNodeType(validatorToolbox.dotenv_file)
    setVar(validatorToolbox.dotenv_file, "NETWORK", "mainnet")
    setVar(validatorToolbox.dotenv_file, "NETWORK_SWITCH", "t")
    setVar(validatorToolbox.dotenv_file, "RPC_NET", "https://rpc.s0.t.hmny.io")
    setAPIPaths(validatorToolbox.dotenv_file)
    setVar(validatorToolbox.dotenv_file, "SETUP_STATUS", "0")
    loadVarFile()
    checkForInstall()
    printStars()
    # load installer


def recheckVars():
    loadVarFile()
    getShardMenu(validatorToolbox.dotenv_file)
    getNodeType(validatorToolbox.dotenv_file)
    setVar(validatorToolbox.dotenv_file, "NETWORK", "mainnet")
    setVar(validatorToolbox.dotenv_file, "NETWORK_SWITCH", "t")
    setVar(validatorToolbox.dotenv_file, "RPC_NET", "https://rpc.s0.t.hmny.io")
    setAPIPaths(validatorToolbox.dotenv_file)
    loadVarFile()


def checkForInstall() -> str:
    loadVarFile()
    if not os.path.exists(validatorToolbox.harmonyDirPath):
        print(
            f"* You selected Shard: {environ.get('SHARD')}. "
        )
        installHarmony()
        if environ.get('NODE_WALLET') == "true":
            restoreWallet()
        printStars()
        print("* All harmony files now installed. Database download starting now...")
        printStars()
        cloneShards()
        finish_node_install()
    else:
        question = askYesNo(
            "* You already have a harmony folder on this system, would you like to re-run installation and rclone? (YES/NO)"
        )
        if question:
            installHarmony()
            if environ.get('NODE_WALLET') == "true":
                restoreWallet()
            printStars()
            print("* All harmony files now installed. Database download starting now...")
            printStars()
            cloneShards()
            finish_node_install()



def installHarmony() -> None:
    # check disk space, find mounted disks
    mntCount = 0
    if os.path.isdir("/dev/disk/by-id/"):
        testMnt = '/mnt'
        for subdir, dirs, files in os.walk(testMnt):
            for dir in dirs:
                tester = os.path.join(subdir, dir)
                if os.path.ismount(tester):
                    myVolumePath = tester
                    mntCount = mntCount + 1

        # if you have more than one, we'll have to find a way to list them and let people choose
        if mntCount > 1:
            print(
                "* You have multiple mounts in /mnt - Review mounts, only 1 allowed for our installer at this time!"
            )
            raise SystemExit(0)
        # Checks Passed at this point, only 1 folder in /mnt and it's probably our volume (can scope this down further later)
        if environ.get("SHARD") == "0":
            if mntCount == 1:
                myLongHmyPath = myVolumePath + "/harmony"
                dotenv.set_key(validatorToolbox.dotenv_file,
                            "MOUNT_POINT", myLongHmyPath)
                print("* Creating all Harmony Files & Folders")
                os.system(
                    f"sudo chown {validatorToolbox.activeUserName} {myVolumePath}")
                os.system(f"mkdir -p {myLongHmyPath}/.hmy/blskeys")
                os.system(
                    f"ln -s {myLongHmyPath} {validatorToolbox.harmonyDirPath}")
            # Let's make sure your volume is mounted
            if mntCount == 0:
                question = askYesNo(
                    "* You have a volume but it is not mounted.\n* Would you like to install Harmony in ~/harmony on your main disk instead of your volume? (Yes/No) "
                )
                if question:
                    dotenv.set_key(validatorToolbox.dotenv_file,
                                "MOUNT_POINT", validatorToolbox.harmonyDirPath)
                else:
                    raise SystemExit(0)
    # Setup folders now that symlink exists or we know we're using ~/harmony
    if not os.path.isdir(f"{validatorToolbox.userHomeDir}/.hmy_cli/account-keys/"):
        os.system(
            f"mkdir -p {validatorToolbox.userHomeDir}/.hmy_cli/account-keys/")
    if not os.path.isdir(f"{validatorToolbox.harmonyDirPath}/.hmy/blskeys"):
        print("* Creating all Harmony Files & Folders")
        os.system(f"mkdir -p {validatorToolbox.harmonyDirPath}/.hmy/blskeys")
    os.chdir(f"{validatorToolbox.harmonyDirPath}")
    printStars()
    installHmyApp(validatorToolbox.harmonyDirPath)
    printStars()
    installHarmonyApp(validatorToolbox.harmonyDirPath, validatorToolbox.blsKeyFile)
    # install hmy files
    print("* Installing rclone application & rclone configuration files")
    printStars()
    try:
        os.system("curl https://rclone.org/install.sh | sudo bash")
    except (ValueError, KeyError, TypeError):
        input("* rclone site is offline, we can install rclone from the Ubuntu repo as a workaround, do you want to continue?")
    os.system(
        f"mkdir -p {validatorToolbox.userHomeDir}/.config/rclone && cp {validatorToolbox.toolboxLocation}/toolbox/bin/rclone.conf {validatorToolbox.userHomeDir}/.config/rclone/"
    )
    # setup the harmony service
    printStars()
    print("* Customizing, Moving & Enabling your harmony.service systemd file")
    if validatorToolbox.activeUserName == 'root':
        os.system(
            f"sudo cp {validatorToolbox.toolboxLocation}/toolbox/bin/harmony.service . && sed -i 's/home\/serviceharmony/{validatorToolbox.activeUserName}/g' 'harmony.service' && sed -i 's/serviceharmony/{validatorToolbox.activeUserName}/g' 'harmony.service' && sudo mv harmony.service /etc/systemd/system/harmony.service && sudo chmod a-x /etc/systemd/system/harmony.service && sudo systemctl enable harmony.service"
        )
    else:
        os.system(
            f"sudo cp {validatorToolbox.toolboxLocation}/toolbox/bin/harmony.service . && sed -i 's/serviceharmony/{validatorToolbox.activeUserName}/g' 'harmony.service' && sudo mv harmony.service /etc/systemd/system/harmony.service && sudo chmod a-x /etc/systemd/system/harmony.service && sudo systemctl enable harmony.service"
        )


def cloneShards():
    os.chdir(f"{validatorToolbox.harmonyDirPath}")
    os.system("clear")
    printStars()
    if environ.get("SHARD") != "0":
        print(f"* Now cloning shard {environ.get('SHARD')}")
        printStars()
        os.system(
            f"rclone -P sync release:pub.harmony.one/{environ.get('NETWORK')}.min/harmony_db_{environ.get('SHARD')} {validatorToolbox.harmonyDirPath}/harmony_db_{environ.get('SHARD')} --multi-thread-streams 4 --transfers=32"
        )
        printStars()
        print(f"Shard {environ.get('SHARD')} completed.")
        printStars()
    else:
        print("* Now cloning Shard 0, kick back and relax for awhile...")
        printStars()
        os.system(
            f"rclone -P -L --checksum sync release:pub.harmony.one/{environ.get('NETWORK')}.snap/harmony_db_0 {validatorToolbox.harmonyDirPath}/harmony_db_0 --multi-thread-streams 4 --transfers=32"
        )

def restoreWallet() -> str:
    if environ.get("NODE_WALLET") == "true":
        if not os.path.exists(validatorToolbox.hmyWalletStorePath):
            os.system("clear")
            printStars()
            print(
                "* Harmony ONE Validator Wallet Import"
            )
            printStars()
            if environ.get("EXPRESS") == "1":
                question = askYesNo(
                    "\n* You will directly utilize the harmony application interface"
                    + "\n* We do not store any pass phrases  or data inside of our application"
                    + "\n* Respond yes to recover your validator wallet via Mnemonic phrase now or say NO to create a new wallet post-install"
                    + "\n* Restore an existing wallet now? (YES/NO) "
                )
                if question:
                    passphraseStatus()
                    recoverWallet()
                printStars()
                return
            passphraseStatus()
            recoverWallet()
            return
        printStars()
        print("* Wallet already setup for this user account")


def setMountedPoint():
    # First let's make sure your volume is mounted
    totalDir = len(os.listdir("/mnt"))
    if totalDir > 0:
        volumeMountPath = os.listdir("/mnt")
        myVolumePath = "/mnt/" + str(volumeMountPath[0])
        myLongHmyPath = myVolumePath + "/harmony"
    else:
        myVolumePath = validatorToolbox.harmonyDirPath
    if totalDir == 1:
        dotenv.set_key(validatorToolbox.dotenv_file,
                       "MOUNT_POINT", myLongHmyPath)
    else:
        dotenv.set_key(validatorToolbox.dotenv_file, "MOUNT_POINT",
                       f"{validatorToolbox.harmonyDirPath}")


def finish_node_install():
    ourShard = environ.get('SHARD')
    passphraseSwitch = environ.get("PASS_SWITCH")
    nodeWallet = environ.get("NODE_WALLET")
    printStars()
    print("* Installation is completed"
          + "\n* Create a new wallet or recover your existing wallet into ./hmy"
          + "\n* Create or upload your bls key & pass files into ~/harmony/.hmy/blskeys"
          + "\n* Finally, reboot to start synchronization."
          )
    printStars()
    if nodeWallet == "false":
        print("* Post installation quick tips:"
            + "\n* To recover your wallet on this server run:"
            + f"\n* python3 ~/validatortoolbox/toolbox/load_wallet.py"
            + "\n*"
            + "\n* To create BLS keys run:"
            + f"\n* ./hmy keys generate-bls-keys --count 1 --shard {ourShard} --passphrase"
            + "\n*"
            )
    else:
        print("* Post installation quick tips:"
            + "\n* To recover your wallet again, run:"
            + f"\n* python3 ~/validatortoolbox/toolbox/load_wallet.py"
            + "\n*"
            + "\n* To create BLS keys run:"
            + f"\n* ./hmy keys generate-bls-keys --count 1 --shard {ourShard} {passphraseSwitch}"
            + "\n*"
            )
    printStars()
    print("* Thanks for using Easy Node - Validator Node Server Software Installer!")
    printStars()
    setVar(validatorToolbox.dotenv_file, "SETUP_STATUS", "1")
    raise SystemExit(0)
