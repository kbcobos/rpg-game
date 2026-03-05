import sys
import time

from config import GAME_TITLE, GAME_VERSION, setup_terminal, clr, Color, load_prefs, save_prefs
from utils.lang import t, set_lang, get_lang, AVAILABLE_LANGUAGES
from entities.player import Player
from data.classes import CLASSES, ClassTemplate
from systems.dungeon import run_dungeon_floor
from systems.inventory import show_inventory
from systems.shop import show_shop
from systems.skilltree import show_skill_tree, get_available_to_unlock
from systems.quests import show_quests
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
    prefs = load_prefs()
    if "lang" in prefs:
        set_lang(prefs["lang"])
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
        options.append(t("continue_game"))
    options.append(t("new_game"))
    options.append(t("credits"))
    options.append(t("change_language"))
    options.append(t("quit"))

    print(box_top())
    print(box_row(clr(t("main_menu_title"), Color.YELLOW), align="center"))
    print(box_bottom())

    choice = prompt_choice(options, t("main_menu_prompt"))
    label = options[choice]

    if label == t("continue_game"):
        return _load_and_play()
    elif label == t("new_game"):
        return _new_game()
    elif label == t("credits"):
        _show_credits()
        return "menu"
    elif label == t("change_language"):
        _language_selector()
        return "menu"
    elif label == t("quit"):
        return "quit"

    return "menu"


def _language_selector():
    """Show language selection screen."""
    print()
    print(box_top())
    print(box_row(clr(t("lang_title"), Color.YELLOW), align="center"))
    print(box_bottom())
    options = [t("lang_es"), t("lang_en")]
    choice = prompt_choice(options, t("lang_prompt"))
    lang = "es" if choice == 0 else "en"
    set_lang(lang)
    save_prefs({"lang": lang})
    print_message(t("lang_changed"), "good")
    press_enter()


def _new_game() -> str:
    """Handle new game creation, overwriting save if needed."""
    if save_exists():
        options = [t("overwrite_yes"), t("overwrite_no")]
        choice = prompt_choice(options, t("overwrite_save"))
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
    typewriter(f"  {t('opening_1')}", 0.018)
    typewriter(f"  {t('opening_2')}", 0.018)
    typewriter(f"  {t('opening_3')}", 0.018)
    typewriter("", 0.01)
    typewriter(f"  {t('opening_4', name=player.name, class_name=player.char_class.name)}", 0.018)
    typewriter(f"  {t('opening_5')}", 0.018)
    typewriter(f"  {t('opening_6')}", 0.018)
    print()
    print(clr("  " + "═" * 58, Color.GREY))
    press_enter(f"  {t('opening_press')}")

    return _play_game(player)


def _character_creation() -> Player | None:
    """Interactive character creation. Returns a Player or None if cancelled."""
    clear_screen()

    print(box_top())
    print(box_row(clr(t("char_creation_title"), Color.YELLOW), align="center"))
    print(box_bottom())

    while True:
        name = prompt_input(t("enter_name"))
        if 2 <= len(name) <= 20:
            break
        print_message("El nombre tiene que tener entre 2 y 20 caracteres. No es mucho pedir.", "warning")

    class_list = list(CLASSES.values())
    clear_screen()
    _draw_class_selection(class_list)

    class_options = [f"{ct.name:12s} — {t(ct.description)}" for ct in class_list]
    class_options.append("-- Cancelar --")

    choice = prompt_choice(class_options, t("class_select_prompt"))
    if choice == len(class_options) - 1:
        return None

    selected_class = class_list[choice]

    clear_screen()
    _draw_class_details(selected_class)
    confirm_options = [t("class_confirm_yes"), t("class_confirm_no")]
    confirm = prompt_choice(confirm_options, t("class_confirm_prompt"))
    if confirm == 1:
        return _character_creation()

    player = Player(name=name, class_template=selected_class)
    print()
    print_message(f"  {t("char_ready", name=name, class_name=selected_class.name)}", "good")
    time.sleep(1.0)
    return player


