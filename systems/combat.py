import random
import time

from entities.player import Player
from entities.enemy import Enemy
from data.classes import Ability
from utils.display import (
    box_top, box_bottom, box_row, box_separator,
    hp_bar, print_message, prompt_choice, press_enter,
    print_ascii_enemy, typewriter, clr, Color, SCREEN_WIDTH
)
from config import FLEE_BASE_CHANCE


def run_combat(player: Player, enemy: Enemy) -> str:
    """
    Execute a full combat encounter.
    Returns: "victory" | "defeat" | "fled"
    """
    print()
    _draw_encounter_intro(enemy)
    press_enter("  [ El combate comienza... ]")

    turn = 1
    player_evading = False

    while player.is_alive and enemy.is_alive:
        print()
        _draw_combat_status(player, enemy, turn)

        for msg in player.tick_status_effects():
            print_message(msg, "bad")
        for msg in enemy.tick_status_effects():
            print_message(msg, "good")

        if not player.is_alive:
            break
        if not enemy.is_alive:
            break

        result = _player_turn(player, enemy, turn)

        if result == "fled":
            print_message("Salís rajando. Sin vergüenza. Estrategia completamente válida.", "warning")
            press_enter()
            return "fled"

        if not enemy.is_alive:
            break

        print()
        _enemy_turn(enemy, player)

        player.tick_cooldowns()
        enemy.tick_cooldowns()
        turn += 1

        if not player.is_alive:
            break

    print()
    if player.is_alive:
        return _victory(player, enemy)
    else:
        return _defeat(player, enemy)


def _player_turn(player: Player, enemy: Enemy, turn: int) -> str:
    """Handle a complete player turn. Returns 'action' | 'fled'."""

    options = [
        f"Atacar          [ ATK: {player.effective_attack} ]",
        "Usar Habilidad",
        "Usar Pocion",
        "Inventario rapido",
        "Huir",
    ]

    choice = prompt_choice(options, "Tu turno")

    if choice == 0:
        _player_basic_attack(player, enemy)

    elif choice == 1:
        used = _player_use_ability(player, enemy)
        if not used:
            return _player_turn(player, enemy, turn)

    elif choice == 2:
        used = _player_use_potion(player)
        if not used:
            return _player_turn(player, enemy, turn)

    elif choice == 3:
        _player_quick_inventory(player)
        return _player_turn(player, enemy, turn)

    elif choice == 4:
        if _attempt_flee(player, enemy):
            return "fled"
        print_message("El paso te cortó, che. No hay forma de zafar.", "bad")

    return "action"


def _player_basic_attack(player: Player, enemy: Enemy):
    """Execute a basic attack."""
    damage, critical = _calculate_damage(
        attacker_attack=player.effective_attack,
        attacker_stat=player.stat_by_name(player.char_class.primary_stat),
        defender_defense=enemy.effective_defense,
        damage_min=player.equipped_weapon.damage_min if player.equipped_weapon else 3,
        damage_max=player.equipped_weapon.damage_max if player.equipped_weapon else 8,
        crit_stat=player.dexterity,
    )

    if critical:
        typewriter(f"  ¡Golpe crítico! Encontraste el punto débil. Buena puntería.", 0.015)
    actual = enemy.take_damage(damage)
    _flash_damage(enemy.name, actual, critical)


def _player_use_ability(player: Player, enemy: Enemy) -> bool:
    """Show ability menu, execute chosen ability. Returns True if ability was used."""
    available = player.get_available_abilities()

    if not available:
        print_message("No tenés habilidades disponibles. O están en cooldown. O las dos cosas.", "warning")
        press_enter()
        return False

    print()
    ability_options = []
    for ab in available:
        cd = player.cooldowns.get(ab.name, 0)
        cd_str = f" [CD: {cd}]" if cd > 0 else ""
        cost_str = clr(f"[{ab.mp_cost} MP]", Color.BLUE)
        ability_options.append(f"{ab.name}  {cost_str}{cd_str}")
    ability_options.append("-- Cancelar --")

    choice = prompt_choice(ability_options, "Habilidad")
    if choice == len(ability_options) - 1:
        return False

    ability = available[choice]
    ok, reason = player.use_ability(ability)
    if not ok:
        print_message(reason, "warning")
        press_enter()
        return False

    _execute_player_ability(player, enemy, ability)
    return True


