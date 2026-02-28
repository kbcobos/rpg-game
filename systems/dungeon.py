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
from config import DUNGEON_ROOMS


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
        ))
    return rooms


def _generate_room_description(room_type: str) -> str:
    """Generate atmospheric room descriptions."""
    combat_descs = [
        "La antorcha titila. Algo se mueve al fondo del pasillo. Clásico.",
        "Llegó un olor horrible. Algo vive acá y claramente está al tanto de tu visita.",
        "Huesos antiguos crujen bajo tus pies. Quien hizo este cuarto todavía considera que es suyo.",
        "Gruñidos bajos desde la oscuridad. Agarrás el arma. Respirás. Dos de las tres cosas sirven.",
        "Las paredes tienen raspaduras frescas. Algo con garras estuvo acá hace muy poco. No es tranquilizador.",
    ]
    treasure_descs = [
        "Un brillo metálico desde abajo de los escombros. Puede ser oro. Puede ser otra trampa. Fifty-fifty.",
        "Un cofre de piedra tallada, intacto, con un cierre de hierro. Nadie lo abrió. Eso puede ser bueno o muy malo.",
        "Los restos de un aventurero con menos suerte que vos. Sus cosas siguen acá. Los muertos no usan equipo.",
        "Una piedra suelta revela un hueco escondido. Adentro: oportunidad. O arañas. Probablemente las dos.",
    ]
    rest_descs = [
        "Un rincón seco con los restos de un fogón viejo. Seguro como un domingo después del asado.",
        "Agua limpia que gotea de una grieta en la piedra. Fría, cristalina y, en este lugar, casi un milagro.",
        "La mazmorra se abre en una sala tranquila. Por un momento, nada quiere matarte. Aprovechalo.",
    ]
    merchant_descs = [
        "Un tipo detrás de un puesto improvisado, totalmente tranquilo en medio de la mazmorra. Tiene mucha presencia o no tiene nada que perder.",
        "Una caravana de mercader, sí, acá, en el pasillo de la mazmorra. Sin explicaciones. Aparentemente funciona.",
    ]
    trap_descs = [
        "El piso está muy liso. Demasiado liso. En una mazmorra eso no es buena señal.",
        "Hilos finísimos capturan la luz de la antorcha. Parás en seco. Muy repentinamente cuidadoso.",
        "Una placa de presión tiene una inscripción en tres idiomas muertos: 'Volvete'. Mensaje claro.",
    ]
    mystery_descs = [
        "Un altar raro en el centro de la sala, con símbolos que pulsan en luz tenue. Adiviná si esto termina bien.",
        "Un espejo apoyado en la pared. Tu reflejo no se mueve al mismo tiempo que vos. Clásico.",
        "Palabras talladas en el piso: 'Elegí bien. O directamente no elegís'. Filosofía de mazmorra.",
    ]

    mapping = {
        "combat": combat_descs,
        "treasure": treasure_descs,
        "rest": rest_descs,
        "merchant": merchant_descs,
        "trap": trap_descs,
        "mystery": mystery_descs,
        "boss": ["Al final de un pasillo largo, unas puertas enormes están entreabiertas. "
                 "Algo respira del otro lado. Lento, enorme y con mucha paciencia."],
    }
    pool = mapping.get(room_type, combat_descs)
    return random.choice(pool)


def run_dungeon_floor(player: Player) -> str:
    """
    Navigate a complete dungeon floor.
    Returns: "next_floor" | "game_over" | "quit"
    """
    floor = player.dungeon_floor
    rooms = generate_floor(floor)

    _draw_floor_intro(floor, player)
    press_enter()

    for room in rooms:
        result = _enter_room(player, room, floor)

        if result == "game_over":
            return "game_over"
        if result == "quit":
            return "quit"
        if result == "floor_complete":
            player.dungeon_floor += 1
            player.floors_cleared += 1
            return "next_floor"

        save_game(player.to_dict())

    return "next_floor"


