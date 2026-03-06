import sys
import os

def setup_terminal():
    """Configure terminal for cross-platform UTF-8 and ASCII art support."""
    if sys.platform == "win32":
        os.system("chcp 65001 > nul 2>&1")
        os.system("")
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

GAME_TITLE   = "DUNGEONS OF AETHORIA"
GAME_VERSION = "1.0"

if getattr(sys, "frozen", False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SAVE_DIR   = os.path.join(BASE_DIR, "saves")
SAVE_FILE  = os.path.join(SAVE_DIR, "save_game.json")
PREFS_FILE = os.path.join(BASE_DIR, "prefs.json")


def load_prefs() -> dict:
    """Load user preferences (language, etc.) from disk."""
    try:
        import json
        with open(PREFS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_prefs(prefs: dict):
    """Save user preferences to disk."""
    import json
    os.makedirs(BASE_DIR, exist_ok=True)
    with open(PREFS_FILE, "w", encoding="utf-8") as f:
        json.dump(prefs, f, ensure_ascii=False, indent=2)

SCREEN_WIDTH = 62

MAX_INVENTORY_SIZE  = 20
XP_BASE             = 100
DUNGEON_ROOMS       = 10
HEAL_COST_PER_HP    = 2
FLEE_BASE_CHANCE    = 0.45

MAX_LEVEL   = 20
STAT_CAP    = 30

class Color:
    RESET   = "\033[0m"
    BOLD    = "\033[1m"
    RED     = "\033[31m"
    GREEN   = "\033[32m"
    YELLOW  = "\033[33m"
    BLUE    = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN    = "\033[36m"
    WHITE   = "\033[37m"
    GREY    = "\033[90m"

    @staticmethod
    def supported() -> bool:
        """Check if the terminal likely supports ANSI codes."""
        if sys.platform == "win32":
            return os.environ.get("TERM_PROGRAM") is not None or \
                   "WT_SESSION" in os.environ or \
                   "ANSICON" in os.environ
        return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()

USE_COLOR = Color.supported()

def clr(text: str, color: str) -> str:
    """Wrap text in color code if supported, otherwise return plain text."""
    if USE_COLOR:
        return f"{color}{text}{Color.RESET}"
    return text
