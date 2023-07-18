import subprocess
from toolbox.library import loader_intro, print_stars

# This is just a temp file to replace start.py to guide people to harmony.sh. 

if __name__ == "__main__":
    subprocess.run("clear")
    loader_intro()
    subprocess.run("clear")
    print_stars()
    print("* We have moved to using harmony.sh to launch our toolbox and get stats.\n*\n* Run the following to download and setup the new harmony.sh file:\n*\n* cd ~/ && wget -O harmony.sh https://raw.githubusercontent.com/easy-node-pro/harmony-toolbox/main/src/bin/harmony.sh && chmod +x harmony.sh\n*\n* Now you can launch the toolbox with ./harmony.sh or get just stats with ./harmony.sh -s\n* See ./harmony.sh -h for help!\n*")    
    print_stars()