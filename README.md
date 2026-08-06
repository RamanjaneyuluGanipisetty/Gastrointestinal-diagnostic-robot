Gastrointestinal Diagnostic Robot Simulation

A simulated, manually controlled pill-sized capsule robot designed to navigate through a human gastrointestinal tract model in Webots. Built as part of my MSc Mechatronics program at the University of Chester, focusing on constrained navigation, onboard image capture and detailed telemetric capture.



Demonstration

Short Preview
![Capsule Robot Navigating GI Tract](./media/demo.gif)

📹 Full Video Demo: [Watch the complete video recording here](./media/full_demo.mp4)



## What This Project Does

Simulated Navigation: Controls a capsule robot through a realistic 3D GI tract CAD model using Webots physics.
Manual Control Script: Uses a custom Python controller (`Pill_controller.py`) to handle directional movement and steering inside narrow anatomical boundaries.
Onboard Diagnostic Capture: Captures and saves internal camera views into the `captured_images/` folder during movement runs to evaluate inspection performance.
Physical Interaction: Tests how the capsule geometry interacts with curved internal walls without getting stuck.
