from typing import List, Dict

SUMMARIZATION_SYSTEM_PROMPT = """당신은 컨텍스트 요약 보조원입니다. 사용자와 AI 코딩 어시스턴트 간의 대화를 읽고, 지정된 형식에 맞춰 구조화된 요약을 생성하십시오.
**대화를 계속하지 마십시오. 질문에 답하지 마십시오. 오직 구조화된 요약만 출력하십시오.**

형식:
## Goal
(사용자의 최종 목적)

## Constraints & Preferences
(제약 사항 및 선호도)

## Progress
(완료된 작업, 진행 중인 작업, 차단된 작업)

## Key Decisions
(주요 결정 사항 및 근거)

## Next Steps
(향후 단계)
"""

def format_conversation_for_summary(messages: List[Dict]) -> str:
    """Serializes conversation messages into a single string for summarization."""
    formatted_text = ""
    for msg in messages:
        role = msg.get("role", "unknown")
        content = msg.get("content", "")
        
        if role == "user":
            formatted_text += f"[User]: {content}\n\n"
        elif role == "assistant":
            formatted_text += f"[Assistant]: {content}\n\n"
        elif role == "system":
            # System prompts might be too long, but we might need some of them.
            # For now, let's include them but marked.
            formatted_text += f"[System]: {content}\n\n"
        elif role == "tool":
            # Truncate tool results if too long to save context tokens
            max_chars = 2000
            if len(content) > max_chars:
                content = content[:max_chars] + "... (truncated)"
            formatted_text += f"[Tool result]: {content}\n\n"
        else:
            formatted_text += f"[{role}]: {content}\n\n"
            
    return formatted_text.strip()
