import random
from dataclasses import dataclass, field
from typing import Callable

from entities.player import Player
from entities.enemy import Enemy
from data.enemies import get_random_enemy, get_boss, ENEMIES
from data.items import ALL_ITEMS, POTIONS, MISC_ITEMS
from systems.combat import run_combat
from systems.inventory import show_inventory
from utils.display import (
    box_top, box_bottom, box_row, box_separator,
    print_panel, print_message, prompt_choice, press_enter,
    typewriter, clr, Color, hp_bar, SCREEN_WIDTH
)
from utils.save_load import save_game
from utils.namegen import generate_dungeon_name, generate_floor_name, generate_room_name
from config import DUNGEON_ROOMS
from utils.lang import t, item_desc


ROOM_TYPES = [
    "combat",
    "combat",
    "combat",
    "treasure",
    "rest",
    "merchant",
    "trap",
    "mystery",
    "boss",
]


@dataclass
class Room:
    number: int
    room_type: str
    is_last: bool = False
    visited: bool = False
    description: str = ""
    name: str = ""
    grid_x: int = 0
    grid_y: int = 0


def generate_floor(floor_number: int) -> list[Room]:
    """Generate a randomized list of rooms for a dungeon floor."""
    rooms = []
    for i in range(1, DUNGEON_ROOMS + 1):
        is_last = (i == DUNGEON_ROOMS)
        if is_last:
            rtype = "boss"
        else:
            if i == 3:
                rtype = "rest"
            elif i == 6:
                rtype = "treasure"
            else:
                rtype = random.choice(ROOM_TYPES[:-1])

        rooms.append(Room(
            number=i,
            room_type=rtype,
            is_last=is_last,
            description=_generate_room_description(rtype),
            name=generate_room_name(rtype),
            grid_x=(i - 1) % 5,
            grid_y=(i - 1) // 5,
        ))
    return rooms


def _generate_room_description(room_type: str) -> str:
    """Generate atmospheric room descriptions using current language."""
    import random
    pools = {
        "combat":   ["room_desc_combat_1","room_desc_combat_2","room_desc_combat_3","room_desc_combat_4","room_desc_combat_5"],
        "treasure": ["room_desc_treasure_1","room_desc_treasure_2","room_desc_treasure_3","room_desc_treasure_4"],
        "rest":     ["room_desc_rest_1","room_desc_rest_2","room_desc_rest_3"],
        "merchant": ["room_desc_merchant_1","room_desc_merchant_2"],
        "trap":     ["room_desc_trap_1","room_desc_trap_2","room_desc_trap_3"],
        "mystery":  ["room_desc_mystery_1","room_desc_mystery_2","room_desc_mystery_3"],
        "boss":     ["room_desc_boss"],
    }
    pool = pools.get(room_type, pools["combat"])
    return random.choice(pool)


def run_dungeon_floor(player: Player) -> str:
    """
    Navigate a complete dungeon floor.
    Returns: "next_floor" | "game_over" | "quit"
    """
    floor = player.dungeon_floor
    rooms = generate_floor(floor)

    _draw_floor_intro(floor, player)
    _draw_dungeon_map(rooms, current_room=0)
    press_enter()

    for room in rooms:
        _draw_dungeon_map(rooms, current_room=room.number - 1)
        press_enter(t("dungeon_entering", name=room.name))

        result = _enter_room(player, room, floor)

        if result == "game_over":
            return "game_over"
        if result == "quit":
            return "quit"
        if result == "floor_complete":
            player.dungeon_floor += 1
            player.floors_cleared += 1
            msgs = player.quest_manager.check_and_reward(
                player,
                player_kills=player.kills,
                player_floors=player.floors_cleared,
                player_level=player.level,
            )
            for m in msgs:
                print_message(m, "good" if ("MISIÓN" in m or "QUEST" in m) else "normal")
            if msgs:
                press_enter()
            return "next_floor"

        save_game(player.to_dict())

    return "next_floor"


def _enter_room(player: Player, room: Room, floor: int) -> str:
    """Handle a single room encounter. Returns outcome string."""
    _draw_room_header(room, floor)
    typewriter(f"  {t(room.description)}", 0.014)
    print()

    handler = {
        "combat":   _room_combat,
        "treasure": _room_treasure,
        "rest":     _room_rest,
        "merchant": _room_merchant,
        "trap":     _room_trap,
        "mystery":  _room_mystery,
        "boss":     _room_boss,
    }.get(room.room_type, _room_combat)

    result = handler(player, floor)
    room.visited = True
    return result


