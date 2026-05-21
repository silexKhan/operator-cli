import sys
from pathlib import Path
from typing import List, Dict, Any

def get_project_root() -> Path:
    """
    프로젝트 루트 경로를 결정합니다.
    1. 현재 작업 디렉토리(CWD)에 'protocols' 또는 'knowledge'가 있으면 CWD를 반환 (로컬 프로젝트 모드)
    2. 그렇지 않으면 바이너리/스크립트 설치 위치를 반환 (글로벌 모드)
    """
    cwd = Path.cwd()
    if (cwd / "protocols").exists() or (cwd / "knowledge").exists():
        return cwd
        
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent
    else:
        # src/operator_cli/core/utils.py -> root is 4 levels up
        return Path(__file__).parent.parent.parent.parent

def get_protocols_dir() -> Path:
    """프로토콜 저장소 디렉토리 경로 반환 (로컬 우선)"""
    # 1. CWD/protocols 체크
    cwd_proto = Path.cwd() / "protocols"
    if cwd_proto.exists() and cwd_proto.is_dir():
        return cwd_proto
        
    # 2. 설치 경로 기반 protocols 반환
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

def get_safe_symbol(unicode_sym: str, ascii_sym: str) -> str:
    """환경에 따라 안전한 기호 반환"""
    import sys
    if sys.platform == "win32":
        # Windows에서는 ASCII 안전 기호 우선 사용
        return ascii_sym
    return unicode_sym

# 글로벌 안전 기호 정의
S_OK = get_safe_symbol("✓", "[OK]")
S_WARN = get_safe_symbol("⚠", "[!]")
S_ERR = get_safe_symbol("✕", "[X]")
S_CIRCUIT = get_safe_symbol("📡", ">>")
S_PROTO = get_safe_symbol("📜", "--")
S_KNOWLEDGE = get_safe_symbol("🧠", "KN")
