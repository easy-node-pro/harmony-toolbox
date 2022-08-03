import os
import dotenv
import time
from utils.shared import setVar
from utils.config import validatorToolbox
from os import environ
from colorama import Fore, Style
from utils.shared import setAPIPaths, getShardMenu, getExpressStatus, setMainOrTest, getNodeType, firstRunMenu, printStars, loadVarFile, askYesNo, save_text, installHarmonyApp, installHmyApp, recoveryType, passphraseStatus, passphraseSet


def firstSetup():
    os.system("touch ~/.easynode.env")
    # first run stuff
    print("* This is the first time you've launched start.py, loading config menus.")
    printStars()
    time.sleep(1)
    setVar(validatorToolbox.dotenv_file, "SETUP_STATUS", "2")
    if environ.get("EASY_VERSION"):
        setVar(validatorToolbox.dotenv_file, "EASY_VERSION", validatorToolbox.easyVersion)
    firstRunMenu()
    recheckVars()
    getExpressStatus(validatorToolbox.dotenv_file)
    checkForInstall()
    printStars()
    # load installer


def recheckVars():
    loadVarFile()
    getShardMenu(validatorToolbox.dotenv_file)
    getNodeType(validatorToolbox.dotenv_file)
    setMainOrTest(validatorToolbox.dotenv_file)
    setAPIPaths(validatorToolbox.dotenv_file)
    loadVarFile()

def checkForInstall() -> str:
    loadVarFile()
    if not os.path.exists(validatorToolbox.harmonyDirPath):
        print(
            f"* You selected Shard: {environ.get('SHARD')}. "
        )
        if environ.get("EXPRESS") == "1":
            question = askYesNo(
                "* Would you like to install the Harmony Software and Databases now? (YES/NO) "
            )
            if question:
                # run install on server
                installHarmony()
                printStars()
                print(
                    "* All harmony files now installed. Database download starting now...")
                printStars()
            question = askYesNo(
                "* Wallet Creation"
                + "\n* Skip for Full Node or to create a new wallet after installation."
                + "\n* Would you like to save your wallet password & restore a validator wallet now? (YES/NO) "
            )
            if question:
                restoreWallet()
            question = askYesNo(
                "* Clone Shards\n* Would you like to clone your shards now? (YES/NO) "
            )
            if question:
                cloneShards()
                finish_node_install()
            finish_node_install()
        else:
            installHarmony()
            if environ.get('NODE_WALLET') == "true":
                restoreWallet()
            printStars()
            print("* All harmony files now installed. Database download starting now...")
            printStars()
            cloneShards()
            finish_node_install()
    if environ.get("SETUP_STATUS") == "0":
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
    testOrMain = environ.get("NETWORK")
    if environ.get("EXPRESS") == "0":
        os.system("clear")
        printStars()
        if environ.get("SHARD") != "0":
            print(f"* Now cloning shard {environ.get('SHARD')}")
            printStars()
            os.system(
                f"rclone -P sync storj:pub.harmony.one/{testOrMain}.min/harmony_db_{environ.get('SHARD')} {validatorToolbox.harmonyDirPath}/harmony_db_{environ.get('SHARD')} --multi-thread-streams 4 --transfers=32"
            )
            printStars()
            print(f"Shard {environ.get('SHARD')} completed.")
            printStars()
        else:
            print("* Now cloning Shard 0, kick back and relax for awhile...")
            printStars()
            os.system(
                f"rclone -P -L --checksum sync storj:pub.harmony.one/{testOrMain}.snap/harmony_db_0 {validatorToolbox.harmonyDirPath}/harmony_db_0 --multi-thread-streams 4 --transfers=32"
            )
    else:
        os.system("clear")
        print(f"* We are now ready to rclone your database(s).\n")
        if environ.get("SHARD") != "0":
            question = askYesNo(
                f"* Would you like to download the shard {environ.get('SHARD')} database now? (YES/NO) "
            )
            if question:
                print(f"* Now cloning shard {environ.get('SHARD')}")
                os.system(
                    f"rclone -P sync storj:pub.harmony.one/{testOrMain}.min/harmony_db_{environ.get('SHARD')} {validatorToolbox.harmonyDirPath}/harmony_db_{environ.get('SHARD')} --multi-thread-streams 4 --transfers=32"
                )
        else:
            question = askYesNo(
                "* Would you like to download the shard 0 database now? (YES/NO) "
            )
            if question:
                print("* Now cloning Shard 0, kick back and relax for awhile...")
                os.system(
                    f"rclone -P -L --checksum sync storj:pub.harmony.one/{testOrMain}.snap/harmony_db_0 {validatorToolbox.harmonyDirPath}/harmony_db_0 --multi-thread-streams 4 --transfers=32"
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
  

def recoverWallet():
    question = askYesNo(
        f"* Would you like to import a wallet? (YES/NO) "
        )
    if question:
        recoveryType()
        loadVarFile()
        validatorWallet = environ.get("VALIDATOR_WALLET")
        passphraseSwitch = environ.get("PASS_SWITCH")
        print(
            "\n* Verify the address above matches the address below: "
            + "\n* Detected Wallet: "
            + Fore.GREEN
            + f"{validatorWallet}"
            + Style.RESET_ALL
            + "\n* If a different wallet is showing you can remove it and retry it after installation."
            + "\n*"
            + f"\n* .{validatorToolbox.hmyAppPath} keys remove {validatorToolbox.activeUserName}"
            + "\n*"
            + "\n* To restore a wallet once again, run the following:"
            + "\n*"
            + f"\n* .{validatorToolbox.hmyAppPath} keys recover-from-mnemonic {validatorToolbox.activeUserName} {passphraseSwitch}"
            + "\n* "
        )
        printStars()
        input("* Verify your wallet information above.\n* Press ENTER to continue Installation.")
    else:
        wallet = input(f"* If you'd like to use the management menu, we need a one1 address, please input your address now: ")
        setVar(validatorToolbox.dotenv_file, "VALIDATOR_WALLET", wallet)
        return


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
    dotenv.unset_key(validatorToolbox.dotenv_file, "SETUP_STATUS")
    dotenv.set_key(validatorToolbox.dotenv_file, "SETUP_STATUS", "1")
    raise SystemExit(0)
