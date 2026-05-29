import sys
from pathlib import Path
from typing import List, Dict, Any

def get_project_root() -> Path:
    """
    오퍼레이터 실행 파일 혹은 소스 코드를 기준으로 메인 디렉토리(홈폴더)를 찾아 반환합니다.
    환경변수 OPERATOR_HOME 이 정의되어 있다면 최우선적으로 해당 경로를 홈폴더로 지정합니다.
    어떤 환경에서든 operator-cli 폴더를 이동시키면 거기가 완벽한 홈폴더가 됩니다.
    """
    import os
    import sys
    
    # 0. 환경 변수 OPERATOR_HOME 이 지정되어 있다면 최우선적으로 해당 경로 반환
    env_home = os.environ.get("OPERATOR_HOME")
    if env_home:
        return Path(env_home).resolve()
        
    # 1. PyInstaller 바이너리로 실행 중인 경우 (getattr(sys, 'frozen') 이 True)
    if getattr(sys, 'frozen', False):
        exe_path = Path(sys.executable).resolve()
        temp = exe_path
        # 바이너리 상위 10단계 부모 디렉토리를 탐색하여 실제 개발 프로젝트 루트인 operator-cli 검색
        for _ in range(10):
            if temp.name.lower() == "operator-cli" or (temp / "src" / "operator_cli").exists():
                return temp
            if temp.parent == temp:
                break
            temp = temp.parent
            
        # [백업 가이드] 바이너리가 단독 복사되어 전역 경로(~/.local/bin 등)에 위치해 있고,
        # 조상 디렉토리 중에 operator-cli가 전혀 감지되지 않을 경우, 실제 마스터 프로젝트 경로를 기본값으로 완벽하게 추적
        default_workspace = Path("/Users/silex/workspace/private/operator-cli")
        if default_workspace.exists():
            return default_workspace
            
        return exe_path.parent

    # 2. 소스 코드(파이썬 스크립트)로 실행 중인 경우
    # __file__ (src/operator_cli/core/utils.py) 을 기점으로 하여 부모 폴더를 안전하게 역추적
    curr = Path(__file__).resolve()
    temp = curr
    
    # 상위 10단계까지 'operator-cli' 폴더 검색
    for _ in range(10):
        if temp.name.lower() == "operator-cli" or (temp / "src" / "operator_cli").exists():
            return temp
            
        if temp.parent == temp:
            break
        temp = temp.parent

    # 찾지 못하면 무조건 현재 작업 디렉토리(CWD) 반환
    return Path.cwd().resolve()

def get_protocols_dir() -> Path:
    """
    프로토콜 저장소 디렉토리 경로를 항상 메인 홈폴더(operator-cli) 기준으로 반환합니다.
    이를 통해 엉뚱한 임의의 디렉토리에 빈 protocols 폴더가 생성되는 현상을 원천적으로 차단합니다.
    """
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
