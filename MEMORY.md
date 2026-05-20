

--- Session Summary ---
## Goal
`operator-cli`에 요약(Summarization) 기능을 추가하는 것.

## Constraints & Preferences
*   요약 기능 구현을 위해 모듈화가 필요함.

## Progress
*   **완료된 작업:** `operator_cli/core/compaction.py` 모듈 생성.
*   **진행 중인 작업:** 생성된 `compaction.py` 모듈에 LLM 기반의 요약 메서드를 추가하는 작업.

## Key Decisions
*   요약 기능을 구현하기 위해 새로운 모듈인 `compaction.py`를 생성하여 기능을 분리하고 관리하기로 결정함.

## Next Steps
*   `compaction.py` 모듈 내에 LLM을 활용한 실제 요약 메서드를 구현해야 함.