def _enter_room(player: Player, room: Room, floor: int) -> str:
    """Handle a single room encounter. Returns outcome string."""
    _draw_room_header(room, floor)
    typewriter(f"  {room.description}", 0.014)
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

    options = [
        "Entrar en combate",
        "Ver inventario primero",
    ]
    choice = prompt_choice(options, "¿Qué hacés?")

    if choice == 1:
        show_inventory(player)

    result = run_combat(player, enemy)

    if result == "defeat":
        return "game_over"
    return "continue"


def _room_treasure(player: Player, floor: int) -> str:
    """Generate and offer treasure."""
    print_message("¡Encontraste un escondite con cosas! Alguien las dejó acá. Ahora son tuyas.", "good")
    print()

    if floor >= 7:
        item_pool = [i for i in ALL_ITEMS.values() if i.rarity in ("rare", "legendary", "uncommon")]
    elif floor >= 4:
        item_pool = [i for i in ALL_ITEMS.values() if i.rarity in ("uncommon", "common")]
    else:
        item_pool = [i for i in ALL_ITEMS.values() if i.rarity == "common"]

    gold_found = random.randint(10 * floor, 30 * floor)
    print_message(f"  Oro: {clr(str(gold_found), Color.YELLOW)} gp. No está nada mal.", "good")
    player.earn_gold(gold_found)

    num_items = random.randint(1, 3)
    found_items = random.sample(item_pool, min(num_items, len(item_pool)))

    for item in found_items:
        rarity_colors = {"common": Color.WHITE, "uncommon": Color.GREEN,
                         "rare": Color.CYAN, "legendary": Color.YELLOW}
        name_str = clr(item.name, rarity_colors.get(item.rarity, Color.WHITE))
        options = [f"Llevar: {name_str}", "Dejarlo acá"]
        choice = prompt_choice(options, "¿Qué hacés con esto?")
        if choice == 0:
            ok, msg = player.add_to_inventory(item)
            print_message(msg, "good" if ok else "warning")

    press_enter()
    return "continue"


def _room_rest(player: Player, floor: int) -> str:
    """Rest room: recover HP/MP."""
    print_message("Encontrás un rincón tranquilo. Te tirás como si fuera domingo. Merecido.", "good")
    print()

    heal_amount = int(player.max_hp * 0.35)
    mp_amount   = int(player.max_mp * 0.40)

    restored_hp = player.heal(heal_amount)
    restored_mp = player.restore_mp(mp_amount)

    player.remove_status("poison")
    player.remove_status("burn")
    player.remove_status("curse")

    print_message(f"  Recuperaste {restored_hp} HP y {restored_mp} MP. Eso es vida.", "good")
    print_message("  Los estados negativos se van. La mazmorra puede esperar un toque.", "system")
    print()

    print(box_top(44))
    print(box_row(clr("ESTADO AL DESCANSAR", Color.YELLOW), width=44, align="center"))
    print(box_separator(44))
    print(box_row(f"  HP : {hp_bar(player.current_hp, player.max_hp, 16)}", width=44))
    print(box_row(f"  MP : {player.current_mp}/{player.max_mp}", width=44))
    print(box_bottom(44))

    press_enter()
    return "continue"


def _room_merchant(player: Player, floor: int) -> str:
    """Merchant room: buy and sell items."""
    print_message('"Che, pasá pasá. Mirá esto, posta que te sirve. No te voy a mentir... mucho."', "normal")
    print()

    stock_count = 4
    if floor >= 5:
        stock_pool = [i for i in ALL_ITEMS.values() if i.rarity in ("uncommon", "rare") and i.value > 0]
    else:
        stock_pool = [i for i in ALL_ITEMS.values() if i.rarity == "common" and i.value > 0]

    stock = random.sample(stock_pool, min(stock_count, len(stock_pool)))

    while True:
        _draw_merchant_menu(player, stock)
        options = ["Comprar", "Vender", "Salir"]
        choice = prompt_choice(options, "¿Qué querés hacer?")

        if choice == 0:
            _merchant_buy(player, stock)
        elif choice == 1:
            _merchant_sell(player)
        else:
            break

    return "continue"


