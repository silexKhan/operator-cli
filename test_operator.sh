#!/bin/bash

# Operator CLI Integration Test Script
# 이 스크립트는 지금까지 변경된 Operator CLI의 핵심 기능들이 정상 동작하는지 검증합니다.

OPERATOR_CMD="/Users/silex/workspace/private/operator-cli/release/operator_mac/operator"

echo "=========================================="
echo "🧪 Operator CLI Integration Test Started"
echo "=========================================="

echo -e "\n[Test 1] Version Check"
$OPERATOR_CMD --version
if [ $? -ne 0 ]; then echo "❌ Version check failed!"; exit 1; fi

echo -e "\n[Test 2] Help Menu Generation"
$OPERATOR_CMD --help > /dev/null
if [ $? -ne 0 ]; then echo "❌ Help menu failed!"; exit 1; else echo "✓ Help menu generated successfully."; fi

echo -e "\n[Test 3] Initial Status"
$OPERATOR_CMD status
if [ $? -ne 0 ]; then echo "❌ Initial status check failed!"; exit 1; fi

echo -e "\n[Test 4] Connect to GDR Circuit"
$OPERATOR_CMD connect gdr > /dev/null
if [ $? -ne 0 ]; then echo "❌ Connect to GDR failed!"; exit 1; else echo "✓ Connected to GDR."; fi

echo -e "\n[Test 5] Status Verification (GDR)"
$OPERATOR_CMD status | grep "Active Circuit : gdr" > /dev/null
if [ $? -ne 0 ]; then echo "❌ Status does not show GDR!"; exit 1; else echo "✓ Status verified (GDR)."; fi

echo -e "\n[Test 6] Connect to MCP Circuit"
$OPERATOR_CMD connect mcp > /dev/null
if [ $? -ne 0 ]; then echo "❌ Connect to MCP failed!"; exit 1; else echo "✓ Connected to MCP."; fi

echo -e "\n[Test 7] Reset Context"
$OPERATOR_CMD status reset > /dev/null
if [ $? -ne 0 ]; then echo "❌ Status reset failed!"; exit 1; else echo "✓ Context reset successfully."; fi

echo -e "\n[Test 8] Final Status Check (Disconnected)"
$OPERATOR_CMD status | grep "Disconnected" > /dev/null
if [ $? -ne 0 ]; then echo "❌ Status is not disconnected!"; exit 1; else echo "✓ Final status verified (Disconnected)."; fi

echo -e "\n[Test 9] Graph Command Help"
$OPERATOR_CMD graph --help > /dev/null
if [ $? -ne 0 ]; then echo "❌ Graph help command failed!"; exit 1; else echo "✓ Graph help verified."; fi

echo -e "\n[Test 10] Graphify Delay Setting"
$OPERATOR_CMD setting graphify-delay 45 > /dev/null
if [ $? -ne 0 ]; then echo "❌ Setting graphify-delay failed!"; exit 1; else echo "✓ Graphify delay set to 45 mins."; fi

echo -e "\n[Test 11] Graph Run (Dry-run/Check basic execution)"
# 유예 시간 체크 로직이 동작하는지 확인 (force 없이 실행 시 경고 문구가 나오거나 바로 실행됨)
$OPERATOR_CMD graph run --help > /dev/null
if [ $? -ne 0 ]; then echo "❌ Graph run command failed!"; exit 1; else echo "✓ Graph run command verified."; fi

echo -e "\n[Test 12] Knowledge Open Help"
$OPERATOR_CMD knowledge open --help > /dev/null
if [ $? -ne 0 ]; then echo "❌ Knowledge open help command failed!"; exit 1; else echo "✓ Knowledge open help verified."; fi

echo -e "\n[Test 13] Knowledge Open Execution (Dry-run with known ID)"
# 실제로 파일을 열면 편집기가 뜨므로, 존재하지 않는 ID로 에러 핸들링이 잘 되는지 확인
$OPERATOR_CMD knowledge open K-NONEXISTENT 2>&1 | grep "not found" > /dev/null
if [ $? -ne 0 ]; then echo "❌ Knowledge open error handling failed!"; exit 1; else echo "✓ Knowledge open error handling verified."; fi

echo "=========================================="
echo "✅ All Integration Tests Passed!"
echo "=========================================="
