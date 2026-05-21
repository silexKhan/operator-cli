# Operator AI Knowledge System (OAKS) 설계안

이 문서는 `operator-cli`에 도입할 **검증 기반 AI 지식 관리 시스템**의 아키텍처와 운영 전략을 정의합니다.

## 1. 철학: Protocols vs Knowledge
- **Protocols (가이드라인):** AI의 행동 강령, 페르소나, 작업 절차 (How to act).
- **Knowledge (지식):** 프로젝트 도메인 정보, 비즈니스 로직, 사용자의 의도, 기술적 사실 (What to know).
- **핵심 원칙:** 모든 지식은 **사용자의 검증**을 거쳐 저장되며, AI는 모르는 내용에 대해 추측하지 않고 지식 베이스를 참조합니다.

## 2. 지식 저장소 구조 (`knowledge/`)
지식은 계층적으로 관리되어 AI가 효율적으로 탐색할 수 있도록 합니다.

```
knowledge/
├── index.md            # [Librarian] 전체 지식의 지도 (llms.txt 역할)
├── library/            # [Verified] 검증된 지식 (Markdown)
│   ├── business/       # 비즈니스 로직 및 도메인 지식
│   ├── technical/      # 프로젝트 기술 스택 및 아키텍처 사실
│   └── history/        # 주요 결정 사항 및 변경 이력
├── basement/           # [Raw] 가공되지 않은 원본 소스 및 참고 문서
└── proposals/          # [Pending] 검증 대기 중인 지식 후보 (Drafts)
```

## 3. 지식 생명주기 (Lifecycle)
1. **Extraction (추출):** 대화 중 새로운 정보나 사용자의 지시를 감지하여 지식 후보 생성.
2. **Proposal (제안):** `proposals/` 폴더에 마크다운 형태로 요약본 생성.
3. **Verification (검증):** 사용자가 내용을 확인하고 승인 (예: `operator knowledge approve <id>`).
4. Hardening (고착화): 검증된 내용을 `library/`로 이동하고 `index.md` 업데이트.
5. Indexing (인덱싱): 지식 그래프(Graphify)에 동기화.

## 4. 기술적 구현 방향
- **Knowledge Engine:** `src/operator_cli/core/knowledge/`에서 지식 CRUD 및 인덱싱 관리.
- **Conflict Resolver:** 새로운 지식이 기존 지식과 충돌할 경우 AI가 이를 감지하고 리포트.
- **Standard Support:** `llms.txt` 규격을 준수하여 외부 AI 도구와의 호환성 확보.

## 5. Integration (공통 인터페이스 아키텍처)
다른 AI 도구(Cursor, Claude, Windsurf 등)가 이 지식 체계를 활용할 수 있도록 두 가지 인터페이스를 제공합니다.

### 5.1. Passive File Interface (`llms.txt`)
- 지식 업데이트 시 프로젝트 루트의 `llms.txt` 및 `llms-full.txt`를 자동으로 동기화.
- 파일 시스템 기반의 AI 모델이 전체 지식 구조를 즉시 파악할 수 있는 인덱스 제공.

### 5.2. Active CLI Interface (`operator knowledge`)
- 쉘 접근 권한이 있는 AI 에이전트를 위한 질의/제안 인터페이스.
- `--format json` 옵션을 통해 AI가 파싱하기 쉬운 기계 판독형 데이터 출력 지원.

---

# Sentinel 구현 단계별 로드맵 (Task Steps)

Sentinel 규약(S-0)에 따라 다음 단계로 임무를 수행합니다.

### Step 1: 지식 저장소 뼈대 구축 (Scaffolding)
- [ ] `knowledge/` 디렉토리 구조(basement, library, proposals) 생성.
- [ ] `src/operator_cli/core/knowledge/` 패키지 생성 및 기본 저장/로드 로직 구현.

### Step 2: CLI 인터페이스 및 추출 엔진 구현
- [ ] `operator knowledge` 명령어 세트 추가 (query, propose, list, approve).
- [ ] LLM을 통한 지식 후보(Proposal) 추출 로직 구현.

### Step 3: Passive Interface (`llms.txt`) 구현
- [ ] `knowledge/` 내부 마크다운 파일을 분석하여 `llms.txt`를 생성하는 Generator 구현.
- [ ] 지식 변경 시 자동 갱신 트리거 연동.

### Step 4: 검증(Verification) 워크플로우 완성 및 테스트
- [ ] 제안 -> 사용자 확인 -> 승인 -> 인덱싱의 전체 라이프사이클 테스트.
- [ ] 지식 충돌 감지 로직 검증.


---

# 심층 질의 및 논의 사항

시스템 구축을 위해 추가적으로 결정이 필요한 사항들입니다.

### Q1. 지식 검증(Verification)의 방식
- **Option A (Interactive):** 대화 중 즉시 "방금 말씀하신 내용을 지식으로 저장할까요?"라고 묻고 승인받는 방식.
- **Option B (Asynchronous):** 일단 `proposals/`에 저장해두고, 사용자가 나중에 한꺼번에 검토/승인하는 방식.
- **Option C (Hybrid):** 중요한 지식은 즉시 묻고, 사소한 이력은 나중에 정리.

### Q2. 지식의 '검증' 기준
- 단순 사실(Fact) 외에 "사용자의 선호도(Preference)"나 "미확정된 아이디어"도 지식으로 분류하여 저장할까요?
- 지식의 유효 기간(TTL)을 설정하여 오래된 지식을 자동으로 아카이빙할 필요가 있을까요?

### Q3. 기존 Protocols와의 관계
- 현재의 `protocols/`에 있는 내용 중 일부(예: 프로젝트 개요)를 `knowledge/`로 이관하여 통합 관리하는 것에 대해 어떻게 생각하시나요?

### Q4. 지식 추출 트리거
- AI가 자율적으로 "이건 지식이다"라고 판단하여 제안하는 것이 좋을까요, 아니면 사용자가 명시적으로 "이거 기억해"라고 할 때만 작동하는 것이 좋을까요?
