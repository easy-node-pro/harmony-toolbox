# Easy Node - Validator Toolbox
by [EasyNode.ONE](http://EasyNode.ONE "EasyNode.ONE")

This repository provides two functions in one application:
- Harmony Validator Menu Driven Installer
- Harmony Validator Management Interface Menu

[![Easy Node - Harmony Validator Operations Toolbox](http://img.youtube.com/vi/ydvMXFDrHwg/0.jpg)](http://www.youtube.com/watch?v=ydvMXFDrHwg "Easy Node - Harmony Validator Operations Toolbox")

# Quickstart Guide
#### Pre-Installation Requirements:
- ✔️ A new Ubuntu 20.04LTS server
- ✔️ Login as a user account with sudoless root access or run and install as root
	- Digital Ocean Admins: Use the same guide as our validator-toolbox Application to setup "User Data" on your Digital Ocean Droplet.
	- Other Providers Admins: Use the Any Other Provider Guide on how to edit your sudoers file or give access via groups.
- ✔️ Volume Support
	- Digital Ocean Auto Mounted Volumes will be detected and used for installation
	- Any other setup: Mount a volume at ~/harmony before you start or in a folder in /mnt and we\'ll install there and symlink to ~/harmony

#### Installation - New & Existing servers:
After completing the pre-requisits pull the repository into your home directory.
```bash
git clone https://github.com/easy-node-one/validator-toolbox.git
```
Install requirements.
```bash
cd validator-toolbox
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