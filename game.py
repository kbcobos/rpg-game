import sys
import time

from config import GAME_TITLE, GAME_VERSION, setup_terminal, clr, Color
from entities.player import Player
from data.classes import CLASSES, ClassTemplate
from systems.dungeon import run_dungeon_floor
from systems.inventory import show_inventory
from utils.display import (
    print_title, print_panel, print_message, print_section,
    box_top, box_bottom, box_row, box_separator,
    hp_bar, xp_bar, prompt_choice, prompt_input, press_enter,
    typewriter, clear_screen, clr, Color, SCREEN_WIDTH
)
from utils.save_load import save_game, load_game, save_exists, delete_save


def start_game():
    """Main entry point — initialize terminal and show title screen."""
    setup_terminal()
    print_title()

    while True:
        result = _main_menu()
        if result == "quit":
            _quit_game()
            break


def _main_menu() -> str:
    """Show the main menu and handle selection."""
    has_save = save_exists()

    options = []
    if has_save:
        options.append("Continuar partida guardada")
    options.append("Nueva partida")
    options.append("Creditos")
    options.append("Salir")

    print(box_top())
    print(box_row(clr("MENÚ PRINCIPAL", Color.YELLOW), align="center"))
    print(box_bottom())

    choice = prompt_choice(options, "¿Qué hacés?")
    label = options[choice]

    if label == "Continuar partida guardada":
        return _load_and_play()
    elif label == "Nueva partida":
        return _new_game()
    elif label == "Creditos":
        _show_credits()
        return "menu"
    elif label == "Salir":
        return "quit"

    return "menu"


def _new_game() -> str:
    """Handle new game creation, overwriting save if needed."""
    if save_exists():
        options = ["Sí, empezar de nuevo (perder todo)", "No, volver al menú"]
        choice = prompt_choice(options, "Hay una partida guardada. ¿La borramos y empezamos de cero?")
        if choice == 1:
            return "menu"
        delete_save()

    player = _character_creation()
    if player is None:
        return "menu"

    clear_screen()
    print()
    print(clr("  " + "═" * 58, Color.GREY))
    typewriter("", 0.01)
    typewriter("  Las puertas del calabozo más profundo de Aethoria se cierran detrás tuyo.", 0.018)
    typewriter("  No hay antorcha. No hay mapa. Clásico.", 0.018)
    typewriter("  Solo hay oscuridad y lo que sea que se mueve adentro.", 0.018)
    typewriter("", 0.01)
    typewriter(f"  Sos {player.name}, {player.char_class.name}.", 0.018)
    typewriter("  Viniste buscando gloria, tesoros, o venganza. O simplemente no sabías adónde más ir.", 0.018)
    typewriter("  A la mazmorra le chupa un huevo cuál de las tres. Igual te va a comer.", 0.018)
    print()
    print(clr("  " + "═" * 58, Color.GREY))
    press_enter("  [ Tu historia arranca ahora. Suerte, que la vas a necesitar. ]")

    return _play_game(player)


def _character_creation() -> Player | None:
    """Interactive character creation. Returns a Player or None if cancelled."""
    clear_screen()

    print(box_top())
    print(box_row(clr("CREACIÓN DE PERSONAJE", Color.YELLOW), align="center"))
    print(box_bottom())

    while True:
        name = prompt_input("Nombre de tu personaje (el que van a poner en la lápida)")
        if 2 <= len(name) <= 20:
            break
        print_message("El nombre tiene que tener entre 2 y 20 caracteres. No es mucho pedir.", "warning")

    class_list = list(CLASSES.values())
    clear_screen()
    _draw_class_selection(class_list)

    class_options = [f"{ct.name:12s} — {ct.description}" for ct in class_list]
    class_options.append("-- Cancelar --")

    choice = prompt_choice(class_options, "¿Cuál es tu clase? (elegí bien)")
    if choice == len(class_options) - 1:
        return None

    selected_class = class_list[choice]

    clear_screen()
    _draw_class_details(selected_class)
    confirm_options = ["Sí, quiero esta clase", "Mmm no, mejor elijo otra"]
    confirm = prompt_choice(confirm_options, "¿Confirmamos esta clase?")
    if confirm == 1:
        return _character_creation()

    player = Player(name=name, class_template=selected_class)
    print()
    print_message(f"  {name} el {selected_class.name} da el primer paso hacia la leyenda. O hacia el desastre. Probablemente los dos.", "good")
    time.sleep(1.0)
    return player


def _draw_class_selection(class_list: list):
    """Draw a summary table of all available classes."""
    print(box_top())
    print(box_row(clr("CLASES DISPONIBLES — elegí bien, che", Color.YELLOW), align="center"))
    print(box_separator())
    print(box_row(f"  {'CLASE':<14} {'HP':>4} {'MP':>4} {'Principal':<10} {'Descripcion'}"))
    print(box_separator())
    for ct in class_list:
        stat_label = ct.primary_stat.upper()
        print(box_row(
            f"  {clr(ct.name, Color.CYAN):<23} "
            f"{ct.base_hp:>4} {ct.base_mp:>4}  "
            f"{stat_label:<10} {ct.description[:22]}"
        ))
    print(box_bottom())


