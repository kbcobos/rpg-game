import time
import sys
from config import SCREEN_WIDTH, clr, Color

BOX = {
    "tl": "╔", "tr": "╗", "bl": "╚", "br": "╝",
    "h":  "═", "v":  "║",
    "ml": "╠", "mr": "╣", "mt": "╦", "mb": "╩", "mc": "╬",
}

BOX_THIN = {
    "tl": "+", "tr": "+", "bl": "+", "br": "+",
    "h":  "-", "v":  "|",
    "ml": "+", "mr": "+",
}

try:
    BOX["tl"].encode(sys.stdout.encoding or "utf-8")
    DRAW = BOX
except (UnicodeEncodeError, TypeError):
    DRAW = BOX_THIN

TITLE_ART = r"""
  ____  _   _ _   _  ____ _____ ___  _   _ ____
 |  _ \| | | | \ | |/ ___| ____/ _ \| \ | / ___|
 | | | | | | |  \| | |  _|  _|| | | |  \| \___ \
 | |_| | |_| | |\  | |_| | |__| |_| | |\  |___) |
 |____/ \___/|_| \_|\____|_____\___/|_| \_|____/

        ___  _____    _    _____ _   _  ___  ____  ___    _
       / _ \|  ___|  / \  |_   _| | | |/ _ \|  _ \|_ _|  / \
      | | | | |_    / _ \   | | | |_| | | | | |_) || |  / _ \
      | |_| |  _|  / ___ \  | | |  _  | |_| |  _ < | | / ___ \
       \___/|_|   /_/   \_\ |_| |_| |_|\___/|_| \_\___/_/   \_\
"""

SWORD_ART = r"""
              |
             /|\
            / | \
           /  |  \
          / , | , \
         /  |||  \
            |||
            |||
            |||
           _|||_
          |_____|
"""

def horizontal_line(char: str = "═", width: int = SCREEN_WIDTH) -> str:
    return char * width

def box_top(width: int = SCREEN_WIDTH) -> str:
    return DRAW["tl"] + DRAW["h"] * (width - 2) + DRAW["tr"]

def box_bottom(width: int = SCREEN_WIDTH) -> str:
    return DRAW["bl"] + DRAW["h"] * (width - 2) + DRAW["br"]

def box_separator(width: int = SCREEN_WIDTH) -> str:
    return DRAW["ml"] + DRAW["h"] * (width - 2) + DRAW["mr"]

def box_row(text: str = "", width: int = SCREEN_WIDTH, align: str = "left") -> str:
    inner = width - 4
    plain = _strip_ansi(text)
    pad = inner - len(plain)
    if align == "center":
        lpad = pad // 2
        rpad = pad - lpad
        content = " " * lpad + text + " " * rpad
    elif align == "right":
        content = " " * pad + text
    else:
        content = text + " " * max(pad, 0)
    return f"{DRAW['v']}  {content}  {DRAW['v']}"

def box_empty(width: int = SCREEN_WIDTH) -> str:
    return box_row("", width)

def _strip_ansi(text: str) -> str:
    """Remove ANSI escape codes for accurate length measurement."""
    import re
    return re.sub(r'\033\[[0-9;]*m', '', text)

def print_title():
    """Print the full title screen."""
    clear_screen()
    print(clr(TITLE_ART, Color.YELLOW))
    print()
    print(clr("  " + "~" * 58, Color.GREY))
    print(clr('         "Not all those who wander dungeons are lost."', Color.GREY))
    print(clr("  " + "~" * 58, Color.GREY))
    print()

def print_panel(title: str, lines: list, width: int = SCREEN_WIDTH):
    """Print a decorated panel with a title and content lines."""
    print(box_top(width))
    print(box_row(clr(title.upper(), Color.YELLOW), width, align="center"))
    print(box_separator(width))
    for line in lines:
        print(box_row(line, width))
    print(box_bottom(width))

