# Squirrel Yarn - Asset Generation Guide for PixelLab.ai

Use this guide to generate all game assets using [PixelLab.ai](https://www.pixellab.ai).

## Art Style Guidelines

- **Style**: Cozy, colorful pixel art with soft edges
- **Palette**: Warm autumn colors (browns, oranges, golds) with vibrant yarn colors
- **Mood**: Cheerful, whimsical, family-friendly
- **Consistency**: Generate squirrel first, then use as style reference for other assets

---

## Required Assets

### 1. Squirrel (Main Character)
**File**: `assets/sprites/squirrel.png`
**Size**: 40x40 pixels (code reference: player.py:29-30)

**Prompt suggestion**:
> Cute cartoon squirrel character, side view facing right, running pose, fluffy tail, warm brown fur with cream belly, big expressive eyes, pixel art style, cozy game aesthetic, transparent background

**Animation frames** (optional sprite sheet):
- Running (4-6 frames)
- Jumping (mid-air pose)
- Hit/stunned (red tint or stars)

---

### 2. Ground Tile
**File**: `assets/sprites/ground.png`
**Size**: 64x64 pixels (code reference: obstacles.py:49)

**Prompt suggestion**:
> Tileable grass and dirt ground tile, green grass on top with brown soil below, pixel art style, side-scroller platformer, seamless edges left and right, cozy autumn game aesthetic

**Notes**: Must tile seamlessly horizontally

---

### 3. Platform
**File**: `assets/sprites/platform.png`
**Size**: 128x32 pixels (code reference: obstacles.py:13)

**Prompt suggestion**:
> Wooden log platform, horizontal wooden branch or plank, brown wood texture with bark details, pixel art style, platformer game, transparent background, cozy forest aesthetic

**Notes**: Will be scaled to various widths (96, 128, 160)

---

### 4. Bush (Obstacle)
**File**: `assets/sprites/bush.png`
**Size**: 64x48 pixels (code reference: obstacles.py:86)

**Prompt suggestion**:
> Thorny bush obstacle, dark green spiky shrub, dangerous-looking but cute, small thorns visible, pixel art style, side-view, transparent background, forest game aesthetic

**Notes**: Should look hazardous but not scary (cozy game)

---

### 5. Yarn Skeins (Collectibles)
**Size**: 32x32 pixels each (code reference: yarn.py:60)

Generate each color as a separate file:

| File | Color | Prompt |
|------|-------|--------|
| `yarn_red.png` | Red | Cute yarn ball, crimson red color, wound yarn skein with loose thread, pixel art, transparent background, small highlight |
| `yarn_green.png` | Green | Cute yarn ball, forest green color, wound yarn skein with loose thread, pixel art, transparent background |
| `yarn_blue.png` | Blue | Cute yarn ball, sky blue color, wound yarn skein with loose thread, pixel art, transparent background |
| `yarn_cyan.png` | Cyan | Cute yarn ball, cyan/turquoise color, wound yarn skein, pixel art, transparent background |
| `yarn_magenta.png` | Magenta | Cute yarn ball, bright magenta/pink color, wound yarn skein, pixel art, transparent background |
| `yarn_yellow.png` | Yellow | Cute yarn ball, golden yellow color, wound yarn skein, pixel art, transparent background |
| `yarn_black.png` | Black | Cute yarn ball, dark charcoal black color, wound yarn skein, pixel art, transparent background, subtle gray highlight |
| `yarn_orange.png` | Orange | Cute yarn ball, bright orange color, wound yarn skein, pixel art, transparent background |
| `yarn_purple.png` | Purple | Cute yarn ball, deep purple/violet color, wound yarn skein, pixel art, transparent background |
| `yarn_lime.png` | Lime | Cute yarn ball, bright lime green color, wound yarn skein, pixel art, transparent background |
| `yarn_teal.png` | Teal | Cute yarn ball, teal/dark cyan color, wound yarn skein, pixel art, transparent background |
| `yarn_pink.png` | Pink | Cute yarn ball, hot pink color, wound yarn skein, pixel art, transparent background |
| `yarn_brown.png` | Brown | Cute yarn ball, warm brown color, wound yarn skein, pixel art, transparent background |
| `yarn_rainbow.png` | Rainbow | Magical yarn ball with rainbow gradient colors, sparkles, glowing effect, pixel art, transparent background |

**Tip**: Generate one yarn ball first, then use PixelLab's style consistency feature to generate all colors with the same style.

---

### 6. Background Elements

#### Sky Background
**File**: `assets/backgrounds/sky.png`
**Size**: 800x600 pixels

**Prompt suggestion**:
> Parallax sky background, soft gradient from light blue to deeper blue, fluffy white clouds, autumn afternoon, pixel art style, peaceful cozy game aesthetic, tileable horizontally

#### Far Trees (Parallax layer)
**File**: `assets/backgrounds/trees_far.png`
**Size**: 800x300 pixels

**Prompt suggestion**:
> Distant forest silhouette, autumn trees in background, oranges and yellows, soft pixelated style, parallax layer, transparent bottom, cozy endless runner game

#### Near Trees (Parallax layer)
**File**: `assets/backgrounds/trees_near.png`
**Size**: 800x400 pixels

**Prompt suggestion**:
> Forest treeline, autumn trees closer view, fall colors orange red yellow, pixel art platformer background, transparent areas, tileable horizontally

---

### 7. Splash Screen
**File**: `assets/splash/title.png`
**Size**: 800x600 pixels

**Prompt suggestion**:
> Game title screen "SQUIRREL YARN", cute squirrel character surrounded by colorful yarn balls, autumn forest background, cozy warm lighting, pixel art style, whimsical game aesthetic, space for "Press SPACE to start" text at bottom

**Elements to include**:
- Title text "SQUIRREL YARN" in playful font
- Squirrel character prominently featured
- Scattered yarn balls in various colors
- Warm autumn forest setting
- Leaves falling

---

### 8. UI Elements (Optional)

#### Milestone Sign
**File**: `assets/sprites/sign.png`
**Size**: 64x80 pixels

**Prompt suggestion**:
> Wooden signpost, rustic forest sign, brown wood with weathered look, pixel art style, transparent background, would display distance marker

---

## Directory Structure

```
assets/
├── sprites/
│   ├── squirrel.png
│   ├── ground.png
│   ├── platform.png
│   ├── bush.png
│   ├── sign.png
│   ├── yarn_red.png
│   ├── yarn_green.png
│   ├── yarn_blue.png
│   ├── yarn_cyan.png
│   ├── yarn_magenta.png
│   ├── yarn_yellow.png
│   ├── yarn_black.png
│   ├── yarn_orange.png
│   ├── yarn_purple.png
│   ├── yarn_lime.png
│   ├── yarn_teal.png
│   ├── yarn_pink.png
│   ├── yarn_brown.png
│   └── yarn_rainbow.png
├── backgrounds/
│   ├── sky.png
│   ├── trees_far.png
│   └── trees_near.png
├── splash/
│   └── title.png
├── sounds/
│   └── (existing sounds)
└── music/
    └── (existing music)
```

---

## PixelLab.ai Workflow Tips

1. **Start with the squirrel** - This sets the style reference for everything else
2. **Use style consistency** - After generating squirrel, use it as reference for other assets
3. **Generate yarn as a batch** - Create one yarn ball, then recolor with inpainting
4. **Test tiles** - Download ground tile and test horizontal tiling before finalizing
5. **Export as PNG** - Ensure transparent backgrounds where noted
6. **Match sizes exactly** - The game code expects specific dimensions

---

## Color Reference (RGB Values)

For consistency, here are the exact RGB values the game uses for fallback rendering:

| Color | RGB |
|-------|-----|
| Red | (220, 20, 60) |
| Green | (34, 139, 34) |
| Blue | (30, 144, 255) |
| Cyan | (0, 255, 255) |
| Magenta | (255, 0, 255) |
| Yellow | (255, 215, 0) |
| Black | (40, 40, 40) |
| Orange | (255, 140, 0) |
| Purple | (148, 0, 211) |
| Lime | (50, 205, 50) |
| Teal | (0, 128, 128) |
| Pink | (255, 105, 180) |
| Brown | (139, 69, 19) |
| Squirrel Brown | (139, 69, 19) |
| Ground Green | (34, 139, 34) |
| Platform Brown | (101, 67, 33) |
