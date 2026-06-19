---
description: "틈(Teum) 휴식/알림 앱 프로젝트"
units:
  - swift
  - planning
---
# Teum Circuit Protocols
- **T-1 (Deployment Target):** macOS 15.0 (Sequoia)를 타겟으로 함. (15.6.1 완벽 호환). 레거시 API 사용 금지.
- **T-2 (Frameworks):** SwiftUI, Combine, SMAppService 등 최신 Apple 네이티브 프레임워크만을 활용하여 설계됨.
- **T-3 (Timer Feature):** 타이머는 간격(interval) 방식과 특정 시간(specificTime) 방식을 모두 지원. 타이머 추가 로직은 별도의 시트 뷰(TimerEditView)를 통해 처리함.
- **T-4 (Delete Interaction):** 설정 화면에서의 타이머 삭제는 스와이프(swipeActions) 또는 우클릭(contextMenu)으로만 동작하며, 반드시 삭제 여부를 묻는 팝업(Confirmation Alert)을 띄움.
- **T-5 (Project Name vs Display Name):** 빌드, 서명(CodeSign) 오류 방지를 위해 내부 프로젝트 및 타겟명은 영문 `Teum`을 사용하며, 사용자 표시 앱 이름(CFBundleDisplayName)만 `틈`으로 유지함.
