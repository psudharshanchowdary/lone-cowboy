#!/usr/bin/env bash
# Launcher for Lone Cowboy: Wild West Outlaws

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if [ -f "$SCRIPT_DIR/.venv/bin/python" ]; then
    PYTHON_CMD="$SCRIPT_DIR/.venv/bin/python"
elif command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
else
    echo "Python 3 is required to run the game."
    exit 1
fi

echo "Launching Lone Cowboy: Wild West Outlaws..."
"$PYTHON_CMD" main.py
