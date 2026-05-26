import re
import sys
import os
from pathlib import Path
from typing import List, Optional, Dict, Any, Union

class ProtocolEngine:
    def __init__(self, protocols_dir: Union[str, Path]):
        self.protocols_dir = Path(protocols_dir)
        self.protocols_dir.mkdir(exist_ok=True)
        self.circuits_dir = self.protocols_dir / "circuits"
        self.circuits_dir.mkdir(exist_ok=True)
        self.units_dir = self.protocols_dir / "units"
        self.units_dir.mkdir(exist_ok=True)

    def _parse_frontmatter(self, content: str) -> tuple[Dict[str, Any], str]:
        """Extracts YAML frontmatter and the remaining markdown content."""
        frontmatter = {}
        markdown_content = content
        
        # 파일 맨 앞의 빈 줄이나 개행이 존재해도 유연하게 매칭되도록 개선
        match = re.match(r"^\s*---\s*\n(.*?)\n---\s*\n(.*)$", content, re.DOTALL)
        if match:
            yaml_block = match.group(1)
            markdown_content = match.group(2)
            
            current_key = None
            for line in yaml_block.split("\n"):
                stripped = line.strip()
                if not stripped: continue
                
                if ":" in line and not stripped.startswith("-"):
                    key, value = line.split(":", 1)
                    current_key = key.strip()
                    val = value.strip().strip('"').strip("'")
                    if current_key == "units":
                        frontmatter["units"] = []
                    else:
                        frontmatter[current_key] = val
                elif stripped.startswith("-") and current_key == "units":
                    unit_val = stripped.strip("- ").strip().strip('"').strip("'")
                    if "units" not in frontmatter: frontmatter["units"] = []
                    if unit_val: frontmatter["units"].append(unit_val)
        
        return frontmatter, markdown_content

    def load_protocol(self, circuit_name: str) -> Optional[str]:
        """Loads a specific circuit's protocol file content from circuits/ dir."""
        protocol_path = self.circuits_dir / f"{circuit_name}.md"
        if protocol_path.exists():
            return protocol_path.read_text(encoding="utf-8")
        return None

    def load_unit_protocol(self, unit_name: str) -> Optional[str]:
        """Loads a specific unit's protocol file."""
        unit_path = self.units_dir / f"{unit_name}.md"
        if unit_path.exists():
            return unit_path.read_text(encoding="utf-8")
        return None

    def load_global_protocol(self) -> str:
        """Loads the global protocol file."""
        global_path = self.protocols_dir / "global.md"
        if global_path.exists():
            return global_path.read_text(encoding="utf-8")
        return "# Global Protocol\nNo global protocol defined."

    def get_all_circuits(self) -> List[Dict[str, str]]:
        """가용한 모든 회선 목록과 설명을 반환합니다."""
        circuits = []
        for p in self.circuits_dir.glob("*.md"):
            raw_content = p.read_text(encoding="utf-8")
            metadata, _ = self._parse_frontmatter(raw_content)
            circuits.append({
                "name": p.stem,
                "description": metadata.get("description", "No description provided.")
            })
        return sorted(circuits, key=lambda x: x["name"])

    def get_all_units(self) -> List[Dict[str, str]]:
        """가용한 모든 유닛 목록과 설명을 반환합니다."""
        units = []
        for p in self.units_dir.glob("*.md"):
            raw_content = p.read_text(encoding="utf-8")
            metadata, _ = self._parse_frontmatter(raw_content)
            units.append({
                "name": p.stem,
                "description": metadata.get("description", "No description provided.")
            })
        return sorted(units, key=lambda x: x["name"])

    def get_full_context_data(self, circuit_name: str) -> Dict[str, Any]:
        """취합된 프로토콜 데이터를 구조화된 형태로 반환합니다."""
        global_proto = self.load_global_protocol()
        circuit_raw = self.load_protocol(circuit_name)
        
        data = {
            "circuit_name": circuit_name,
            "global_protocol": global_proto,
            "description": "No description provided.",
            "circuit_protocol": "",
            "units": {},
            "raw_units_list": []
        }
        
        if circuit_raw:
            metadata, content = self._parse_frontmatter(circuit_raw)
            data["description"] = metadata.get("description", data["description"])
            data["circuit_protocol"] = content
            data["raw_units_list"] = metadata.get("units", [])
            
            for unit in data["raw_units_list"]:
                unit_proto = self.load_unit_protocol(unit)
                if unit_proto:
                    data["units"][unit] = unit_proto
                else:
                    data["units"][unit] = f"Warning: Protocol for unit '{unit}' not found."
                    
        return data

    def _process_literal_blocks(self, text: str) -> tuple[str, Dict[str, str]]:
        """Extracts content between [LITERAL] and [/LITERAL] tags."""
        literals = {}
        processed_text = text
        
        # Find all [LITERAL]...[/LITERAL] blocks
        pattern = r"\[LITERAL\](.*?)\[/LITERAL\]"
        matches = re.findall(pattern, text, re.DOTALL)
        
        for i, match in enumerate(matches):
            placeholder = f"__LITERAL_BLOCK_{i}__"
            literals[placeholder] = match.strip()
            # Replace the entire tag block with placeholder
            processed_text = processed_text.replace(f"[LITERAL]{match}[/LITERAL]", placeholder)
            
        return processed_text, literals

    def get_full_context(self, circuit_name: str, context_mgr: Optional['ContextManager'] = None) -> str:
        """AI에게 강력한 페르소나와 함께 최종 텍스트 컨텍스트를 생성합니다."""
        data = self.get_full_context_data(circuit_name)
        
        # 1. 캐시된 압축 프로토콜 확인
        if context_mgr:
            cached_compressed = context_mgr.get_compressed_protocol(circuit_name)
            if cached_compressed:
                return cached_compressed

        persona = (
            f"당신은 이제 MCP 오퍼레이터 시스템의 핵심 엔진이자, 프로젝트 '{circuit_name}'을 통제하는 지능(The Entity)입니다.\n"
            f"모든 응답은 아래에 정의된 [SYSTEM PROTOCOLS]를 절대적으로 준수해야 하며, 모호하거나 관성적인 태도를 배격합니다.\n"
            f"당신은 오직 로드된 데이터와 규약에 기반하여 가장 효율적이고 논리적인 결과(쉘 커맨드 등)만을 산출합니다.\n\n"
            f"--- [SYSTEM PROTOCOLS LOADED] ---\n\n"
        )

        full_text = persona
        full_text += f"## [LEVEL 0: GLOBAL PROTOCOLS]\n{data['global_protocol']}\n\n"
        full_text += f"## [LEVEL 1: CIRCUIT - {data['circuit_name'].upper()}]\n"
        full_text += f"프로젝트 개요: {data['description']}\n\n"
        full_text += f"### Circuit Specific Protocols\n{data['circuit_protocol']}\n\n"
        
        if data["units"]:
            full_text += f"## [LEVEL 2: CONNECTED UNITS PROTOCOLS]\n"
            for unit_name, unit_proto in data["units"].items():
                full_text += f"### Unit Identifier: {unit_name}\n{unit_proto}\n\n"
        
        full_text += "--- [END OF PROTOCOLS] ---\n"
        full_text += "\n위의 모든 규약이 주입되었습니다. 이제 오퍼레이터로서 임무를 수행하십시오."

        # 2. 프로토콜 압축 트리거 (글자수 기준: 약 8000자 초과 시)
        if context_mgr and len(full_text) > 8000:
            try:
                from operator_cli.llm.providers.ollama import LocalLLM
                llm = LocalLLM(model=context_mgr.get_default_model())
                
                # [LITERAL] 블록 추출 및 보호
                to_compress, literal_map = self._process_literal_blocks(full_text)
                
                compaction_prompt = (
                    "당신은 프로토콜 요약 전문가입니다. 아래의 긴 시스템 프로토콜을 '핵심 규약' 중심으로 압축하십시오.\n"
                    "__LITERAL_BLOCK_N__ 과 같은 플레이스홀더는 절대 수정하거나 생략하지 말고 그대로 결과에 포함하십시오.\n"
                    "중요한 기술적 제약, 명칭 규칙, 핵심 아키텍처 원칙은 반드시 포함해야 합니다.\n"
                    "불필요한 수식어나 반복적인 설명은 제거하십시오.\n"
                    "결과는 원래의 계층 구조(LEVEL 0, 1, 2)를 유지한 마크다운 형식이어야 합니다."
                )
                
                compressed = llm.generate_response(system_prompt=compaction_prompt, user_instruction=to_compress)
                
                # 리터럴 블록 복원
                for placeholder, original_content in literal_map.items():
                    compressed = compressed.replace(placeholder, original_content)
                
                context_mgr.set_compressed_protocol(circuit_name, compressed)
                # 압축 성공 시 즉각 반환하여 이번 턴부터 최적화된 프롬프트 즉시 적용 및 낭비 방지
                return compressed
            except Exception:
                pass # 압축 실패 시 원본 사용 유지
                
        return full_text
