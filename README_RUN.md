# Squirrel Yarn - Running Instructions

## Quick Start

To run the game:

```bash
python3 main.py
```

## Controls

- **SPACE** or **UP ARROW** - Jump
- **ESC** or close window - Quit game

## Current Features

### Player (Squirrel)
- Automatic rightward movement
- Jump mechanic with gravity physics
- Speed increases over time (up to 3x)
- Yarn collection tracking
- Hit/stun mechanic - when hit, you lose yarn in a Sonic-style explosion and slow down temporarily
- Visual placeholder (brown rectangle with eyes and tail)

### Camera
- Dynamic following system
- Smooth lerp-based movement
- Position adjusts based on player speed (faster = squirrel moves further left on screen)

### Game System
- 60 FPS game loop
- Collision detection ready
- Score tracking (stash and distance)
- Basic yarn spawning (test objects)
- UI overlay showing yarn count, stash, distance, and speed

### Placeholder Graphics
- Squirrel: Brown rectangle with eyes and tail
- Yarn: Pink circles
- Ground: Green
- Sky: Blue

## Files Created

1. **main.py** - Entry point with Pygame initialization and main loop
2. **player.py** - Squirrel class with movement, jumping, and yarn mechanics
3. **camera.py** - Dynamic camera following system
4. **game.py** - Game state management and coordination

## Next Steps

To complete the game, you'll need to add:
- obstacles.py (obstacle generation and management)
- yarn.py (yarn ball objects)
- generator.py (procedural level generation)
- ui.py (enhanced UI elements)
- save.py (save/load system)

## Requirements

- Python 3.x
- Pygame 2.x

Install pygame:
```bash
pip install pygame
```
