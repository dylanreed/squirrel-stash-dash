# Squirrel Yarn - Game Design

## Core Concept

**Genre:** Endless runner platformer

**Premise:** A squirrel in a yellow sweater runs through an endless forest, jumping over bushes, leaping between tree platforms, and collecting yarn skeins for their stash.

**Win/Lose Conditions:**
- No win state - play for high score (stash count)
- Game over ONLY when falling into a gap
- Getting hit by a bush: lose half your yarn (skeins explode outward Sonic-style), squirrel slows down significantly
- If hit with zero yarn = knocked out, game over

**Score:** "Stash = X" displaying total yarn value collected

## Gameplay Mechanics

**Controls:**
- Arrow keys or WASD - Left/Right to influence speed slightly, Up/Space to jump
- No climbing - trees have platforms you jump between

**Movement:**
- Squirrel runs automatically to the right
- Base speed increases gradually over time
- After bush hit: speed drops significantly, must build back up
- Dynamic camera: squirrel moves forward on screen when fast, settles back when slowed

**Obstacles:**
- **Bushes** - Ground-level obstacles. Hit = yarn explosion + slowdown
- **Gaps** - Missing ground/platforms. Fall = game over

**Platform Generation:**
- Procedural with rules ensuring always a safe path exists
- Mix of ground running and tree platform sections
- Platforms at varying heights requiring different jump timings

**Yarn Skeins:**
- Float in air AND sit on platforms (mixed placement)
- Spawn more frequently as game progresses
- Higher value colors appear later in runs

## Scoring & Milestones

**Two Tracking Systems:**

1. **Stash (Score)** - Total yarn value collected this run
   - Displayed prominently: "Stash = X"
   - Lost yarn from bush hits can be re-collected if you're quick

2. **Distance** - How far you've traveled this run
   - Measured in units (pixels/meters, shown as simple number)
   - Used for milestone and color tier progression

**Milestone Sign:**
- Physical sign in the game world showing your furthest run ever
- When you pass your previous best, sign appears and updates
- Persists between sessions (saved to file)

**Color Tier Progression (distance-based):**
- Tiers unlock as you travel further
- Bush hit = resets back to RGB tier only
- Must travel the distance again to unlock higher tiers
- Creates risk/reward: do you play safe with your stash, or push for rare skeins?

**Persistence:**
- High score (best stash) saved
- Furthest distance saved (for milestone sign)

## Visuals & Technical

**Resolution:** 800x600 (4:3 retro style)

**Sprite Size:** 64x64 pixels for main elements

**Art Assets (via PixelLab):**
- Squirrel in yellow sweater (running animation, jumping, hit/stunned)
- Tree trunks and platforms
- Bushes (obstacle)
- Ground/grass tiles
- Forest background (parallax layers)
- Yarn skeins in all colors: RGB, CMYK, Secondary, Rainbow shimmer

**Yarn Color Values:**

| Tier | Colors | Points | Appears |
|------|--------|--------|---------|
| Basic | Red, Green, Blue | +1 | From start |
| Mid | Cyan, Magenta, Yellow, Black | +2 | After ~30 sec |
| Late | Orange, Purple, Lime, Teal, Pink, Brown | +3 | After ~60 sec |
| Rare | Rainbow/Gold shimmer | +5 | Random, any time |

**UI:**
- "Stash = X" score display (top corner)
- Simple, clean pixel font

## Implementation Structure

**File Structure:**
```
squirrel-yarn/
├── main.py              # Entry point, game loop
├── game.py              # Game state, spawning, collision
├── player.py            # Squirrel class, movement, animations
├── obstacles.py         # Bush and platform classes
├── yarn.py              # Yarn skein class, colors, values
├── camera.py            # Dynamic camera following
├── generator.py         # Procedural level generation
├── ui.py                # Score display, milestone sign
├── save.py              # High score/distance persistence
└── assets/
    ├── sprites/         # PixelLab-generated PNGs
    └── sounds/          # (future: optional sound effects)
```

**Core Game Loop:**
1. Update squirrel position/animation
2. Generate new terrain ahead, remove behind
3. Check collisions (bushes, yarn, gaps)
4. Update camera position (dynamic follow)
5. Update UI (stash, distance)
6. Increase speed based on time/distance
7. Render everything

**PixelLab Asset Generation:**
- Generate all sprites upfront before gameplay coding
- Save to assets/sprites/ folder
- Load once at game start
