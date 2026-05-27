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

echo "=========================================="
echo "✅ All Integration Tests Passed!"
echo "=========================================="
