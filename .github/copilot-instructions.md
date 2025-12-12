# Harmony Toolbox - AI Coding Agent Instructions

## Project Overview
**Harmony Toolbox** is a Python-based TUI (Terminal User Interface) application for managing Harmony ONE blockchain validator nodes. It handles node installation, upgrades, monitoring, wallet management, and multi-shard setups. The project targets Linux systems (Ubuntu/Debian) and interacts with system services, blockchain APIs, and external binaries.

- **Repository**: https://github.com/easy-node-pro/harmony-toolbox
- **Primary Users**: Harmony ONE validator node operators
- **Target Environment**: Linux servers (systemd-based distributions)

## Architecture & Key Components

### Directory Structure
```
src/
├── toolbox/
│   ├── config.py      # Singleton config object, RPC endpoints, paths
│   ├── utils.py       # 1600+ lines of utility functions (downloads, system checks, validation)
│   ├── toolbox.py     # Main menu system, workflow orchestration
│   └── cli.py         # CLI flags parser (--stats, --upgrade-harmony, etc.)
├── menu.py            # Entry point: loads config, runs menu
├── bin/
│   ├── harmony.sh     # Bootstrap script (git clone/pull, pip install, launch)
│   ├── harmony.service # systemd service template
│   └── rclone.conf    # Database sync configuration
└── messages/
    └── regularmenu.txt # ASCII art menu text
```

### Configuration System (`toolbox/config.py`)
- **Singleton Pattern**: `config = Config()` instantiated once at module level
- **Environment File**: `~/.easynode.env` stores user-specific settings (shard, wallet addresses, paths)
- **Dynamic Properties**: `working_rpc_endpoint` tests multiple RPC endpoints at runtime and returns first working one
- **Path Resolution**: All paths use `os.path.join()` and `path.expanduser("~")` for cross-environment compatibility
- **Version Reading**: Reads version from `setup.cfg` metadata section

**Key Config Properties**:
```python
config.harmony_dir       # ~/harmony or custom install path
config.hmy_app          # Path to hmy CLI binary
config.validator_wallet # User's ONE address (one1... or 0x...)
config.shard            # Shard number (0-3)
config.working_rpc_endpoint # Auto-selected working RPC endpoint
```

## Critical Patterns & Conventions

### 1. Command Execution Standardization
**Always use `process_command()` for shell commands**, not raw `subprocess`:

```python
# ✅ CORRECT - Uses process_command wrapper
process_command("wget https://harmony.one/binary -O harmony", print_output=False)

# ❌ AVOID - Raw subprocess calls
subprocess.call(["wget", "..."], stdout=devnull, stderr=devnull)
```

**Rationale**: `process_command()` provides consistent error handling, output suppression control, and return value handling.

### 2. File Download Pattern
Use `wget` consistently for downloads (not `curl`):
```python
# Download to /tmp for version checks
process_command(f"wget https://harmony.one/binary -O {config.harmony_tmp_path}", print_output=False)

# Download directly to final destination
process_command("wget https://harmony.one/binary -O harmony && chmod +x harmony")
```

### 3. Environment Variable Management
```python
# Reading env vars (with fallback)
shard = environ.get("SHARD") or "4"

# Writing env vars (updates ~/.easynode.env)
set_var(config.dotenv_file, "VALIDATOR_WALLET", wallet_address)
load_var_file(config.dotenv_file)  # Reload after changes
```

### 4. Error Handling Philosophy
- **Silent Failures for Optional Operations**: Version checks, stats gathering (return defaults on failure)
- **User-Facing Errors**: Installation, wallet recovery, space checks (print colored error + exit)
- **Retry Logic**: Network operations use retry loops with delays (see `process_folder()`)

### 5. Multi-Folder Support Pattern
The toolbox supports managing multiple harmony installations (harmony, harmony0, harmony1...):

```python
folders = get_folders()  # Returns dict: {"harmony": "9500", "harmony0": "9501"}
for folder, port in folders.items():
    # Each folder has its own harmony.conf, service, and database
```

## Development Workflows

