# link-skills

A flexible command-line tool that discovers skills across multiple repositories and symlinks them into standard AI coding tool skill directories (Claude, Kiro, Agent Skills, etc.).

## Features

- 🔗 **Multi-Repository Support**: Link skills from multiple repositories
- ⚙️ **Flexible Configuration**: TOML config file for easy customization
- 🎯 **Smart Duplicate Handling**: Configurable strategies for duplicate skill names
- 🚀 **Zero Configuration**: Works out of the box with sensible defaults
- 🔍 **Dry Run Mode**: Preview changes before applying
- ✅ **Easy to Use**: Just run `./link-skills.sh`

## Quick Start

```bash
# Clone the repository
cd ~/src
git clone https://github.com/andrewjdarnell/link-skills.git
cd link-skills

# Quick install (recommended)
make quickstart  # Installs as 'link-skills' command + creates config

# OR run directly without installing
./link-skills.sh --dry-run  # Preview what would happen
./link-skills.sh            # Actually link skills
```

## Requirements

One of the following:
- **UV** (recommended): Fast Python package manager with automatic dependency handling
  ```bash
  # Install UV
  curl -LsSf https://astral.sh/uv/install.sh | sh
  # or
  brew install uv
  ```

- **Python 3.9+**: Built-in support (auto-installs dependencies if needed)
  - Python 3.11+ has built-in TOML support
  - Python 3.9-3.10 will auto-install `tomli` if needed

## Usage

```bash
# Basic usage - links all configured repos to all destinations
./link-skills.sh
# or if installed:
link-skills

# Preview what would be linked (dry run)
make dry-run
# or if installed:
link-skills --dry-run

# Show detailed output
make verbose
# or if installed:
link-skills --verbose

# Use custom config file (after installation)
link-skills --config ~/my-config.toml

# Get help
./link-skills.sh --help
# or if installed:
link-skills --help
```

## Makefile Targets

The project includes a comprehensive Makefile for common tasks:

```bash
make              # Show all available commands
make test         # Run tests
make test-coverage # Run tests with coverage report
make install      # Install to ~/scripts
make quickstart   # Install everything and setup config
make clean        # Remove build artifacts
make show-config  # Show config file locations
```

See `make help` for all available targets.

## Configuration

Create a config file at one of these locations (first found wins):
- `~/.config/link-skills/config.toml`
- `~/scripts/link-skills-config.toml`
- `./link-skills-config.toml` (next to the script)

See [`link-skills-config.example.toml`](link-skills-config.example.toml) for a complete example.

### Example Configuration

```toml
# Repositories to scan for skills
[[repositories]]
name = "mattpocock-skills"
path = "~/src/mattpocock/skills"
enabled = true
exclude_dirs = ["deprecated", "misc"]

[[repositories]]
name = "anthropic-skills"
path = "~/src/anthropic/skills"
enabled = true
exclude_dirs = ["experimental"]

# Destinations where skills will be linked
[[destinations]]
path = "~/.claude/skills"
enabled = true

[[destinations]]
path = "~/.kiro/skills"
enabled = true

# Global settings
[settings]
global_exclude_dirs = ["deprecated", "misc", "node_modules"]
duplicate_strategy = "warn"  # warn, skip, overwrite, error
require_skill_md = true
```

### Duplicate Handling Strategies

When the same skill name exists in multiple repositories:

- **`warn`** (default): Link the first found, warn about duplicates
- **`skip`**: Silently skip duplicates, only link first found
- **`overwrite`**: Last repository wins, overwrite previous links
- **`error`**: Stop execution if duplicates are found

## How It Works

1. Scans each enabled repository for directories containing `SKILL.md` files
2. Excludes directories matching global or per-repository exclude patterns
3. Creates symlinks in each destination directory pointing to the source skill directories
4. Handles duplicates according to configured strategy
5. Reports what was linked and any warnings

## Default Behavior

Without a config file, the tool:
- Links skills from the repository where the script lives
- Links to: `~/.claude/skills`, `~/.agents/skills`, `~/.kiro/skills`
- Excludes: `deprecated`, `misc`, `node_modules`, `.git`, `__pycache__`

## Installation Options

### Recommended: UV Tool Install (Best for CLI tools)

```bash
# Install globally with uv (fastest, isolated)
make install-uv
# or manually:
uv tool install .

# Uninstall
uv tool uninstall link-skills
```

