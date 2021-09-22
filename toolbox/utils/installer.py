import os
import socket
import dotenv
from os import environ
from dotenv import load_dotenv
from colorama import Fore, Style
from utils.shared import setAPIPaths, getShardMenu, getExpressStatus, setMainOrTest, getNodeType, setWalletEnv, process_command, printStars, printStarsReset, printWhiteSpace, askYesNo, save_text, installHarmonyApp, installHmyApp


easyVersion = "1.1.0"
serverHostName = socket.gethostname()
userHomeDir = os.path.expanduser("~")
dotenv_file = f"{userHomeDir}/.easynode.env"
if os.path.exists(dotenv_file) == False:
    os.system("touch ~/.easynode.env")
    dotenv.set_key(dotenv_file, "FIRST_RUN", "1")
else:
    if environ.get("FIRST_RUN"):
        dotenv.unset_key(dotenv_file, "FIRST_RUN")
activeUserName = os.path.split(userHomeDir)[-1]
harmonyDirPath = os.path.join(userHomeDir, "harmony")
harmonyAppPath = os.path.join(harmonyDirPath, "harmony")
hmyAppPath = os.path.join(harmonyDirPath, "hmy")
blskeyDirPath = os.path.join(hmyAppPath, ".hmy", "blskeys")
hmyWalletStorePath = os.path.join(userHomeDir, ".hmy_cli", "account-keys", activeUserName)
toolboxLocation = os.path.join(userHomeDir, "validatortoolbox")
validatorData = os.path.join(toolboxLocation, "toolbox", "metadata", "validator.json")
dotenv_file = f"{userHomeDir}/.easynode.env"
passwordPath = os.path.join(harmonyDirPath, "passphrase.txt")


def checkForInstall() -> str:
    if os.path.exists(harmonyDirPath) == False:
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
                print("* All harmony files now installed. Database download starting now...")
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
            if environ.get('NODE_TYPE') == "regular":
                restoreWallet()
            printStars()
            print("* All harmony files now installed. Database download starting now...")
            printStars()
            cloneShards()
            finish_node_install()
    # Harmony already exists but this is the first time this ran
    return


def installHarmony() -> None:
    testOrMain = environ.get("NETWORK")
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
            dotenv.set_key(dotenv_file, "MOUNT_POINT", myLongHmyPath)
            print("* Creating all Harmony Files & Folders")
            os.system(f"sudo chown {activeUserName} {myVolumePath}")
            os.system(f"mkdir -p {myLongHmyPath}/.hmy/blskeys")
            os.system(f"ln -s {myLongHmyPath} {harmonyDirPath}")
        # Let's make sure your volume is mounted
        if mntCount == 0:
            question = askYesNo(
                "* You have a volume but it is not mounted.\n* Would you like to install Harmony in ~/harmony on your main disk instead of your volume? (Yes/No) "
            )
            if question:
                dotenv.set_key(dotenv_file, "MOUNT_POINT", harmonyDirPath)
            else:
                raise SystemExit(0)
    # Setup folders now that symlink exists or we know we're using ~/harmony
    if not os.path.isdir(f"{harmonyDirPath}/.hmy/blskeys"):
        print("* Creating all Harmony Files & Folders")
        os.system(f"mkdir -p {harmonyDirPath}/.hmy/blskeys")
    os.chdir(f"{harmonyDirPath}")
    printStars()
    installHmyApp(harmonyDirPath)
    printStars()
    installHarmonyApp(harmonyDirPath)
    # install hmy files
    print("* Installing rclone application & rclone configuration files")
    printStars()
    os.system("curl https://rclone.org/install.sh | sudo bash")
    os.system(
        f"mkdir -p {userHomeDir}/.config/rclone && cp {toolboxLocation}/toolbox/bin/rclone.conf {userHomeDir}/.config/rclone/"
    )
    # setup the harmony service
    printStars()
    print("* Customizing, Moving & Enabling your harmony.service systemd file")
    if activeUserName == 'root':
        os.system(
        f"sudo cp {toolboxLocation}/toolbox/bin/harmony.service . && sed -i 's/home\/serviceharmony/{activeUserName}/g' 'harmony.service' && sed -i 's/serviceharmony/{activeUserName}/g' 'harmony.service' && sudo mv harmony.service /etc/systemd/system/harmony.service && sudo chmod a-x /etc/systemd/system/harmony.service && sudo systemctl enable harmony.service"
    )
    else:
        os.system(
            f"sudo cp {toolboxLocation}/toolbox/bin/harmony.service . && sed -i 's/serviceharmony/{activeUserName}/g' 'harmony.service' && sudo mv harmony.service /etc/systemd/system/harmony.service && sudo chmod a-x /etc/systemd/system/harmony.service && sudo systemctl enable harmony.service"
        )