def _draw_merchant_menu(player: Player, stock: list):
    """Draw merchant shop display."""
    print()
    print(box_top())
    print(box_row(clr("TIENDA DEL MERCADER", Color.YELLOW), align="center"))
    print(box_row(clr('"Calidad garantizada. Mayormente."', Color.GREY), align="center"))
    print(box_separator())
    print(box_row(f"  Tu Oro: {clr(str(player.gold), Color.YELLOW)} gp"))
    print(box_separator())
    for i, item in enumerate(stock, 1):
        price = int(item.value * 1.4)
        print(box_row(f"  {i}. {item.name:25s}  {clr(str(price)+'gp', Color.YELLOW)}"))
    print(box_bottom())


def _merchant_buy(player: Player, stock: list):
    options = [f"{item.name}  ({int(item.value * 1.4)}gp)" for item in stock]
    options.append("-- Cancelar --")
    choice = prompt_choice(options, "Comprar")
    if choice == len(options) - 1:
        return
    item = stock[choice]
    price = int(item.value * 1.4)
    if player.spend_gold(price):
        ok, msg = player.add_to_inventory(item)
        print_message(msg if ok else "La mochila está llena, flaco.", "good" if ok else "warning")
    else:
        print_message("Con esa guita no alcanza. Juntá más oro primero.", "warning")
    press_enter()


def _merchant_sell(player: Player):
    if not player.inventory:
        print_message("No tenés nada para vender. Ni un hueso.", "warning")
        press_enter()
        return
    options = [f"{item.name}  ({int(item.value * 0.6)}gp)" for item in player.inventory]
    options.append("-- Cancelar --")
    choice = prompt_choice(options, "Vender")
    if choice == len(options) - 1:
        return
    item = player.inventory[choice]
    sell_price = int(item.value * 0.6)
    player.remove_from_inventory(item)
    player.earn_gold(sell_price)
    print_message(f"Vendiste {item.name} por {sell_price}gp. Trato hecho.", "good")
    press_enter()


def _room_trap(player: Player, floor: int) -> str:
    """Trap room: damage with possible avoidance via DEX."""
    print_message("Algo no está bien acá. Una trampa. Claro que hay una trampa.", "warning")
    print()

    dex_roll = random.randint(1, 20) + (player.dexterity - 10) // 2
    threshold = 12 + floor

    if dex_roll >= threshold:
        typewriter("  ¡Tus reflejos te salvaron! Saltaste justo a tiempo. Que susto, uh.", 0.015)
        print_message("  ¡Trampa evitada! La destreza sirvió para algo.", "good")
    else:
        damage = random.randint(5 * floor, 10 * floor)
        actual = player.take_damage(damage)
        typewriter(f"  ¡La trampa se activó! Recibís {actual} de daño. Debiste fijarte mejor.", 0.015)
        print_message(f"  Daño de trampa: {clr(str(actual), Color.RED)} HP. Duele.", "bad")

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
    typewriter("  Un altar oscuro pulsa con energía maligna. Algo pide tributo. Siempre hay algo pidiendo algo.", 0.015)
    options = ["Ofrecer 20 HP (capaz recibís poder)", "Dejarlo tranquilo"]
    choice = prompt_choice(options, "Your decision")
    if choice == 0:
        player.current_hp = max(1, player.current_hp - 20)
        if random.random() < 0.65:
            bonus = random.randint(10, 30)
            atk_bonus = random.randint(2, 5)
            player.max_hp += bonus
            player.base_attack += atk_bonus
            print_message(f"¡El poder oscuro te llenó! +{bonus} HP máx, +{atk_bonus} ATQ. Raro pero copado.", "good")
        else:
            player.add_status("curse", 5, int(player.max_hp * 0.04), "Cursed by dark altar!")
            print_message("¡El altar te rechazó! Quedaste maldito. Era esperable.", "bad")
    else:
        print_message("Prudente. El altar te mira irse. Igual no te va a olvidar.", "system")
    press_enter()
    return "continue"


