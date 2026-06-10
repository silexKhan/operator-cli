# Operator CLI Development Review

작성일: 2026-06-08

## Executive Summary

Operator CLI는 "프로젝트별 Protocol 주입 + 로컬 LLM 기반 Agent + OAKS 지식 저장소 + Graphify 구조 탐색"이라는 방향이 분명한 도구다. 현재 구현은 주요 축이 모두 들어와 있으며, `call`, `status`, `agent`, `knowledge`, `graph`, `summarize`, `setting` 명령도 기본 골격을 갖췄다.

다만 지금 상태는 "개념 검증이 된 프로토타입"에 가깝다. 운영 도구로 계속 쓰려면 다음 세 가지를 우선적으로 정리해야 한다.

1. 릴리즈 실행 성능과 패키징 전략
2. 실제 세션/지식/프로토콜 상태의 무결성
3. 테스트와 문서가 실제 명령 체계와 동기화되는 구조

이 리포트는 단순 결함 지적이 아니라, 각 항목이 왜 문제가 되는지와 개선 후 어떤 효과가 생기는지까지 함께 정리한다.

## Current Architecture

현재 구조는 다음 계층으로 볼 수 있다.

- CLI entrypoint: `src/operator_cli/main.py`
- Command modules: `commands/ops`, `commands/info`, `commands/config`
- Core engines: `core/protocol`, `core/knowledge`, `core/compaction`, `core/models`
- LLM provider: `llm/providers/ollama.py`
- Release packaging: `scripts/build.sh`, `scripts/build.ps1`, `.github/workflows/build.yml`
- Protocol assets: `protocols/global.md`, `protocols/circuits`, `protocols/units`
- Knowledge assets: `knowledge`, `llms.txt`, `llms-full.txt`

문서상 의도도 이 구조와 대체로 일치한다.

- Protocols: AI의 행동 규약
- OAKS Knowledge: 검증된 도메인 지식
- Graphify: 코드/문서 관계망 탐색
- Local LLM Agent: 로컬 모델 기반 명령 분석 및 제안

## Findings And Improvements

### 1. Release Startup Is Dominated By PyInstaller Onefile Boot Cost

근거:

- `scripts/build.sh`는 `pyinstaller --clean --onefile`로 빌드한다.
- 릴리즈 바이너리 `operator --version`은 약 4초 이상, `operator --help`는 약 5초 이상 걸린다.
- 같은 소스를 `.venv/bin/operator`로 실행하면 `--version`과 `--help`는 0.1초대다.

왜 문제인가:

`operator`는 자주 호출되는 CLI다. `status`, `call`, `knowledge query`, `--help` 같은 명령이 매번 4-6초 걸리면 도구가 "항상 켜져 있는 조작 인터페이스"가 아니라 "가끔 실행하는 무거운 앱"처럼 느껴진다. 특히 에이전트가 작업 중 여러 번 호출하면 이 지연은 누적된다.

개선 방향:

- 기본 릴리즈는 `--onedir`로 전환한다.
- 단일 파일 배포가 필요한 경우만 별도 `onefile` 빌드 타깃으로 유지한다.
- 쉘 alias는 `release/operator_mac/operator/operator`처럼 onedir 내부 실행 파일을 가리키게 한다.
- 빌드 스크립트에 `--mode onedir|onefile` 옵션을 둔다.

개선 효과:

- 릴리즈 실행 속도가 개발 실행에 가까워진다.
- 개발/릴리즈 분리는 유지된다.
- 사용자는 단일 파일의 깔끔함보다 실제 CLI 응답성을 얻는다.
- 추후 `operator status` 같은 짧은 명령을 자주 쓰는 워크플로우가 자연스러워진다.

### 2. CLI Entrypoint Still Does Too Much At Import Time

근거:

