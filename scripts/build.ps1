# Operator CLI Windows Build Script (PowerShell)
$ErrorActionPreference = "Stop"

Write-Host "📂 [1/5] Activating virtual environment..."
if (Test-Path ".venv\Scripts\activate.ps1") {
    . .venv\Scripts\activate.ps1
} else {
    Write-Error "❌ .venv directory not found. Please create virtual environment first."
    exit 1
}

Write-Host "📦 [2/5] Installing dependencies..."
pip install -q --upgrade pip
pip install -q -e .
pip install -q pyinstaller

Write-Host "📝 [3/5] Generating AI Agent Guide..."
python scripts/generate_guide.py

Write-Host "🔨 [4/5] Building binary with PyInstaller (onefile mode)..."
if (Test-Path "dist") { Remove-Item -Recurse -Force "dist" }
if (Test-Path "build") { Remove-Item -Recurse -Force "build" }
pyinstaller --clean --onefile --name operator src/operator_cli/main.py

Write-Host "📦 [5/5] Organizing release package..."
if (Test-Path "release") { Remove-Item -Recurse -Force "release" }
New-Item -ItemType Directory -Force -Path "release\operator_win"

Move-Item -Path "dist\operator.exe" -Destination "release\operator_win"
Remove-Item -Recurse -Force "dist"

Copy-Item -Recurse -Path "protocols" -Destination "release\operator_win"
Copy-Item -Path "docs\AGENT_GUIDE.md" -Destination "release\operator_win"

Write-Host "✅ Build and Packaging Complete!"
Write-Host "------------------------------------------------"
Write-Host "Release Location: .\release\operator_win\"
Write-Host "Components:"
Write-Host "  - operator.exe"
Write-Host "  - protocols/"
Write-Host "  - AGENT_GUIDE.md"
Write-Host "------------------------------------------------"
