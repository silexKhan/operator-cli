import os
import sys
from pathlib import Path

# 소스 경로 추가 (src layout 대응)
sys.path.append(str(Path(__file__).parent.parent / "src"))

from operator_cli.core.utils import get_circuit_names, get_unit_names, get_project_root
from operator_cli.core.protocol.engine import ProtocolEngine

def generate_guide(output_path: Path):
    """Generates a guide for other AI agents to understand Operator CLI."""
    
    protocols_dir = get_project_root() / "protocols"
    engine = ProtocolEngine(protocols_dir)
    
    guide_content = """# AI Agent Guide for Operator CLI

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
{circuits}

### 유닛 (Units)
{units}

## 4. 핵심 프로토콜 (Global Core Protocols)
오퍼레이터는 다음의 글로벌 규약을 절대적으로 준수합니다:
{global_protocols}

## 5. 사용 가이드
다른 에이전트가 `operator`를 활용할 때는 다음과 같이 호출하십시오:
1. `operator status`로 현재 환경을 파악합니다.
2. `operator agent`를 사용하여 복잡한 쉘 명령어나 아키텍처 결정을 제안받습니다.
3. 작업 완료 후 `operator summarize`를 실행하여 기억을 영속화합니다.
"""
    
    circuits = "\n".join([f"- **{c}**" for c in get_circuit_names()])
    units = "\n".join([f"- **{u}**" for u in get_unit_names()])
    
    global_proto = engine.load_global_protocol()
    # Remove LITERAL tags for cleaner guide
    global_proto = global_proto.replace("[LITERAL]\n", "").replace("[/LITERAL]\n", "").replace("[LITERAL]", "").replace("[/LITERAL]", "")

    formatted_guide = guide_content.format(
        circuits=circuits,
        units=units,
        global_protocols=global_proto
    )
    
    output_path.write_text(formatted_guide, encoding="utf-8")
    print(f"SUCCESS: AGENT_GUIDE.md generated at {output_path}")

if __name__ == "__main__":
    PROJECT_ROOT = Path(__file__).parent.parent
    target_path = PROJECT_ROOT / "docs" / "AGENT_GUIDE.md"
    generate_guide(target_path)