- `main.py`는 `knowledge`, `graph`, `setting`, `status`, `circuits`, `units`, 호환 명령 모듈을 top-level에서 등록한다.
- `main.py`는 help 텍스트 생성을 위해 `get_circuit_names()`를 import 시점에 호출한다.
- 이번 점검 중 일부 무거운 import는 lazy import로 옮겼지만, entrypoint 전체는 여전히 모든 서브앱을 구성한 뒤 `--version`을 처리한다.

왜 문제인가:

CLI의 가장 가벼운 경로인 `--version`도 전체 명령 트리 구성 비용을 지불한다. 지금은 onefile 비용이 더 커서 가려져 있지만, onedir 전환 후에는 이 구조가 다시 병목이 된다. 또한 명령 추가가 많아질수록 단순 명령의 시작 시간이 같이 증가한다.

개선 방향:

- `--version`은 Typer callback 이전에 `sys.argv`를 직접 빠르게 처리하는 fast path를 둔다.
- help에 들어가는 동적 회선/유닛 목록은 필요할 때만 계산하거나 캐시한다.
- 서브명령 등록은 최소 모듈만 import하고 실제 구현은 command 함수 내부에서 import한다.

개선 효과:

- 단순 명령의 체감 속도가 안정된다.
- 명령 수가 늘어나도 startup 비용이 선형으로 증가하지 않는다.
- 패키징 방식과 무관하게 CLI가 가볍게 유지된다.

### 3. `summarize` Is Advertised As Memory Management But Uses Dummy History

근거:

- `commands/ops/summarize.py`는 실제 `ContextManager.history`를 쓰지 않고 `dummy_history`를 요약한다.
- README와 AGENT_GUIDE는 `operator summarize`를 작업 이력 영속화 기능으로 설명한다.

왜 문제인가:

사용자는 `operator summarize`가 현재 작업 맥락을 저장한다고 믿게 된다. 하지만 실제로는 고정된 데모 메시지를 요약하므로, MEMORY.md가 쌓일수록 신뢰할 수 없는 메모리가 된다. Operator의 핵심 가치가 "기억을 통한 지속성"이라면 이 불일치는 기능 결함보다 더 큰 신뢰 문제다.

개선 방향:

- `ContextManager.get_history()`를 실제 입력으로 사용한다.
- 요약 성공 후 history를 "요약 + 최근 N턴"으로 압축하는 정책을 만든다.
- `MEMORY.md` 위치를 `Path.cwd()`가 아니라 Operator project root 또는 active circuit별 memory로 명확히 한다.
- history가 비어 있으면 명확히 "요약할 이력이 없다"고 종료한다.

개선 효과:

- Operator가 실제 작업을 기억하는 도구가 된다.
- 장기 세션에서 컨텍스트 누적과 요약이 연결된다.
- 잘못된 MEMORY.md가 에이전트 판단을 오염시키는 위험이 줄어든다.

### 4. Protocol Compression Can Silently Change The Rules

근거:

- `ProtocolEngine.get_full_context()`는 8000자 초과 시 LLM으로 프로토콜을 압축한다.
- 압축 실패는 `except Exception: pass`로 조용히 무시된다.
- 압축 결과는 `compressed_protocols`에 저장되지만 원본 프로토콜 변경 여부와 캐시 무효화 기준이 없다.

왜 문제인가:

Protocol은 Operator의 행동 규칙이다. LLM 압축이 핵심 지시를 누락하거나 표현을 바꾸면, 이후 agent는 원본 규칙이 아니라 변형된 규칙을 따르게 된다. 더 위험한 점은 이 변화가 사용자에게 잘 드러나지 않는다는 것이다.

개선 방향:

- 압축 캐시에 원본 파일 해시, 압축 모델, 생성 시각을 함께 저장한다.
- 원본 프로토콜 해시가 바뀌면 캐시를 무효화한다.
- 압축 결과에는 "must preserve" 섹션을 별도 검증한다.
- 압축 실패 또는 캐시 사용 여부를 `status`에서 표시한다.
- 중요한 회선은 기본적으로 압축 없이 원문을 유지하거나, 사용자가 승인한 압축본만 사용한다.

개선 효과:

