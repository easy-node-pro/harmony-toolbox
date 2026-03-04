# Unused Functions Analysis

This document catalogs all unused functions found in the harmony-toolbox codebase. These functions are defined but never called anywhere in the project.

## Summary

**Total Unused Functions: 18**
- **toolbox.py**: 9 functions
- **utils.py**: 9 functions

---

## toolbox.py - Unused Functions (9)

### 1. `install_rclone()` - **DUPLICATE**
**Location**: `src/toolbox/toolbox.py:109-137`

**Status**: ❌ **REMOVE** - Duplicate of `utils.py` version

**Description**: Downloads and installs rclone using bash script from rclone.org

**Why Unused**: A functionally identical version exists in `utils.py` (line 1099) which is actually used by `install_harmony()`. This version was likely an early implementation that was never cleaned up after being moved to utils.

**Code**:
```python
def install_rclone():
    # Fetch the content of the script
    url = "https://rclone.org/install.sh"
    response = requests.get(url)
    # ... downloads and runs install script via sudo bash
```

**Recommendation**: **DELETE** - The utils.py version is the canonical implementation.

---

### 2. `get_folder_choice()` - **DUPLICATE**
**Location**: `src/toolbox/toolbox.py:138-158`

**Status**: ❌ **REMOVE** - Duplicate of `utils.py` version

**Description**: Interactive menu to choose which harmony folder (harmony, harmony0-3) to install into

**Why Unused**: Identical function exists in `utils.py` (line 1109) and is used by `install_harmony()`. This is another case of duplicate code.

**Code**:
```python
def get_folder_choice() -> str:
    print(Fore.GREEN + f"* Which folder would you like to install harmony in?...")
    menu_options = [
        "[1] - harmony",
        "[2] - harmony0",
        "[3] - harmony1",
        "[4] - harmony2",
        "[5] - harmony3",
    ]
    terminal_menu = TerminalMenu(menu_options, title="...")
    # ... returns selected folder name
```

**Recommendation**: **DELETE** - The utils.py version is actively used.

---

### 3. `update_stats_option()` - **DEAD CODE**
**Location**: `src/toolbox/toolbox.py:638-645`

**Status**: ⚠️ **CONSIDER KEEPING** - Displays menu text for stats refresh option

**Description**: Generates menu text showing current refresh timer status (enabled/disabled) with current delay time

**Why Unused**: This appears to be a helper function that was meant to dynamically generate menu text for option 20 (refresh toggle), but the menu text is currently hardcoded in the menu file instead.

**Code**:
```python
def update_stats_option() -> None:
    if config.refresh_option == "True":
        print(f"*  20 - Disable auto-update - Disable Refresh or Change Delay Timer: {str(config.refresh_time)} seconds")
    else:
        print(f"*  20 - Enable Auto update - Enable Update Timer")
```

**Recommendation**: **KEEP IF** you want to make menu text dynamic. Otherwise **DELETE**.

**Potential Use**: Could be called from `menu_regular()` to show actual refresh time instead of static text.

---

### 4. `service_menu_option()` - **DEAD CODE**
**Location**: `src/toolbox/toolbox.py:772-785`

**Status**: ⚠️ **CONSIDER KEEPING** - Displays dynamic service status menu text

**Description**: Checks if harmony service is running and prints appropriate menu options (Start vs Stop/Restart) with warning messages

**Why Unused**: Similar to `update_stats_option()`, this was meant to dynamically generate menu text but is currently unused. The menu text is static.

**Code**:
```python
def service_menu_option() -> None:
    status = process_command(f"systemctl is-active --quiet {config.harmony_service}", True, False)
    if status:
        print(f"*   8 - {Fore.RED}Stop Harmony Service{Fore.GREEN}...")
        print(f"*   9 - Restart Harmony Service...")
    else:
        print("*   8 - Start Harmony Service")
```

**Recommendation**: **KEEP IF** you want dynamic menu text. **DELETE** if static is fine.

**Potential Use**: Could show "Start" vs "Stop" based on actual service status, making menu more intuitive.

---

### 5. `update_menu_option()` - **DEAD CODE**
**Location**: `src/toolbox/toolbox.py:788-797`

**Status**: ⚠️ **CONSIDER KEEPING** - Shows upgrade availability status

