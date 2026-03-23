# Stickman AI Sandbox (Pymunk)

A 2D physics sandbox for a stickman ragdoll using the Pymunk physics engine.

## Features
- **Realistic Ragdoll**: Realistic human mass distribution (~75kg total) and physically-accurate joint limits.
- **Pymunk Engine**: Migrated from Box2D for improved stability and a more modern API.
- **Environment**:
  - **Stairs**: A large platform at the top for exercise and maneuvers.
  - **Pull-up Bar (Bar Fix)**: Positioned reachable above the stickman's head.
  - **Soccer Goal & Ball**: Includes a physics-enabled ball for kicking practice.
- **Interactions**:
  - **Mouse Drag**: Grab any part of the stickman or objects with the mouse.
  - **Reset**: Press **'R'** to reset the ragdoll and objects to their starting points.
  - **Quit**: Press **'Q'** or close the window to exit.

## Requirements
- Python 3.10+
- `pygame`
- `pymunk`

Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Sandbox
```bash
python main.py
```

## Project Structure
- `main.py`: Main loop, input handling, and HUD.
- `sandbox.py`: Physics space management, floor/walls, and environment objects.
- `body.py`: Stickman ragdoll construction (torso, head, limbs, joints).
- `utils/config.py`: Global constants for geometry, physics, and AI.
- `brain/`: 
  - `low.py`: Low-level joint/pD controller.
  - `high.py`: High-level command interpreter.
- `skills/`: Intended directory for RL skill models (currently empty, ready for training).
