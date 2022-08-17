import os
from os import environ
from utils.config import validatorToolbox
from utils.shared import loaderIntro, loadVarFile, askYesNo, setVar, updateTextFile, printStars

def installVstats(vstatsToken, validatorAddress) -> None:
    # Check if it exists already
    if os.path.isdir(f"{validatorToolbox.userHomeDir}/harmony_node_stats"):
        question = askYesNo("* You already have vstats installed, would you like to update & reinstall vstats? (YES/NO)")
        if question is False:
            raise SystemExit(0)
        else:
            # stop and wipe for re-install if yes
            os.system("sudo service harmony_node_stats stop")
            os.system("sudo rm -r ~/harmony_node_stats")
        
    # Install it bud, pull git repo
    os.chdir(f"{validatorToolbox.userHomeDir}")
    os.system("git clone https://github.com/FortuneV13/harmony_node_stats")
    os.chdir(f"{validatorToolbox.userHomeDir}/harmony_node_stats")
    # setup python stuff
    os.system("sudo apt install python3-pip -y")
    os.system("pip3 install -r requirements.txt")
    # customize config file
    os.system("cp config.example.py config.py")
    updateTextFile(f"{validatorToolbox.userHomeDir}/harmony_node_stats/config.py", 'VSTATS_TOKEN=""', f'VSTATS_TOKEN="{vstatsToken}"')
    updateTextFile(f"{validatorToolbox.userHomeDir}/harmony_node_stats/config.py", 'VALIDATOR_ADDRESS=""', f'VALIDATOR_ADDRESS="{validatorAddress}"')
    if os.path.isdir(f"{validatorToolbox.userHomeDir}/harmony"):
        updateTextFile(f"{validatorToolbox.userHomeDir}/harmony_node_stats/config.py", '"harmony_folder":"/home/serviceharmony/harmony"', f'"harmony_folder":"{validatorToolbox.userHomeDir}/harmony"')
    else:
        if os.path.isfile(f"{validatorToolbox.userHomeDir}/harmony"):
            updateTextFile(f"{validatorToolbox.userHomeDir}/harmony_node_stats/config.py", '"harmony_folder":"/home/serviceharmony/harmony"', f'"harmony_folder":"{validatorToolbox.userHomeDir}"')
    # Do service stuff here
    if validatorToolbox.activeUserName == 'root':
        os.system(
        f"sudo cp {validatorToolbox.toolboxLocation}/toolbox/bin/harmony_node_stats.service . && sed -i 's/home\/serviceharmony/{validatorToolbox.activeUserName}/g' 'harmony_node_stats.service' && sed -i 's/serviceharmony/{validatorToolbox.activeUserName}/g' 'harmony_node_stats.service' && sudo mv harmony_node_stats.service /etc/systemd/system/harmony_node_stats.service && sudo chmod a-x /etc/systemd/system/harmony_node_stats.service && sudo systemctl enable harmony_node_stats.service && sudo service harmony_node_stats start"
    )
    else:
        os.system(
        f"sudo cp {validatorToolbox.toolboxLocation}/toolbox/bin/harmony_node_stats.service . && sed -i 's/serviceharmony/{validatorToolbox.activeUserName}/g' 'harmony_node_stats.service' && sudo mv harmony_node_stats.service /etc/systemd/system/harmony_node_stats.service && sudo chmod a-x /etc/systemd/system/harmony_node_stats.service && sudo systemctl enable harmony_node_stats.service && sudo service harmony_node_stats start"
    )
    return
    


def getValidatorAddress():
    if environ.get("VALIDATOR_WALLET") is None:
        # ask info to get wallet here.
        validatorAddress = input("* Validator one1 wallet address not found in our env file.\n* Please input your Validator's one1 wallet address now: ")
    else:
        validatorAddress = environ.get("VALIDATOR_WALLET")
    return validatorAddress


def getToken():
    if environ.get("VSTATSBOT_TOKEN") is None:
        question = askYesNo(
            f"* No token found, please run /token on vStats Bot to obtain your token. Would you like to enter one now? (YES/NO)"
        )
        if question:
            vstatsToken = input(
                f"* Please input your vStats token here: "
            )
            setVar(validatorToolbox.dotenv_file, "VSTATSBOT_TOKEN", vstatsToken)
    else:
        vstatsToken = environ.get("VSTATSBOT_TOKEN")
    return vstatsToken


if __name__ == '__main__':
    os.system("clear")
    loaderIntro()
    # check if it exists, load anyway if it does
    if os.path.exists(validatorToolbox.dotenv_file) is None:
        # ask a bunch of questions to gather data since we don't have env
        vstatsToken = getToken()
        validatorAddress = getValidatorAddress()
        
    
    else:
        loadVarFile()
        # load env configuration
        vstatsToken = getToken()
        validatorAddress = getValidatorAddress()
        

    # install once we have the info to customize
    installVstats(vstatsToken, validatorAddress)

    # Goodbye!
    printStars()
    print("\n*\n* Installer has finished, you should have a ping waiting on vStats if everything was input correctly\n* You can also run `sudo service harmony_node_stats status` to verify your service is online and running!\n*")
    printStars()
