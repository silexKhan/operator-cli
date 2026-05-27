import sys
from pathlib import Path
from typing import List, Dict, Any

def get_project_root() -> Path:
    """
    현재 위치에서 프로젝트의 실제 루트(operator-cli)를 찾습니다.
    실패 시 현재 작업 디렉토리(CWD)를 반환합니다.
    """
    curr = Path.cwd().resolve()
    temp = curr
    
    # 상위 10단계까지 'operator-cli' 폴더 검색
    for _ in range(10):
        # 이름이 일치하거나 확실한 소스 구조가 있는 경우
        if temp.name.lower() == "operator-cli" or (temp / "src" / "operator_cli").exists():
            return temp
            
        if temp.parent == temp:
            break
        temp = temp.parent

    # 찾지 못하면 무조건 현재 위치 반환 (사용자 요청: "그냥 이폴더에서만")
    return curr

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
S_INFO = get_safe_symbol("ℹ", "(i)")
S_LIGHT = get_safe_symbol("💡", "TIP")