def _mystery_magic_fountain(player: Player, floor: int) -> str:
    typewriter("  Una fuente con líquido brillante. Huele a magia antigua. Tomás igual, que queda poco HP.", 0.015)
    player.heal(int(player.max_hp * 0.50))
    player.restore_mp(int(player.max_mp * 0.50))
    player.remove_status("poison")
    player.remove_status("curse")
    player.remove_status("burn")
    print_message("¡Las aguas mágicas te restauraron! El cuerpo y el alma. Un lujo en esta mazmorra.", "good")
    press_enter()
    return "continue"


def _mystery_cursed_chest(player: Player, floor: int) -> str:
    typewriter("  Un cofre abierto lleno de oro. Algo no cierra. En una mazmorra, rara vez cierra.", 0.015)
    options = ["Agarrar el oro (YOLO)", "Dejarlo y seguir"]
    choice = prompt_choice(options, "Your decision")
    if choice == 0:
        gold = random.randint(30 * floor, 80 * floor)
        player.earn_gold(gold)
        if random.random() < 0.5:
            damage = random.randint(15, 35)
            actual = player.take_damage(damage)
            print_message(f"¡Maldición! Recibís {actual} de daño. Pero el oro es tuyo. Valió la pena.", "bad")
        else:
            print_message(f"Te guardás {gold}gp. Sin maldición. Hoy el universo fue amable.", "good")
    else:
        print_message("Te alejás. El cofre sisea. Claramente una buena decisión.", "system")
    press_enter()
    return "continue"


def _mystery_wandering_soul(player: Player, floor: int) -> str:
    typewriter("  Un fantasma aparece. El espíritu de un aventurero caído. Tuvo menos suerte que vos.", 0.015)
    print_message('"Tomá esto... ya no me sirve de nada."', "normal")
    possible = [i for i in ALL_ITEMS.values() if i.rarity in ("uncommon", "rare")]
    if possible:
        gift = random.choice(possible)
        ok, msg = player.add_to_inventory(gift)
        print_message(f"El espíritu te da: {clr(gift.name, Color.CYAN)}. Un gesto copado desde el más allá.", "good")
    press_enter()
    return "continue"


def _mystery_enchanted_shrine(player: Player, floor: int) -> str:
    typewriter("  Un santuario con runas ofrece una bendición. Parece que te considera digno. Buen día.", 0.015)
    stat_options = ["FUE (+2 Fuerza — para los que resuelven todo a piñas)", "DES (+2 Destreza — sigiloso y ágil)", "INT (+2 Inteligencia — el libro lo dice)",
                    "SAB (+2 Sabiduría — que dicen los que saben)", "CON (+2 Constitución — aguantá más, que falta)"]
    choice = prompt_choice(stat_options, "¿Qué bendición elegís?")
    bonuses = {0: ("strength", 2), 1: ("dexterity", 2), 2: ("intelligence", 2),
               3: ("wisdom", 2), 4: ("constitution", 2)}
    attr, val = bonuses[choice]
    current = getattr(player, attr)
    setattr(player, attr, current + val)
    player._recalculate_stats()
    print_message(f"¡El santuario te otorga +{val} {attr.upper()}! Se nota que eras el elegido.", "good")
    press_enter()
    return "continue"


