# Easy Node - Validator Operations Toolbox
## Now with Easy Setup on first boot!

# Harmony ONE Easy Mode Validator Operations Toolbox 
by [EasyNode.ONE](http://EasyNode.ONE "EasyNode.ONE")

#### A menu driven python application to manage your Harmony ONE Validator Node.
Preview Video:

[![Easy Node - Harmony Validator Operations Toolbox](http://img.youtube.com/vi/ydvMXFDrHwg/0.jpg)](http://www.youtube.com/watch?v=ydvMXFDrHwg "Easy Node - Harmony Validator Operations Toolbox")

# Current Application Features:
#### Installer - Detects install and runs if necessary
- First boot, application will install harmony if it's not present
- Will download all harmony files
- Will setup all necessary folders
- rclone will download shard 0 & the shard # in your config file
- After installation of harmony the only manual step is loading or creating BLS Keys

#### Easy Node Menu - The main application
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

## Future additions
- BLS Key Management
- Select between testnet/mainnet
- Raspberry Pi detection and setup
- Guides for other providers that utilize cloud-init to configure servers

# Pre-Setup Guides
Being a harmony validator currently isn't fully automated but we're getting there. Brand new validators have some tasks to complete before they jump into the tool and setup a wallet as a validator for the first time. They have their own guide pre-setup to go through. Existing validators simply need to choose the guide for their provider (if available, or use the other providers for any Ubuntu 20.04LTS server configuration)

- Brand New Validators - [Read this guide](https://github.com/easy-node-one/validator-toolbox/blob/main/docs/new_validators.md "Read this guide") and complete 1 time tasks before using one of the guides below
- Existing Validators - [Digital Ocean Setup Guide](https://github.com/easy-node-one/validator-toolbox/blob/docs/digital_ocean.md "Digital Ocean Setup Guide")
- Existing Validators - [Any Other Cloud Provider Setup Guide](https://github.com/easy-node-one/validator-toolbox/blob/docs/other_provider.md "Other Providers")

# Installation
#### Step 1: Clone our Github repository while inside your home folder
Log into your new server as the user account you created. From the home folder of your non-root user account clone our repository using the HTTPS or SSH commands below:

	cd
	git clone git@github.com:easy-node-one/validator-toolbox.git
	
#### Step 2: Edit your configuration file
Update these two lines in the config.py file:
- use nano or vim to edit `~/validator-toolbox/toolbox/includes/config.py`
- validatorWallet = Your validator wallet address
- nodeShard = The shard THIS NODE we are setting up will run on

Configuration file example:

	# Fill in this section of config.py before running the application:
	# your validator wallet address
	validatorWallet = 'oneXXXXXXXXXXXX'

	# the shard this node should run on - 0,1,2,3:
	nodeShard = 1

#### Step 3: Install requirements & run the application
Easy Node Validator Toolbox Menu makes running a validator a breeze. To get everything installed for Easy Menu run the following command:

	cd ~/validator-toolbox/
	pip3 install -r requirements.txt
	python3 ~/validator-toolbox/toolbox/toolbox.py

At this point the application is running and the menu will walk you through loading your Harmony Validator Node software or load right into the main menu.

#### Run the Easy Node Validator Toolbox Application!!!
To run the easy menu application anytime on your node **from any folder location** run the following command:

	python3 ~/validator-toolbox/toolbox/toolbox.py

#### Upgrade Easy Node Validator Operations Toolbox
Since you have run this out of our git repository, you can check for upgrades any time by running:

	cd ~/validator-toolbox
	git pull
