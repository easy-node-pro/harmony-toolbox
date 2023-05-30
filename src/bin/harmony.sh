#!/bin/bash
HOME_DIR=$(echo ~)

# Check if the harmony-toolbox directory exists
if [ -d "$HOME_DIR/harmony-toolbox" ]; then
  # If it exists, go into it and pull updates
  cd ~/harmony-toolbox
  git pull --quiet
else
  # If it doesn't exist, clone the repository
  git clone https://github.com/easy-node-pro/harmony-toolbox.git ~/harmony-toolbox
  # Go into the new directory, we already ahve updates
  cd ~/harmony-toolbox
fi

# Install requirements for both
pip3 install -r requirements.txt --quiet

# Start toolbox, with flags if passed
python3 ~/harmony-toolbox/src/menu.py "$@"