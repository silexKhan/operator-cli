import sys
from pathlib import Path
from typing import List, Dict, Any

def get_project_root() -> Path:
    """바이너리/스크립트 환경을 모두 지원하는 프로젝트 루트 경로 반환"""
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent
    else:
        # src/operator_cli/core/utils.py -> root is 4 levels up
        return Path(__file__).parent.parent.parent.parent

def get_protocols_dir() -> Path:
    """프로토콜 저장소 디렉토리 경로 반환"""
    return get_project_root() / "protocols"

def get_engine():
    """초기화된 ProtocolEngine 인스턴스 반환"""
    from operator_cli.core.protocol.engine import ProtocolEngine
    return ProtocolEngine(protocols_dir=get_protocols_dir())

def get_circuit_list() -> List[Dict[str, str]]:
    """가용한 모든 회선 정보(이름, 설명) 목록 반환"""
    return get_engine().get_all_circuits()

def get_unit_list() -> List[Dict[str, str]]:
    """가용한 모든 유닛 정보(이름, 설명) 목록 반환"""
    return get_engine().get_all_units()

def get_circuit_names() -> List[str]:
    """회선 이름 목록만 반환 (도움말/검증용)"""
    return [c["name"] for c in get_circuit_list()]

def get_unit_names() -> List[str]:
    """유닛 이름 목록만 반환 (도움말/검증용)"""
    return [u["name"] for u in get_unit_list()]