def _draw_class_selection(class_list: list):
    """Draw a summary table of all available classes."""
    print(box_top())
    print(box_row(clr(t("classes_title"), Color.YELLOW), align="center"))
    print(box_separator())
    print(box_row(f"  {t('ui_class_label'):<14} {t('ui_hp_label'):>4} {t('ui_mp_label'):>4} {t('ui_principal_label'):<10} {t('ui_desc_label')}"))
    print(box_separator())
    for ct in class_list:
        stat_label = ct.primary_stat.upper()
        print(box_row(
            f"  {clr(ct.name, Color.CYAN):<23} "
            f"{ct.base_hp:>4} {ct.base_mp:>4}  "
            f"{stat_label:<10} {t(ct.description)[:22]}"
        ))
    print(box_bottom())


def _draw_class_details(ct: ClassTemplate):
    """Draw full class info panel for confirmation screen."""
    print(box_top())
    print(box_row(clr(f"  {ct.name.upper()}", Color.YELLOW)))
    print(box_separator())
    lore_text = t(ct.lore)
    print(box_row(f"  {lore_text[:55]}"))
    if len(lore_text) > 55:
        print(box_row(f"  {lore_text[55:110]}"))
    if len(lore_text) > 110:
        print(box_row(f"  {lore_text[110:165]}"))
    print(box_separator())
    print(box_row(clr(t("ui_base_stats"), Color.CYAN)))
    print(box_row(
        f"  HP:{ct.base_hp:>4}  MP:{ct.base_mp:>4}  "
        f"STR:{ct.base_str:>3}  DEX:{ct.base_dex:>3}  INT:{ct.base_int:>3}"
    ))
    print(box_row(
        f"  WIS:{ct.base_wis:>3}  CHA:{ct.base_cha:>3}  CON:{ct.base_con:>3}  "
        f"{t('ui_stat_primary')}: {ct.primary_stat.upper()}"
    ))
    print(box_separator())
    print(box_row(clr(t("ui_abilities"), Color.CYAN)))
    for ability in ct.abilities:
        cost_str = clr(f"[{ability.mp_cost}MP]", Color.BLUE)
        print(box_row(f"  * {t(ability.name)}  {cost_str}"))
        print(box_row(f"    {t(ability.description)}"))
    print(box_separator())
    print(box_row(f"{t('ui_start_weapon')}: {ct.starting_weapon}"))
    print(box_row(f"{t('ui_start_armor')}: {ct.starting_armor}"))
    print(box_bottom())


def _load_and_play() -> str:
    """Load a saved game and resume."""
    data = load_game()
    if data is None:
        print_message(t("load_failed"), "warning")
        press_enter()
        return "menu"

    player = Player.from_dict(data)
    print_message(t("game_loaded", name=player.name, class_name=player.char_class.name, level=player.level), "good")
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
            print_message(t("saved_quit"), "system")
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

    available_skills = get_available_to_unlock(
        player.char_class.key, player.unlocked_skills, player.level)
    skill_notif = clr(" [NUEVO!]", Color.YELLOW) if available_skills else ""
    quest_count = len(player.quest_manager.active)
    quest_notif = clr(f" [{quest_count}]", Color.CYAN) if quest_count else ""

    options = [
        t("camp_enter", floor=player.dungeon_floor),
        t("camp_inventory"),
        t("camp_stats"),
        f"{t('camp_skilltree')}{skill_notif}",
        t("camp_shop"),
        f"{t('camp_quests')}{quest_notif}",
        t("camp_save_quit"),
    ]

    choice = prompt_choice(options, t("camp_prompt"))

    if choice == 0:
        return "enter_dungeon"
    elif choice == 1:
        show_inventory(player)
        return _camp_menu(player)
    elif choice == 2:
        _show_stats(player)
        return _camp_menu(player)
    elif choice == 3:
        show_skill_tree(player)
        return _camp_menu(player)
    elif choice == 4:
        show_shop(player)
        return _camp_menu(player)
    elif choice == 5:
        show_quests(player)
        return _camp_menu(player)
    elif choice == 6:
        return "quit"

    return "enter_dungeon"


