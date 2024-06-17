# For autobidder startup. Drop into your autobidder folder, run with `python3 target.py <new_slot>`
import os
import sys
import re

session_name = 'autobidder'
user_home_dir = os.path.expanduser("~")
ab_dir = 'harmony_autobidder'
config_file_path = f"{user_home_dir}/{ab_dir}/config.py"
autobid_file_path = f"{user_home_dir}/{ab_dir}/autobid.py"

def getCurrentTargetSlot(file_name):
    with open(file_name, 'r') as f:
        file_data = f.read()
    
    # Use a regular expression to find the value of TARGET_SLOT
    match = re.search(r"TARGET_SLOT\s*=\s*(\d+)", file_data)
    if match:
        return int(match.group(1))
    else:
        raise ValueError("TARGET_SLOT not found in config file")

def updateAB(file_name, original_value, new_value):
    with open(file_name, 'r') as f:
        file_data = f.read()

    updated_file_data = file_data.replace(original_value, new_value)

    with open(file_name, 'w') as f:
        f.write(updated_file_data)

def getNewSlot(current_slot):
    print("Current TARGET_SLOT:", current_slot)
    print("++++++++")
    new_slot = input("Enter new TARGET_SLOT: ")
    return new_slot if new_slot else current_slot

if __name__ == '__main__':
    current_slot = getCurrentTargetSlot(config_file_path)
    new_slot = sys.argv[1] if len(sys.argv) > 1 else getNewSlot(current_slot)

    original_target_slot = "TARGET_SLOT = " + str(current_slot)
    new_target_slot = "TARGET_SLOT = " + str(new_slot)
    
    updateAB(config_file_path, original_target_slot, new_target_slot)

    print("++++++++")
    print("Target slot updated to", new_slot)

    os.system(f"tmux kill-ses -t {session_name}")
    os.system(f"tmux new-session -s {session_name} 'python3 {autobid_file_path}'")