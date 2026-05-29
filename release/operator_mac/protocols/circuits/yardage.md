---
description: "야디지(Yardage) 모바일 앱 개발 프로젝트"
units:
  - swift
  - sentinel
  - planning
  - markdown
---
# Yardage Circuit Protocols
- **Y-1 (UIKit & Storyboard Standard):** 이 프로젝트는 SwiftUI가 아닌 UIKit 및 Storyboard 기반으로 개발됩니다. 모든 화면 분기는 Storyboard 및 Safe Auto-layout 규칙을 준수하며 UI 레이아웃을 작성합니다.
- **Y-2 (GDSService Delegate Interface):** 기기 통신 및 하드웨어 API 데이터 통제를 위해 `GDSService.shared` 인스턴스를 적극 활용하고, 반드시 `GDSServiceDelegate` 규약을 성실히 이행합니다. 데이터 응답(`onCCDataReady`, `onCCDataFailed`) 수신 시 비동기 UI 갱신(`DispatchQueue.main.async`)을 무조건 수반해야 합니다.
- **Y-3 (Deca GDS Model Mapping):** GDS 하드웨어가 제공하는 `GDSClub`, `GDSHoleData`, `GDSUndulationData` 등의 오리지널 데이터 모델 구조를 존중하고, `YardageStorage` 및 `StorageService`를 연동하여 기기 오프라인 환경에서도 안전하게 데이터를 캐싱/로드합니다.
- **Y-4 (Strict Optional Binding):** 하드웨어/외부 통신 간 빈번한 입출력 상황 속에서 옵셔널 언래핑 오류로 인한 크래시를 전면 예방하기 위해 강제 언래핑(`!`)을 전면 금지하며, `if let` / `guard let` 바인딩을 철저히 준수합니다.
- **Y-5 (Project Workspace Path):** 이 프로젝트의 메인 코드베이스 경로는 `/Users/silex/workspace/project/yardage`입니다.