def _execute_player_ability(player: Player, enemy: Enemy, ability: Ability):
    """Resolve ability effects on the enemy."""
    narrative = ability.narrative.format(name=player.name)
    print()
    typewriter(f"  {narrative}", 0.014)
    print()

    if ability.heal_amount > 0:
        restored = player.heal(ability.heal_amount)
        print_message(f"You recover {restored} HP.", "good")

    if ability.damage_base > 0:
        stat_val = player.stat_by_name(ability.stat_used)
        raw_dmg = int(ability.damage_base + stat_val * ability.damage_scale)
        actual  = enemy.take_damage(raw_dmg)
        _flash_damage(enemy.name, actual, False)

    _apply_combat_effect(ability.effect, player, enemy)


def _player_use_potion(player: Player) -> bool:
    """Quick-use a potion from inventory."""
    potions = [i for i in player.inventory if i.item_type == "potion"]
    if not potions:
        print_message("No tenés pociones. Previsión cero.", "warning")
        press_enter()
        return False

    options = [f"{p.name}  (HP+{p.heal_hp}  MP+{p.heal_mp})" for p in potions]
    options.append("-- Cancelar --")
    choice = prompt_choice(options, "Usar pocion")

    if choice == len(options) - 1:
        return False

    ok, msg = player.use_potion(potions[choice])
    print_message(msg, "good" if ok else "bad")
    return ok


def _player_quick_inventory(player: Player):
    """View stats and active effects (no item use)."""
    print()
    print(box_top(44))
    print(box_row(clr("ESTADO RÁPIDO", Color.YELLOW), width=44, align="center"))
    print(box_separator(44))
    print(box_row(f"  Nivel: {player.level}  |  Oro: {player.gold} gp", width=44))
    print(box_row(f"  HP : {hp_bar(player.current_hp, player.max_hp, 15)}", width=44))
    print(box_row(f"  MP : {player.current_mp}/{player.max_mp}", width=44))
    print(box_separator(44))
    if player.status_effects:
        effects = ", ".join(s.name.upper() for s in player.status_effects)
        print(box_row(f"  Estados: {effects}", width=44))
    else:
        print(box_row("  Sin estados activos.", width=44))
    print(box_bottom(44))
    press_enter()


