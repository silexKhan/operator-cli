# Graph Report - .  (2026-05-29)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 44 nodes · 37 edges · 19 communities (5 shown, 14 thin omitted)
- Extraction: 38% EXTRACTED · 62% INFERRED · 0% AMBIGUOUS · INFERRED: 23 edges (avg confidence: 0.97)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `91f5b520`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- [[_COMMUNITY_Connection & Circuit Management|Connection & Circuit Management]]
- [[_COMMUNITY_OAKS Wiki Generation|OAKS Wiki Generation]]
- [[_COMMUNITY_LLM Model Management|LLM Model Management]]
- [[_COMMUNITY_Knowledge Extraction|Knowledge Extraction]]
- [[_COMMUNITY_Context Compaction & Summarization|Context Compaction & Summarization]]
- [[_COMMUNITY_Protocol & Circuit Engine|Protocol & Circuit Engine]]
- [[_COMMUNITY_Agent Command Execution|Agent Command Execution]]
- [[_COMMUNITY_Circuit Protocols (MCPGDR)|Circuit Protocols (MCP/GDR)]]
- [[_COMMUNITY_Agent Guides & Circuit Definitions|Agent Guides & Circuit Definitions]]
- [[_COMMUNITY_Operator CLI Core|Operator CLI Core]]
- [[_COMMUNITY_Corporate & Tech Knowledge|Corporate & Tech Knowledge]]
- [[_COMMUNITY_Core Engine & Compaction|Core Engine & Compaction]]
- [[_COMMUNITY_Planning Unit Protocols|Planning Unit Protocols]]
- [[_COMMUNITY_Environment & Shell Wrapper|Environment & Shell Wrapper]]
- [[_COMMUNITY_Build Script (Bash)|Build Script (Bash)]]
- [[_COMMUNITY_Test Script|Test Script]]
- [[_COMMUNITY_Documentation and Planning|Documentation and Planning]]
- [[_COMMUNITY_Package Setup|Package Setup]]
- [[_COMMUNITY_Test Execution Module|Test Execution Module]]

## God Nodes (most connected - your core abstractions)
1. `Operator CLI Documentation` - 7 edges
2. `OAKS Knowledge System Design Plan` - 6 edges
3. `Global Project Protocols` - 6 edges
4. `LLM System/Knowledge Base` - 4 edges
5. `Python Unit Protocols` - 4 edges
6. `Sentinel Unit Protocols` - 4 edges
7. `Session Memory Log` - 3 edges
8. `AI Agent Guide for Operator CLI` - 3 edges
9. `Core Engine Analysis Report` - 3 edges
10. `OAKS System Overview and Functionality` - 2 edges

## Surprising Connections (you probably didn't know these)
- `OAKS Knowledge System Design Plan` --conceptually_related_to--> `OAKS Knowledge Index`  [INFERRED]
  docs/KNOWLEDGE_SYSTEM_DESIGN.md → knowledge/index.md
- `OAKS System Overview and Functionality` --conceptually_related_to--> `Operator CLI Documentation`  [INFERRED]
  llms-full.txt → README.md
- `Multi-Platform Build Workflow` --conceptually_related_to--> `Operator CLI Documentation`  [INFERRED]
  .github/workflows/build.yml → README.md
- `OAKS System Overview and Functionality` --conceptually_related_to--> `OAKS Knowledge System Design Plan`  [INFERRED]
  llms-full.txt → docs/KNOWLEDGE_SYSTEM_DESIGN.md
- `OAKS Knowledge System Design Plan` --references--> `LLM Full Knowledge Base`  [EXTRACTED]
  docs/KNOWLEDGE_SYSTEM_DESIGN.md → llms-full.txt

## Communities (19 total, 14 thin omitted)

### Community 0 - "Connection & Circuit Management"
Cohesion: 0.33
Nodes (10): AI Agent Guide for Operator CLI, Multi-Platform Build Workflow, Core Engine Analysis Report, OAKS Knowledge System Design Plan, LLM System/Knowledge Base, LLM Full Knowledge Base, OAKS Passive Interface Standard Compliance, OAKS System Overview and Functionality (+2 more)

### Community 1 - "OAKS Wiki Generation"
Cohesion: 0.33
Nodes (7): Global Project Protocols, OAKS 시스템 개요, Unit: Markdown (Documentation Integrity), Unit: Planning (Architectural Specs), Unit: Python (Clean Architecture), Research & Analysis Protocols, Unit: Sentinel (Autonomous Commander)

### Community 2 - "LLM Model Management"
Cohesion: 1.00
Nodes (3): 주식회사 골프존 핵심 기업 정보 및 시장 지위, 골프존의 핵심 기술 제품군 및 특징, 글로벌 플랫폼 기업 전환을 위한 성장 전략

### Community 3 - "Knowledge Extraction"
Cohesion: 0.67
Nodes (3): OAKS 시스템 개요 및 기능, OAKS Passive Interface 표준 준수, OAKS 시스템 개요

### Community 4 - "Context Compaction & Summarization"
Cohesion: 1.67
Nodes (3): Python Unit Protocols, Sentinel Unit Protocols, Operator CLI Guide

## Knowledge Gaps
- **24 isolated node(s):** `LLM Full Knowledge Base`, `OAKS Passive Interface Standard Compliance`, `Multi-Platform Build Workflow`, `Global Platform Company Strategy`, `OAKS Passive Interface 표준 준수` (+19 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **14 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `OAKS Knowledge System Design Plan` connect `Connection & Circuit Management` to `Agent Command Execution`?**
  _High betweenness centrality (0.032) - this node is a cross-community bridge._
- **Are the 4 inferred relationships involving `Operator CLI Documentation` (e.g. with `OAKS Knowledge System Design Plan` and `OAKS System Overview and Functionality`) actually correct?**
  _`Operator CLI Documentation` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `OAKS Knowledge System Design Plan` (e.g. with `Operator CLI Documentation` and `OAKS System Overview and Functionality`) actually correct?**
  _`OAKS Knowledge System Design Plan` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Are the 6 inferred relationships involving `Global Project Protocols` (e.g. with `OAKS 시스템 개요` and `Research & Analysis Protocols`) actually correct?**
  _`Global Project Protocols` has 6 INFERRED edges - model-reasoned connections that need verification._
- **What connects `LLM Full Knowledge Base`, `OAKS Passive Interface Standard Compliance`, `Multi-Platform Build Workflow` to the rest of the system?**
  _24 weakly-connected nodes found - possible documentation gaps or missing edges._