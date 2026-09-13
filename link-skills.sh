#!/usr/bin/env bash
# Wrapper script to run link-skills with uv (if available) or python3
# This makes it easy for users - they just run ./link-skills

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PYTHON_SCRIPT="$SCRIPT_DIR/link_skills.py"

# Check if the Python script exists
if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo "✗ Error: link_skills.py not found at $PYTHON_SCRIPT" >&2
    exit 1
fi

# Try uv first (fastest, handles dependencies automatically)
if command -v uv >/dev/null 2>&1; then
    exec uv run --script "$PYTHON_SCRIPT" "$@"
fi

# Fall back to python3
if command -v python3 >/dev/null 2>&1; then
    # Check if tomli is needed (Python < 3.11)
    python3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)" 2>/dev/null
    if [ $? -ne 0 ]; then
        # Python < 3.11, check for tomli
        if ! python3 -c "import tomli" 2>/dev/null; then
            echo "⚠ Python < 3.11 detected. Installing tomli..." >&2
            python3 -m pip install --user tomli 2>/dev/null || {
                echo "✗ Error: Failed to install tomli" >&2
                echo "Please install manually: pip3 install tomli" >&2
                echo "Or install uv for automatic dependency handling: https://docs.astral.sh/uv/" >&2
                exit 1
            }
        fi
    fi
    exec python3 "$PYTHON_SCRIPT" "$@"
fi

# No Python found
echo "✗ Error: Neither uv nor python3 found" >&2
echo "Please install Python 3 or uv" >&2
exit 1