def print_section(title: str, width: int = SCREEN_WIDTH):
    """Print a section separator with a title."""
    print()
    print(box_separator(width))
    print(box_row(clr(f"  {title.upper()}", Color.CYAN), width))
    print(box_separator(width))

def hp_bar(current: int, maximum: int, length: int = 20) -> str:
    """Render a visual HP bar."""
    ratio = max(0, current) / max(1, maximum)
    filled = int(ratio * length)
    empty = length - filled

    if ratio > 0.6:
        color = Color.GREEN
    elif ratio > 0.3:
        color = Color.YELLOW
    else:
        color = Color.RED

    bar = clr("█" * filled, color) + clr("░" * empty, Color.GREY)
    return f"[{bar}] {current}/{maximum}"

def xp_bar(current: int, needed: int, length: int = 20) -> str:
    """Render a visual XP bar."""
    ratio = min(1.0, current / max(1, needed))
    filled = int(ratio * length)
    empty = length - filled
    bar = clr("▓" * filled, Color.CYAN) + clr("░" * empty, Color.GREY)
    return f"[{bar}] {current}/{needed} XP"

def print_message(text: str, style: str = "normal", delay: float = 0.0):
    """
    Print a narrative or system message.
    Styles: normal | good | bad | warning | system
    """
    prefixes = {
        "normal":  "",
        "good":    clr("  >> ", Color.GREEN),
        "bad":     clr("  !! ", Color.RED),
        "warning": clr("  ** ", Color.YELLOW),
        "system":  clr("  -- ", Color.GREY),
    }
    prefix = prefixes.get(style, "")
    print(f"{prefix}{text}")
    if delay:
        time.sleep(delay)

def typewriter(text: str, speed: float = 0.018):
    """Print text character by character for dramatic effect."""
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(speed)
    print()

def clear_screen():
    """Clear terminal cross-platform."""
    os.system("cls" if sys.platform == "win32" else "clear")

def press_enter(prompt: str = "  [ Presioná ENTER para continuar ]"):
    print()
    print(clr(prompt, Color.GREY))
    input()

def prompt_input(question: str) -> str:
    """Styled input prompt."""
    print()
    return input(clr(f"  >> {question}: ", Color.CYAN)).strip()

def prompt_choice(options: list, prompt: str = "Tu eleccion") -> int:
    """
    Display a numbered menu and return the validated choice index (0-based).
    options: list of strings
    """
    print()
    for i, option in enumerate(options, 1):
        print(f"  {clr(str(i), Color.YELLOW)}.  {option}")
    print()
    while True:
        raw = input(clr(f"  > {prompt} [1-{len(options)}]: ", Color.CYAN)).strip()
        if raw.isdigit():
            choice = int(raw)
            if 1 <= choice <= len(options):
                return choice - 1
        print(clr("  Opción inválida. De nuevo, dale.", Color.RED))

def print_ascii_enemy(name: str):
    """Print simple ASCII art for enemy type."""
    key = name.lower().split()[0]
    lines = {
        "goblin":   ["    .-.", "   (o o)  GOBLIN", "   | O |", "   `---'"],
        "orc":      ["   _____", "  /     \\  ORC", " | () () |", "  \\  ^  /", "   |||||"],
        "skeleton": ["   _____", "  |     |  SKELETON", "  | 0 0 |", "   \\___/", "  /|   |\\"],
        "dragon":   ["      __   _", "   _  \\_/ \\   DRAGON", "  / ` |    \\___/", " /    `-.  /", " |      | |"],
        "demon":    ["   /\\  /\\", "  (  *  )  DEMON", "  |-----|", "  / === \\"],
        "witch":    ["   /\\_/\\", "  ( o.o )  WITCH", "   > ^ <", "  /|   |\\"],
        "vampire":  ["  __|__", " (     )  VAMPIRE", " |v   v|", "  \\___/"],
    }
    art_lines = lines.get(key, ["  [?????]", "  [" + name.upper() + "]"])
    print(clr("\n".join(art_lines), Color.RED))
    print()


import os