### Adding New Menu Options
1. Add menu item to `menu_regular()` in `toolbox.py`
2. Create handler function following naming pattern: `menu_*_option()`
3. Use `TerminalMenu` from `simple-term-menu` for user input
4. Add CLI flag to `cli.py` if needed for automation

### Testing & Validation
- **No Unit Tests**: Project uses manual validation on live systems
- **Testing Approach**: Test on staging validator node before production
- **Version Validation**: `version_checks()` compares local vs online binary versions

### Building & Distribution
```bash
# Build process (from build.sh)
python3 -m pip install --upgrade build
python3 -m build
```

**Package Structure**: Pure Python package, no compilation required. Dependencies in `requirements.txt`.

## External Dependencies & Integration Points

### Blockchain Interaction
- **pyhmy Library**: Harmony ONE Python SDK for blockchain queries
  - `pyhmy.account.get_balance()` - Wallet balance checks
  - `pyhmy.staking.get_validator_information()` - Validator stats
  - `pyhmy.numbers.convert_atto_to_one()` - Unit conversion

### System Service Management
```python
# Service status checks (returns 0 for active, non-zero for inactive)
subprocess.call(["systemctl", "is-active", "--quiet", service_name])

# Service control
subprocess.run(["sudo", "systemctl", "restart", service_name])
```

### Database Synchronization
- **rclone**: Used for syncing blockchain databases from remote WebDAV sources
- **Configuration**: `src/bin/rclone.conf` with snap/fulldb endpoints
- **Size Estimation**: `get_rclone_estimate()` queries remote size before download

## Project-Specific Idioms

### Color Coding with Colorama
```python
from colorama import Fore, Back, Style

# Error messages
print(f"{Fore.RED}* Error: Installation failed")

# Success/info
print(f"{Fore.GREEN}* Success!")
print(f"{Fore.CYAN}* Info: {Fore.YELLOW}some_value{Fore.GREEN}")

# Always reset after styled text
print(f"{Style.RESET_ALL}")
```

### Menu String Stars Pattern
```python
# Used for visual menu borders (93 asterisks)
print(f"{string_stars()}")  # Returns "*" * 93
print(f"* Menu Item Text {' ' * padding} *")
print(f"{string_stars()}")
```

### File Existence Checks Before Operations
```python
# Always check before copying from /tmp
if os.path.isfile(config.hmy_tmp_path):
    process_command(f"cp {config.hmy_tmp_path} {destination_path}")
else:
    # Download fresh copy
```

## Common Pitfalls & Solutions

### Path Handling
❌ **Don't hardcode paths**: `"/home/user/harmony"`
✅ **Use config paths**: `f"{config.harmony_dir}/harmony"`

### Wallet Address Validation
```python
# Addresses start with "one1" (42 chars) or "0x" (42 chars)
if wallet.startswith(("one1", "0x")) and len(wallet) == 42:
    # Valid address
```

### Port Detection from harmony.conf
The `find_port()` function looks for the 4th occurrence of "Port =" (HTTP RPC port), not the first occurrence (which would be P2P port).

### Temporary File Cleanup
```python
# Clean /tmp files after version checks
clean_tmp_folder()  # Removes /tmp/hmy, /tmp/binary, /tmp/harmony
```

## Key Files for Reference

- **utils.py** (1600+ lines): Contains all core functionality - study this for patterns
- **config.py**: Single source of truth for all paths, endpoints, and settings
- **harmony.conf**: Generated TOML config for harmony node (not in repo, created during install)
- **.easynode.env**: User environment file (not in repo, see `.easynode.env.example`)

## Versioning & Updates
- Version stored in `setup.cfg` metadata section
- Update mechanism: Users run `~/harmony.sh` which pulls latest git changes
- Binary updates: Compare local vs remote versions, download if newer available

## Support & Documentation
- Primary docs: https://docs.easynodepro.com/harmony/toolbox
- Discord support: https://discord.gg/Rcz5T6D9CV
- Issues: https://github.com/easy-node-pro/harmony-toolbox/issues
