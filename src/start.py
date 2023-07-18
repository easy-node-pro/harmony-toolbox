import subprocess, os
from toolbox.library import loader_intro, print_stars

if __name__ == "__main__":
    subprocess.run("clear")
    loader_intro()
    subprocess.run("clear")
    print_stars()
    if os.path.isfile("~/harmony.sh"):
        print("* harmony.sh already exists in ~/\n*\n* This will exit, please run ~/harmony.sh to launch the toolbox.\n*")
    else:
        print("* Downloading harmony.sh to ~/")
        subprocess.run("cd ~/ && wget -O harmony.sh https://raw.githubusercontent.com/easy-node-pro/harmony-toolbox/main/src/bin/harmony.sh && chmod +x harmony.sh", shell=True)
    print_stars()