# Easy Node - Validator Operations Toolbox
Now with Easy Setup on first boot!

## Harmony ONE Easy Mode Validator Operations Toolbox by [EasyNode.ONE](http://EasyNode.ONE "EasyNode.ONE")
A menu driven python application to manage your Harmony ONE Validator Node.

## Current Application Features:
### Installer - Detects install and runs if necessary
- First boot, application will install harmony if it's not present
- Will download all harmony files
- Will setup all necessary folders
- rclone will download shard 0 & the shard # in your config file
- After installation of harmony the only manual step is loading or creating BLS Keys

### Easy Node Menu - The main application
Once installed and loaded, the interface menu will assist with common tasks like:

- Checking your Stats
- Show Active BLS Keys (Up to 20 currently, customize able)
- Show Any Wallet Balance
- Collect pending rewards on validator wallet
	- Mainnet & Testnet!
- Restart Harmony Service
- Stop Harmony Service
- Start Harmony Service
- Update Harmony Binary
- Update Operating System
- Rebooting your Harmony Server

#  Pre-Installation 
## Option A: If you're using [Digital Ocean](https://m.do.co/c/b761e5fdd694 "Digital Ocean") as your provider:
Here\'s what **you need to setup** for our application to run smoothly the first time you want to setup a new node:

During your node creation screen, Copy the box below and edit the information to use inside the \"User Data\" box.
- Customize the username: We have pre-filled `serviceharmony` as our suggestion. Use anything other than **root**!
- Add your own ssh-rsa public key in place of the ssh-rsa example key below.

```bash
#cloud-config
users:
  - name: serviceharmony
    groups: sudo
    shell: /bin/bash
    sudo: ['ALL=(ALL) NOPASSWD:ALL']
    ssh-authorized-keys:
      - ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAA_EXAMPLE_KEY_ONLY_OOHch79N5OnB136TaVdXPQFaYFzubA1Lzbeus5H2BcbMieDyGBBTh4gEEkz2hsGCXeaw==
package_upgrade: true
packages:
 - dnsutils
 - nethogs
 - python3-pip
```

## Option B: If you're using any other VPS service as your provider:
Here\'s what **you need to setup** for our application to run smoothly the first time you want to setup a new node:
- Ubuntu 20.04LTS - The suggested operating system from harmony
- Be logged into any user account not named root
- Give that account sudoless root access on your server

# Installation
## Step 1: Clone our repo in your home folder
Log into your new server as the user account you created. From the home folder of your non-root user account clone our repository using the HTTPS or SSH commands below:

HTTPS Clone (login required while repo is private:)

	cd
	git clone https://github.com/easy-node-one/ez-node.git

**or** 

SSH Clone (need keys on node while repo is private:)

	cd
	git clone git@github.com:easy-node-one/ez-node.git
	
### Step 2: Add your wallet and shard number to config.py file in the includes folder
Update these two lines in the config.py file:
- use nano or vim to edit `~/ez-node/ez_node/includes/config.py`
- validatorWallet = Your validator wallet address
- nodeShard = The shard THIS NODE will run on

Configuration file example:

	# Fill in this section of config.py before running the application:
	# your validator wallet address
	validatorWallet = 'oneXXXXXXXXXXXX'

	# the shard this node should run on - 0,1,2,3:
	nodeShard = 1

### Step 3: Install Requirements for Easy Node Validator Toolbox Menu
Easy Node Validator Toolbox Menu makes running a validator a breeze. To get everything installed for Easy Menu run the following command:

	cd ~/ez-node/
	pip3 install -r requirements.txt

If you receive an error, you may need to install pip3 by running `sudo apt install python3-pip -y`

## Run the Easy Node Validator Toolbox Application!!!
To run the easy menu application anytime on your node **from any folder location** run the following command:

	python3 ~/ez-node/ez_node/toolbox.py

## Upgrade Easy Node Validator Operations Toolbox
Since you have run this out of our git repository, you can check for upgrades any time by running:

	cd ~/ez-node
	git pull
