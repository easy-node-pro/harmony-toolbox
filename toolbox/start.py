import os
from simple_term_menu import TerminalMenu
from utils.shared import loaderIntro, setWalletEnv, askYesNo, loadVarFile, printStars

# This is just a temp file to replace start.py to guide people to install.py or menu.py in the interim. 

if __name__ == "__main__":
    os.system("clear")
    loaderIntro()
    os.system("clear")
    printStars()
    print("We've split this into two applications, installer.py & menu.py - please update your startup commands.\n\npython3 ~/validatortoolbox/toolbox/install.py\n\npython3 ~/validatortoolbox/toolbox/menu.py\n\n")
    printStars()