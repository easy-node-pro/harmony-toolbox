#!/bin/bash
set -e  # Exit on any error

HOME_DIR="$HOME"
TOOLBOX_DIR="$HOME_DIR/harmony-toolbox"
SELF="$HOME_DIR/harmony.sh"
G="\033[0;32m"
R="\033[0m"

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

printf "${G}⚙ harmony.sh:${R}"

# Check if the harmony-toolbox directory exists
if [ -d "$TOOLBOX_DIR" ]; then
    # If it exists, go into it and pull updates
    cd "$TOOLBOX_DIR"
    printf "${G} [toolbox${R}"
    if ! git pull --quiet > /dev/null 2>&1; then
        printf "${G} ⚠]${R}"
    else
        printf "${G} ✓]${R}"
    fi
else
    # If it doesn't exist, clone the repository
    printf "${G} [cloning toolbox${R}"
    if ! git clone https://github.com/easy-node-pro/harmony-toolbox.git "$TOOLBOX_DIR" > /dev/null 2>&1; then
        echo ""
        echo "✗ Error: Failed to clone harmony-toolbox repository."
        exit 1
    fi
    printf "${G} ✓]${R}"
    cd "$TOOLBOX_DIR"
fi

# Self-update: if ~/harmony.sh differs from the toolbox version, update and re-exec
TOOLBOX_SH="$TOOLBOX_DIR/src/bin/harmony.sh"
if [ -f "$TOOLBOX_SH" ] && [ -f "$SELF" ]; then
    if ! diff -q "$TOOLBOX_SH" "$SELF" > /dev/null 2>&1; then
        cp "$TOOLBOX_SH" "$SELF"
        chmod +x "$SELF"
        printf "${G} [self-updated, restarting]\n${R}"
        exec "$SELF" "$@"
    fi
fi

# Install/update requirements if requirements.txt exists
if [ -f "requirements.txt" ]; then
    printf "${G} [packages${R}"
    if ! pip3 install -r requirements.txt --quiet > /dev/null 2>&1; then
        printf "${G} ⚠]${R}"
    else
        printf "${G} ✓]${R}"
    fi
fi

printf "${G} [launching]\n${R}"

# Start toolbox, with flags if passed
python3 "$TOOLBOX_DIR/src/menu.py" "$@"
