"""
Save/load system for Squirrel Yarn game.
Persists high scores and furthest distance between sessions.
"""

import json
import os
from typing import Dict, Any

# Save file location
SAVE_FILE = "squirrel_yarn_save.json"


def get_save_path() -> str:
    """Get the full path to the save file."""
    # Save in the same directory as the game
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), SAVE_FILE)


def load_save() -> Dict[str, Any]:
    """Load save data from file. Returns defaults if no save exists."""
    default_save = {
        "high_score": 0,
        "best_distance": 0,
        "total_yarn_collected": 0,
        "total_runs": 0,
    }

    save_path = get_save_path()

    if not os.path.exists(save_path):
        return default_save

    try:
        with open(save_path, "r") as f:
            data = json.load(f)
            # Merge with defaults to handle missing keys
            return {**default_save, **data}
    except (json.JSONDecodeError, IOError):
        return default_save


def save_game(high_score: int, best_distance: int,
              total_yarn: int = 0, total_runs: int = 0) -> bool:
    """Save game data to file. Returns True on success."""
    data = {
        "high_score": high_score,
        "best_distance": best_distance,
        "total_yarn_collected": total_yarn,
        "total_runs": total_runs,
    }

    save_path = get_save_path()

    try:
        with open(save_path, "w") as f:
            json.dump(data, f, indent=2)
        return True
    except IOError:
        return False


def update_high_score(new_score: int) -> bool:
    """Update high score if new score is higher. Returns True if updated."""
    data = load_save()

    if new_score > data["high_score"]:
        data["high_score"] = new_score
        save_game(
            data["high_score"],
            data["best_distance"],
            data.get("total_yarn_collected", 0),
            data.get("total_runs", 0)
        )
        return True
    return False


def update_best_distance(new_distance: int) -> bool:
    """Update best distance if new distance is further. Returns True if updated."""
    data = load_save()

    if new_distance > data["best_distance"]:
        data["best_distance"] = new_distance
        save_game(
            data["high_score"],
            data["best_distance"],
            data.get("total_yarn_collected", 0),
            data.get("total_runs", 0)
        )
        return True
    return False


def get_high_score() -> int:
    """Get the current high score."""
    return load_save()["high_score"]


def get_best_distance() -> int:
    """Get the current best distance."""
    return load_save()["best_distance"]


def increment_runs() -> None:
    """Increment the total runs counter."""
    data = load_save()
    data["total_runs"] = data.get("total_runs", 0) + 1
    save_game(
        data["high_score"],
        data["best_distance"],
        data.get("total_yarn_collected", 0),
        data["total_runs"]
    )


def add_yarn_to_total(amount: int) -> None:
    """Add yarn to the lifetime total."""
    data = load_save()
    data["total_yarn_collected"] = data.get("total_yarn_collected", 0) + amount
    save_game(
        data["high_score"],
        data["best_distance"],
        data["total_yarn_collected"],
        data.get("total_runs", 0)
    )


def get_stats() -> Dict[str, Any]:
    """Get all saved statistics."""
    return load_save()


def reset_save() -> None:
    """Delete save file and reset all progress."""
    save_path = get_save_path()
    if os.path.exists(save_path):
        os.remove(save_path)