def cloneShards():
    os.chdir(f"{harmonyDirPath}")
    testOrMain = environ.get("NETWORK")
    if environ.get("NETWORK") == "rasppi_main":
        testOrMain = "mainnet"
    if environ.get("EXPRESS") == "0":
        os.system("clear")
        printStars()
        print(f"* Now cloning shard {environ.get('SHARD')}")
        printStars()
        os.system(
            f"rclone -P sync release:pub.harmony.one/{testOrMain}.min/harmony_db_{environ.get('SHARD')} {harmonyDirPath}/harmony_db_{environ.get('SHARD')}"
        )
        printStars()
        print(f"Shard {environ.get('SHARD')} completed.")
        printStars()
        if environ.get('SHARD') == '0':
            return
        print("* Now cloning Shard 0, kick back and relax for awhile...")
        printStars()
        os.system(
            f"rclone -P sync release:pub.harmony.one/{testOrMain}.min/harmony_db_0 {harmonyDirPath}/harmony_db_0"
        )
        return
    else:
        os.system("clear")
        question = askYesNo(
            "* We are now ready to rclone your databases.\n"
            + f"* Would you like to download the shard {environ.get('SHARD')} database now? (YES/NO) "
        )
        if question:
            print(f"* Now cloning shard {environ.get('SHARD')}")
            os.system(
                f"rclone -P sync release:pub.harmony.one/{testOrMain}.min/harmony_db_{environ.get('SHARD')} {harmonyDirPath}/harmony_db_{environ.get('SHARD')}"
            )
        question = askYesNo(
            "* Would you like to download the shard 0 database now? (YES/NO) "
        )
        if question:
            print("* Now cloning Shard 0, kick back and relax for awhile...")
            os.system(
                f"rclone -P sync release:pub.harmony.one/{testOrMain}.min/harmony_db_0 {harmonyDirPath}/harmony_db_0"
            )
        else:
            return
        return


def passphraseStatus():
    if environ.get("NODE_TYPE") == "regular":
        if os.path.exists(passwordPath) is not True:
            passphraseSet()
        dotenv.unset_key(dotenv_file, "PASS_SWITCH")
        dotenv.set_key(dotenv_file, "PASS_SWITCH", f"--passphrase-file {harmonyDirPath}/passphrase.txt")
        return
    if environ.get("NODE_TYPE") == "full":
        dotenv.unset_key(dotenv_file, "PASS_SWITCH")
        dotenv.set_key(dotenv_file, "PASS_SWITCH", "--passphrase")
        return


def passphraseSet():
    if os.path.exists(passwordPath):
        return
    import getpass
    os.system("clear")
    printStars()
    print("* Setup ~/harmony/passphrase.txt file for use with autobidder & validatortoolbox.")
    printStars()
    # take input
    while True:
        print("* ")
        password1 = getpass.getpass(prompt="* Please set a wallet password for this node\n* Enter your password now: ", stream=None)
        password2 = getpass.getpass(
            prompt="* Re-enter your password: ", stream=None
        )
        if not password1 == password2:
            print("* Passwords do NOT match, Please try again..")
        else:
            print("* Passwords Match!")
            break
    # Save file, we won't encrypt because if someone has access to the file, they will also have the salt and decrpyt code at their disposal.
    save_text(passwordPath, password1)
    return