- Protocol이 예측 가능한 시스템 자산이 된다.
- 지침 변경 원인을 추적할 수 있다.
- 장기적으로 "프로토콜은 절대적"이라는 제품 철학과 구현이 맞아진다.

### 5. Context Storage Needs Stronger State Integrity

근거:

- `OperatorContext`는 `compressed_protocols: Dict[str, str] = {}`와 `history: List[...] = []`를 클래스 필드 기본값으로 둔다.
- `ContextManager._load_context()`는 JSON 파싱 실패 시 조용히 새 `OperatorContext()`를 반환한다.
- 저장은 일반 파일 write로 수행되며 atomic write나 backup이 없다.

왜 문제인가:

Operator의 상태 파일은 active circuit, model, history, 압축 프로토콜을 담는 핵심 데이터다. 파일이 깨지거나 동시 쓰기가 발생하면 사용자는 갑자기 회선이 사라지거나 히스토리가 초기화된 것처럼 보게 된다. 조용한 초기화는 문제를 숨겨서 복구 기회도 줄인다.

개선 방향:

- Pydantic `Field(default_factory=dict/list)`를 사용한다.
- JSON 파싱 실패 시 `.bak`를 만들고 사용자에게 경고한다.
- 저장은 임시 파일에 쓴 뒤 atomic rename 한다.
- context schema version을 둔다.

개선 효과:

- 상태 손상 시 원인과 복구 지점이 생긴다.
- 동시 호출이나 강제 종료에도 상태 보존성이 올라간다.
- active circuit 기반 워크플로우가 더 안정적이 된다.

### 6. Shell Execution Uses `shell=True` With Keyword Blocking

근거:

- `ShellExecutor.execute()`는 `subprocess.run(..., shell=True)`를 사용한다.
- 위험 명령 차단은 `"rm -rf"`, `"mkfs"` 같은 문자열 포함 검사에 의존한다.
- 실행 여부 확인은 LLM이 제안한 fenced code block을 정규식으로 추출한 뒤 사용자 confirm으로 처리한다.

왜 문제인가:

문자열 차단은 우회가 쉽고, 반대로 안전한 명령도 오탐할 수 있다. `shell=True`는 파이프, 리다이렉션, 환경 변수, command substitution까지 모두 쉘에 맡기기 때문에 실행 표면이 넓다. Operator가 `--execute`를 제공하는 순간 이 부분은 제품 신뢰의 핵심이다.

개선 방향:

- 명령을 shell segment 단위로 파싱하고 위험한 operator를 별도 모델링한다.
- 기본은 dry-run 또는 command proposal만 제공한다.
- 실행은 allowlist/approval policy를 별도 파일에 저장한다.
- stdout/stderr 최대 크기 제한, binary output sanitization, timeout 정책을 강화한다.
- 작업 디렉토리와 환경 변수를 명시적으로 표시하고 실행 전 diff-like preview를 준다.

개선 효과:

- 자율 실행 기능을 켜도 사고 가능성이 줄어든다.
- 사용자가 어떤 권한을 허용했는지 추적할 수 있다.
- 향후 CI나 다중 프로젝트 환경에서 실행 정책을 재사용할 수 있다.

### 7. OAKS Storage Format Is Useful But Not Yet Durable Enough

근거:

- `KnowledgeManager.save_knowledge()`는 `---` 사이에 JSON을 저장한다.
- `load_knowledge()`는 front matter 파싱 실패 시 metadata를 `None`으로 반환한다.
- `save_knowledge()`에서 llms refresh 실패를 조용히 무시한다.
- `query_knowledge()`는 본문 substring 검색만 수행한다.

왜 문제인가:

OAKS는 "검증된 지식"을 관리하는 시스템이다. 지식 파일의 메타데이터가 깨지거나 llms 동기화가 실패해도 사용자가 모르면, AI가 보는 지식과 실제 저장소가 달라진다. substring 검색은 빠르지만 동의어, 태그, 제목, 카테고리 기반 질의에는 약하다.