This installs `link-skills` command globally in an isolated environment. No PATH modification needed!

### Alternative: Pipx (Also great for CLI tools)

```bash
# Install with pipx
make install-pipx
# or manually:
pipx install .

# Uninstall
pipx uninstall link-skills
```

### Simple: Copy to ~/scripts (No Python packaging)

```bash
# Quick and simple - just copies files
make quickstart  # Installs + creates config

# Or manual install
make install
make install-config
```

This copies files to `~/scripts/link-skills`. You'll need to add `~/scripts` to your PATH.

### Development: Editable Install

```bash
# For development - changes reflect immediately
make install-editable
# or manually:
uv pip install -e .

# Uninstall
uv pip uninstall link-skills
```

## Which Method Should I Use?

| Method | Best For | Pros | Cons |
|--------|----------|------|------|
| **`uv tool install`** | Most users | Fast, isolated, global | Requires UV |
| **`pipx install`** | Python users | Isolated, standard tool | Requires pipx |
| **`make install`** | Simplicity | No Python packaging knowledge | Manual PATH setup |
| **`make install-editable`** | Development | Live updates | Local venv only |

**My recommendation:** Use `make install-uv` or `make quickstart-uv` - it's the modern, fast way to install Python CLI tools.

### Option 1: Install to ~/scripts
```bash
cd ~/src
git clone <your-repo-url> link-skills
cd link-skills
./link-skills.sh
```

### Option 2: Global Installation
```bash
# Link to ~/scripts or ~/bin
ln -s ~/src/link-skills/link-skills.sh ~/scripts/link-skills
```

### Option 3: Copy Files
```bash
# Copy just what you need
cp link-skills.sh ~/scripts/
cp link-skills.py ~/scripts/
cp pyproject.toml ~/scripts/
```

## Supported AI Tools

- **Claude Desktop / Claude Code**: `~/.claude/skills`
- **Kiro IDE**: `~/.kiro/skills`
- **Agent Skills (Codex, etc.)**: `~/.agents/skills`
- **Custom tools**: Add any destination in your config

## Development

### Setting Up Development Environment

The project uses `uv` which automatically manages the virtual environment:

```bash
# Install development dependencies (creates .venv automatically)
make dev-install

# Or manually create venv first (optional, uv does this automatically)
make venv

# Run tests (uses .venv automatically via uv)
make test
```

The virtual environment (`.venv`) is created and managed automatically by `uv`. You don't need to activate it manually - `uv run` handles this transparently.

### Running Tests

The project includes comprehensive unit and integration tests:

```bash
# Using Makefile (recommended)
make test                # Run all tests
make test-verbose        # Run with verbose output
make test-coverage       # Run with coverage report
make test-fast           # Run quickly without coverage

# Using uv directly
uv run pytest
uv run pytest -v
uv run pytest --cov=. --cov-report=html
```

For more details, see [TESTING.md](TESTING.md).

### Test Coverage

- **Configuration**: TOML parsing, path expansion, defaults
- **Discovery**: Skill finding, exclusion patterns, SKILL.md validation
- **Linking**: Symlink creation, duplicate handling, multiple destinations
- **Integration**: Full workflows from config to linked skills

## Troubleshooting

### "No TOML parser found"
Install UV (recommended) or ensure Python 3.9+ is available:
```bash
brew install uv
# or
brew install python3
```

### "Config file not found"
The tool works without a config file! It will use sensible defaults. To create a config:
```bash
# Create config with example repos
cp link-skills-config.example.toml ~/.config/link-skills/config.toml
# Edit with your repositories
nano ~/.config/link-skills/config.toml
```

Or use: `make install-config`

### Skills not appearing
1. Check that `SKILL.md` exists in each skill directory
2. Verify paths in your config are correct (use `link-skills --verbose` if installed, or `./link-skills.sh --verbose` from source)
3. Check that directories aren't in exclude lists
4. Try `--dry-run` to see what would be linked: `link-skills --dry-run` or `./link-skills.sh --dry-run`

## Credits

Original concept from [mattpocock/skills](https://github.com/mattpocock/skills) `scripts/link-skills.sh`

Enhanced with multi-repository support and flexible configuration by Andrew Darnell.

## License

MIT License - See [LICENSE](LICENSE) file for details.


