from pathlib import Path
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

class KnowledgeMetadata(BaseModel):
    """
    지식 문서의 메타데이터를 정의하는 스키마 클래스입니다. (Protocol P-2 준수)
    
    Attributes:
        id (str): 지식 문서의 고유 식별자.
        title (str): 지식 문서의 제목.
        category (str): 지식 분류 (e.g., library, proposals, basement).
        tags (List[str]): 검색 및 분류를 위한 태그 리스트.
        created_at (datetime): 문서 생성 일시.
        updated_at (datetime): 문서 최종 수정 일시.
        author (Optional[str]): 문서 작성자.
    """
    id: str = Field(..., description="Unique identifier for the knowledge entry")
    title: str = Field(..., description="Title of the knowledge entry")
    category: str = Field(..., description="Category of the knowledge (e.g., library, proposals, basement)")
    tags: List[str] = Field(default_factory=list, description="List of tags for classification")
    created_at: datetime = Field(default_factory=datetime.now, description="Timestamp of creation")
    updated_at: datetime = Field(default_factory=datetime.now, description="Timestamp of last update")
    author: Optional[str] = Field(None, description="Author of the knowledge entry")

class KnowledgeManager:
    """
    OAKS 지식 파일을 관리하는 핵심 클래스입니다. (Protocol P-5 준수)
    
    이 클래스는 프로젝트 루트의 `knowledge/` 디렉토리를 참조하여 지식 문서를
    저장, 로드 및 인덱싱하는 기능을 제공합니다.
    """
    
    def __init__(self, base_path: Optional[Path] = None):
        """
        KnowledgeManager를 초기화합니다.
        
        Args:
            base_path (Optional[Path]): 지식 저장소의 기본 경로. 
                                     지정되지 않을 경우 실행 파일의 물리적 폴더 또는 마스터 프로젝트 루트의 'knowledge' 폴더를 사용합니다.
        """
        if base_path:
            self.base_path = Path(base_path)
        else:
            import sys
            from operator_cli.core.utils import get_project_root
            
            project_root = get_project_root()
            
            # 1. PyInstaller 바이너리로 기동 중일 때 (Portable Mode 지원)
            if getattr(sys, 'frozen', False):
                # 실행 파일(sys.executable) 옆에 'knowledge' 폴더가 있는지 체크
                exe_knowledge = Path(sys.executable).resolve().parent / "knowledge"
                if exe_knowledge.exists() and exe_knowledge.is_dir():
                    self.base_path = exe_knowledge
                else:
                    self.base_path = project_root / "knowledge"
            else:
                # 2. 소스 코드 기동 중일 때는 항상 메인 프로젝트의 'knowledge'를 지향
                self.base_path = project_root / "knowledge"
            
        self._ensure_directories()

    def _ensure_directories(self) -> None:
        """지식 저장소의 필수 디렉토리 구조가 존재하는지 확인하고 없으면 생성합니다."""
        categories = ["basement", "library", "proposals"]
        for cat in categories:
            (self.base_path / cat).mkdir(parents=True, exist_ok=True)

    def get_knowledge_path(self, category: str, filename: str) -> Path:
        """
        지정된 카테고리와 파일명에 해당하는 전체 경로를 반환합니다.
        
        Args:
            category (str): 지식 분류.
            filename (str): 파일명 (확장자 포함).
            
        Returns:
            Path: 파일의 절대 경로.
        """
        return self.base_path / category / filename

    def save_knowledge(self, metadata: KnowledgeMetadata, content: str) -> Path:
        """
        지식 문서와 메타데이터를 저장합니다.
        
        Args:
            metadata (KnowledgeMetadata): 문서의 메타데이터.
            content (str): 문서 본문 내용 (Markdown 형식 권장).
            
        Returns:
            Path: 저장된 파일의 경로.
        """
        file_path = self.get_knowledge_path(metadata.category, f"{metadata.id}.md")
        
        # 메타데이터를 YAML Front Matter 형식으로 포함하여 저장할 수도 있으나, 
        # 현재는 단순 파일 저장과 메타데이터 관리에 집중합니다.
        full_content = f"---\n{metadata.model_dump_json(indent=2)}\n---\n\n{content}"
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(full_content)
            
        # library 지식이 변경된 경우 llms.txt 자동 갱신 (Protocol M-1 준수)
        if metadata.category == "library":
            try:
                from operator_cli.core.knowledge.generator import WikiGenerator
                generator = WikiGenerator(manager=self)
                generator.refresh()
            except Exception:
                # 갱신 실패가 지식 저장 자체의 실패로 이어지지 않도록 예외 처리
                pass
                
        return file_path

    def load_knowledge(self, category: str, knowledge_id: str) -> tuple[Optional[KnowledgeMetadata], Optional[str]]:
        """
        저장된 지식 문서를 로드합니다.
        
        Args:
            category (str): 지식 분류.
            knowledge_id (str): 지식 고유 식별자.
            
        Returns:
            tuple: (메타데이터 객체, 본문 내용) 쌍. 파일을 찾을 수 없는 경우 (None, None).
        """
        file_path = self.get_knowledge_path(category, f"{knowledge_id}.md")
        
        if not file_path.exists():
            return None, None
            
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            
        # 메타데이터 파싱 (단순 구현)
        if len(lines) > 0 and lines[0].strip() == "---":
            # 메타데이터 블록 탐색
            end_idx = -1
            for i, line in enumerate(lines[1:], 1):
                if line.strip() == "---":
                    end_idx = i
                    break
            
            if end_idx != -1:
                try:
                    json_meta = "".join(lines[1:end_idx])
                    metadata = KnowledgeMetadata.model_validate_json(json_meta)
                    content = "".join(lines[end_idx+1:]).lstrip()
                    return metadata, content
                except Exception:
                    # 파싱 실패 시 일반 텍스트로 처리
                    pass
                
        return None, "".join(lines)

    def list_knowledge(self, category: Optional[str] = None) -> List[KnowledgeMetadata]:
        """
        지식 문서 목록을 조회합니다.
        
        Args:
            category (Optional[str]): 특정 카테고리만 조회할 경우 지정.
            
        Returns:
            List[KnowledgeMetadata]: 메타데이터 객체 리스트.
        """
        results = []
        categories = [category] if category else ["basement", "library", "proposals"]
        
        for cat in categories:
            cat_path = self.base_path / cat
            if not cat_path.exists():
                continue
                
            for file_path in cat_path.glob("*.md"):
                metadata, _ = self.load_knowledge(cat, file_path.stem)
                if metadata:
                    results.append(metadata)
        
        # 최신순 정렬
        results.sort(key=lambda x: x.updated_at, reverse=True)
        return results

    def detect_conflicts(self, metadata: KnowledgeMetadata) -> List[tuple[KnowledgeMetadata, str]]:
        """
        제안된 지식과 기존 지식 사이의 충돌을 감지합니다. (Protocol P-8 보강)
        제목 유사도 및 태그 중첩을 검사합니다.
        
        Args:
            metadata (KnowledgeMetadata): 검사할 지식 메타데이터.
            
        Returns:
            List[tuple[KnowledgeMetadata, str]]: 충돌 원인과 함께 발견된 기존 지식 리스트.
        """
        conflicts = []
        all_existing = self.list_knowledge()
        
        new_title = metadata.title.lower()
        new_tags = set(metadata.tags)
        
        for existing in all_existing:
            # 자기 자신(proposals에 이미 저장된 경우 등)은 제외
            if existing.id == metadata.id:
                continue
                
            reasons = []
            
            # 1. 제목 유사성 (완전 일치 또는 포함 관계)
            existing_title = existing.title.lower()
            if new_title == existing_title:
                reasons.append("Exact title match")
            elif new_title in existing_title or existing_title in new_title:
                reasons.append(f"Similar title found ('{existing.title}')")
                
            # 2. 태그 중첩 (3개 이상 겹치면 경고)
            existing_tags = set(existing.tags)
            common_tags = new_tags.intersection(existing_tags)
            if len(common_tags) >= 3:
                reasons.append(f"Significant tag overlap: {', '.join(common_tags)}")
            elif len(common_tags) > 0 and new_title == existing_title:
                 reasons.append(f"Common tags: {', '.join(common_tags)}")

            if reasons:
                conflicts.append((existing, " / ".join(reasons)))
                
        return conflicts

    def query_knowledge(self, query: str) -> List[tuple[KnowledgeMetadata, str]]:
        """
        지식 베이스에서 텍스트를 검색합니다. (단순 부분 일치 검색)
        
        Args:
            query (str): 검색어.
            
        Returns:
            List[tuple[KnowledgeMetadata, str]]: 검색 결과 (메타데이터, 일치하는 부분의 컨텍스트).
        """
        results = []
        all_metadata = self.list_knowledge()
        
        for meta in all_metadata:
            _, content = self.load_knowledge(meta.category, meta.id)
            if content and query.lower() in content.lower():
                # 간단한 컨텍스트 추출 (첫 번째 일치 항목 주변 100자)
                idx = content.lower().find(query.lower())
                start = max(0, idx - 40)
                end = min(len(content), idx + len(query) + 40)
                context = f"...{content[start:end]}..."
                results.append((meta, context))
                
        return results

    def approve_proposal(self, proposal_id: str) -> Path:
        """
        제안된 지식을 승인하여 library 카테고리로 이동합니다.
        
        Args:
            proposal_id (str): 제안 문서의 ID.
            
        Returns:
            Path: 이동된 파일의 경로.
            
        Raises:
            FileNotFoundError: 제안 문서를 찾을 수 없는 경우.
        """
        metadata, content = self.load_knowledge("proposals", proposal_id)
        if not metadata:
            raise FileNotFoundError(f"Proposal with ID '{proposal_id}' not found.")
            
        # 기존 파일 삭제
        old_path = self.get_knowledge_path("proposals", f"{proposal_id}.md")
        old_path.unlink()
        
        # 메타데이터 업데이트
        metadata.category = "library"
        metadata.updated_at = datetime.now()
        
        # 새 카테고리에 저장
        return self.save_knowledge(metadata, content)
