import os
from toolbox.library import loader_intro, print_stars

# This is just a temp file to replace start.py to guide people to install.py or menu.py in the interim. 

if __name__ == "__main__":
    subprocess.run("clear")
    loader_intro()
    subprocess.run("clear")
    print_stars()
    print("We've split this into two applications, installer.py & menu.py - please update your startup commands.\n\npython3 ~/validatortoolboxinstall.py\n\npython3 ~/validatortoolboxmenu.py\n\n")
    print_stars()