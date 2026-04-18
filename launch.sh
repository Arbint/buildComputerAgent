#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=== DIY PC Build Assistant - Linux ==="

# Detect package manager
if command -v apt-get &>/dev/null; then
    PKG_INSTALL="sudo apt-get install -y"
    PKG_UPDATE="sudo apt-get update -y"
    PYTHON_PKG="python3.12"
elif command -v dnf &>/dev/null; then
    PKG_INSTALL="sudo dnf install -y"
    PKG_UPDATE="sudo dnf check-update -y || true"
    PYTHON_PKG="python3.12"
elif command -v pacman &>/dev/null; then
    PKG_INSTALL="sudo pacman -S --noconfirm"
    PKG_UPDATE="sudo pacman -Sy"
    PYTHON_PKG="python"
else
    echo "ERROR: Unsupported package manager. Install Python 3.12+ and uv manually."
    exit 1
fi

# Check Python 3.12+
PYTHON_BIN=""
for candidate in python3.12 python3.13 python3.14 python3; do
    if command -v "$candidate" &>/dev/null; then
        VERSION=$("$candidate" -c "import sys; print(sys.version_info >= (3,12))" 2>/dev/null)
        if [ "$VERSION" = "True" ]; then
            PYTHON_BIN="$candidate"
            break
        fi
    fi
done

if [ -z "$PYTHON_BIN" ]; then
    echo "Python 3.12+ not found. Installing..."
    $PKG_UPDATE
    $PKG_INSTALL "$PYTHON_PKG"
    PYTHON_BIN="python3.12"
fi
echo "Using Python: $($PYTHON_BIN --version)"

# Check uv
if ! command -v uv &>/dev/null; then
    echo "uv not found. Installing via pip..."
    "$PYTHON_BIN" -m pip install --user uv
    export PATH="$HOME/.local/bin:$PATH"
fi

if ! command -v uv &>/dev/null; then
    echo "ERROR: uv could not be installed. Install it manually: https://github.com/astral-sh/uv"
    exit 1
fi
echo "Using uv: $(uv --version)"

# Check CLAUDE_API_KEY
if [ -z "${CLAUDE_API_KEY:-}" ]; then
    echo ""
    echo "WARNING: CLAUDE_API_KEY is not set."
    read -rp "Enter your Anthropic API key: " CLAUDE_API_KEY
    export CLAUDE_API_KEY
fi

# Install dependencies and run
cd "$SCRIPT_DIR"
echo "Syncing dependencies..."
uv sync

echo ""
echo "Launching..."
uv run buildcomputer
