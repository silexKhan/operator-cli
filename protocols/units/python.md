---
description: "파이썬 전용 Clean Architecture 기술 규약 (Dumb Controller, Strict Schema)"
---
# Unit: Python (Clean Architecture)
- **Protocol P-1 (Dumb Controller):** 모든 요청 수신부(Action/Router)는 로직을 가지지 않으며, 모든 비즈니스 판단은 Service Layer로 위임한다.
- **Protocol P-2 (Strict Schema):** 모든 입출력(I/O)은 Pydantic 모델로 정의하며, 필드 상세 주석을 통해 그 자체로 시스템 최종 명세서 역할을 수행한다.
- **Protocol P-3 (Async Safety):** 모든 I/O 작업 및 비즈니스 로직은 비동기(async/await)로 작성하여 시스템의 동시성과 가독성을 확보한다.
- **Protocol P-4 (Handler Separation):** 서비스 진입점은 [Action]handler로 명명하고, 3줄 이상의 상세 로직은 언더바(_) 내부 메서드로 철저히 분리한다.
- **Protocol P-5 (Documentation):** 모든 클래스, 함수, Enum 멤버에는 상세한 Docstring과 주석을 작성하여 파이썬을 몰라도 구조 파악이 가능하게 한다.
- **Protocol P-6 (Strict Enum):** 하드코딩된 문자열/숫자를 엄격히 금지하며, 모든 고정 상태값은 Enum으로 관리하고 Pydantic 모델과 연동하여 검증한다.
- **Protocol P-7 (Pattern Matching):** 3개 이상의 복잡한 분기나 Enum 처리 시 match-case를 사용하고, 반드시 와일드카드(case _:)를 포함하여 예외를 방지한다.
- **Protocol P-8 (Pre-flight Check):** 서버 리로드 전 py_compile 및 mypy 등 정적 분석을 필수로 수행하여 임포트 누락 및 런타임 에러를 사전에 차단한다.
