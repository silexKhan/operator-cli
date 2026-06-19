---
description: "Ball Flight Simulator Circuit"
units:
  - swift
  - planning
  - sentinel
---
# Ball Flight Simulator Circuit Protocols

- **Project Objective:** Build a physics-based ball flight simulator that calculates 3D flight trajectory, carry distance, peak height, flight time, landing angle, and offline distance from initial ball data measured by a camera-based golf sensor.
- **Mandatory Inputs:** Ball Speed, Launch Angle, Launch Direction, Back Spin, Spin Axis (or Side Spin), Initial Ball Position, Air Density (or Temperature, Altitude, Humidity), Wind Speed, Wind Direction.
- **Optional Inputs:** Ball Type, Drag Coefficient (Cd) correction, Lift Coefficient (Cl) correction, Spin Decay correction.
- **Core Formulas:**
  - Gravity: Fg = m * g
  - Drag Force: Fd = 0.5 * rho * Cd * A * |v|^2 (Direction: opposite to velocity)
  - Lift Force (Magnus Force): Fl = 0.5 * rho * Cl * A * |v|^2 (Direction: spinAxis x velocity)
  - Spin Decay: dω/dt = -Cm * |v| * ω or simple model: ω(t + dt) = ω(t) * exp(-k * dt)
  - Equations of Motion: a = (Fg + Fd + Fl) / m, v(t + dt) = v(t) + a * dt, p(t + dt) = p(t) + v(t) * dt
- **Recommended Integration Methods:** Start with Euler integration for the initial version, then upgrade to RK4 (Runge-Kutta 4th order) for better accuracy.
- **Expected Outputs:** 3D Trajectory Points, Carry Distance, Total Distance, Peak Height, Flight Time, Landing Angle, Offline Distance, Shot Shape, Spin Decay Curve.
- **Design Structure:**
  - **Domain:** GolfShotInput, GolfBallState, GolfEnvironment, GolfTrajectoryPoint, GolfFlightResult, GolfFlightSimulator
  - **Data:** AerodynamicCoefficientProvider, FixedCoefficientProvider, TableCoefficientProvider, MachineLearningCoefficientProvider
  - **Physics:** Vector3, ForceCalculator, DragForceCalculator, LiftForceCalculator, SpinDecayCalculator, Integrator, EulerIntegrator, RK4Integrator
  - **Presentation:** GolfFlightViewModel, GolfTrajectoryView, GolfResultView
- **Development Sequence:**
  1. Define input value models.
  2. Implement Vector3 operations.
  3. Implement gravity, drag, and lift force calculations.
  4. Implement spin decay.
  5. Calculate trajectory using Euler method.
  6. Simulate ground collision.
  7. Calculate Carry, Peak Height, and Flight Time.
  8. Upgrade to RK4 integration.
  9. Compare with actual shot data.
  10. Add Cd, Cl, Cm correction tables or ML models.
- **Development Constraints (Critical):**
  - Club Speed, Club Path, and Face Angle are NOT mandatory inputs for the flight simulation.
  - After the ball leaves the club, Ball Speed, Launch Angle, Launch Direction, Spin Rate, and Spin Axis are the core factors.
  - Accuracy relies heavily on the measurement precision of the Spin Axis rather than just physical formulas.
  - Prioritize using Spin Axis over Side Spin for calculations.
  - Start with fixed values for Cd, Cl, and Cm, then dynamically correct them based on velocity and spin ratio later.
