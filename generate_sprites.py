#!/usr/bin/env python3
"""
Generate placeholder sprite assets for Squirrel Yarn game.
Creates simple colored shapes using PIL/Pillow for development use.
"""

from PIL import Image, ImageDraw
import os

# Output directory
SPRITES_DIR = "/Users/nervous/Library/CloudStorage/Dropbox/Github/squirrel-stash-dsah/assets/sprites"

def create_squirrel(filename, size=(64, 64)):
    """Create squirrel sprite - orange/brown rectangle with yellow sweater"""
    img = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Brown body
    draw.rectangle([8, 8, 56, 56], fill=(205, 133, 63, 255))

    # Yellow sweater in middle
    draw.rectangle([12, 24, 52, 44], fill=(255, 215, 0, 255))

    # Darker outline
    draw.rectangle([8, 8, 56, 56], outline=(139, 90, 43, 255), width=2)

    img.save(os.path.join(SPRITES_DIR, filename))
    print(f"Created: {filename}")

def create_platform(filename, size=(128, 32)):
    """Create tree platform - brown rectangle"""
    img = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Brown platform
    draw.rectangle([0, 0, 127, 31], fill=(139, 90, 43, 255))

    # Wood grain lines
    for i in range(0, 128, 16):
        draw.line([i, 0, i, 31], fill=(101, 67, 33, 255), width=1)

    # Darker outline
    draw.rectangle([0, 0, 127, 31], outline=(101, 67, 33, 255), width=2)

    img.save(os.path.join(SPRITES_DIR, filename))
    print(f"Created: {filename}")

def create_bush(filename, size=(64, 48)):
    """Create bush obstacle - green oval/rounded shape"""
    img = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Green oval bush
    draw.ellipse([4, 4, 60, 44], fill=(34, 139, 34, 255))

    # Darker green outline
    draw.ellipse([4, 4, 60, 44], outline=(0, 100, 0, 255), width=2)

    # Some texture circles
    draw.ellipse([12, 10, 28, 26], fill=(50, 160, 50, 255))
    draw.ellipse([36, 14, 52, 30], fill=(50, 160, 50, 255))
    draw.ellipse([20, 24, 36, 40], fill=(50, 160, 50, 255))

    img.save(os.path.join(SPRITES_DIR, filename))
    print(f"Created: {filename}")

def create_ground_tile(filename, size=(64, 64)):
    """Create ground tile - green/brown gradient"""
    img = Image.new('RGBA', size, (0, 0, 0, 0))
    pixels = img.load()

    # Create vertical gradient from green (top) to brown (bottom)
    for y in range(size[1]):
        ratio = y / size[1]
        r = int(34 * (1 - ratio) + 139 * ratio)
        g = int(139 * (1 - ratio) + 90 * ratio)
        b = int(34 * (1 - ratio) + 43 * ratio)

        for x in range(size[0]):
            pixels[x, y] = (r, g, b, 255)

    # Add some texture dots
    draw = ImageDraw.Draw(img)
    for i in range(10):
        x = (i * 13) % 60 + 2
        y = (i * 17) % 60 + 2
        draw.ellipse([x, y, x+3, y+3], fill=(80, 60, 40, 255))

    img.save(os.path.join(SPRITES_DIR, filename))
    print(f"Created: {filename}")

def create_background_far(filename, size=(800, 600)):
    """Create far background - light blue sky"""
    img = Image.new('RGBA', size, (0, 0, 0, 0))
    pixels = img.load()

    # Gradient sky from lighter blue at top to slightly darker at bottom
    for y in range(size[1]):
        ratio = y / size[1]
        r = int(135 + (ratio * 20))
        g = int(206 - (ratio * 20))
        b = int(235 - (ratio * 15))

        for x in range(size[0]):
            pixels[x, y] = (r, g, b, 255)

    img.save(os.path.join(SPRITES_DIR, filename))
    print(f"Created: {filename}")

def create_background_mid(filename, size=(800, 600)):
    """Create mid background - distant trees silhouette (dark green)"""
    img = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Dark green distant tree silhouettes
    tree_color = (0, 100, 0, 180)

    # Draw several triangular tree shapes
    for i in range(8):
        x_offset = i * 120 - 50
        y_base = 400 + (i % 3) * 30

        # Triangle tree
        draw.polygon([
            (x_offset + 60, y_base - 150),
            (x_offset, y_base),
            (x_offset + 120, y_base)
        ], fill=tree_color)

        # Trunk
        draw.rectangle([x_offset + 50, y_base, x_offset + 70, y_base + 50],
                      fill=(101, 67, 33, 180))

    img.save(os.path.join(SPRITES_DIR, filename))
    print(f"Created: {filename}")

