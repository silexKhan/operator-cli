# Operator CLI Windows Build Script (PowerShell)
# Windows 환경에서 실행하십시오.

$ErrorActionPreference = "Stop"

echo "📂 [1/5] 가상환경 활성화 중..."
if (Test-Path ".venv\Scripts\activate.ps1") {
    . .venv\Scripts\activate.ps1
} else {
    echo "❌ .venv 디렉토리를 찾을 수 없습니다. 가상환경을 먼저 생성해주세요."
    exit
}

echo "📦 [2/5] 종속성 및 빌드 도구 설치 중..."
pip install -q --upgrade pip
pip install -q -e .
pip install -q pyinstaller

echo "📝 [3/5] AI 에이전트 가이드(AGENT_GUIDE.md) 생성 중..."
python scripts/generate_guide.py

echo "🔨 [4/5] PyInstaller를 사용하여 바이너리 빌드 중 (onedir 모드)..."
if (Test-Path "dist") { Remove-Item -Recurse -Force "dist" }
if (Test-Path "build") { Remove-Item -Recurse -Force "build" }
pyinstaller --clean --onedir --name operator_bin src/operator_cli/main.py

echo "📦 [5/5] 배포 패키지 구성 중 (Platform: Windows)..."
# 플랫폼별 폴더 구조 생성
New-Item -ItemType Directory -Force -Path "dist\win"

# 빌드 결과물 이동
Move-Item -Path "dist\operator_bin\*" -Destination "dist\win"
Remove-Item -Path "dist\operator_bin"

# 에셋 복사 (protocols 및 가이드)
Copy-Item -Recurse -Path "protocols" -Destination "dist\win"
Copy-Item -Path "docs\AGENT_GUIDE.md" -Destination "dist\win"

echo "✅ 빌드 및 패키징 완료!"
echo "------------------------------------------------"
echo "배포 패키지 위치: .\dist\win\"
echo "구성 요소:"
echo "  - operator_bin.exe (실행 파일)"
echo "  - protocols/ (규약 폴더)"
echo "  - AGENT_GUIDE.md (에이전트용 가이드)"
echo "------------------------------------------------"
