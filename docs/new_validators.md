# Welcome new validators!

There's a lot of stuff to cover before you even create a node. Be sure to review our [Validator Operator Companion Guide](https://guides.easynode.one "Validator Operator Companion Guide") before jumping in!

Here's what you'll need to get completed. Once you've setup your first node building future nodes becomes quicker and with our software it only takes as long as cloning the database does.

## The steps:
For a new validator, here's all the steps:

# Pre Validator Server Setup Requirements - AKA, all the 1-Time Steps:
- Determine shard choice 
	- (1-3 recommended at this time for single key validators)
- Create ssh key pub/priv pairs for use to auth on cloud provider service
- Create a keybase account with your validator logo
- Create a github account and upload your .pub key to it so you can see it @ github.com/username.keys
- Sign up on [Digital Ocean](https://m.do.co/c/b761e5fdd694 "Digital Ocean") and rent server, or utilize another provider of your choice
- Setup SSH tools for your workstation (Will you be using Windows or MAC to connect to your Ubuntu Linux Server?) - Mobaxterm is our windows recommendation
- Create a brand for your validator

# Digital Ocean Setup
- Research the hardware required to run a Harmony ONE Validator Node
	- We currently Recommend:
		- Shard 0: 4 CPU Optimized Nodes with at least 225GB Volume Block Storage Added
		- Shards 1-3: 2 CPU Optimized Nodes with at least 250GB Volume Block Storage Added

## Customize User Data
Use our [Validator Toolbox Application](https://github.com/easy-node-one/validator-toolbox/blob/main/README.md "Validator Toolbox Application") at this point to install & run the Easy Node Validator Operatiors Toolbox which will install the Harmony Validator Node Software

# Digital Ocean Post Node Configuration
## Since this is your first rodeo, you need a Wallet and some keys. These are both 1-Time steps if you save your BLS key/pass files to your home workstation.
- Create wallet you would like to use for the validator
	- Save mnemonic phrase and never share it
	- Can be created on your server after you install the software & key files
	- Must have over 10000 ONE in it to delegate when creating your validator + gas fees.
- Create blskeys & pass files
- Transfer a copy of the blskeys to your home pc or another server for "backup"

Return to the [main README.md file](https://github.com/easy-node-one/validator-toolbox/blob/main/README.md).