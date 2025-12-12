#!/bin/bash
set -e  # Exit on any error

HOME_DIR="$HOME"

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check if required commands are installed
if ! command_exists git; then
    echo "Error: git is not installed. Please install git and try again."
    exit 1
fi

if ! command_exists python3; then
    echo "Error: python3 is not installed. Please install python3 and try again."
    exit 1
fi

if ! command_exists pip3; then
    echo "Error: pip3 is not installed. Please install python3-pip and try again."
    exit 1
fi

# Check if the harmony-toolbox directory exists
if [ -d "$HOME_DIR/harmony-toolbox" ]; then
    # If it exists, go into it and pull updates
    cd "$HOME_DIR/harmony-toolbox"
    printf "⚙ Updating harmony-toolbox... "
    if ! git pull --quiet > /dev/null 2>&1; then
        echo "⚠ Warning: Failed to update. Continuing with existing version."
    else
        echo "✓"
    fi
else
    # If it doesn't exist, clone the repository
    printf "⚙ Cloning harmony-toolbox... "
    if ! git clone https://github.com/easy-node-pro/harmony-toolbox.git "$HOME_DIR/harmony-toolbox" > /dev/null 2>&1; then
        echo "✗ Error: Failed to clone harmony-toolbox repository."
        exit 1
    else
        echo "✓"
    fi
    # Go into the new directory, we already have updates
    cd "$HOME_DIR/harmony-toolbox"
fi

# Install/update requirements if requirements.txt exists
if [ -f "requirements.txt" ]; then
    printf "⚙ Installing requirements... "
    if ! pip3 install -r requirements.txt --quiet > /dev/null 2>&1; then
        echo "⚠ Warning: Failed to install some requirements."
    else
        echo "✓"
    fi
else
    echo "⚠ Warning: requirements.txt not found. Skipping requirements installation."
fi

# Clear the startup messages before launching the toolbox
printf "\033[2J\033[H"

# Start toolbox, with flags if passed
python3 "$HOME_DIR/harmony-toolbox/src/menu.py" "$@"
