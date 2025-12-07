# Web Deployment with Pygbag

This guide explains how to deploy Stash Dash to the web using Pygbag, which compiles Pygame to WebAssembly.

## Prerequisites

- Python 3.8+
- pip

## Installation

```bash
pip install pygbag --user --upgrade
```

## Required Code Changes

The `main.py` file needs modifications for async web execution:

### 1. Add asyncio import

```python
import asyncio
```

### 2. Convert main() to async

Change:
```python
def main():
```

To:
```python
async def main():
```

### 3. Add await in game loop

After `clock.tick(FPS)`, add:
```python
await asyncio.sleep(0)
```

### 4. Change entry point

Replace:
```python
if __name__ == "__main__":
    main()
```

With:
```python
asyncio.run(main())
```

### Complete Modified main.py

```python
"""
Squirrel Yarn - Main Entry Point
An endless runner game where you play as a squirrel collecting yarn.
"""

import pygame
import sys
import asyncio
from game import Game


async def main():
    """Initialize Pygame and run the main game loop."""
    pygame.init()

    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 600
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Stash Dash")

    clock = pygame.time.Clock()
    FPS = 60

    game = Game(SCREEN_WIDTH, SCREEN_HEIGHT)

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                result = game.handle_keypress(event.key)
                if result == "quit":
                    running = False

        keys = pygame.key.get_pressed()
        game.update(dt, keys)
        game.render(screen)
        pygame.display.flip()

        await asyncio.sleep(0)  # Required for web

    pygame.quit()


asyncio.run(main())
```

## Audio Requirements

Pygbag works best with OGG audio format. If you have MP3 or WAV files, convert them:

```bash
# Using ffmpeg
ffmpeg -i sound.mp3 sound.ogg
ffmpeg -i sound.wav sound.ogg
```

## Building for Web

From the **parent directory** of your project:

```bash
cd /path/to/parent/folder
pygbag squirrel-stash-dsah
```

Or from within the project:

```bash
pygbag .
```

This will:
1. Package all assets
2. Compile Python to WebAssembly
3. Start a local test server at `http://localhost:8000`

## Testing Locally

After running `pygbag`, open your browser to:
```
http://localhost:8000
```

## Deployment Options

### Option 1: Netlify (Static Hosting)

1. Build with pygbag (creates `build/web` folder)
2. Go to [netlify.com](https://netlify.com)
3. Drag and drop the `build/web` folder to deploy

**Note:** Some users report issues with Netlify. If you encounter 404 errors for `pythonrc.py`, try GitHub Pages instead.

### Option 2: GitHub Pages (Recommended)

1. Create a `gh-pages` branch or use `/docs` folder
2. Copy contents of `build/web` to that location
3. Enable GitHub Pages in repository settings
4. Access at `https://username.github.io/repo-name`

### Option 3: itch.io

1. Go to [itch.io](https://itch.io) and create account
2. Create new project, select "HTML" as kind of project
3. Zip the contents of `build/web`
4. Upload the zip file
5. Set viewport to 800x600
6. Check "SharedArrayBuffer support" if needed

## Known Limitations

- **Performance**: CPU-intensive code runs slower in WebAssembly
- **Audio**: Some audio formats may not work in all browsers (use OGG)
- **File size**: Larger than native JS games due to WASM runtime
- **Threading**: Limited multi-threading support

## Troubleshooting

### Game doesn't load
- Check browser console for errors
- Ensure all assets are in the project folder
- Verify audio files are OGG format

### 404 errors for pythonrc.py
- This is a known Pygbag issue with some hosts
- Try GitHub Pages or itch.io instead of Netlify

### Sound not working
- Convert audio to OGG format
- Chrome may block autoplay - user interaction required first

## Project Structure for Pygbag

Ensure your project looks like this:
```
squirrel-stash-dsah/
├── main.py          # Entry point (must be named main.py)
├── game.py
├── player.py
├── ... other .py files
└── assets/
    ├── sprites/
    ├── sounds/      # Use .ogg files
    └── ...
```

All assets must be inside the project folder to be packaged.
