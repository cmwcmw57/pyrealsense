#!/usr/bin/env bash
set -e

echo "=== RealSense Python environment setup ==="

if [ "$EUID" -eq 0 ]; then
    SUDO=""
else
    SUDO="sudo"
fi

echo "[1/4] Installing system packages..."
$SUDO apt update
$SUDO apt install -y python3-pip python3-venv libusb-1.0-0 libgl1

echo "[2/4] Creating Python virtual environment..."
VENV_DIR="$HOME/realsense_venv"

if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv "$VENV_DIR"
else
    echo "Virtual environment already exists: $VENV_DIR"
fi

echo "[3/4] Installing Python packages..."
"$VENV_DIR/bin/python" -m pip install --upgrade pip
"$VENV_DIR/bin/python" -m pip install -r requirements.txt

echo "[4/4] Done."
echo
echo "Activate the environment with:"
echo "  source $VENV_DIR/bin/activate"
echo
echo "Run the RealSense example with:"
echo "  python3 realsense_test.py"