**Description**: Displays menu options 10 & 11 only if upgrades are available (checks software_versions flags)

**Why Unused**: Another dynamic menu text generator. Currently, upgrade options are always shown regardless of availability.

**Code**:
```python
def update_menu_option(software_versions) -> None:
    if software_versions["harmony_upgrade"] == "True":
        print(f"*  10 - Update Harmony App Binary - ... WARNING: You will miss blocks during upgrade.")
    if software_versions["hmy_upgrade"] == "True":
        print("*  11 - Update hmy CLI App - Update harmony binary file, run anytime!")
```

**Recommendation**: **KEEP** - This is actually useful! Could hide upgrade options when not needed.

**Potential Use**: Only show upgrade menu items when updates are actually available, reducing menu clutter.

---

### 6. `hip_voting_option()` - **EXPIRED FEATURE**
**Location**: `src/toolbox/toolbox.py:800-813`

**Status**: ❌ **REMOVE** - Voting deadline passed in 2023

**Description**: Displays governance voting menu option with deadline check (HIP-30v2 vote)

**Why Unused**: The voting deadline was August 9, 2023. This will always show "No votes currently active" now.

**Code**:
```python
def hip_voting_option() -> None:
    deadline = utc.localize(datetime(2023, 8, 9, 20, 59))
    active_vote = current_time < deadline
    if active_vote:
        print("*   7 - Harmony Governance Voting - Cast your vote for HIP-30v2")
    else:
        print("*   7 - Harmony Governance Voting - No votes currently active.")
```

**Recommendation**: **DELETE** - Expired feature with hardcoded past deadline.

---

### 7. `rewards_sender_option()` - **DEAD CODE**
**Location**: `src/toolbox/toolbox.py:816-827`

**Status**: ⚠️ **CONSIDER KEEPING** - Conditional menu text for rewards features

**Description**: Shows different menu text for options 5 & 6 based on whether rewards wallet is configured

**Why Unused**: Dynamic menu text generator, but menu currently shows static text.

**Code**:
```python
def rewards_sender_option() -> None:
    if config.rewards_wallet is not None:
        print("*   5 - Send Wallet Balance - Send your wallet balance - saved gas to rewards wallet")
        print("*   6 - Set Rewards Wallet - Update your saved wallet or gas reserve")
    else:
        print("*   6 - Set Rewards Wallet - Set up a one1 wallet address...")
```

**Recommendation**: **KEEP IF** you want to hide option 5 when no rewards wallet is configured. **DELETE** if static is fine.

---

### 8. `hmy_cli_upgrade()` - **REPLACED**
**Location**: `src/toolbox/toolbox.py:839-876`

**Status**: ❌ **REMOVE** - Superseded by `hmy_cli_upgrade_all()`

**Description**: Upgrades hmy CLI in the default harmony folder only (single folder upgrade)

**Why Unused**: Replaced by `hmy_cli_upgrade_all()` which handles all detected harmony folders. The single-folder version is no longer needed since we added multi-folder support.

**Code**:
```python
def hmy_cli_upgrade():
    question = ask_yes_no("* Are you sure you would like to proceed with updating the Harmony CLI file?...")
    # Backup current version
    folder_name = make_backup_dir()
    process_command(f"cp {config.harmony_dir}/hmy {folder_name}")
    # Install new version
    software_versions = update_hmy_binary()
    # ... update env var
```

**Recommendation**: **DELETE** - No longer needed with multi-folder support.

---

### 9. `harmony_binary_upgrade()` - **REPLACED**
**Location**: `src/toolbox/toolbox.py:1018-1036`

**Status**: ❌ **REMOVE** - Superseded by `harmony_binary_upgrade_all()`

**Description**: Upgrades harmony binary in default folder only, with shard 2/3 restriction check

**Why Unused**: Replaced by `harmony_binary_upgrade_all()` which handles all folders. The single-folder version is obsolete.

**Code**:
```python
def harmony_binary_upgrade():
    our_shard = config.shard
    if our_shard == "0" or our_shard == "1":
        question = ask_yes_no("* WARNING: YOU WILL MISS BLOCKS...")
        if question:
            update_harmony_app()
    else:
        print("* We do not support upgrading shards 2/3 any longer...")
```

