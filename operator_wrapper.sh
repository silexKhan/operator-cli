#!/bin/bash
# Operator CLI Ultra-Fast Wrapper
# 가상환경의 파이썬을 사용하여 즉시 실행합니다.

PROJECT_ROOT="/Users/silex/workspace/private/operator-cli"
VENV_PYTHON="$PROJECT_ROOT/.venv/bin/python"
MAIN_SCRIPT="$PROJECT_ROOT/src/operator_cli/main.py"

# PYTHONPATH 설정 (src layout 보장)
export PYTHONPATH="$PROJECT_ROOT/src:$PYTHONPATH"

# 파이썬 실행
exec "$VENV_PYTHON" "$MAIN_SCRIPT" "$@"
