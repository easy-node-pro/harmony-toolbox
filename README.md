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

# Quickstart Guide
#### Pre-Installation Requirements:
Digital Ocean users can use [this pre-installation quick guide](https://validator-toolbox-guide.easynode.one/full-manual/pre-installation-information/pre-installation/digital-ocean-validator-node-setup "this pre-installation quick guide").

Any other provider or hardware pre-install requirements:
-   ✔️ A new Ubuntu 20.04LTS server
-   ✔️ Login as a user account with sudoless root access or run and install as root
	-   Our tips on setting this up for our installer to perform sudo commands is [right here](https://validator-toolbox-guide.easynode.one/full-manual/pre-installation-information/pre-installation/any-other-provider-validator-node-setup/sudoless-root-access "right here"). You can revert this after installation is complete.
	-   If you skip this step, you will be prompted for your password during rclone setup but it will be hidden in the menu. If it pauses there type your user account password.
-   ✔️ Volume Support
	-   Mount a volume at ~/harmony before you start or in a folder in /mnt and we\'ll install there and symlink to ~/harmony

#### Installation - New & Existing servers:
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

# Full Installation Guide & Documentation
See the gitbook for validator-toolbox to [install our software here](https://validator-toolbox-guide.easynode.one/ "validator-toolbox gitbook guide").

# Community
Join our [Discord](https://discord.gg/babnYCEZ7Q "Discord") or [Telegram](https://t.me/easynodesupport "Telegram") servers for free comunity driven support.