개선 방향:

- JSON front matter라면 명시적으로 `format: json-frontmatter`를 문서화하거나, 표준 YAML front matter로 전환한다.
- metadata parse 실패는 `operator knowledge doctor`에서 진단 가능하게 만든다.
- refresh 실패는 warning으로 노출하고, 마지막 성공 시각을 기록한다.
- 검색은 title/tags/content 가중치 기반으로 개선한다.
- `--format json` 옵션을 실제로 추가해 AI가 결과를 안정적으로 파싱하게 한다.

개선 효과:

- OAKS가 단순 파일 묶음이 아니라 운영 가능한 지식 DB가 된다.
- AI와 사람이 같은 지식 상태를 보게 된다.
- 지식 검색의 재현성과 설명 가능성이 올라간다.

### 8. Public Documentation Needs An Explicit Private Circuit Policy

근거:

- README는 macOS 빌드 결과 위치를 `dist/mac/`라고 설명하지만 스크립트는 `release/operator_mac/`에 둔다.
- 개인 작업 회선은 public commit/agent guide에 노출되지 않아야 한다.
- 기존에는 private 회선 제외 정책이 생성 스크립트 내부 하드코딩으로 표현될 수 있었다.
- `protocols/global.md`나 생성된 `AGENT_GUIDE.md` 같은 공용 문서 경로에는 개인 회선 관련 규약이 섞일 수 있다.

왜 문제인가:

개인 회선을 public 문서에서 숨기는 방향은 맞다. 문제는 그 정책이 명시적인 설정이나 별도 runtime home이 아니라 생성 스크립트 내부 하드코딩으로만 존재할 때 생긴다. 이렇게 두면 새 개인 회선을 추가할 때 누락되기 쉽고, 반대로 공개해야 할 회선이 실수로 빠질 수도 있다. 또한 회선 목록만 숨겨도 global protocol이나 예시 문서에 개인 프로젝트명이 남으면 숨김 정책이 깨진다.

개선 방향:

- README의 빌드 결과 경로를 실제 release 경로로 수정한다.
- 개발 repo에는 public 회선만 두고, 실제 사용 runtime home에는 private 회선을 둔다.
- 추가로 공개/비공개 회선 정책이 필요하면 설정 파일로 분리한다. 예: `protocols/visibility.toml` 또는 각 circuit front matter의 `visibility: public|private`.
- `generate_guide.py`는 visibility 설정을 기준으로 public guide를 생성한다.
- private 회선 전용 global rules는 public guide 생성 시 제외하거나, private overlay protocol로 분리한다.
- `operator doctor docs` 같은 검증 명령으로 README/AGENT_GUIDE/CLI help의 주요 항목 불일치와 private leakage를 검사한다.

개선 효과:

- public commit에 개인 회선이 섞이는 위험이 줄어든다.
- 개인 환경에서는 runtime home의 private 회선을 계속 쓸 수 있고, 공개 문서에는 개발 repo의 public 회선만 노출된다.
- 회선 추가/삭제 시 문서 생성 정책이 코드 수정 없이 유지된다.
- 다른 AI 에이전트가 public guide를 읽어도 개인 프로젝트명이나 내부 규약을 기준으로 잘못된 명령을 만들지 않는다.

### 9. Integration Test Script Is Stale And Mutates Real User State

근거:

- `test_operator.sh`는 과거 회선명을 테스트하고 있었고, 현재 공개 회선명은 `matrix`다.
- 테스트는 실제 release binary와 실제 `.operator_context.json` 상태를 사용한다.
- `setting graphify-delay 45`처럼 사용자 설정을 변경한다.

왜 문제인가:

테스트는 회귀를 잡는 안전망이어야 한다. 현재 테스트는 실행 자체가 실패할 가능성이 있고, 성공하더라도 사용자의 실제 Operator 상태를 바꾼다. 그러면 테스트를 자주 돌리기 어렵고, 결국 릴리즈 전에 검증이 약해진다.

개선 방향:

