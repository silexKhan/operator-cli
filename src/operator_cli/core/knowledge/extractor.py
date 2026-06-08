import json
import uuid
from typing import TYPE_CHECKING, List, Optional, Dict, Any
from datetime import datetime
from .manager import KnowledgeMetadata

if TYPE_CHECKING:
    from ...llm.providers.ollama import LocalLLM

KNOWLEDGE_EXTRACTION_PROMPT = """
당신은 'OAKS(Operator Advanced Knowledge System)'의 지식 추출 엔진입니다.
제공된 텍스트(대화 이력 또는 소스 코드)에서 중요한 지식 요소를 추출하여 구조화된 형식으로 변환하십시오.

추출해야 할 지식의 유형:
1. Fact: 프로젝트의 사실 관계, 기술 스택, 라이브러리 버전 등.
2. Preference: 사용자의 선호 스타일, 팀의 코딩 규약 등.
3. Strategy: 특정 문제 해결 방법론, 아키텍처 결정 등.

출력 형식은 반드시 아래의 JSON 리스트 형식이어야 합니다:
[
  {
    "title": "지식의 간결한 제목",
    "content": "Markdown 형식의 상세 지식 내용",
    "tags": ["태그1", "태그2"],
    "category": "proposals"
  }
]

추출할 내용이 없다면 빈 리스트 []를 반환하십시오.
"""

class KnowledgeExtractor:
    """
    LLM을 활용하여 텍스트 데이터에서 지식을 추출하는 클래스입니다. (Protocol P-5 준수)
    """

    def __init__(self, llm: Optional["LocalLLM"] = None):
        """
        KnowledgeExtractor를 초기화합니다.

        Args:
            llm (Optional[LocalLLM]): 지식 추출에 사용할 LLM 인스턴스. 
                                    지정되지 않을 경우 기본 설정을 사용합니다.
        """
        if llm is None:
            from ...llm.providers.ollama import LocalLLM
            llm = LocalLLM(thinking_level="high")
        self.llm = llm

    def extract_from_text(self, text: str) -> List[Dict[str, Any]]:
        """
        주어진 텍스트에서 지식 후보를 추출합니다.

        Args:
            text (str): 지식을 추출할 원본 텍스트.

        Returns:
            List[Dict[str, Any]]: 추출된 지식 후보 리스트. 
                                각 항목은 'title', 'content', 'tags', 'category'를 포함합니다.
        """
        user_instruction = f"다음 텍스트에서 지식을 추출하십시오:\n\n{text}"
        
        response = self.llm.generate_response(
            system_prompt=KNOWLEDGE_EXTRACTION_PROMPT,
            user_instruction=user_instruction
        )

        try:
            # JSON 블록 추출 (Markdown 백틱 제거 포함)
            clean_response = response.strip()
            if clean_response.startswith("```json"):
                clean_response = clean_response[7:]
            if clean_response.endswith("```"):
                clean_response = clean_response[:-3]
            
            extracted = json.loads(clean_response)
            return extracted if isinstance(extracted, list) else []
        except (json.JSONDecodeError, Exception):
            # 추출 실패 시 빈 리스트 반환
            return []

    def create_knowledge_proposal(self, raw_data: Dict[str, Any], author: Optional[str] = None) -> tuple[KnowledgeMetadata, str]:
        """
        추출된 원본 데이터를 바탕으로 정규 지식 제안 객체를 생성합니다.

        Args:
            raw_data (Dict[str, Any]): 추출된 원본 데이터.
            author (Optional[str]): 작성자 이름.

        Returns:
            tuple: (KnowledgeMetadata, content) 쌍.
        """
        knowledge_id = f"K-{uuid.uuid4().hex[:8].upper()}"
        
        metadata = KnowledgeMetadata(
            id=knowledge_id,
            title=raw_data.get("title", "Untitled Knowledge"),
            category="proposals",
            tags=raw_data.get("tags", []),
            created_at=datetime.now(),
            updated_at=datetime.now(),
            author=author
        )
        
        content = raw_data.get("content", "")
        return metadata, content