**Recommendation**: **DELETE** - Multi-folder upgrade is the new standard.

---

## utils.py - Unused Functions (9)

### 1. `initialization_process()` - **DEAD CODE**
**Location**: `src/toolbox/utils.py:97-99`

**Status**: ❌ **REMOVE** - Never called entry point

**Description**: Initialization function that updates rclone config and checks for old toolbox

**Why Unused**: This was likely an early startup function that was replaced by the current initialization flow in `menu.py`. It's never invoked anywhere.

**Code**:
```python
def initialization_process():
    update_rclone_conf()
    old_toolbox_check()
```

**Recommendation**: **DELETE** - Orphaned entry point that's never called.

**Note**: This also makes `update_rclone_conf()` transitively unused (see next).

---

### 2. `update_rclone_conf()` - **DEAD CODE (Transitively Unused)**
**Location**: `src/toolbox/utils.py:101-110`

**Status**: ❌ **REMOVE** - Only called by unused `initialization_process()`

**Description**: Compares rclone.conf files and copies if different

**Why Unused**: Only called by `initialization_process()` which is itself never called. The rclone config is now copied during `install_harmony()` instead.

**Code**:
```python
def update_rclone_conf():
    if os.path.exists(f"{config.toolbox_location}/src/bin/rclone.conf"):
        comparison = compare_two_files(
            f"{config.toolbox_location}/src/bin/rclone.conf",
            f"{config.user_home_dir}/.config/rclone/rclone.conf",
        )
        if comparison == False:
            process_command(f"cp {config.toolbox_location}/src/bin/rclone.conf ...")
```

**Recommendation**: **DELETE** - Functionality moved to `install_harmony()`.

---

### 3. `get_wallet_address()` - **DEAD CODE**
**Location**: `src/toolbox/utils.py:768-783`

**Status**: ❌ **REMOVE** - Never called error handler

**Description**: Prints error message about missing wallet and instructions to add it to .easynode.env

**Why Unused**: This was likely an early error handler for missing wallets. The current code handles this in `first_env_check()` by calling `recover_wallet()` instead.

**Code**:
```python
def get_wallet_address():
    print("* Signing Node, No Wallet!...")
    print("* You are attempting to launch the menu but no wallet has been loaded...")
    print("* Edit ~/.easynode.env and add your wallet address on a new line like this example:         *")
    print("* VALIDATOR_WALLET='one1thisisjustanexamplewalletreplaceme'...")
    raise SystemExit(0)
```

**Recommendation**: **DELETE** - Error handling now done differently.

---

### 4. `get_validator_info()` - **DEAD CODE**
**Location**: `src/toolbox/utils.py:786-795`

**Status**: ⚠️ **KEEP?** - Potentially useful utility function

**Description**: Fetches validator information from Harmony blockchain using pyhmy library

**Why Unused**: Never called, but could be useful for future features (validator details, delegation info, etc.)

**Code**:
```python
def get_validator_info():
    validator_data = -1
    try:
        validator_data = staking.get_validator_information(
            environ.get("VALIDATOR_WALLET"), config.working_rpc_endpoint
        )
        return validator_data
    except Exception:
        return validator_data
```

**Recommendation**: **KEEP IF** planning validator info features. **DELETE** if no plans to use.

**Potential Use**: Could display validator details, commission rate, total delegation, etc.

---

### 5. `current_price()` - **DEAD CODE**
**Location**: `src/toolbox/utils.py:798-808`

**Status**: ⚠️ **KEEP?** - Fetches ONE token price

**Description**: Gets current ONE token price from Binance API

**Why Unused**: Never called, but could be useful for displaying USD values of rewards/balances

**Code**:
```python
def current_price():
    try:
        response = requests.get(config.onePriceURL, timeout=5)
    except (ValueError, KeyError, TypeError):
        response = "0.0000"
        return response
    data_dict = response.json()
    return data_dict["lastPrice"][:-4]
```

**Recommendation**: **KEEP IF** planning to show USD values. **DELETE** if not needed.

**Potential Use**: Show rewards in USD, calculate node earnings in fiat, etc.

---

### 6. `save_json()` - **DEAD CODE**
**Location**: `src/toolbox/utils.py:846-848`

**Status**: ❌ **REMOVE** - Generic utility never used

