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
    print("* Select an option below:")
    printStars()
    print("* [0] = install.py - Install Harmony Validator Software - For Brand NEW SERVERS ONLY           *")
    print("* [1] = menu.py - Load Validator Toolbox Menu App    - For Servers Loaded with our Installer   *")
    printStars()
    menuOptions = ["[0] - install.py", "[1] - menu.py", ]
    terminal_menu = TerminalMenu(menuOptions, title="* Run installer or menu?")
    results = terminal_menu.show()
    if results == 0:
        exec(open("./toolbox/install.py").read())
    elif results == 1:
        exec(open("./toolbox/menu.py").read())
    else:
        print("* Bad Option, Thanks for playing!!!")
