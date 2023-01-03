[![Codacy Badge](https://app.codacy.com/project/badge/Grade/215c4479f0304b40a535f7e84ce75f55)](https://www.codacy.com/gh/easy-node-pro/harmony-toolbox/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=easy-node-pro/harmony-toolbox&amp;utm_campaign=Badge_Grade)
[![Codacy Security Scan](https://github.com/easy-node-pro/harmony-toolbox/actions/workflows/codacy.yml/badge.svg?branch=main)](https://github.com/easy-node-pro/harmony-toolbox/actions/workflows/codacy.yml)
[![Discord Badge](https://img.shields.io/badge/chat-discord-purple?logo=discord)](https://discord.gg/Rcz5T6D9CV)
[![Stake Now Badge](https://img.shields.io/badge/stake-harmony-brightgreen)](https://bit.ly/easynode)

# Easy Node - Validator Toolbox
by [EasyNode.PRO](http://EasyNode.PRO "EasyNode.PRO")

This repository provides two functions in one application:
-   Harmony Validator Menu Driven Installer (install.py)
-   Harmony Validator Management Interface Menu (menu.py)

[![Easy Node - Harmony Validator Operations Toolbox](http://img.youtube.com/vi/mtlgZQc7BjM/0.jpg)](https://www.youtube.com/watch?v=mtlgZQc7BjM "Easy Node - Harmony Validator Operations Toolbox")

## Quickstart Guide
### Pre-Installation Requirements
Experienced validators use [this pre-installation quick guide](https://guides.easynode.pro/harmonyquick-install "this pre-installation quick guide").

New Validators should [read the companion guide](https://guides.easynode.pro/harmony/companion) and manually configure a validator by hand before using the toolbox to install Harmony Validator software.

**Operating System**
Ubuntu 20.04LTS - The suggested operating system from harmony

**Account**
-   Be logged into any user account, we strongly suggest not using root.
	-   Account should have sudoless root access
	-   If you skip this step, you will be prompted for your password during rclone setup but it will be hidden in the menu. If it pauses there type your user account password.

**Storage Volume**
If you need to use a storage volume for any reason, we will detect and use any single disk mounted in `/mnt` for installation of all files. Otherwise all content is installed at `~/harmony`.

### Installation
**After** completing the Pre-Instlalation Requirements pull the repository into your home directory.
```text
cd ~/ && git clone https://github.com/easy-node-pro/harmony-toolbox.git
```
Install requirements.
```text
cd harmony-toolbox && sudo apt update && sudo apt upgrade -y && sudo apt-get install bind9-dnsutils git python3-pip python3-dotenv unzip -y && pip3 install -r requirements.txt --quiet
```

## Run Installer
Run the installer from anywhere. You'll be presented with our menu to grab configuration details. We suggest the following string to keep you updated when launching.
```text
cd ~/harmony-toolbox && git pull && pip3 install -r requirements.txt --quiet && cd ~/harmony && python3 ~/harmony-toolbox/src/menu.py
```

## Management Menu
After you've got harmony installed, you can run our management menu with the following command:
```text
python3 ~/harmony-toolbox/src/menu.py
```

## vStats Bot Installer
First grab your token from the [Telegram vStats Bot](https://t.me/vstatsbot) by sending the command `/token` (or have your already created token handy)

Next install vStats bot on your server (toolbox not required but suggested) by running the following command:
```text
python3 ~/harmony-toolbox/src/vstats_install.py
```

## Full Installation Guide & Documentation
See [our guides page](https://guides.easynode.pro/harmony) for full documentation on the validatortoolbox.