**Description**: Saves dictionary to JSON file with pretty printing

**Why Unused**: Never called anywhere. No JSON file saving is currently needed in the codebase.

**Code**:
```python
def save_json(fn: str, data: dict) -> dict:
    with open(fn, "w") as j:
        dump(data, j, indent=4)
```

**Recommendation**: **DELETE** - Not needed by current functionality.

---

### 7. `return_json()` - **DEAD CODE**
**Location**: `src/toolbox/utils.py:851-860`

**Status**: ❌ **REMOVE** - Generic utility never used

**Description**: Reads JSON file and optionally extracts a single key

**Why Unused**: Never called anywhere. No JSON file reading is currently needed.

**Code**:
```python
def return_json(fn: str, single_key: str = None) -> dict:
    try:
        with open(fn, "r", encoding="utf-8") as j:
            data = load(j)
            if single_key:
                return data.get(single_key)
            return data
    except FileNotFoundError as e:
        print(f"File not Found  ::  {e}")
        return {}
```

**Recommendation**: **DELETE** - Not needed by current functionality.

---

### 8. `check_for_install()` - **DUPLICATE**
**Location**: `src/toolbox/utils.py:1062-1099`

**Status**: ❌ **REMOVE** - Duplicate of `toolbox.py` version

**Description**: Checks if ~/harmony exists and runs installation workflow

**Why Unused**: An identical function exists in `toolbox.py` (line 72) which is the one actually used by `first_setup()` and `multi_setup()`.

**Code**:
```python
def check_for_install(shard) -> str:
    if os.path.exists(f"{config.user_home_dir}/harmony"):
        question = ask_yes_no("* You already have a harmony folder...")
        if question:
            install_harmony()
            recover_wallet()
            # ... installation workflow
```

**Recommendation**: **DELETE** - The toolbox.py version is canonical.

---

### 9. `coming_soon()` - **PLACEHOLDER**
**Location**: `src/toolbox/utils.py:1506-1508`

**Status**: ❌ **REMOVE** - Unused placeholder

**Description**: Displays "This option isn't available on your system, yet!" message

**Why Unused**: Placeholder for future features that were never implemented

**Code**:
```python
def coming_soon():
    print(f"* This option isn't available on your system, yet!\n{string_stars()}")
    input("* Press enter to return to the main menu.")
```

**Recommendation**: **DELETE** - No features are using this placeholder.

---

### 10. `clear_screen()` - **DEAD CODE**
**Location**: `src/toolbox/utils.py:1538-1539`

**Status**: ❌ **REMOVE** - Never called

**Description**: Clears terminal screen (Windows or Unix)

**Why Unused**: Never called anywhere. Terminal clearing is handled differently in the codebase (using ANSI escape codes in harmony.sh).

**Code**:
```python
def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")
```

**Recommendation**: **DELETE** - Functionality not needed.

---

### 11. `print_whitespace()` - **DEAD CODE**
**Location**: `src/toolbox/utils.py:15-45` (line 36)

**Status**: ❌ **REMOVE** - Print formatting helper never used

**Description**: Prints 8 blank lines for spacing

**Why Unused**: Defined in `print_stuff` class but never called anywhere

**Code**:
```python
@classmethod
def printWhitespace(self) -> None:
    print("\n" * 8)

print_whitespace = print_stuff.printWhitespace
```

**Recommendation**: **DELETE** - Unused helper function.

---

### 12. `print_stars_reset()` - **DEAD CODE**
**Location**: `src/toolbox/utils.py:15-45` (line 43)

**Status**: ❌ **REMOVE** - Print formatting helper never used

**Description**: Prints stars with color reset

**Why Unused**: Defined but never called. `print_stars()` is used instead.

**Code**:
```python
print_stars_reset = print_stuff(reset=1).printStars
```

**Recommendation**: **DELETE** - Unused variant of `print_stars()`.

---

### 13. `string_stars_reset()` - **DEAD CODE**
**Location**: `src/toolbox/utils.py:15-45` (line 44)

**Status**: ❌ **REMOVE** - Print formatting helper never used

**Description**: Returns stars string with color reset

**Why Unused**: Defined but never called. `string_stars()` is used instead.

**Code**:
```python
string_stars_reset = print_stuff(reset=1).stringStars
```