def _room_combat(player: Player, floor: int) -> str:
    """Spawn and fight a random enemy appropriate to the floor."""
    tier = min(3, 1 + (floor - 1) // 3)
    template = get_random_enemy(tier)
    level_mod = floor - 1
    enemy = Enemy(template, level_modifier=level_mod)

    options = [t("combat_enter_combat"), t("combat_check_inv")]
    choice = prompt_choice(options, t("camp_prompt"))

    if choice == 1:
        show_inventory(player)

    result = run_combat(player, enemy)

    if result == "defeat":
        return "game_over"

    if result == "victory":
        msgs = player.quest_manager.on_enemy_killed(enemy)
        msgs += player.quest_manager.check_and_reward(
            player,
            player_kills=player.kills,
            player_floors=player.floors_cleared,
            player_level=player.level,
        )
        for m in msgs:
            print_message(m, "good" if ("MISIÓN" in m or "QUEST" in m) else "normal")
        if any(("MISIÓN" in m or "QUEST" in m) for m in msgs):
            press_enter()

    elif result == "fled":
        player.quest_manager.on_fled_combat()

    return "continue"


def _room_treasure(player: Player, floor: int) -> str:
    """Generate and offer treasure."""
    print_message(t("dungeon_treasure_found"), "good")
    print()

    if floor >= 7:
        item_pool = [i for i in ALL_ITEMS.values() if i.rarity in ("rare", "legendary", "uncommon")]
    elif floor >= 4:
        item_pool = [i for i in ALL_ITEMS.values() if i.rarity in ("uncommon", "common")]
    else:
        item_pool = [i for i in ALL_ITEMS.values() if i.rarity == "common"]

    gold_found = random.randint(20 * floor, 60 * floor)
    print_message(t("dungeon_gold_found", amount=clr(str(gold_found), Color.YELLOW)), "good")
    player.earn_gold(gold_found)
    player.quest_manager.on_gold_earned(gold_found)

    num_items = random.randint(1, 3)
    found_items = random.sample(item_pool, min(num_items, len(item_pool)))

    for item in found_items:
        rarity_colors = {"common": Color.WHITE, "uncommon": Color.GREEN,
                         "rare": Color.CYAN, "legendary": Color.YELLOW}
        name_str = clr(item.name, rarity_colors.get(item.rarity, Color.WHITE))
        options = [t("dungeon_take_item", item=name_str), t("dungeon_leave_item")]
        choice = prompt_choice(options, t("dungeon_item_prompt"))
        if choice == 0:
            ok, msg = player.add_to_inventory(item)
            print_message(msg, "good" if ok else "warning")
            if ok:
                player.quest_manager.on_item_collected()

    press_enter()
    return "continue"


def _room_rest(player: Player, floor: int) -> str:
    """Rest room: recover HP/MP."""
    print_message(t("dungeon_rest_found"), "good")
    print()

    heal_amount = int(player.max_hp * 0.35)
    mp_amount   = int(player.max_mp * 0.40)

    restored_hp = player.heal(heal_amount)
    restored_mp = player.restore_mp(mp_amount)

    player.remove_status("poison")
    player.remove_status("burn")
    player.remove_status("curse")

    print_message(t("dungeon_rest_recovered", hp=restored_hp, mp=restored_mp), "good")
    print_message(t("dungeon_rest_ailments"), "system")
    print()

    print(box_top(44))
    print(box_row(clr(t("combat_status_rest"), Color.YELLOW), width=44, align="center"))
    print(box_separator(44))
    print(box_row(f"  HP : {hp_bar(player.current_hp, player.max_hp, 16)}", width=44))
    print(box_row(f"  MP : {player.current_mp}/{player.max_mp}", width=44))
    print(box_bottom(44))

    press_enter()
    return "continue"


def _room_merchant(player: Player, floor: int) -> str:
    """Merchant room: buy and sell items."""
    print_message(t("dungeon_merchant_line"), "normal")
    print()

    stock_count = 4
    if floor >= 5:
        stock_pool = [i for i in ALL_ITEMS.values() if i.rarity in ("uncommon", "rare") and i.value > 0]
    else:
        stock_pool = [i for i in ALL_ITEMS.values() if i.rarity == "common" and i.value > 0]

    stock = random.sample(stock_pool, min(stock_count, len(stock_pool)))

    while True:
        _draw_merchant_menu(player, stock)
        options = [t("combat_buy"), t("combat_sell"), t("combat_exit")]
        choice = prompt_choice(options, t("camp_prompt"))

        if choice == 0:
            _merchant_buy(player, stock)
        elif choice == 1:
            _merchant_sell(player)
        else:
            break

    return "continue"


def _draw_merchant_menu(player: Player, stock: list):
    """Draw merchant shop display."""
    rarity_colors = {"common": Color.WHITE, "uncommon": Color.GREEN,
                     "rare": Color.CYAN, "legendary": Color.YELLOW}
    print()
    print(box_top())
    print(box_row(clr(t("combat_merchant_title"), Color.YELLOW), align="center"))
    print(box_row(clr(t("dungeon_merchant_stock"), Color.GREY), align="center"))
    print(box_separator())
    print(box_row(f"  {t('combat_gold_label')}: {clr(str(player.gold), Color.YELLOW)} gp"))
    print(box_separator())
    for i, item in enumerate(stock, 1):
        price = int(item.value * 1.4)
        name_str = clr(item.name, rarity_colors.get(item.rarity, Color.WHITE))
        price_str = clr(str(price)+'gp', Color.YELLOW)
        stats = []
        if item.attack_bonus:  stats.append(f"ATK+{item.attack_bonus}")
        if item.defense_bonus: stats.append(f"DEF+{item.defense_bonus}")
        if item.heal_hp:       stats.append(f"HP+{item.heal_hp}")
        if item.heal_mp:       stats.append(f"MP+{item.heal_mp}")
        stat_str = clr("  " + "  ".join(stats), Color.GREEN) if stats else ""
        print(box_row(f"  {i}. {name_str}  {price_str}"))
        print(box_row(f"     {clr(item_desc(item)[:55], Color.GREY)}{stat_str}"))
    print(box_bottom())


def _merchant_buy(player: Player, stock: list):
    options = [f"{item.name}  ({int(item.value * 1.4)}gp)" for item in stock]
    options.append(t("combat_cancel"))
    choice = prompt_choice(options, t("combat_buy_prompt"))
    if choice == len(options) - 1:
        return
    item = stock[choice]
    price = int(item.value * 1.4)
    if player.spend_gold(price):
        ok, msg = player.add_to_inventory(item)
        print_message(msg if ok else t("dungeon_bag_full"), "good" if ok else "warning")
    else:
        print_message(t("dungeon_no_gold"), "warning")
    press_enter()


def _merchant_sell(player: Player):
    if not player.inventory:
        print_message(t("dungeon_nothing_sell"), "warning")
        press_enter()
        return
    options = [f"{item.name}  ({int(item.value * 0.6)}gp)" for item in player.inventory]
    options.append(t("combat_cancel"))
    choice = prompt_choice(options, t("combat_sell_prompt"))
    if choice == len(options) - 1:
        return
    item = player.inventory[choice]
    sell_price = int(item.value * 0.6)
    player.remove_from_inventory(item)
    player.earn_gold(sell_price)
    print_message(t("dungeon_sold", item=item.name, price=sell_price), "good")
    press_enter()


def _room_trap(player: Player, floor: int) -> str:
    """Trap room: damage with possible avoidance via DEX."""
    print_message(t("dungeon_trap_sense"), "warning")
    print()

    dex_roll = random.randint(1, 20) + (player.dexterity - 10) // 2
    threshold = 12 + floor

    if dex_roll >= threshold:
        typewriter(f"  {t('dungeon_trap_avoided')}", 0.015)
        print_message(t("dungeon_trap_avoided_msg"), "good")
        player.quest_manager.on_trap_avoided()
    else:
        damage = random.randint(5 * floor, 10 * floor)
        actual = player.take_damage(damage)
        typewriter(f"  {t('dungeon_trap_hit', damage=actual)}", 0.015)
        print_message(t("dungeon_trap_damage", damage=clr(str(actual), Color.RED)), "bad")

        if not player.is_alive:
            press_enter()
            return "game_over"

    press_enter()
    return "continue"


def _room_mystery(player: Player, floor: int) -> str:
    """Mystery room with a random special event."""
    events = [
        _mystery_dark_altar,
        _mystery_magic_fountain,
        _mystery_cursed_chest,
        _mystery_wandering_soul,
        _mystery_enchanted_shrine,
    ]
    event = random.choice(events)
    return event(player, floor)


def _mystery_dark_altar(player: Player, floor: int) -> str:
    typewriter(f"  {t('dungeon_altar_event')}", 0.015)
    options = [t("dungeon_altar_offer"), t("dungeon_altar_skip")]
    choice = prompt_choice(options, t("dungeon_altar_prompt"))
    if choice == 0:
        player.current_hp = max(1, player.current_hp - 20)
        if random.random() < 0.65:
            bonus = random.randint(10, 30)
            atk_bonus = random.randint(2, 5)
            player.max_hp += bonus
            player.base_attack += atk_bonus
            print_message(t("dungeon_altar_power", hp=bonus, atk=atk_bonus), "good")
        else:
            player.add_status("curse", 5, int(player.max_hp * 0.04), "Cursed by dark altar!")
            print_message(t("dungeon_altar_curse"), "bad")
    else:
        print_message(t("dungeon_altar_leave"), "system")
    press_enter()
    return "continue"


def _mystery_magic_fountain(player: Player, floor: int) -> str:
    typewriter(f"  {t('dungeon_fountain_event')}", 0.015)
    player.heal(int(player.max_hp * 0.50))
    player.restore_mp(int(player.max_mp * 0.50))
    player.remove_status("poison")
    player.remove_status("curse")
    player.remove_status("burn")
    print_message(t("dungeon_fountain_healed"), "good")
    press_enter()
    return "continue"


def _mystery_cursed_chest(player: Player, floor: int) -> str:
    typewriter(f"  {t('dungeon_chest_event')}", 0.015)
    options = [t("dungeon_chest_take"), t("dungeon_chest_leave")]
    choice = prompt_choice(options, t("dungeon_item_prompt"))
    if choice == 0:
        gold = random.randint(60 * floor, 160 * floor)
        player.earn_gold(gold)
        if random.random() < 0.5:
            damage = random.randint(15, 35)
            actual = player.take_damage(damage)
            print_message(t("dungeon_chest_cursed", damage=actual), "bad")
        else:
            print_message(t("dungeon_chest_safe", gold=gold), "good")
    else:
        print_message(t("dungeon_chest_walk"), "system")
    press_enter()
    return "continue"


def _mystery_wandering_soul(player: Player, floor: int) -> str:
    typewriter(f"  {t('dungeon_ghost_event')}", 0.015)
    print_message(t("dungeon_ghost_gift"), "normal")
    possible = [i for i in ALL_ITEMS.values() if i.rarity in ("uncommon", "rare")]
    if possible:
        gift = random.choice(possible)
        ok, msg = player.add_to_inventory(gift)
        print_message(t("dungeon_ghost_item", item=clr(gift.name, Color.CYAN)), "good")
    press_enter()
    return "continue"


def _mystery_enchanted_shrine(player: Player, floor: int) -> str:
    typewriter(f"  {t('dungeon_shrine_event')}", 0.015)
    stat_options = [t("dungeon_shrine_str"), t("dungeon_shrine_dex"), t("dungeon_shrine_int"), t("dungeon_shrine_wis"), t("dungeon_shrine_con")]
    choice = prompt_choice(stat_options, t("dungeon_shrine_prompt"))
    bonuses = {0: ("strength", 2), 1: ("dexterity", 2), 2: ("intelligence", 2),
               3: ("wisdom", 2), 4: ("constitution", 2)}
    attr, val = bonuses[choice]
    current = getattr(player, attr)
    setattr(player, attr, current + val)
    player._recalculate_stats()
    print_message(t("dungeon_shrine_granted", val=val, stat=attr.upper()), "good")
    press_enter()
    return "continue"


def _room_boss(player: Player, floor: int) -> str:
    """Boss room — dramatic encounter."""
    typewriter(f"  {t('dungeon_boss_doors')}", 0.014)
    typewriter(f"  {t('dungeon_boss_stirs')}", 0.014)
    print()

    if floor >= 9:
        boss_template = get_boss("ancient_demon")
    elif floor >= 6:
        boss_template = get_boss("lich")
    else:
        boss_template = get_boss("dragon")

    level_mod = floor
    boss = Enemy(boss_template, level_modifier=level_mod)

    press_enter(t("dungeon_boss_press", boss=boss.name))
    result = run_combat(player, boss)

    if result == "defeat":
        return "game_over"
    elif result == "fled":
        print_message(t("dungeon_boss_sealed"), "bad")
        result = run_combat(player, boss)
        if result == "defeat":
            return "game_over"

    print()
    typewriter(f"  {t('dungeon_stairs')}", 0.014)
    print_message(t("dungeon_floor_cleared", floor=floor), "good")
    press_enter()
    return "floor_complete"


def _draw_floor_intro(floor: int, player: Player):
    """Draw the floor introduction screen."""
    print()
    floor_descriptions = {
        1: "floor_1", 2: "floor_2", 3: "floor_3", 4: "floor_4", 5: "floor_5",
        6: "floor_6", 7: "floor_7", 8: "floor_8", 9: "floor_9", 10: "floor_10",
    }
    desc = t(floor_descriptions.get(floor, "floor_1"))

    print(box_top())
    floor_name = generate_floor_name(floor)
    floor_word = 'FLOOR' if 'FLOOR' in t('dungeon_map_title') else 'PISO'
    print(box_row(clr(f"{floor_word} {floor} — {floor_name}", Color.MAGENTA), align="center"))
    print(box_separator())
    print(box_row(f"  {desc}"))
    print(box_separator())
    print(box_row(f"  {player.name}  |  {player.char_class.name} Lvl.{player.level}  |  "
                  f"HP: {player.current_hp}/{player.max_hp}  |  Oro: {player.gold}gp"))
    print(box_bottom())


def _draw_room_header(room: Room, floor: int):
    """Draw the room header."""
    type_labels = {
        "combat": clr(t("room_combat"), Color.RED),
        "treasure": clr(t("room_treasure"), Color.YELLOW),
        "rest": clr(t("room_rest"), Color.GREEN),
        "merchant": clr(t("room_merchant"), Color.CYAN),
        "trap": clr(t("room_trap"), Color.MAGENTA),
        "mystery": clr(t("room_mystery"), Color.BLUE),
        "boss": clr(t("room_boss"), Color.RED),
    }
    label = type_labels.get(room.room_type, t("room_generic"))
    print()
    print(box_separator())
    print(box_row(f"  Piso {floor}  |  Hab. {room.number}/{DUNGEON_ROOMS}  |  {label}"))
    print(box_row(f"  {clr(room.name, Color.GREY)}"))
    print(box_separator())
    print()


def _draw_dungeon_map(rooms: list, current_room: int = -1):
    """
    Draw an ASCII map of the current dungeon floor.
    Shows visited, current, and unknown rooms in a grid.
    """
    icons = {
        "combat":   "[ C ]",
        "treasure": "[ T ]",
        "rest":     "[ R ]",
        "merchant": "[ $ ]",
        "trap":     "[ X ]",
        "mystery":  "[ ? ]",
        "boss":     "[!!!]",
    }
    unknown = "[ . ]"

    COLS = 5
    print()
    print(box_separator())
    print(box_row(clr(f"  {t('dungeon_map_title')}", Color.CYAN)))
    print(box_separator())

    print(box_row(
        clr("  C", Color.RED) + "=Combate  " +
        clr("T", Color.YELLOW) + "=Tesoro  " +
        clr("R", Color.GREEN) + "=Descanso  " +
        clr("$", Color.CYAN) + "=Mercader  " +
        clr("X", Color.MAGENTA) + "=Trampa  " +
        clr("?", Color.BLUE) + "=Misterio  " +
        clr("!!!", Color.RED) + "=Jefe"
    ))
    print(box_row(""))

    num_rows = (len(rooms) + COLS - 1) // COLS
    for row in range(num_rows):
        row_str = "  "
        for col in range(COLS):
            idx = row * COLS + col
            if idx >= len(rooms):
                row_str += "      "
                continue
            room = rooms[idx]
            room_num = idx

            if room_num == current_room:
                icon = clr(f"[{room.number:2d}*]", Color.YELLOW)
            elif room.visited:
                raw_icon = icons.get(room.room_type, "[ ? ]")
                type_colors = {
                    "combat":   Color.RED,
                    "treasure": Color.YELLOW,
                    "rest":     Color.GREEN,
                    "merchant": Color.CYAN,
                    "trap":     Color.MAGENTA,
                    "mystery":  Color.BLUE,
                    "boss":     Color.RED,
                }
                color = type_colors.get(room.room_type, Color.WHITE)
                icon = clr(raw_icon, color)
            else:
                icon = clr(unknown, Color.GREY)

            if col < COLS - 1 and idx + 1 < len(rooms):
                connector = clr("-", Color.GREY)
            else:
                connector = " "

            row_str += icon + connector

        print(box_row(row_str))

        if row < num_rows - 1:
            vert_row = "  "
            for col in range(COLS):
                idx = row * COLS + col
                if idx < len(rooms):
                    vert_row += clr("  |  ", Color.GREY) + " "
            print(box_row(vert_row))

    print(box_row(""))
    print(box_separator())
