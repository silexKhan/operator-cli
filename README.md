# Operator CLI

**Operator CLI**는 프로젝트 전용 규약(Protocols)을 기반으로 AI 모델의 행동을 정교하게 제어하고 작업을 수행하는 지능형 에이전트 기반 CLI 도구입니다.

## 🚀 주요 특징 (Key Features)

### 1. 정제된 클린 아키텍처 (Clean Architecture)
- **src layout** 적용으로 비즈니스 로직과 메타 데이터를 명확히 분리.
- 목적별 명령어 분류 (`info`, `ops`, `config`) 및 핵심 로직 패키지화.
- LLM 제공자 추상화 레이어를 통해 다양한 모델(Ollama, OpenAI 등) 확장성 확보.

### 2. 지능형 컨텍스트 관리 (Intelligent Context Control)
- **자동 요약 (Compaction)**: 작업 이력을 구조화된 포맷(Goal, Progress, Decisions)으로 요약하여 `MEMORY.md` 자동 갱신.
- **히스토리 및 Split Turn**: 대화 이력을 영구 저장하며, 임계값 초과 시 지능적으로 부분 요약을 수행하여 흐름을 유지.
- **핵심 규약 보호**: `[LITERAL]` 태그를 통해 압축 시에도 핵심 기술 지침이 희석되지 않도록 보호.
- **페르소나 리프레시**: 매 턴마다 모델의 정체성을 재주입하여 명령 이탈(Instruction Drift) 방지.

### 3. 멀티 플랫폼 및 자동 배포
- **Cross-Platform**: macOS와 Windows 환경을 모두 지원하는 빌드 시스템.
- **GitHub Actions**: 푸시 시 각 OS용 배포 패키지(.zip, .exe) 자동 생성 및 아티팩트 업로드.
- **AI Agent Guide**: 다른 AI 도구(Cursor, Windsurf 등)가 오퍼레이터를 즉시 이해할 수 있는 `AGENT_GUIDE.md` 자동 생성.

## 🛠 설치 방법 (Installation)

```bash
# 저장소 복제
git clone https://github.com/silexKhan/operator-cli.git
cd operator-cli

# 가상환경 생성 및 활성화
python3 -m venv .venv
source .venv/bin/activate

# 의존성 및 에디터블 모드 설치
pip install -e .
```

## 📖 사용 방법 (Usage)

### 기본 워크플로우
1. **회선 연결**: 작업할 프로젝트 노드로 전환합니다.
   ```bash
   operator call matrix
   ```
2. **명령 수행**: AI 에이전트에게 지시를 내립니다.
   ```bash
   operator agent "신규 API 모듈을 설계해줘" --thinking high
   ```
3. **상태 확인**: 현재 로드된 프로토콜과 활성 회선을 확인합니다.
   ```bash
   operator status
   ```
4. **기억 영속화**: 작업 완료 후 이력을 요약 기록합니다.
   ```bash
   operator summarize
   ```

### 추론 제어 (Thinking Levels)
`-t` 또는 `--thinking` 옵션을 통해 모델의 사고 깊이를 조절할 수 있습니다:
- `minimal`, `low`, `medium`, `high`, `xhigh`

## 🧩 확장성 및 하네싱 (Extensibility & Harnessing)

Operator CLI는 규약(Protocol) 기반의 확장을 통해 특정 프로젝트나 기술 스택에 맞게 AI를 최적화할 수 있습니다.

### 1. 회선(Circuit) 추가
`protocols/circuits/` 디렉토리에 새로운 마크다운 파일을 추가하여 새로운 프로젝트 환경을 정의하십시오.
- 예: `my-project.md` 추가 시 `operator call my-project`로 연결 가능.

### 2. 유닛(Unit) 추가
`protocols/units/` 디렉토리에 특정 기술 스택이나 도메인 지침을 추가하십시오.
- 예: `react-ts.md`, `cloud-native.md` 등을 추가하여 AI에게 전문 지식을 주입(Harnessing)할 수 있습니다.

이러한 구조를 통해 복잡한 비즈니스 로직이나 엄격한 코딩 컨벤션이 필요한 환경에서도 AI 에이전트를 강력하게 제어할 수 있습니다.

## 🏗 빌드 (Build)

### macOS (맥 터미널)
```bash
./build.sh
```
결과물 위치: `release/operator_mac/`

로컬 환경에서는 빌드된 바이너리를 `${OPERATOR_RUNTIME_HOME:-${OPERATOR_HOME:-$HOME/.operator}}/bin/operator`로도 복사합니다. 이 단계는 runtime의 개인 회선/프로토콜 파일을 덮어쓰지 않고 실행 파일만 갱신합니다.

### Windows (PowerShell)
```bash
powershell ./scripts/build.ps1
```
결과물 위치: `dist/win/`

## 📄 라이선스 (License)
이 프로젝트는 개인 개발용 도구로 배포됩니다.