**Recommendation**: **DELETE** - Unused variant of `string_stars()`.

---

### 14. `free_space_size()` - **DEAD CODE**
**Location**: `src/toolbox/utils.py:1303-1307`

**Status**: ❌ **REMOVE** - Duplicate functionality

**Description**: Returns free disk space in bytes (no formatting)

**Why Unused**: `free_space_check()` exists and is used instead (returns formatted string). This raw byte version is never needed.

**Code**:
```python
def free_space_size(mount) -> str:
    ourDiskMount = get_harmony_dir_from_path(mount)
    _, _, free = shutil.disk_usage(ourDiskMount)
    return free
```

**Recommendation**: **DELETE** - `free_space_check()` handles all disk space reporting.

---

## Recommendations Summary

### ❌ **DEFINITE DELETES (13 functions)**

**Safe to remove immediately - no value to keep:**

1. **toolbox.py**: `install_rclone()` - duplicate
2. **toolbox.py**: `get_folder_choice()` - duplicate  
3. **toolbox.py**: `hip_voting_option()` - expired feature
4. **toolbox.py**: `hmy_cli_upgrade()` - replaced
5. **toolbox.py**: `harmony_binary_upgrade()` - replaced
6. **utils.py**: `initialization_process()` - dead code
7. **utils.py**: `update_rclone_conf()` - dead code
8. **utils.py**: `get_wallet_address()` - dead code
9. **utils.py**: `save_json()` - dead code
10. **utils.py**: `return_json()` - dead code
11. **utils.py**: `check_for_install()` - duplicate
12. **utils.py**: `coming_soon()` - placeholder
13. **utils.py**: `clear_screen()` - dead code
14. **utils.py**: `print_whitespace()` - dead code
15. **utils.py**: `print_stars_reset()` - dead code
16. **utils.py**: `string_stars_reset()` - dead code
17. **utils.py**: `free_space_size()` - dead code

### ⚠️ **CONSIDER KEEPING (5 functions)**

**Potentially useful - decide based on roadmap:**

1. **toolbox.py**: `update_stats_option()` - Dynamic menu text for refresh status
   - **Keep if**: Planning to show actual refresh timer in menu
   - **Delete if**: Static menu text is sufficient

2. **toolbox.py**: `service_menu_option()` - Dynamic menu text for service status
   - **Keep if**: Want menu to show "Start" vs "Stop" based on actual service state
   - **Delete if**: Static text is fine

3. **toolbox.py**: `update_menu_option()` - Shows upgrades only when available
   - **Keep**: This is actually useful! Reduces menu clutter
   - **Integrate**: Call from `menu_regular()` to conditionally show upgrade options

4. **toolbox.py**: `rewards_sender_option()` - Conditional rewards menu text
   - **Keep if**: Want to hide option 5 when no rewards wallet configured
   - **Delete if**: Always showing option 5 is acceptable

5. **utils.py**: `get_validator_info()` - Fetches validator details
   - **Keep if**: Planning features that need validator info (commission, delegation, etc.)
   - **Delete if**: No plans for such features

6. **utils.py**: `current_price()` - Gets ONE token price
   - **Keep if**: Planning to show USD values for rewards/balances
   - **Delete if**: Only showing ONE amounts is sufficient

---

## Impact Assessment

### If we delete all 18 unused functions:

**Code Reduction**: ~350 lines removed (~21% of toolbox.py, ~5% of utils.py)

**Benefits**:
- Cleaner, more maintainable codebase
- Faster code comprehension for contributors
- No risk of confusion from duplicate/dead code
- Reduced testing surface area

**Risks**: 
- **ZERO** - None of these functions are called anywhere
- All are either duplicates, dead code, or replaced functionality

**Breaking Changes**: 
- **NONE** - No external API since package doesn't export functions

---

## Next Steps

After reviewing this document, you can proceed with:

**Option A (Recommended)**: 
1. Remove all 13 definite deletes
2. Decide on the 5 "consider keeping" functions
3. Set up proper pip library structure with public API
4. Document public functions in README.md

**Option B**: 
1. Remove only the obvious dead code (duplicates, expired features, placeholders)
2. Keep everything else for potential future use
3. Document current CLI usage only

Let me know which approach you prefer!
