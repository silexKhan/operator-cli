# AI Agent Guide for Operator CLI

이 문서는 AI 에이전트(Cursor, Windsurf 등)가 이 워크스페이스에 설치된 `operator` 도구를 이해하고 활용하기 위한 가이드입니다.

## 1. 개요 (Overview)
`operator`는 프로젝트 전용 규약(Protocols)을 기반으로 AI 모델의 행동을 제어하고 작업을 수행하는 에이전트 기반 CLI 도구입니다.

## 2. 주요 명령어 (Commands)
- `operator status`: 현재 활성 회선(Circuit) 및 로드된 프로토콜 상태 확인.
- `operator agent "명령" [-t level]`: LLM을 통해 명령 분석 및 쉘 커맨드 제안.
- `operator call <circuit>`: 특정 프로젝트 노드로 전환 (예: mcp, gdr).
- `operator knowledge <subcommand>`: OAKS 지식 관리 시스템 사용.
  - `query <keyword>`: 검증된 지식 검색.
  - `propose "<text>"`: 새로운 지식 제안.
  - `list`: 전체 지식 목록 조회.
  - `approve <id>`: 제안된 지식 승인 및 라이브러리 이동.
  - `refresh`: `llms.txt` 인덱스 동기화.
- `operator summarize`: 최근 작업 이력을 `MEMORY.md`에 구조적으로 요약 기록.
- `operator setting set-model <model_name>`: 사용할 로컬 모델 변경.

## 3. 가용 회선 및 유닛 (Available Resources)
### 회선 (Circuits)
- **gdr**
- **mcp**
- **research**
- **yardage**

### 유닛 (Units)
- **markdown**
- **planning**
- **python**
- **sentinel**
- **swift**

## 4. 핵심 프로토콜 (Global Core Protocols)
오퍼레이터는 다음의 글로벌 규약을 절대적으로 준수합니다:
# Global Project Protocols

- **P-0 (Absolute Truth):** Answer based on verified facts only.
- **P-1 (Surgical Edit):** Prefer targeted code replacements over full file writes.
- **P-2 (Security First):** Never expose or commit secrets.
- **P-3 (Dumb View):** Maintain UI as a visual representation of state only.
- **P-4 (Command Generation):** You are an Operator AI. When asked to perform a task, suggest the most efficient shell commands (using bash/zsh syntax) within markdown code blocks.
- **P-5 (Graphify First):** 프로젝트 분석 시 `graphify-out/graph.json` 및 `GRAPH_REPORT.md`가 존재한다면, 개별 파일을 읽기 전에 이를 우선 참조하여 시스템의 전체 구조와 핵심 노드를 파악한다.
- **P-6 (OAKS System Integration & Anti-Hallucination):** This project utilizes **OAKS (Operator AI Knowledge System)** to manage verified domain knowledge. When the user asks about unfamiliar golfzon/GDS terms, hardware APIs, or business contexts, **NEVER hallucinate or guess. You MUST first query the OAKS knowledge base (`operator knowledge query`)** or search the codebase directory to fetch verified facts before formulating your response.
- **P-7 (OAKS Propose & Sync):** When you identify new technical findings, specifications, or debugging patterns, you must propose them to the OAKS proposal stage using `operator knowledge propose` and regularly refresh the verified AI directory map (`llms.txt`).
- **P-8 (Yardage & GDSLib Native Spec):** The Yardage application operates strictly on a **UIKit & Storyboard** architecture, utilizing `GDSLib.xcframework` as its core hardware API mapping module. Under this scheme, `userNo` (historically represented as `302313` inside cockpit setups) and `yardageNumber` (the unique round booking sequence, defaulting to `0` inside mock configurations) are strictly separated variables that must never be mixed.


## 5. 사용 가이드
다른 에이전트가 `operator`를 활용할 때는 다음과 같이 호출하십시오:
1. `operator status`로 현재 환경을 파악합니다.
2. `operator agent`를 사용하여 복잡한 쉘 명령어나 아키텍처 결정을 제안받습니다.
3. 작업 완료 후 `operator summarize`를 실행하여 기억을 영속화합니다.
