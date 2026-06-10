import json
import os
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from tempfile import NamedTemporaryFile
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, Dict, List

class OperatorContext(BaseModel):
    model_config = ConfigDict(extra='ignore')
    
    schema_version: int = 1
    active_circuit: Optional[str] = None
    default_model: str = "gemma4:latest"
    graphify_auto_update_delay: int = 30  # 유예 시간 (분 단위)
    last_knowledge_update: Optional[str] = None  # 마지막 지식 업데이트 시점 (ISO 형식)
    compressed_protocols: Dict[str, str] = Field(default_factory=dict)  # {circuit_name: compressed_text}
    compressed_protocol_metadata: Dict[str, Dict[str, str]] = Field(default_factory=dict)
    history: List[Dict[str, str]] = Field(default_factory=list)  # [{"role": "...", "content": "..."}]

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
            except Exception as exc:
                backup_path = self._backup_corrupt_context()
                backup_message = f" Backed up to {backup_path}." if backup_path else ""
                print(
                    f"Warning: failed to load Operator context at {self.context_path}: {exc}.{backup_message} "
                    "Using a fresh context.",
                    file=sys.stderr,
                )
                return OperatorContext()
        return OperatorContext()

    def _backup_corrupt_context(self) -> Optional[Path]:
        if not self.context_path.exists():
            return None

        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        backup_path = self.context_path.with_name(f"{self.context_path.name}.bak.{timestamp}")
        try:
            shutil.copy2(self.context_path, backup_path)
            return backup_path
        except Exception as exc:
            print(
                f"Warning: failed to back up corrupt Operator context at {self.context_path}: {exc}.",
                file=sys.stderr,
            )
            return None

    def _write_context(self):
        self.context_path.parent.mkdir(parents=True, exist_ok=True)
        tmp_path = None

        try:
            with NamedTemporaryFile(
                "w",
                encoding="utf-8",
                dir=self.context_path.parent,
                prefix=f".{self.context_path.name}.",
                suffix=".tmp",
                delete=False,
            ) as tmp_file:
                tmp_path = Path(tmp_file.name)
                json.dump(self.context.model_dump(), tmp_file, ensure_ascii=False, indent=2)
                tmp_file.write("\n")
                tmp_file.flush()
                os.fsync(tmp_file.fileno())

            os.replace(tmp_path, self.context_path)
        finally:
            if tmp_path and tmp_path.exists():
                tmp_path.unlink()

    def save_context(self, active_circuit: Optional[str] = None, default_model: Optional[str] = None, 
                     graphify_delay: Optional[int] = None, last_update: Optional[str] = None,
                     compressed_protocols: Optional[Dict[str, str]] = None,
                     compressed_protocol_metadata: Optional[Dict[str, Dict[str, str]]] = None,
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
        if compressed_protocol_metadata is not None:
            self.context.compressed_protocol_metadata.update(compressed_protocol_metadata)
        if history is not None:
            self.context.history = history

        self._write_context()

    def get_active_circuit(self) -> Optional[str]:
        return self.context.active_circuit

    def clear_active_circuit(self):
        self.context.active_circuit = None
        self._write_context()

    def get_default_model(self) -> str:
        return self.context.default_model

    def get_compressed_protocol(
        self,
        circuit_name: str,
        source_hash: Optional[str] = None,
        model: Optional[str] = None,
    ) -> Optional[str]:
        compressed = self.context.compressed_protocols.get(circuit_name)
        if not compressed:
            return None

        if source_hash is None and model is None:
            return compressed

        metadata = self.context.compressed_protocol_metadata.get(circuit_name)
        if not metadata:
            return None
        if source_hash is not None and metadata.get("source_hash") != source_hash:
            return None
        if model is not None and metadata.get("model") != model:
            return None
        return compressed

    def set_compressed_protocol(
        self,
        circuit_name: str,
        compressed_text: str,
        metadata: Optional[Dict[str, str]] = None,
    ):
        self.context.compressed_protocols[circuit_name] = compressed_text
        if metadata is not None:
            self.context.compressed_protocol_metadata[circuit_name] = metadata
        self.save_context()

    def get_compressed_protocol_metadata(self, circuit_name: str) -> Optional[Dict[str, str]]:
        metadata = self.context.compressed_protocol_metadata.get(circuit_name)
        return dict(metadata) if metadata else None

    def add_history(self, role: str, content: str):
        """Adds a message to the conversation history."""
        self.context.history.append({"role": role, "content": content})
        self.save_context()

    def get_history(self) -> List[Dict[str, str]]:
        return list(self.context.history)

    def clear_history(self):
        self.context.history = []
        self._write_context()
