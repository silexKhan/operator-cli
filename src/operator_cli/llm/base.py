from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any

class LLMProvider(ABC):
    """Abstract Base Class for LLM Providers."""
    
    @abstractmethod
    def generate_response(self, system_prompt: str, user_instruction: str, **kwargs) -> str:
        """Generates a plain text response."""
        pass

    @abstractmethod
    def generate_command(self, system_prompt: str, user_instruction: str, **kwargs) -> Optional[str]:
        """Generates a shell command."""
        pass

    @abstractmethod
    def generate_summary(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Generates a structured summary for context compaction."""
        pass
