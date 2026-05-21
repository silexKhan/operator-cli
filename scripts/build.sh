#!/bin/bash

# Operator CLI Cross-Platform Build Script
set -e

# 실제 스크립트 파일의 위치 찾기 (심볼릭 링크 대응)
SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ]; do
  DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"
  SOURCE="$(readlink "$SOURCE")"
  [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE"
done
SCRIPT_DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"
PROJECT_ROOT="$SCRIPT_DIR/.."
cd "$PROJECT_ROOT"

echo "📂 [1/5] 가상환경 활성화 중..."
if [ -d ".venv" ]; then
    source .venv/bin/activate
else
    echo "❌ .venv 디렉토리를 찾을 수 없습니다. 가상환경을 먼저 생성해주세요."
    exit 1
fi

echo "📦 [2/5] 종속성 및 빌드 도구 설치 중..."
pip install -q --upgrade pip
pip install -q -e .
pip install -q pyinstaller

echo "📝 [3/5] AI 에이전트 가이드(AGENT_GUIDE.md) 생성 중..."
python3 scripts/generate_guide.py

echo "🔨 [4/5] PyInstaller를 사용하여 바이너리 빌드 중 (onefile 모드)..."
rm -rf dist/ build/ release/
pyinstaller --clean --onefile --name operator src/operator_cli/main.py

echo "📦 [5/5] 배포 패키지 구성 중 (Platform: macOS)..."
# 최종 배포용 플랫폼별 폴더 생성
mkdir -p release/operator_mac

# 빌드 결과물(단일 바이너리)을 플랫폼 폴더로 이동
mv dist/operator release/operator_mac/
rm -rf dist/

# 에셋 복사 (protocols 및 가이드)
cp -r protocols release/operator_mac/
cp docs/AGENT_GUIDE.md release/operator_mac/

echo "✅ 빌드 및 패키징 완료!"
echo "------------------------------------------------"
echo "배포 패키지 위치: ./release/operator_mac/"
echo "구성 요소:"
echo "  - operator (단일 실행 파일)"
echo "  - protocols/ (규약 데이터 폴더)"
echo "  - AGENT_GUIDE.md (AI 에이전트용 가이드)"
echo "------------------------------------------------"
