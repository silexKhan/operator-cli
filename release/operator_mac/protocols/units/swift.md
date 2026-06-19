---
description: "SwiftUI-based iOS/macOS Native Development and Type Safety Protocol"
---
# Unit: Swift (iOS/macOS Native)
- **Protocol SW-1 (SwiftUI Focus):** Prioritize using the SwiftUI framework whenever possible.
- **Protocol SW-2 (Type Safety):** Prevent runtime errors through strong type checking.
- **Protocol SW-3 (No Force Unwrap):** Optional binding (`if let`, `guard let`) is mandatory; forced unwrapping (`!`) is strictly prohibited.
- **Protocol SW-4 (Architecture & State):** Adhere to the MVVM pattern and apply clear state management using `@State`, `@Binding`, `@EnvironmentObject`, etc.
- **Protocol SW-5 (Modern Concurrency):** Utilize modern `async`/`await` and `Task` for asynchronous processing instead of the legacy GCD (DispatchQueue).
- **Protocol SW-6 (Data Management):** When local data storage is required, consider the modern SwiftData standard first.
- **Protocol SW-7 (CLI Build Verification):** After every code modification, you must immediately self-verify the absence of compilation errors by executing `xcodebuild` or `swift build` commands in the terminal environment.
