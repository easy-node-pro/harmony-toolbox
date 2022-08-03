[![Codacy Badge](https://app.codacy.com/project/badge/Grade/215c4479f0304b40a535f7e84ce75f55)](https://www.codacy.com/gh/easy-node-one/validatortoolbox/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=easy-node-one/validatortoolbox&amp;utm_campaign=Badge_Grade)
[![Discord Badge](https://img.shields.io/badge/chat-discord-purple?logo=discord)](https://discord.gg/Rcz5T6D9CV)
[![Stake Now Badge](https://img.shields.io/badge/stake-harmony-brightgreen)](https://bit.ly/easynode)

# Easy Node - Validator Toolbox
by [EasyNode.ONE](http://EasyNode.ONE "EasyNode.ONE")

This repository provides two functions in one application:
-   Harmony Validator Menu Driven Installer (install.py)
-   Harmony Validator Management Interface Menu (menu.py)

[![Easy Node - Harmony Validator Operations Toolbox](http://img.youtube.com/vi/mtlgZQc7BjM/0.jpg)](https://www.youtube.com/watch?v=mtlgZQc7BjM "Easy Node - Harmony Validator Operations Toolbox")

## Quickstart Guide
### Pre-Installation Requirements
Experienced validators use [this pre-installation quick guide](https://guides.easynode.one/harmony/toolbox/quick-install "this pre-installation quick guide").

New Validators should [read the companion guide](https://guides.easynode.one/harmony/companion) and manually configure a validator by hand before using the toolbox to install Harmony Validator software.

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
```bash
cd ~/ && git clone https://github.com/easy-node-one/validatortoolbox.git
```
Install requirements.
```bash
cd validatortoolbox && sudo apt update && sudo apt upgrade -y && sudo apt-get install bind9-dnsutils git python3-pip python3-dotenv unzip -y && pip3 install -r requirements.txt
```
Run the installer from anywhere. You'll be presented with our menu to grab configuration details.
```bash
python3 ~/validatortoolbox/toolbox/install.py
```

### Management Menu
After you've got harmony installed, you can run our management menu with the following command:
```bash
python3 ~/validatortoolbox/toolbox/menu.py
```

## Full Installation Guide & Documentation
See [our guides page](https://guides.easynode.one/harmony) for full documentation on the validatortoolbox.
