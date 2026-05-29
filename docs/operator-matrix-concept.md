# 💊 Operator CLI: The Matrix System Overview

> *"You take the blue pill, the story ends. You take the red pill, you stay in Wonderland, and I show you how deep the rabbit hole goes."*

**Operator CLI**는 단순한 터미널 보조 도구가 아닙니다. 당신의 개발 환경을 통제하는 **'매트릭스(Matrix)'**이자, 당신을 대신해 가상 세계(코드베이스) 안으로 뛰어들어 임무를 수행하는 **요원(Agent)**들을 관리하는 지능형 오퍼레이팅 시스템입니다.

---

## 🧠 1. 세계관 및 핵심 컨셉

### ① 회선 접속 (Plug-in to the Circuit)
매트릭스에서 오퍼레이터가 네오를 특정 가상 공간으로 전송하듯, 당신은 `operator call <circuit>` 명령을 통해 시스템을 특정 프로젝트(회선)에 접속시킵니다.
*   **각성 (The Entity):** 회선에 연결되는 순간, AI는 해당 프로젝트의 아키텍처, 룰(Protocol), 히스토리를 뇌에 직접 다운로드받아 프로젝트에 최적화된 통제 지능으로 각성합니다.

### ② 요원 투입 (Deploying Units)
특수한 임무가 필요할 때, 특정 훈련 프로그램(무술이나 무기 다루기)을 로드하는 것처럼 전문 **유닛(Unit)**을 투입합니다.
*   `python`: 파이썬 훈련을 마친 요원.
*   `sentinel`: 코드를 감시하고 품질을 통제하는 감시자(QA) 요원.
*   `planning`: 전략과 계획을 세우는 네비게이터.

---

## ⚡ 2. 독립적인 사고 코어: Local LLM (Agent)

매트릭스 내부의 요원들은 클라우드(외부 서버)에 의존하지 않고, 당신의 로컬 시스템 자원을 활용하여 스스로 사고하고 움직입니다. 단, 이 강력한 요원을 구동하기 위해서는 **적절한 하드웨어(특히 GPU VRAM)가 뒷받침되어야 합니다.**

### 하드웨어 요구사항 (Hardware Constraints)
요원의 지능 수준(모델 크기)은 당신의 장비 스펙에 비례합니다.
*   **최소 사양:** NVIDIA RTX 3060 (12GB VRAM) 이상 권장. 8B 규모의 경량화된 요원을 원활하게 구동할 수 있습니다.
*   **권장 사양:** RTX 4060 Ti (16GB) 이상. 더 복잡한 추론과 지식 정리 작업을 수행할 수 있습니다.

### 명령어 구조 및 기능
`operator agent` 명령어는 로컬 지능을 깨우는 명령어입니다.
*   `-m, --model`: 요원의 뇌(LLM)를 교체합니다. (예: `gemma4`, `llama3`)
*   `-t, --thinking`: 추론의 깊이를 조절합니다. 가벼운 작업은 짧게, 복잡한 코드 분석은 깊게 고민하게 만듭니다.
*   `-e, --execute`: 요원이 터미널 내에서 직접 커맨드를 실행할 수 있는 자율 행동 권한을 부여합니다.

---

## 📚 3. 매트릭스 지식 시스템: OAKS (Operator AI Knowledge System)

OAKS는 생존과 효율을 위해 **검증된 지식(Verified Knowledge)**만을 보존하는 코어 저장소입니다. 여기서 중요한 점은, **로컬 LLM 요원들이 스스로 지식을 찾아내고 정리하는 역할까지 담당**한다는 것입니다.

### 로컬 LLM 주도의 지식 관리 루프
요원들은 코드를 분석하거나 버그를 수정하는 과정에서 새로운 패턴이나 규약을 발견하면, 이를 스스로 요약하여 지식 저장소에 등록을 요청합니다.

*   `knowledge propose`: 로컬 요원이 작업 중 습득한 기술적 사실을 구조화된 마크다운 문서로 요약하여 시스템에 "제안(Propose)"합니다.
*   `knowledge approve`: 관리자(당신)가 요원이 제안한 지식을 검토하고 승인하여 공식 매트릭스 룰로 만듭니다.
*   `knowledge query`: 다음 임무를 수행하는 요원이 기존에 승인된 지식을 검색하여 즉각적으로 실무에 적용합니다.
*   `knowledge refresh`: 승인된 지식들을 외부 AI(Cursor 등)도 읽을 수 있도록 `llms.txt` 포맷으로 동기화합니다.

---

## 🕸️ 4. 지식의 시각화: Graphify

코드 덩어리들을 단순히 읽는 것을 넘어, 관계망(Network)으로 시각화하여 매트릭스 전체의 구조를 파악합니다.

*   `graph run`: 코드베이스의 의존성과 문서들을 엮어 지식 그래프(Knowledge Graph)를 구축합니다.
*   `graph open`: 구축된 구조를 3D 또는 인터랙티브 HTML로 열어, 매트릭스의 녹색 코드 비가 내리는 것처럼 프로젝트의 맥락을 한눈에 파악합니다.

---

### 🚀 요약: 오퍼레이터 워크플로우
1.  **플러그인:** `operator call gdr` (프로젝트 매트릭스 접속)
2.  **임무 하달:** `operator agent "리팩토링 해" -m llama3 -e` (로컬 지능으로 자율 실행, GPU 자원 활용)
3.  **지식 학습:** 작업 중 요원이 스스로 `operator knowledge propose`를 실행하여 새로운 룰을 정리.
4.  **지식 동기화:** 관리자가 승인 후 `operator knowledge refresh`로 전체 시스템에 배포.