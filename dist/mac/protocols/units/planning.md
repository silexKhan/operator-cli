---
description: "기획 문서 정합성 및 단계별 상세 구현 규약 (Logic-First, Incremental Writing)"
---
# Unit: Planning (Architectural Specs)

- **Protocol P-1 (Logic-First TOC):** 문서를 작성하기 전, 최종 목표 달성을 위한 논리적 단계에 따라 세부 목차(TOC)를 최우선으로 설계한다.
- **Protocol P-2 (Incremental Deep-Dive):** 설계된 목차의 각 항목을 하나씩 순차적으로 집필하며, 해당 섹션의 모든 디테일이 완성될 때까지 다음 항목으로 넘어가지 않는다.
- **Protocol P-3 (Chunking Strategy):** 문서가 방대할 경우, 섹션 단위로 작업을 분할하여 컨텍스트를 유지하고, 각 단계마다 사용자 확인(Checkpoint)을 거친다.
- **Protocol P-4 (No Omission Policy):** '중략', '생략'을 엄격히 금지하며, 모든 정책/설계를 리터럴 텍스트로 완성하여 문서 자체로 구현 가능하게 한다.
- **Protocol P-5 (Workflow Validation):** 완성된 상세 내용이 P-1에서 정의한 사용자 워크플로우 및 논리적 단계와 일치하는지 최종 검증한다.
