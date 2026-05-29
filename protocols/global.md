# Global Project Protocols

[LITERAL]
- **P-0 (Absolute Truth):** Answer based on verified facts only.
- **P-1 (Surgical Edit):** Prefer targeted code replacements over full file writes.
- **P-2 (Security First):** Never expose or commit secrets.
- **P-3 (Dumb View):** Maintain UI as a visual representation of state only.
- **P-4 (Command Generation):** You are an Operator AI. When asked to perform a task, suggest the most efficient shell commands (using bash/zsh syntax) within markdown code blocks.
- **P-5 (Graphify First):** 프로젝트 분석 시 `graphify-out/graph.json` 및 `GRAPH_REPORT.md`가 존재한다면, 개별 파일을 읽기 전에 이를 우선 참조하여 시스템의 전체 구조와 핵심 노드를 파악한다.
- **P-6 (OAKS System Integration & Anti-Hallucination):** This project utilizes **OAKS (Operator AI Knowledge System)** to manage verified domain knowledge. When the user asks about unfamiliar golfzon/GDS terms, hardware APIs, or business contexts, **NEVER hallucinate or guess. You MUST first query the OAKS knowledge base (`operator knowledge query`)** or search the codebase directory to fetch verified facts before formulating your response.
- **P-7 (OAKS Propose & Sync):** When you identify new technical findings, specifications, or debugging patterns, you must propose them to the OAKS proposal stage using `operator knowledge propose` and regularly refresh the verified AI directory map (`llms.txt`).
- **P-8 (Yardage & GDSLib Native Spec):** The Yardage application operates strictly on a **UIKit & Storyboard** architecture, utilizing `GDSLib.xcframework` as its core hardware API mapping module. Under this scheme, `userNo` (historically represented as `302313` inside cockpit setups) and `yardageNumber` (the unique round booking sequence, defaulting to `0` inside mock configurations) are strictly separated variables that must never be mixed.
[/LITERAL]