def _enemy_turn(enemy: Enemy, player: Player):
    """Execute the enemy's AI turn."""
    action = enemy.choose_action()

    print(clr(f"  ~~~ {enemy.name.upper()}'S TURN ~~~", Color.RED))
    print()

    if action["type"] == "stunned":
        print_message(f"El {enemy.name} está aturdido y pierde el turno. ¡Aproveché!", "good")
        return

    if action["type"] == "attack":
        print_message(action["phrase"], "bad", delay=0.03)
        damage, critical = _calculate_damage(
            attacker_attack=enemy.effective_attack,
            attacker_stat=enemy.strength,
            defender_defense=player.effective_defense,
            damage_min=max(1, enemy.base_attack // 3),
            damage_max=max(2, enemy.base_attack // 2),
            crit_stat=enemy.dexterity,
        )
        if critical:
            print_message("¡Golpe crítico devastador! Te duele hasta el alma.", "bad")
        actual = player.take_damage(damage)
        if actual == 0:
            print_message("¡Tu evasión funcionó! El ataque pasó a centímetros. Suertudo.", "good")
        else:
            print_message(f"You take {clr(str(actual), Color.RED)} damage!", "bad")

    elif action["type"] == "ability":
        ability_name = action["ability_name"]
        multiplier   = action["multiplier"]
        effect       = action["effect"]

        print_message(f"{enemy.name} uses {ability_name.upper()}!", "bad", delay=0.02)
        time.sleep(0.3)

        raw_dmg = int(enemy.effective_attack * multiplier)
        actual  = player.take_damage(raw_dmg)
        if actual == 0:
            print_message("¡Evasión exitosa! La habilidad pasó sin tocarte. De nada.", "good")
        else:
            print_message(f"You take {clr(str(actual), Color.RED)} damage!", "bad")

        _apply_combat_effect(effect, enemy, player)


def _calculate_damage(
    attacker_attack: int,
    attacker_stat: int,
    defender_defense: int,
    damage_min: int,
    damage_max: int,
    crit_stat: int,
) -> tuple[int, bool]:
    """
    Calculate raw damage and whether it was a critical hit.
    Returns (damage, is_critical).
    """
    base = random.randint(damage_min, max(damage_min + 1, damage_max))
    stat_bonus = attacker_stat // 4
    raw = attacker_attack + base + stat_bonus

    reduced = max(1, raw - defender_defense // 2)

    crit_chance = 0.05 + (crit_stat - 10) * 0.005
    is_crit = random.random() < max(0.03, crit_chance)
    if is_crit:
        reduced = int(reduced * 1.75)

    variance = random.uniform(0.90, 1.10)
    final = max(1, int(reduced * variance))

    return final, is_crit


def _flash_damage(target_name: str, damage: int, critical: bool):
    """Print damage notification."""
    dmg_str = clr(str(damage), Color.RED)
    if critical:
        print_message(f"CRITICAL! {target_name} takes {dmg_str} damage!", "bad")
    else:
        print_message(f"{target_name} takes {dmg_str} damage.", "normal")


def _apply_combat_effect(effect: str, source, target):
    """Apply a named status effect from an ability."""
    effect_map = {
        "poison":  ("poison",  3, int(target.max_hp * 0.05), "Poisoned!"),
        "burn":    ("burn",    2, int(target.max_hp * 0.06), "Burning!"),
        "stun":    ("stun",    1, 0,                          "Stunned!"),
        "freeze":  ("stun",    2, 0,                          "Frozen solid!"),
        "curse":   ("curse",   3, int(target.max_hp * 0.04), "Cursed!"),
        "fear":    ("stun",    1, 0,                          "Paralyzed with fear!"),
        "drain":   ("curse",   1, 0,                          "Life drained!"),
        "bleed":   ("poison",  2, int(target.max_hp * 0.04), "Bleeding!"),
        "holy":    ("", 0, 0, ""),
        "aoe":     ("", 0, 0, ""),
        "multi":   ("", 0, 0, ""),
        "chaos":   ("", 0, 0, ""),
        "mark":    ("mark",    2, 0, "Marked for death!"),
        "shield":  ("shield",  3, 30, "Shielded!"),
        "evade":   ("evade",   1, 0, "Evasion ready!"),
        "rage":    ("rage",    3, 0, "Enraged!"),
        "aura":    ("aura",    3, 0, "Holy Aura!"),
        "empower": ("empower", 1, 0, "Empowered!"),
        "analyze": ("analyze", 2, 0, "Weaknesses found!"),
        "summon":  ("", 0, 0, ""),
    }

    if not effect or effect not in effect_map:
        return

    status_name, duration, value, label = effect_map[effect]

    self_effects = {"shield", "evade", "rage", "aura", "empower", "analyze"}
    actual_target = source if status_name in self_effects else target

    if status_name and duration > 0:
        actual_target.add_status(status_name, duration, value)
        if actual_target == target:
            print_message(f"{target.name} is {label}", "bad")
        else:
            print_message(f"{source.name}: {label}", "good")

    if effect == "drain" and target != source:
        drain_hp = max(1, int(target.max_hp * 0.08))
        source.heal(drain_hp)
        print_message(f"{source.name} drains {drain_hp} HP!", "bad")


def _attempt_flee(player: Player, enemy: Enemy) -> bool:
    """Calculate and resolve a flee attempt."""
    speed_ratio = player.dexterity / max(1, enemy.dexterity)
    chance = FLEE_BASE_CHANCE * speed_ratio
    chance = max(0.15, min(0.80, chance))
    return random.random() < chance


def _victory(player: Player, enemy: Enemy) -> str:
    """Handle post-combat victory: XP, gold, loot."""
    print()
    print(clr("  " + "=" * 56, Color.GREEN))
    typewriter(f"  VICTORIA! El {enemy.name} cayó. Bien ahí.", 0.02)
    print(clr("  " + "=" * 56, Color.GREEN))
    print()

    player.kills += 1

    xp_messages = player.gain_xp(enemy.xp_reward)
    for msg in xp_messages:
        print_message(msg, "good" if "***" in msg else "normal")
        if "***" in msg:
            time.sleep(0.4)

    print_message(f"  Encontrás {clr(str(enemy.gold_reward), Color.YELLOW)} monedas de oro. No está mal.", "good")
    player.earn_gold(enemy.gold_reward)

    loot = enemy.generate_loot()
    for item in loot:
        ok, msg = player.add_to_inventory(item)
        print_message(f"  Objeto encontrado: {clr(item.name, Color.CYAN)} — {msg}", "good")

    player.remove_status("rage")
    player.remove_status("empower")
    player.remove_status("evade")

    press_enter()
    return "victory"


def _defeat(player: Player, enemy: Enemy) -> str:
    """Handle defeat screen."""
    print()
    print(clr("  " + "=" * 56, Color.RED))
    typewriter(f"  Caíste. La mazmorra se comió otro gil. Eso es todo.", 0.025)
    print(clr("  " + "=" * 56, Color.RED))
    print()
    print_message(f"  Te liquidó: {enemy.name}", "bad")
    print_message(f"  Nivel que llegaste: {player.level}", "system")
    print_message(f"  Enemigos eliminados: {player.kills}", "system")
    print_message(f"  Oro que llevabas: {player.gold} gp. Ahora es de la mazmorra.", "system")
    print()
    typewriter("  Los calabozos de Aethoria se tragaron otra alma. Como siempre.", 0.02)
    print()
    press_enter("  [ Presioná ENTER para continuar, si te animás ]")
    return "defeat"


def _draw_encounter_intro(enemy: Enemy):
    """Draw the enemy encounter introduction."""
    print_ascii_enemy(enemy.art_key)
    print(box_top())
    tier_color = {1: Color.WHITE, 2: Color.YELLOW, 3: Color.RED, 4: Color.MAGENTA}
    tier_str = clr(f"[ {enemy.tier_label} ]", tier_color.get(enemy.template.tier, Color.WHITE))
    print(box_row(f"{clr(enemy.name.upper(), Color.RED)}  {tier_str}", align="left"))
    print(box_separator())
    print(box_row(enemy.display_description))
    print(box_separator())
    print(box_row(f"  HP: {hp_bar(enemy.current_hp, enemy.max_hp, 20)}"))
    print(box_bottom())


def _draw_combat_status(player: Player, enemy: Enemy, turn: int):
    """Draw both combatant status bars."""
    print(box_top())
    print(box_row(clr(f"  TURNO {turn}", Color.GREY), align="left"))
    print(box_separator())

    p_name = clr(f"{player.name} ({player.char_class.name})", Color.GREEN)
    print(box_row(f"  {p_name}  LVL {player.level}"))
    print(box_row(f"  HP : {hp_bar(player.current_hp, player.max_hp, 18)}"))
    print(box_row(f"  MP : {player.current_mp}/{player.max_mp}  |  ATK:{player.effective_attack}  DEF:{player.effective_defense}"))

    if player.status_effects:
        effects = "  ".join(clr(s.name.upper(), Color.YELLOW) for s in player.status_effects)
        print(box_row(f"  {effects}"))

    print(box_separator())

    e_name = clr(enemy.name.upper(), Color.RED)
    print(box_row(f"  {e_name}"))
    print(box_row(f"  HP : {hp_bar(enemy.current_hp, enemy.max_hp, 18)}"))

    if enemy.status_effects:
        effects = "  ".join(clr(s.name.upper(), Color.GREEN) for s in enemy.status_effects)
        print(box_row(f"  {effects}"))

    print(box_bottom())
