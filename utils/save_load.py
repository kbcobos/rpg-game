import json
import os
from config import SAVE_FILE, SAVE_DIR


def ensure_save_dir():
    """Create saves directory if it doesn't exist."""
    os.makedirs(SAVE_DIR, exist_ok=True)


def save_game(player_data: dict) -> bool:
    """
    Save the current game state to JSON.
    Returns True on success, False on failure.
    """
    ensure_save_dir()
    try:
        with open(SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump(player_data, f, indent=2, ensure_ascii=False)
        return True
    except (IOError, OSError) as e:
        print(f"  [ERROR] Could not save game: {e}")
        return False


def load_game() -> dict | None:
    """
    Load game state from JSON.
    Returns the save dict on success, None if no save exists or on error.
    """
    if not os.path.exists(SAVE_FILE):
        return None
    try:
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (IOError, OSError, json.JSONDecodeError) as e:
        print(f"  [ERROR] Could not load save: {e}")
        return None


def save_exists() -> bool:
    """Check if a save file exists."""
    return os.path.exists(SAVE_FILE)


def delete_save() -> bool:
    """Delete the save file (used when starting a new game over existing)."""
    if os.path.exists(SAVE_FILE):
        try:
            os.remove(SAVE_FILE)
            return True
        except OSError:
            return False
    return True