def _draw_class_details(ct: ClassTemplate):
    """Draw full class info panel for confirmation screen."""
    print(box_top())
    print(box_row(clr(f"  {ct.name.upper()}", Color.YELLOW)))
    print(box_separator())
    print(box_row(f"  {ct.lore[:55]}"))
    if len(ct.lore) > 55:
        print(box_row(f"  {ct.lore[55:110]}"))
    print(box_separator())
    print(box_row(clr("  ESTADISTICAS BASE", Color.CYAN)))
    print(box_row(
        f"  HP:{ct.base_hp:>4}  MP:{ct.base_mp:>4}  "
        f"STR:{ct.base_str:>3}  DEX:{ct.base_dex:>3}  INT:{ct.base_int:>3}"
    ))
    print(box_row(
        f"  WIS:{ct.base_wis:>3}  CHA:{ct.base_cha:>3}  CON:{ct.base_con:>3}  "
        f"Stat principal: {ct.primary_stat.upper()}"
    ))
    print(box_separator())
    print(box_row(clr("  HABILIDADES", Color.CYAN)))
    for ability in ct.abilities:
        cost_str = clr(f"[{ability.mp_cost}MP]", Color.BLUE)
        print(box_row(f"  * {ability.name}  {cost_str}"))
        print(box_row(f"    {ability.description}"))
    print(box_separator())
    print(box_row(f"  Arma inicial: {ct.starting_weapon}"))
    print(box_row(f"  Armadura inicial: {ct.starting_armor}"))
    print(box_bottom())


def _load_and_play() -> str:
    """Load a saved game and resume."""
    data = load_game()
    if data is None:
        print_message("No se pudo cargar la partida. Fue, fue.", "warning")
        press_enter()
        return "menu"

    player = Player.from_dict(data)
    print_message(f"Partida cargada: {player.name} el {player.char_class.name} nivel {player.level}. Seguimos.", "good")
    press_enter()
    return _play_game(player)


def _play_game(player: Player) -> str:
    """
    Main game loop: navigate dungeon floors until victory, defeat, or quit.
    """
    while True:
        action = _camp_menu(player)

        if action == "quit":
            save_game(player.to_dict())
            print_message("Partida guardada. Hasta la próxima, aventurero. Descansá.", "system")
            press_enter()
            return "quit"

        if action == "enter_dungeon":
            result = run_dungeon_floor(player)

            if result == "game_over":
                _game_over_screen(player)
                delete_save()
                return "menu"

            elif result == "next_floor":
                player.heal(int(player.max_hp * 0.25))
                player.restore_mp(int(player.max_mp * 0.25))
                save_game(player.to_dict())

                if player.dungeon_floor > 10:
                    _victory_screen(player)
                    delete_save()
                    return "menu"


def _camp_menu(player: Player) -> str:
    """Between-floor hub. Returns 'enter_dungeon' | 'quit'."""
    clear_screen()
    _draw_camp(player)

    options = [
        f"Bajar al Piso {player.dungeon_floor} (sin vuelta atrás)",
        "Ver Inventario",
        "Ver Stats",
        "Guardar y salir (por ahora)",
    ]

    choice = prompt_choice(options, "Que deseas hacer")

    if choice == 0:
        return "enter_dungeon"
    elif choice == 1:
        show_inventory(player)
        return _camp_menu(player)
    elif choice == 2:
        _show_stats(player)
        return _camp_menu(player)
    elif choice == 3:
        return "quit"

    return "enter_dungeon"


def _draw_camp(player: Player):
    """Draw the camp/hub screen."""
    print(box_top())
    print(box_row(clr("CAMPAMENTO — ENTRADA A LA MAZMORRA (todavía estás a tiempo de irte)", Color.YELLOW), align="center"))
    print(box_separator())
    print(box_row(f"  Aventurero  : {clr(player.name, Color.CYAN)}"))
    print(box_row(f"  Clase      : {player.char_class.name}  |  Nivel: {clr(str(player.level), Color.YELLOW)}"))
    print(box_separator())
    print(box_row(f"  HP  : {hp_bar(player.current_hp, player.max_hp, 20)}"))
    print(box_row(f"  MP  : {player.current_mp}/{player.max_mp}"))
    print(box_row(f"  XP  : {xp_bar(player.xp, player.xp_to_next, 20)}"))
    print(box_separator())
    print(box_row(f"  Oro      : {clr(str(player.gold), Color.YELLOW)} gp"))
    print(box_row(f"  Enemigos : {player.kills}  |  Pisos: {player.floors_cleared}"))
    print(box_row(f"  Próximo   : Piso {player.dungeon_floor} — ¿seguro?"))
    print(box_bottom())


