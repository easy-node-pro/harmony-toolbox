[![Codacy Badge](https://api.codacy.com/project/badge/Grade/c023922143c04967bffb1a2469af938e)](https://app.codacy.com/gh/easy-node-one/validator-toolbox?utm_source=github.com&utm_medium=referral&utm_content=easy-node-one/validator-toolbox&utm_campaign=Badge_Grade_Settings)
[![Telegram Badge](https://img.shields.io/badge/chat-telegram-brightgreen?logo=telegram)](https://t.me/easynodesupport)
[![Discord Badge](https://img.shields.io/badge/chat-discord-brightgreen?logo=discord)](https://discord.gg/babnYCEZ7Q)
[![Stake Now Badge](https://img.shields.io/badge/stake-harmony-brightgreen)](https://bit.ly/easynode)


# Easy Node - Validator Toolbox
by [EasyNode.ONE](http://EasyNode.ONE "EasyNode.ONE")

This repository provides two functions in one application:
-   Harmony Validator Menu Driven Installer
-   Harmony Validator Management Interface Menu

[![Easy Node - Harmony Validator Operations Toolbox](http://img.youtube.com/vi/ydvMXFDrHwg/0.jpg)](http://www.youtube.com/watch?v=ydvMXFDrHwg "Easy Node - Harmony Validator Operations Toolbox")

## Quickstart Guide
#### Pre-Installation Requirements:
Digital Ocean users can use [this pre-installation quick guide](https://validator-toolbox-guide.easynode.one/full-manual/pre-installation-information/pre-installation/digital-ocean-validator-node-setup "this pre-installation quick guide").

**Operating System**
-   Ubuntu 20.04LTS - The suggested operating system from harmony
**Account**
-   Be logged into any user account, we strongly suggest not using root.
	-   Account must have sudoless root access (if not using the root account)
	-   If you skip this step, you will be prompted for your password during rclone setup but it will be hidden in the menu. If it pauses there type your user account password.
**Storage Volume**
	-   Mount your volume to any folder inside of /mnt and we'll detect a single mount point inside of that folder, install harmony in /mnt/yourfolder/harmony and symlink that folder to ~/harmony

## Installation
**New & Existing Ubuntu Servers**:
After completing the pre-requisites pull the repository into your home directory.
```bash
git clone https://github.com/easy-node-one/validator-toolbox.git
```
Install requirements.
```bash
cd validator-toolbox
sudo apt-get install dnsutils python3-pip python3-dotenv -y
pip3 install -r requirements.txt
```
Run the installer from anywhere. You'll be presented with our menu to grab configuration details.
```bash
python3 ~/validator-toolbox/toolbox/start.py
```

## Full Installation Guide & Documentation
See the gitbook for validator-toolbox to [install our software here](https://validator-toolbox-guide.easynode.one/ "validator-toolbox gitbook guide").