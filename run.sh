#!/usr/bin/env bash
set -e

VENV_DIR="$HOME/realsense_venv"

if [ ! -d "$VENV_DIR" ]; then
    echo "Virtual environment not found."
    echo "Run ./setup.sh first."
    exit 1
fi

source "$VENV_DIR/bin/activate"
python3 realsense_test.py