def create_background_near(filename, size=(800, 600)):
    """Create near background - closer tree silhouettes"""
    img = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Lighter green closer trees
    tree_color = (34, 139, 34, 150)

    # Draw larger tree shapes on sides
    for i in range(4):
        x_offset = i * 250 - 80
        y_base = 450

        # Larger triangle tree
        draw.polygon([
            (x_offset + 100, y_base - 200),
            (x_offset, y_base),
            (x_offset + 200, y_base)
        ], fill=tree_color)

        # Trunk
        draw.rectangle([x_offset + 85, y_base, x_offset + 115, y_base + 80],
                      fill=(139, 90, 43, 150))

    img.save(os.path.join(SPRITES_DIR, filename))
    print(f"Created: {filename}")

def create_yarn(filename, color, size=(32, 32)):
    """Create yarn skein sprite"""
    img = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Main yarn ball (ellipse)
    draw.ellipse([4, 6, 28, 26], fill=color)

    # Darker outline
    darker = tuple(max(0, c - 40) for c in color[:3]) + (255,)
    draw.ellipse([4, 6, 28, 26], outline=darker, width=2)

    # Yarn strands (curved lines)
    draw.arc([8, 10, 24, 22], 30, 150, fill=darker, width=2)
    draw.arc([10, 12, 22, 20], 210, 330, fill=darker, width=2)

    img.save(os.path.join(SPRITES_DIR, filename))
    print(f"Created: {filename}")

def create_rainbow_yarn(filename, size=(32, 32)):
    """Create special rainbow yarn"""
    img = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Create segments with different colors
    colors = [
        (255, 0, 0),      # Red
        (255, 165, 0),    # Orange
        (255, 255, 0),    # Yellow
        (0, 255, 0),      # Green
        (0, 0, 255),      # Blue
        (128, 0, 128),    # Purple
    ]

    # Draw pie slices
    for i, color in enumerate(colors):
        start_angle = i * 60
        end_angle = (i + 1) * 60
        draw.pieslice([4, 6, 28, 26], start_angle, end_angle, fill=color)

    # Black outline
    draw.ellipse([4, 6, 28, 26], outline=(0, 0, 0, 255), width=2)

    img.save(os.path.join(SPRITES_DIR, filename))
    print(f"Created: {filename}")

def main():
    """Generate all sprite assets"""
    print("=" * 50)
    print("Generating Squirrel Yarn Placeholder Sprites")
    print("=" * 50)

    # Create main sprites
    print("\n[Main Sprites]")
    create_squirrel('squirrel.png')
    create_platform('platform.png')
    create_bush('bush.png')
    create_ground_tile('ground.png')

    # Create backgrounds
    print("\n[Background Layers]")
    create_background_far('bg_far.png')
    create_background_mid('bg_mid.png')
    create_background_near('bg_near.png')

    # Create yarn sprites
    print("\n[Yarn - Basic Tier]")
    create_yarn('yarn_red.png', (255, 0, 0, 255))
    create_yarn('yarn_green.png', (0, 255, 0, 255))
    create_yarn('yarn_blue.png', (0, 0, 255, 255))

    print("\n[Yarn - Mid Tier]")
    create_yarn('yarn_cyan.png', (0, 255, 255, 255))
    create_yarn('yarn_magenta.png', (255, 0, 255, 255))
    create_yarn('yarn_yellow.png', (255, 255, 0, 255))
    create_yarn('yarn_black.png', (50, 50, 50, 255))

    print("\n[Yarn - Late Tier]")
    create_yarn('yarn_orange.png', (255, 165, 0, 255))
    create_yarn('yarn_purple.png', (128, 0, 128, 255))
    create_yarn('yarn_lime.png', (191, 255, 0, 255))
    create_yarn('yarn_teal.png', (0, 128, 128, 255))
    create_yarn('yarn_pink.png', (255, 192, 203, 255))
    create_yarn('yarn_brown.png', (139, 69, 19, 255))

    print("\n[Yarn - Rare]")
    create_rainbow_yarn('yarn_rainbow.png')

    print("\n" + "=" * 50)
    print("All sprites generated successfully!")
    print(f"Location: {SPRITES_DIR}")
    print("=" * 50)

if __name__ == '__main__':
    main()