def _draw_camp(player: Player):
    """Draw the camp/hub screen."""
    print(box_top())
    print(box_row(clr(t("camp_title"), Color.YELLOW), align="center"))
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
    print(box_row(f"  {t("camp_next_floor", floor=player.dungeon_floor)}"))
    print(box_separator())
    skills_av = get_available_to_unlock(
        player.char_class.key, player.unlocked_skills, player.level)
    skill_str = (clr(t("camp_skills_available", n=len(skills_av)), Color.YELLOW)
                 if skills_av else clr(t("camp_skills_none"), Color.GREY))
    quest_str = clr(t("camp_quests_active", n=len(player.quest_manager.active)), Color.CYAN)
    print(box_row(f"  {t('ui_habilidades_label')}: {skill_str}  |  {t('ui_misiones_label')}: {quest_str}"))
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
    print(box_row(clr(t("ui_attributes"), Color.CYAN)))
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
    print(box_row(f"{t('ui_equipped_weapon'):<12}: {w}"))
    print(box_row(f"{t('ui_equipped_armor'):<12}: {a}"))
    print(box_row(f"{t('ui_equipped_ring'):<12}: {r}"))
    print(box_separator())
    print(box_row(clr(t("ui_abilities"), Color.CYAN)))
    for ab in player.char_class.abilities:
        cd = player.cooldowns.get(ab.name, 0)
        cd_str = clr(f" [CD:{cd}]", Color.RED) if cd > 0 else clr(" [Listo]", Color.GREEN)
        print(box_row(f"  * {ab.name}  [{ab.mp_cost}MP]{cd_str}"))
        print(box_row(f"    {t(ab.description)}"))
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
    typewriter(f"         {t('victory_banner')}", 0.05)
    print()
    print(clr("  " + "═" * 58, Color.YELLOW))
    print()
    typewriter(f"  {t('victory_1')}", 0.018)
    typewriter(f"  {t('victory_2')}", 0.018)
    typewriter(f"  {t('victory_3')}", 0.018)
    print()
    print(box_top(44))
    print(box_row(clr(f"  {t('victory_stats')}", Color.YELLOW), width=44))
    print(box_separator(44))
    print(box_row(t("victory_name", name=player.name), width=44))
    print(box_row(t("victory_class", class_name=player.char_class.name, level=player.level), width=44))
    print(box_row(t("victory_kills", kills=player.kills), width=44))
    print(box_row(t("victory_gold", gold=player.gold), width=44))
    print(box_bottom(44))
    press_enter(f"  {t('victory_press')}")


def _game_over_screen(player: Player):
    """Show the game over screen."""
    clear_screen()
    print()
    print(clr("  " + "═" * 58, Color.RED))
    print()
    typewriter(f"         {t('gameover_banner')}", 0.05)
    print()
    print(clr("  " + "═" * 58, Color.RED))
    print()
    typewriter("  La mazmorra se comió otro gil. Eso es todo.", 0.018)
    typewriter(f"  {t('gameover_2')}", 0.018)
    print()
    print_message(t("gameover_char", name=player.name, class_name=player.char_class.name, level=player.level), "system")
    print_message(t("gameover_stats", kills=player.kills, floors=player.floors_cleared), "system")
    print_message(t("gameover_gold", gold=player.gold), "system")
    press_enter()


def _show_credits():
    """Show credits screen."""
    clear_screen()
    print_panel(t("credits_title"), [
        "",
        f"  Version {GAME_VERSION}",
        "",
        t("credits_built"),
        t("credits_dnd"),
        "",
        t("credits_thanks"),
        "",
        t("credits_quote_1"),
        t("credits_quote_2"),
        "",
    ])
    press_enter()


def _quit_game():
    """Exit message."""
    clear_screen()
    print()
    typewriter(f"  {t('quit_1')}", 0.020)
    typewriter(f"  {t('quit_2')}", 0.020)
    print()
    time.sleep(0.5)