def _show_stats(player: Player):
    """Display full character stats screen."""
    clear_screen()
    print(box_top())
    print(box_row(clr(f"  {player.name.upper()} — {player.char_class.name.upper()}", Color.YELLOW)))
    print(box_separator())
    print(box_row(f"  Nivel     : {player.level}  |  XP: {player.xp}/{player.xp_to_next}"))
    print(box_row(f"  HP        : {player.current_hp}/{player.max_hp}"))
    print(box_row(f"  MP        : {player.current_mp}/{player.max_mp}"))
    print(box_separator())
    print(box_row(clr("  ATRIBUTOS", Color.CYAN)))
    print(box_row(f"  FUE (STR) : {player.strength:>3}   DES (DEX) : {player.dexterity:>3}"))
    print(box_row(f"  INT (INT) : {player.intelligence:>3}   SAB (WIS) : {player.wisdom:>3}"))
    print(box_row(f"  CAR (CHA) : {player.charisma:>3}   CON (CON) : {player.constitution:>3}"))
    print(box_separator())
    print(box_row(clr("  COMBATE", Color.CYAN)))
    print(box_row(f"  Ataque    : {player.effective_attack}"))
    print(box_row(f"  Defensa   : {player.effective_defense}"))
    print(box_separator())
    print(box_row(clr("  EQUIPO", Color.CYAN)))
    w = player.equipped_weapon.name if player.equipped_weapon else "Ninguno"
    a = player.equipped_armor.name  if player.equipped_armor  else "Ninguno"
    r = player.equipped_ring.name   if player.equipped_ring   else "Ninguno"
    print(box_row(f"  Arma      : {w}"))
    print(box_row(f"  Armadura  : {a}"))
    print(box_row(f"  Anillo    : {r}"))
    print(box_separator())
    print(box_row(clr("  HABILIDADES", Color.CYAN)))
    for ab in player.char_class.abilities:
        cd = player.cooldowns.get(ab.name, 0)
        cd_str = clr(f" [CD:{cd}]", Color.RED) if cd > 0 else clr(" [Listo]", Color.GREEN)
        print(box_row(f"  * {ab.name}  [{ab.mp_cost}MP]{cd_str}"))
        print(box_row(f"    {ab.description}"))
    print(box_separator())
    print(box_row(f"  Oro: {player.gold}gp  |  Bajas: {player.kills}  |  Pisos: {player.floors_cleared}"))
    print(box_bottom())
    press_enter()


def _victory_screen(player: Player):
    """Show the victory screen."""
    clear_screen()
    print()
    print(clr("  " + "═" * 58, Color.YELLOW))
    print()
    typewriter("         V I C T O R I A  —  LO LOGRASTE", 0.05)
    print()
    print(clr("  " + "═" * 58, Color.YELLOW))
    print()
    typewriter("  Conquistaste los Calabozos de Aethoria. En serio. Nadie lo esperaba.", 0.018)
    typewriter("  La oscuridad final fue derrotada. Por vos. Que clase de loco.", 0.018)
    typewriter("  Tu nombre va a quedar grabado en piedra. O en un grupo de WhatsApp. Es lo mismo.", 0.018)
    print()
    print(box_top(44))
    print(box_row(clr("  ESTADÍSTICAS FINALES", Color.YELLOW), width=44))
    print(box_separator(44))
    print(box_row(f"  Nombre : {player.name}", width=44))
    print(box_row(f"  Clase  : {player.char_class.name}  Nivel {player.level}", width=44))
    print(box_row(f"  Bajas  : {player.kills}", width=44))
    print(box_row(f"  Oro    : {player.gold} gp — que bien gastaste", width=44))
    print(box_bottom(44))
    press_enter("  [ Una leyenda nació. Vos. ]")


def _game_over_screen(player: Player):
    """Show the game over screen."""
    clear_screen()
    print()
    print(clr("  " + "═" * 58, Color.RED))
    print()
    typewriter("         F I N   D E L   J U E G O  —  hasta la próxima", 0.05)
    print()
    print(clr("  " + "═" * 58, Color.RED))
    print()
    typewriter("  La mazmorra se comió otro gil. Eso es todo.", 0.018)
    typewriter("  Tus huesos se quedan acá con los de los demás. Buena compañía.", 0.018)
    print()
    print_message(f"  {player.name} el {player.char_class.name} — Nivel {player.level}", "system")
    print_message(f"  Enemigos eliminados: {player.kills}  |  Pisos completados: {player.floors_cleared}", "system")
    print_message(f"  Oro que te llevaste a la tumba: {player.gold} gp. Inútil, pero tuyo.", "system")
    press_enter()


def _show_credits():
    """Show credits screen."""
    clear_screen()
    print_panel("DUNGEONS OF AETHORIA — Créditos", [
        "",
        f"  Version {GAME_VERSION}",
        "",
        "  Creado con Python 3.11+ y mucho mate",
        "  Inspirado en los RPGs de texto de los años 80",
        "  y los reglamentos originales de Dungeons & Dragons",
        "",
        "  Gracias por jugar. En serio.",
        "",
        "  'No todos los que vagan por mazmorras están perdidos.'",
        "  'La mayoría sí. Completamente.'",
        "",
    ])
    press_enter()


def _quit_game():
    """Exit message."""
    clear_screen()
    print()
    typewriter("  La antorcha se apaga. La mazmorra espera. Siempre espera.", 0.020)
    typewriter("  Hasta la próxima, aventurero. Cuando quieras volvés.", 0.020)
    print()
    time.sleep(0.5)
