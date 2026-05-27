import json
from pathlib import Path
from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, List

class OperatorContext(BaseModel):
    model_config = ConfigDict(extra='ignore')
    
    active_circuit: Optional[str] = None
    default_model: str = "gemma4:latest"
    graphify_auto_update_delay: int = 30  # 유예 시간 (분 단위)
    last_knowledge_update: Optional[str] = None  # 마지막 지식 업데이트 시점 (ISO 형식)
    compressed_protocols: Dict[str, str] = {}  # {circuit_name: compressed_text}
    history: List[Dict[str, str]] = []  # [{"role": "...", "content": "..."}]

class ContextManager:
    def __init__(self, context_path: str = ".operator_context.json"):
        self.context_path = Path(context_path)
        self.context = self._load_context()

    def _load_context(self) -> OperatorContext:
        if self.context_path.exists():
            try:
                with open(self.context_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    # Use model_validate to ensure default values for missing fields
                    return OperatorContext.model_validate(data)
            except Exception:
                return OperatorContext()
        return OperatorContext()

    def save_context(self, active_circuit: Optional[str] = None, default_model: Optional[str] = None, 
                     graphify_delay: Optional[int] = None, last_update: Optional[str] = None,
                     compressed_protocols: Optional[Dict[str, str]] = None,
                     history: Optional[List[Dict[str, str]]] = None):
        if active_circuit is not None:
            self.context.active_circuit = active_circuit
        if default_model is not None:
            self.context.default_model = default_model
        if graphify_delay is not None:
            self.context.graphify_auto_update_delay = graphify_delay
        if last_update is not None:
            self.context.last_knowledge_update = last_update
        if compressed_protocols is not None:
            self.context.compressed_protocols.update(compressed_protocols)
        if history is not None:
            self.context.history = history
            
        with open(self.context_path, "w", encoding="utf-8") as f:
            json.dump(self.context.model_dump(), f, ensure_ascii=False, indent=2)

    def get_active_circuit(self) -> Optional[str]:
        return self.context.active_circuit

    def clear_active_circuit(self):
        self.context.active_circuit = None
        with open(self.context_path, "w", encoding="utf-8") as f:
            json.dump(self.context.model_dump(), f, ensure_ascii=False, indent=2)

    def get_default_model(self) -> str:
        return self.context.default_model

    def get_compressed_protocol(self, circuit_name: str) -> Optional[str]:
        return self.context.compressed_protocols.get(circuit_name)

    def set_compressed_protocol(self, circuit_name: str, compressed_text: str):
        self.context.compressed_protocols[circuit_name] = compressed_text
        self.save_context()

    def add_history(self, role: str, content: str):
        """Adds a message to the conversation history."""
        self.context.history.append({"role": role, "content": content})
        self.save_context()

    def get_history(self) -> List[Dict[str, str]]:
        return self.context.history

    def clear_history(self):
        self.context.history = []
        self.save_context()