def _room_boss(player: Player, floor: int) -> str:
    """Boss room — dramatic encounter."""
    typewriter("  Las puertas enormes crujen al abrirse. Aire frío inunda el pasillo.", 0.014)
    typewriter("  Silencio. Pasos. Algo muy antiguo y muy enojado se despierta.", 0.014)
    print()

    if floor >= 9:
        boss_template = get_boss("ancient_demon")
    elif floor >= 6:
        boss_template = get_boss("lich")
    else:
        boss_template = get_boss("dragon")

    level_mod = floor
    boss = Enemy(boss_template, level_modifier=level_mod)

    press_enter(f"  [ Preparate — el {boss.name} te espera. Buena suerte, la vas a necesitar. ]")
    result = run_combat(player, boss)

    if result == "defeat":
        return "game_over"
    elif result == "fled":
        print_message("La sala se cerró detrás tuyo. No hay salida. Era de esperarse, ¿no?", "bad")
        result = run_combat(player, boss)
        if result == "defeat":
            return "game_over"

    print()
    typewriter("  La mazmorra tiembla. Aparece una escalera que baja más todavía. Siempre hay más.", 0.014)
    print_message(f"  ¡Piso {floor} completado! Seguís. Eso dice mucho de vos.", "good")
    press_enter()
    return "floor_complete"


def _draw_floor_intro(floor: int, player: Player):
    """Draw the floor introduction screen."""
    print()
    floor_descriptions = {
        1: "Las criptas de arriba. Los bichos son flojos pero no te confiés. Nunca.",
        2: "Los salones funerarios. Los muertos se ponen cada vez más inquietos. Spoiler: empeora.",
        3: "Las madrigueras. Algo organizado vive acá y ya sabe que llegaste. Mal comienzo.",
        4: "Las galerías de sombra. La luz muere acá. Los monstruos se ponen más valientes. Vos también, esperemos.",
        5: "Las minas profundas. Las excavaron tipos que encontraron algo que no debían. Así terminaron.",
        6: "Las bóvedas malditas. El mal antiguo sale de las mismas piedras. Arquitectura peligrosa.",
        7: "Los corredores demoníacos. No todos los que entraron acá eran humanos. Algunos ya no lo son.",
        8: "Los salones del abismo. La realidad se siente delgada. Algo te mira desde las paredes. Ignoralo.",
        9: "El descenso final. El dueño de la mazmorra espera. Todos los caminos terminan acá. Los tuyos también.",
        10: "PROFUNDIDAD DESCONOCIDA. Los mapas llegan hasta acá. Las leyendas también. ¿Vos?",
    }
    desc = floor_descriptions.get(floor, f"Floor {floor}: the darkness deepens.")

    print(box_top())
    print(box_row(clr(f"DUNGEON OF AETHORIA — PISO {floor}", Color.MAGENTA), align="center"))
    print(box_separator())
    print(box_row(f"  {desc}"))
    print(box_separator())
    print(box_row(f"  {player.name}  |  {player.char_class.name} Lvl.{player.level}  |  "
                  f"HP: {player.current_hp}/{player.max_hp}  |  Oro: {player.gold}gp"))
    print(box_bottom())


def _draw_room_header(room: Room, floor: int):
    """Draw the room header."""
    type_labels = {
        "combat": clr("[ ENCUENTRO ]", Color.RED),
        "treasure": clr("[ TESORO ]", Color.YELLOW),
        "rest": clr("[ DESCANSO ]", Color.GREEN),
        "merchant": clr("[ MERCADER ]", Color.CYAN),
        "trap": clr("[ TRAMPA ]", Color.MAGENTA),
        "mystery": clr("[ MISTERIO ]", Color.BLUE),
        "boss": clr("[ !! JEFE !! ]", Color.RED),
    }
    label = type_labels.get(room.room_type, "[ HABITACION ]")
    print()
    print(box_separator())
    print(box_row(f"  Piso {floor}  |  Habitacion {room.number}/{DUNGEON_ROOMS}  |  {label}"))
    print(box_separator())
    print()
