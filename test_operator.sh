#!/bin/bash

# Operator CLI smoke test.
# Uses a temporary OPERATOR_HOME so tests never mutate the user's runtime state.

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OPERATOR_CMD="${OPERATOR_CMD:-$PROJECT_ROOT/.venv/bin/operator}"

if [ ! -x "$OPERATOR_CMD" ]; then
    echo "Error: operator command is not executable: $OPERATOR_CMD"
    echo "Set OPERATOR_CMD=/path/to/operator to test a release binary."
    exit 1
fi

TMP_OPERATOR_HOME="$(mktemp -d)"
cleanup() {
    rm -rf "$TMP_OPERATOR_HOME"
}
trap cleanup EXIT

cp -R "$PROJECT_ROOT/protocols" "$TMP_OPERATOR_HOME/protocols"
export OPERATOR_HOME="$TMP_OPERATOR_HOME"

CIRCUIT_PATH="$(find "$TMP_OPERATOR_HOME/protocols/circuits" -maxdepth 1 -type f -name '*.md' | sort | head -n 1)"
if [ -z "$CIRCUIT_PATH" ]; then
    echo "Error: no circuit files found under protocols/circuits."
    exit 1
fi
CIRCUIT="$(basename "$CIRCUIT_PATH" .md)"

echo "=========================================="
echo "Operator CLI Smoke Test Started"
echo "=========================================="
echo "Operator command : $OPERATOR_CMD"
echo "Temporary home   : $TMP_OPERATOR_HOME"
echo "Circuit under test: $CIRCUIT"

echo
echo "[Test 1] Version Check"
"$OPERATOR_CMD" --version

echo
echo "[Test 2] Help Menu Generation"
"$OPERATOR_CMD" --help > /dev/null
echo "OK: help menu generated."

echo
echo "[Test 3] Circuits Command"
"$OPERATOR_CMD" circuits > /dev/null
echo "OK: circuits listed."

echo
echo "[Test 4] Units Command"
"$OPERATOR_CMD" units > /dev/null
echo "OK: units listed."

echo
echo "[Test 5] Initial Status"
"$OPERATOR_CMD" status > /dev/null
echo "OK: status reported."

echo
echo "[Test 6] Doctor Diagnostics"
"$OPERATOR_CMD" doctor --skip-ollama > /dev/null
echo "OK: doctor reported."

echo
echo "[Test 7] Knowledge JSON Query"
"$OPERATOR_CMD" knowledge query smoke --format json > /dev/null
echo "OK: knowledge JSON query reported."

echo
echo "[Test 8] Graph Subcommand Help"
"$OPERATOR_CMD" graph run --help > /dev/null
"$OPERATOR_CMD" graph label --help > /dev/null
"$OPERATOR_CMD" graph viz --help > /dev/null
echo "OK: graph subcommands are registered."

echo
echo "[Test 9] Connect To Valid Circuit"
"$OPERATOR_CMD" call "$CIRCUIT" > /dev/null
echo "OK: connected to $CIRCUIT."

echo
echo "[Test 10] Status Verification"
"$OPERATOR_CMD" status | grep "Active Circuit : $CIRCUIT" > /dev/null
echo "OK: status shows $CIRCUIT."

echo
echo "[Test 11] Reset Context"
"$OPERATOR_CMD" status reset > /dev/null
"$OPERATOR_CMD" status | grep "Disconnected" > /dev/null
echo "OK: context reset without touching user state."

echo "=========================================="
echo "All Operator CLI smoke tests passed."
echo "=========================================="
