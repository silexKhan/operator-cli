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
rm -rf build/
# 전체 폴더를 지우지 않고 오직 새로 빌드할 바이너리만 핀포인트 청소하여 하위 자산(knowledge 등)을 철저히 보호 및 보존합니다.
rm -f release/operator_mac/operator
mkdir -p release/operator_mac

pyinstaller --clean --onefile --distpath release/operator_mac --name operator --exclude-module setuptools src/operator_cli/main.py

echo "[5/5] Organizing release package (Platform: macOS)..."
# Copy assets (이미 최종 폴더로 바이너리가 직배송되었으므로 자원 복사만 깔끔히 수행)
cp -r protocols release/operator_mac/
if [ -d "knowledge" ]; then
    cp -r knowledge release/operator_mac/
fi
cp docs/AGENT_GUIDE.md release/operator_mac/

echo "Build and Packaging Complete!"
echo "------------------------------------------------"
echo "Package Location: ./release/operator_mac/"
echo "------------------------------------------------"
