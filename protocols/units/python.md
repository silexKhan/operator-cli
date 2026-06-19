---
description: "Python-Specific Clean Architecture Technical Protocol (Dumb Controller, Strict Schema)"
---
# Unit: Python (Clean Architecture)
- **Protocol P-1 (Dumb Controller):** All request receivers (Actions/Routers) must not contain business logic; all business decisions must be delegated to the Service Layer.
- **Protocol P-2 (Strict Schema):** All input/output (I/O) must be defined using Pydantic models. Detailed field descriptions must serve as the final system specification.
- **Protocol P-3 (Async Safety):** All I/O operations and business logic must be written asynchronously (`async`/`await`) to ensure system concurrency and readability.
- **Protocol P-4 (Handler Separation):** Service entry points must be named `[Action]handler`. Detailed logic exceeding 3 lines must be strictly separated into internal methods prefixed with an underscore (`_`).
- **Protocol P-5 (Documentation):** Detailed docstrings and comments must be written for all classes, functions, and Enum members so that the structure is understandable even without Python knowledge.
- **Protocol P-6 (Strict Enum):** Hardcoded strings or numbers are strictly prohibited. All fixed state values must be managed via Enums and validated in conjunction with Pydantic models.
- **Protocol P-7 (Pattern Matching):** When handling complex branching (3 or more cases) or Enums, use `match-case` statements. Must always include a wildcard (`case _:`) to prevent unhandled exceptions.
- **Protocol P-8 (Pre-flight Check):** Before reloading the server, static analysis such as `py_compile` and `mypy` must be mandatorily performed to proactively block missing imports and runtime errors.
