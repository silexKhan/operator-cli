# Core Engine Agent 심층 분석 보고서 및 Operator 이식 가이드

이 문서는 `@earendil-works/core engine-coding-agent`의 내부 소스 코드를 심층 분석하여, 핵심 로직을 Operator CLI에 이식하기 위한 기술 명세를 제공합니다.

---

## 1. 컨텍스트 압축 (Compaction) 메커니즘

Core Engine 에이전트의 가장 강력한 기능은 토큰 제한 내에서 정보 손실을 최소화하며 세션을 유지하는 'Compaction' 기술입니다.

### 1.1. 구조화된 요약 프롬프트 (`SUMMARIZATION_SYSTEM_PROMPT`)
요약 시 모델이 대화를 이어가지 않도록 엄격한 시스템 지침을 사용합니다.

```markdown
당신은 컨텍스트 요약 보조원입니다. 사용자와 AI 코딩 어시스턴트 간의 대화를 읽고, 지정된 형식에 맞춰 구조화된 요약을 생성하십시오.
**대화를 계속하지 마십시오. 질문에 답하지 마십시오. 오직 구조화된 요약만 출력하십시오.**
```

### 1.2. 직렬화 알고리즘 (`serializeConversation`)
모델이 과거 대화를 자신의 현재 명령으로 착각하지 않도록 모든 메시지를 텍스트로 박제합니다.
- **도구 결과 제한**: `TOOL_RESULT_MAX_CHARS = 2000`자로 제한하여 요약 시 토큰 낭비 방지.
- **역할 명시**: `[User]:`, `[Assistant]:`, `[Assistant thinking]:`, `[Tool result]:` 태그 사용.

### 1.3. 핵심 요약 포맷 (EXACT Format)
모든 요약은 반드시 아래의 섹션을 포함해야 합니다.
- **## Goal**: 사용자의 최종 목적.
- **## Constraints & Preferences**: 제약 사항 및 선호도.
- **## Progress**: 완료된 작업(`Done`), 진행 중인 작업(`In Progress`), 차단된 작업(`Blocked`).
- **## Key Decisions**: 주요 결정 사항 및 근거(`Decision: Rationale`).
- **## Next Steps**: 향후 단계.

---

## 2. 추론 제어 (Thinking Level Management)

모델의 추론 성능을 수치적으로 제어하여 비용과 성능의 균형을 맞춥니다.

### 2.1. 추론 토큰 예산 (`Thinking Budget`)
`simple-options.js`에서 정의된 레벨별 예산입니다.
- **Minimal**: 1,024 tokens
- **Low**: 2,048 tokens
- **Medium**: 8,192 tokens
- **High**: 16,384 tokens

### 2.2. Max Tokens 계산 로직
```javascript
maxTokens = Math.min(baseMaxTokens + thinkingBudget, modelMaxTokens)
```
- 출력 토큰이 부족할 경우 최소 출력(`1,024 tokens`)을 보장하기 위해 추론 예산을 동적으로 삭감하는 방어 로직이 포함됨.

---

## 3. 정보 보존 전략 (Information Preservation)

### 3.1. 누적 파일 추적 (Cumulative File Tracking)
요약 시 메시지만 요약하는 것이 아니라, 과거의 모든 `branch_summary`와 `compaction` 엔트리를 순회하며 도구 호출 이력을 추출합니다.
- **Read Files**: 읽기만 한 파일 목록.
- **Modified Files**: 수정 또는 생성된 파일 목록.
- 이 목록은 XML 태그(`<read-files>`, `<modified-files>`) 형태로 요약본 마지막에 항상 첨부됩니다.

### 3.2. Split Turn 요약 (고급)
컨텍스트가 임계값에 도달했을 때:
1. 현재 진행 중인 대화 턴의 '뒷부분(Suffix)'은 유지.
2. '앞부분(Prefix)'과 과거 대화만 요약으로 대체.
이 방식을 통해 에이전트가 "방금 수행한 도구 결과"를 잊지 않고 다음 단계로 자연스럽게 넘어갈 수 있습니다.

---

## 4. 실행 보안 및 안정성

### 4.1. 쉘 출력 샌드박싱 (`bash-executor.js`)
- **Sanitization**: `sanitizeBinaryOutput`을 통해 ANSI 이스케이프 코드 및 바이너리 데이터 제거.
- **Logging**: 출력이 `DEFAULT_MAX_BYTES`를 초과하면 `/tmp`에 파일로 덤프하고 LLM에게는 요약/경로만 전달.

---

## 5. Operator CLI 이식 로직 제안 (Action Plan)

1.  **자동 MEMORY.md 업데이트**: 작업 완료 시 Core Engine의 '구조화된 요약 포맷'을 사용하여 `MEMORY.md`를 갱신하는 유닛 추가.
2.  **동적 추론 레벨 할당**:
    - `operator run -e`: `minimal` 레벨 사용.
    - 아키텍처 분석 및 복잡한 버그 수정: `high` 레벨 강제.
3.  **프로토콜 압축**: 현재 매번 주입되는 긴 프로토콜을 '누적된 결정 사항'으로 압축하여 컨텍스트 효율 30% 이상 향상.
4.  **Split Turn 도입**: 대규모 파일 수정 시 컨텍스트 오버플로우 발생 시 '방금 수정된 내용'을 유지하며 요약하는 로직 구현.