- pytest 기반 단위 테스트와 CLI smoke test를 분리한다.
- 테스트용 임시 `OPERATOR_HOME`을 사용한다.
- 회선 목록은 실제 파일에서 읽어 유효한 회선을 선택한다.
- release binary smoke test는 `--version`, `--help`, `circuits`, `units`, `status reset` 정도로 제한한다.

개선 효과:

- 테스트가 사용자 상태를 오염시키지 않는다.
- 회선 변경에도 테스트가 덜 깨진다.
- CI에서 신뢰할 수 있는 품질 신호가 생긴다.

### 10. Graphify Integration Mixes Analysis, Labeling, And Visualization

근거:

- `graph run`은 graphify 실행 후 LLM 기반 community labeling을 수행하고, 이어서 visualization 생성을 시도한다.
- labeling 실패는 일부 warning으로 지나가고, visualization command는 `cmd[:3] + ["cluster-only", "."]` 방식으로 기존 명령을 재조합한다.

왜 문제인가:

Graphify는 구조 분석 도구이고, LLM labeling은 후처리이며, HTML 생성은 시각화 단계다. 세 단계를 한 명령에 강하게 묶으면 어느 단계가 실패했는지 분리하기 어렵다. 특히 LLM이 없거나 Ollama가 꺼진 환경에서도 graph 추출 자체는 가능해야 한다.

개선 방향:

- `operator graph run`, `operator graph label`, `operator graph viz`를 분리한다.
- `graph run --label/--no-label`, `--viz/--no-viz`를 명확히 한다.
- 각 단계의 산출물과 실패 상태를 별도로 기록한다.

개선 효과:

- 분석 파이프라인이 재시도 가능해진다.
- LLM 없는 환경에서도 Graphify 기본 기능을 쓸 수 있다.
- 실패 원인 파악과 자동화가 쉬워진다.

## Prioritized Roadmap

### Phase 1: Stabilize Daily Use

1. [x] `summarize`를 실제 context history 기반으로 수정한다.
2. [x] `test_operator.sh`를 임시 `OPERATOR_HOME` 기반 smoke test로 교체한다.
3. [x] README와 AGENT_GUIDE 생성 로직을 실제 release 경로/회선 목록과 동기화한다.
4. [x] `ContextManager`에 default_factory, atomic write, parse failure warning을 추가한다.

구현 상태:

| 날짜 | 항목 | 상태 | 구현 메모 |
| --- | --- | --- | --- |
| 2026-06-09 | `summarize` 실제 history 연동 | 완료 | 더미 history를 제거하고 `ContextManager.history`를 요약 입력으로 사용한다. 요약 후 `MEMORY.md`와 context history를 함께 갱신한다. |
| 2026-06-09 | context 상태 무결성 | 완료 | `schema_version`, `Field(default_factory=...)`, 손상 파일 백업, atomic write를 적용했다. |
| 2026-06-09 | 격리형 smoke test | 완료 | `test_operator.sh`가 임시 `OPERATOR_HOME`을 만들고 public `protocols/`를 복사해 실행한다. 실제 사용자 runtime 상태를 변경하지 않는다. |
| 2026-06-09 | README/AGENT_GUIDE 동기화 | 완료 | Windows release 경로를 `release/operator_win/`로 수정하고, `generate_guide.py`가 repo public protocols 기준으로 guide를 생성하게 했다. |

### Phase 2: Make Release Fast And Predictable

1. [x] macOS 기본 빌드를 `onedir`로 전환한다.
2. [x] `onefile`은 별도 portable 타깃으로 유지한다.
3. [x] `--version` fast path를 추가한다.
4. [x] `operator doctor` 명령을 추가해 release path, protocols, knowledge, context, Ollama 연결을 점검한다.

구현 상태:

