#!/bin/bash

# Operator CLI Cross-Platform Build Script
set -e

BUILD_MODE="onedir"
if [ "${1:-}" = "--mode" ]; then
    BUILD_MODE="${2:-onedir}"
elif [ "${1:-}" != "" ]; then
    BUILD_MODE="$1"
fi

case "$BUILD_MODE" in
    onedir)
        PYINSTALLER_MODE="--onedir"
        RELEASE_BINARY="release/operator_mac/operator/operator"
        ;;
    onefile)
        PYINSTALLER_MODE="--onefile"
        RELEASE_BINARY="release/operator_mac/operator"
        ;;
    *)
        echo "Invalid build mode: $BUILD_MODE"
        echo "Usage: ./scripts/build.sh [--mode onedir|onefile]"
        exit 1
        ;;
esac

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

echo "[1/6] Checking environment..."
if [ -d ".venv" ]; then
    echo "Activating local virtual environment (.venv)..."
    source .venv/bin/activate
else
    echo "No local .venv found. Proceeding with system/CI python environment."
fi

echo "[2/6] Installing dependencies..."
python3 -m pip install -q --upgrade pip
python3 -m pip install -q -e .
python3 -m pip install -q pyinstaller

echo "[3/6] Generating AI Agent Guide (AGENT_GUIDE.md)..."
python3 scripts/generate_guide.py

echo "[4/6] Building binary with PyInstaller ($BUILD_MODE mode)..."
rm -rf build/
rm -rf release/operator_mac/operator
mkdir -p release/operator_mac

pyinstaller --clean "$PYINSTALLER_MODE" --distpath release/operator_mac --name operator --exclude-module setuptools src/operator_cli/main.py

echo "[5/6] Organizing release package (Platform: macOS)..."
# Copy assets (이미 최종 폴더로 바이너리가 직배송되었으므로 자원 복사만 깔끔히 수행)
rm -rf release/operator_mac/protocols release/operator_mac/knowledge
cp -r protocols release/operator_mac/
if [ -d "knowledge" ]; then
    cp -r knowledge release/operator_mac/
fi
cp docs/AGENT_GUIDE.md release/operator_mac/

if [ "${CI:-}" = "true" ]; then
    echo "[6/6] Skipping runtime deployment in CI."
else
    RUNTIME_HOME="${OPERATOR_RUNTIME_HOME:-${OPERATOR_HOME:-$HOME/.operator}}"
    echo "[6/6] Deploying runtime binary to: $RUNTIME_HOME"
    mkdir -p "$RUNTIME_HOME"
    if [ "$BUILD_MODE" = "onedir" ]; then
        # onedir 모드인 경우, 내부 라이브러리 폴더(_internal)를 포함하여 전체 복사
        cp -R release/operator_mac/operator/* "$RUNTIME_HOME/"
    else
        # onefile 모드인 경우, 단일 실행 파일만 복사
        cp "$RELEASE_BINARY" "$RUNTIME_HOME/operator"
    fi
    chmod +x "$RUNTIME_HOME/operator"
fi

echo "Build and Packaging Complete!"
echo "------------------------------------------------"
echo "Package Location: ./release/operator_mac/"
echo "Build Mode      : $BUILD_MODE"
echo "Release Binary  : $RELEASE_BINARY"
if [ "${CI:-}" != "true" ]; then
    echo "Runtime Binary : ${RUNTIME_HOME}/operator"
fi
echo "------------------------------------------------"
