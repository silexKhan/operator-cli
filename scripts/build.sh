#!/bin/bash

# Operator CLI Cross-Platform Build Script
set -e

# Find script directory
SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ]; do
  DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"
  SOURCE="$(readlink "$SOURCE")"
  [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE"
done
SCRIPT_DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"
PROJECT_ROOT="$SCRIPT_DIR/.."
cd "$PROJECT_ROOT"

echo "[1/5] Checking environment..."
if [ -d ".venv" ]; then
    echo "Activating local virtual environment (.venv)..."
    source .venv/bin/activate
else
    echo "No local .venv found. Proceeding with system/CI python environment."
fi

echo "[2/5] Installing dependencies..."
python3 -m pip install -q --upgrade pip
python3 -m pip install -q -e .
python3 -m pip install -q pyinstaller

echo "[3/5] Generating AI Agent Guide (AGENT_GUIDE.md)..."
python3 scripts/generate_guide.py

echo "[4/5] Building binary with PyInstaller (onefile mode)..."
rm -rf dist/ build/
pyinstaller --clean --onefile --name operator src/operator_cli/main.py

echo "[5/5] Organizing release package (Platform: macOS)..."
mkdir -p release/operator_mac
mv dist/operator release/operator_mac/
rm -rf dist/

# Copy assets
cp -r protocols release/operator_mac/
cp docs/AGENT_GUIDE.md release/operator_mac/

echo "Build and Packaging Complete!"
echo "------------------------------------------------"
echo "Package Location: ./release/operator_mac/"
echo "------------------------------------------------"