| 날짜 | 항목 | 상태 | 구현 메모 |
| --- | --- | --- | --- |
| 2026-06-09 | macOS `onedir` 기본 빌드 | 완료 | `scripts/build.sh` 기본 모드를 `onedir`로 변경하고 runtime 배포용 실행 파일 경로를 mode별로 계산한다. |
| 2026-06-09 | `onefile` portable 타깃 | 완료 | `./scripts/build.sh --mode onefile`로 기존 단일 파일 빌드를 유지한다. |
| 2026-06-09 | `--version` fast path | 완료 | `main.py`가 Typer 및 서브커맨드 import 전에 root `--version`/`-v`를 처리한다. |
| 2026-06-09 | `operator doctor` | 완료 | protocol, context, knowledge index, release binary, Ollama 연결 상태를 진단한다. `--skip-ollama`와 `--strict` 옵션을 제공한다. |

### Phase 3: Harden Agent And Knowledge Workflows

1. [ ] ShellExecutor를 approval policy 기반으로 재설계한다.
2. [x] OAKS에 `--format json`, `doctor`, weighted search를 추가한다.
3. [x] protocol compression cache에 source hash와 model metadata를 저장한다.
4. [x] Graphify 단계를 run/label/viz로 분리한다.

구현 상태:

| 날짜 | 항목 | 상태 | 구현 메모 |
| --- | --- | --- | --- |
| 2026-06-09 | OAKS weighted search / JSON output / doctor | 완료 | `KnowledgeManager.search_knowledge()`가 ID/title/tags/content 가중치로 결과를 정렬한다. `operator knowledge query --format json`과 `operator knowledge doctor --format json`을 추가했다. |
| 2026-06-09 | Protocol compression cache metadata | 완료 | cache metadata에 `source_hash`, `model`, `created_at`을 저장한다. 원본 protocol hash나 model이 바뀌면 cached compression을 재사용하지 않는다. `operator status`에서 cache metadata를 표시한다. |
| 2026-06-09 | Graphify run/label/viz 분리 | 완료 | `operator graph run`은 추출/갱신을 담당하고, `operator graph label`, `operator graph viz`로 후처리를 재시도할 수 있게 했다. `graph run --label/--no-label`, `--viz/--no-viz`를 지원한다. |

남은 작업:

| 항목 | 남은 규모 | 비고 |
| --- | --- | --- |
| ShellExecutor approval policy | 큼 | `shell=True` 실행 표면, allowlist/approval 저장, 출력 제한, timeout 정책을 함께 다뤄야 한다. |

## Suggested Target State

Operator CLI의 좋은 최종 형태는 다음과 같다.

- `operator --version`, `operator status`, `operator knowledge query`는 즉시 응답한다.
- `operator call <circuit>`은 원본 protocol과 압축 protocol 사용 여부를 명확히 표시한다.
- `operator agent`는 실행 권한이 없는 기본 분석 모드와, 승인 정책이 있는 실행 모드가 분리된다.
- `operator summarize`는 실제 세션 history를 압축하고, MEMORY.md와 context history를 일관되게 갱신한다.
- OAKS는 사람이 검증한 지식만 library로 옮기고, AI는 `query` 결과를 구조화된 JSON으로 안정적으로 읽는다.
- 릴리즈 빌드는 빠른 onedir와 휴대용 onefile을 모두 제공한다.
- CI는 소스 단위 테스트, CLI smoke test, release smoke test를 분리해서 실행한다.

## Notes From This Review

- 이번 점검 중 `knowledge`, `graph`, `setting`, `status`, `LocalLLM`, `KnowledgeExtractor`의 일부 eager import 경로는 lazy import로 조정되었다.
- 개발 실행 기준으로 `--version`과 `--help` startup은 0.1초대까지 줄었다.
- 릴리즈 onefile은 여전히 PyInstaller boot cost 때문에 수 초가 걸린다. 이 문제는 소스 import 최적화보다 packaging mode 변경이 더 효과적이다.
- 현재 워크트리에는 이 리포트 외에도 기존 변경 파일이 존재한다. 릴리즈 전에는 `git diff` 기준으로 의도된 변경과 부수 변경을 분리해 확인해야 한다.
