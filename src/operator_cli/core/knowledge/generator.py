from pathlib import Path
from typing import List, Optional
from datetime import datetime
import logging
from operator_cli.core.knowledge.manager import KnowledgeManager, KnowledgeMetadata

logger = logging.getLogger(__name__)

class WikiGenerator:
    """
    OAKS Passive Interface (llms.txt) 자동 생성 엔진입니다. (Protocol P-5 준수)
    
    이 클래스는 'knowledge/library/' 디렉토리의 지식 문서들을 수집하여
    안드레 카파시의 llms.txt 및 llms-full.txt 규격에 맞는 텍스트 파일을 생성합니다.
    (Protocol M-1 Structural Hierarchy 준수)
    """

    def __init__(self, manager: Optional[KnowledgeManager] = None):
        """
        WikiGenerator를 초기화합니다.
        
        Args:
            manager (Optional[KnowledgeManager]): 지식 관리자 객체. 
                                                지정되지 않을 경우 기본 설정을 사용합니다.
        """
        self.manager = manager or KnowledgeManager()
        # 프로젝트 루트 경로를 찾습니다. (바이너리 환경 호환)
        from operator_cli.core.utils import get_project_root
        self.project_root = get_project_root()

    def generate_llms_txt(self) -> str:
        """
        llms.txt 형식의 내용을 생성합니다.
        
        Returns:
            str: 생성된 llms.txt 내용.
        """
        library_knowledge = self.manager.list_knowledge(category="library")
        
        lines = []
        lines.append("# OAKS Knowledge Library")
        lines.append(f"> Automated knowledge base for Operator CLI (OAKS Phase 3)")
        lines.append(f"> Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        lines.append("## Knowledge Entries")
        lines.append("")

        for meta in library_knowledge:
            # 설명이 메타데이터에 없으므로 본문에서 짧게 추출하거나 제목을 사용합니다.
            # 여기서는 제목과 태그를 활용합니다.
            tags_str = ", ".join(meta.tags) if meta.tags else "No tags"
            description = f"Category: {meta.category} | Tags: {tags_str}"
            # llms.txt 규격: [Title](link): Description
            lines.append(f"- [{meta.title}](knowledge/library/{meta.id}.md): {description}")

        return "\n".join(lines)

    def generate_llms_full_txt(self) -> str:
        """
        llms-full.txt 형식의 내용을 생성합니다. (모든 라이브러리 지식 통합본)
        
        Returns:
            str: 생성된 llms-full.txt 내용.
        """
        library_knowledge = self.manager.list_knowledge(category="library")
        # 정렬: 제목순 (기본은 업데이트순이지만 통합본은 제목순이 보기 좋을 수 있음)
        library_knowledge.sort(key=lambda x: x.title)
        
        full_content = []
        full_content.append("# OAKS Full Knowledge Base")
        full_content.append(f"> Total entries: {len(library_knowledge)}")
        full_content.append(f"> Last generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        full_content.append("\n" + "="*80 + "\n")

        for meta in library_knowledge:
            _, content = self.manager.load_knowledge(meta.category, meta.id)
            if content:
                full_content.append(f"## {meta.title}")
                full_content.append(f"Metadata: ID={meta.id}, Tags={', '.join(meta.tags)}")
                full_content.append("\n" + content)
                full_content.append("\n" + "-"*40 + "\n")

        return "\n".join(full_content)

    def refresh(self) -> None:
        """
        llms.txt 및 llms-full.txt 파일을 프로젝트 루트에 갱신합니다.
        """
        try:
            llms_txt_path = self.project_root / "llms.txt"
            llms_full_txt_path = self.project_root / "llms-full.txt"

            llms_content = self.generate_llms_txt()
            llms_full_content = self.generate_llms_full_txt()

            with open(llms_txt_path, "w", encoding="utf-8") as f:
                f.write(llms_content)
            
            with open(llms_full_txt_path, "w", encoding="utf-8") as f:
                f.write(llms_full_content)

            logger.info(f"Successfully refreshed llms.txt and llms-full.txt at {self.project_root}")
        except Exception as e:
            logger.error(f"Failed to refresh llms.txt: {e}")
            raise
