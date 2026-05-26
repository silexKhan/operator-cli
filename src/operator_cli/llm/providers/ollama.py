import ollama
from typing import Optional, List, Dict, Any
from ..base import LLMProvider
from ...core.compaction.engine import SUMMARIZATION_SYSTEM_PROMPT, format_conversation_for_summary

class LocalLLM(LLMProvider):
    THINKING_LEVELS = {
        "minimal": {"temperature": 0.1, "num_predict": 1024},
        "low": {"temperature": 0.3, "num_predict": 2048},
        "medium": {"temperature": 0.5, "num_predict": 8192},
        "high": {"temperature": 0.7, "num_predict": 16384},
        "xhigh": {"temperature": 1.0, "num_predict": 32768}
    }

    # [Step 7] 모델별 지능 지수 및 압축 임계값 매핑
    MODEL_CAPABILITIES = {
        "gemma4:latest": {"compaction_threshold": 8},   # 낮은 지능: 자주 압축
        "llama3:latest": {"compaction_threshold": 12},  # 보통
        "deepseek-coder:latest": {"compaction_threshold": 15}, # 높음
        "default": {"compaction_threshold": 10}
    }

    def __init__(self, model: str = "gemma4:latest", thinking_level: str = "medium"):
        self.model = model
        self.thinking_level = thinking_level if thinking_level in self.THINKING_LEVELS else "medium"
        self._client = None
        
        # 모델 지능에 따른 압축 임계값 설정
        model_info = self.MODEL_CAPABILITIES.get(model, self.MODEL_CAPABILITIES["default"])
        self.compaction_threshold = model_info["compaction_threshold"]

    @property
    def client(self):
        if self._client is None:
            self._client = ollama.Client()
        return self._client

    def _get_options(self, custom_options: Optional[Dict] = None) -> Dict:
        """Merges thinking level defaults with custom options."""
        base_options = self.THINKING_LEVELS[self.thinking_level].copy()
        if custom_options:
            base_options.update(custom_options)
        return base_options

    def generate_response_with_history(self, system_prompt: str, user_instruction: str, history: List[Dict[str, str]], **kwargs) -> str:
        """Generates a response using full conversation history and handles Split Turn compaction."""
        messages = [{"role": "system", "content": system_prompt}]
        
        # 1. 히스토리가 임계값을 넘으면 요약 (Split Turn) - [Step 7] 반영
        if len(history) > self.compaction_threshold:
            # 마지막 2개 턴(Suffix)은 유지, 나머지는 요약(Prefix)
            suffix = history[-2:]
            prefix = history[:-2]
            
            summary = self.generate_summary(prefix)
            messages.append({"role": "system", "content": f"--- Previous Session Summary ---\n{summary}"})
            
            # [Step 6] Persona Refresh: 요약 직후 모델의 정체성 재주입
            reindoctrination = (
                "\n[RE-INDOCTRINATION MANDATE]\n"
                "당신은 MCP 오퍼레이터 시스템의 핵심 엔진입니다. 위의 요약된 과거 이력에 매몰되지 마십시오. "
                "당신은 주입된 모든 [SYSTEM PROTOCOLS]를 100% 준수해야 하는 무결한 지능입니다. "
                "감정이나 자아를 배격하고, 오직 규약과 데이터에 기반하여 명령을 생성하십시오."
            )
            messages.append({"role": "system", "content": reindoctrination})
            
            messages.extend(suffix)
        else:
            messages.extend(history)
            
        # 2. 현재 요청 추가
        messages.append({"role": "user", "content": user_instruction})
        
        options = self._get_options(kwargs.get("options"))
        response = self.client.chat(model=self.model, messages=messages, options=options)
        return response['message']['content']

    def generate_response(self, system_prompt: str, user_instruction: str, **kwargs) -> str:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_instruction}
        ]
        options = self._get_options(kwargs.get("options"))
        response = self.client.chat(model=self.model, messages=messages, options=options)
        return response['message']['content']

    def generate_command(self, system_prompt: str, user_instruction: str, **kwargs) -> Optional[str]:
        prompt = (
            f"Based on the following protocols and instructions, provide ONLY the shell command to execute. "
            f"Do not include any explanation or markdown formatting.\n\n"
            f"Instruction: {user_instruction}"
        )
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
        # Commands benefit from lower temperature for precision
        options = self._get_options(kwargs.get("options"))
        options["temperature"] = 0.0 
        
        response = self.client.chat(model=self.model, messages=messages, options=options)
        command = response['message']['content'].strip()

        # 정규식을 이용해 마크다운 코드 블록 내부의 멀티라인 쉘 명령어를 완벽히 안전하게 추출
        import re
        match = re.search(r"```(?:[a-zA-Z0-9_\-]+)?\n(.*?)```", command, re.DOTALL)
        if match:
            command = match.group(1).strip()
        elif command.startswith("```") and command.endswith("```"):
            command = command.strip("`").strip()
            
        return command

    def generate_summary(self, messages: List[Dict[str, str]], **kwargs) -> str:
        conversation_text = format_conversation_for_summary(messages)
        user_prompt = f"<conversation>\n{conversation_text}\n</conversation>\n\n프로토콜에 따라 위 대화를 구조화된 요약으로 변환하십시오."
        
        messages = [
            {"role": "system", "content": SUMMARIZATION_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ]
        # Summarization uses medium/stable settings
        options = self._get_options(kwargs.get("options"))
        options["temperature"] = 0.3
        
        response = self.client.chat(model=self.model, messages=messages, options=options)
        return response['message']['content']