def restoreWallet() -> str:
    nodeType = environ.get("NODE_TYPE")
    if nodeType == "regular":
        if not os.path.isdir(hmyWalletStorePath):
            os.system("clear")
            printStars()
            print(
                "* Harmony ONE Validator Wallet Import"
            )
            printStars()
            if environ.get("EXPRESS") == 1:
                question = askYesNo(
                    "\n* You will directly utiilize the harmony applicaiton interface"
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
        return
    return


def recoverWallet():
    load_dotenv(dotenv_file)
    os.system("clear")
    nodeType = environ.get("NODE_TYPE")
    passphraseSwitch = environ.get("PASS_SWITCH")
    if nodeType == "full":
        printStars()
        print("* Full node, no wallet recovery")
        return
    printStars()
    print("* Loading harmony wallet recovery tool.")
    printStars()
    print("* Recover your validator wallet now:")
    os.system(
        f"{hmyAppPath} keys recover-from-mnemonic {activeUserName} {passphraseSwitch}"
    )
    printStars()
    validatorWallet = setWalletEnv(dotenv_file)
    print(
        "\n* Verify the address above matches the address below: "
        + "\n* Detected Wallet: "
        + Fore.GREEN
        + f"{validatorWallet}"
        + Style.RESET_ALL
        + "\n* If a different wallet is showing you can remove it and retry it after installation."
        + "\n*"
        + f"\n* .{hmyAppPath} keys remove {activeUserName}"
        + "\n*"
        + "\n* To restore a wallet once again, run the following:"
        + "\n*"
        + f"\n* .{hmyAppPath} keys recover-from-mnemonic {activeUserName} {passphraseSwitch}"
        + "\n* "
    )
    printStars()
    input("* Verify your wallet information above.\n* Press ENTER to continue Installation.")


def setMountedPoint():
    # First let's make sure your volume is mounted
    totalDir = len(os.listdir("/mnt"))
    if totalDir > 0:
        volumeMountPath = os.listdir("/mnt")
        myVolumePath = "/mnt/" + str(volumeMountPath[0])
        myLongHmyPath = myVolumePath + "/harmony"
    else:
        myVolumePath = harmonyDirPath
    if totalDir == 1:
        dotenv.set_key(dotenv_file, "MOUNT_POINT", myLongHmyPath)
    else:
        dotenv.set_key(dotenv_file, "MOUNT_POINT", f"{harmonyDirPath}")
    return


def finish_node_install():
    ourShard = environ.get('SHARD')
    passphraseSwitch = environ.get("PASS_SWITCH")
    printStars()
    print("* Installation is completed"
    + "\n* Create a new wallet or recover your existing wallet into ./hmy"
    + "\n* Create or upload your bls key & pass files into ~/harmony/.hmy/blskeys"
    + "\n* Finally, reboot to start syncronization."
    )
    printStars()
    print("* Post installation quick tips:"
        + "\n* To recover your wallet run:"
        + f"\n* ./hmy keys recover-from-mnemonic {activeUserName} {passphraseSwitch}"
        + "\n*"
        + "\n* To create BLS keys run:"
        + f"\n* ./hmy keys generate-bls-keys --count 1 --shard {ourShard} {passphraseSwitch}"
        + "\n*"
    )
    printStars()
    print("* Thanks for using Easy Node - Validator Node Server Software Installer!")
    printStars()
    dotenv.unset_key(dotenv_file, "SETUP_STATUS")
    dotenv.unset_key(dotenv_file, "FIRST_RUN")
    dotenv.set_key(dotenv_file, "SETUP_STATUS", "1")
    raise SystemExit(0)