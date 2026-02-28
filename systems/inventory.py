from entities.player import Player
from data.items import Item
from utils.display import (
    print_panel, box_top, box_bottom, box_row, box_separator,
    prompt_choice, press_enter, print_message, clr, Color, SCREEN_WIDTH
)


def show_inventory(player: Player):
    """
    Interactive inventory screen.
    Player can use, equip, or inspect items.
    """
    while True:
        _draw_inventory(player)

        if not player.inventory:
            print_message("La mochila está vacía. Literal nada.", "system")
            press_enter()
            return

        options = [f"{item.name}  [{item.item_type.upper()}]" for item in player.inventory]
        options.append("-- Cerrar --")

        choice = prompt_choice(options, "¿Qué objeto?")
        if choice == len(options) - 1:
            return

        selected = player.inventory[choice]
        _item_action_menu(player, selected)


def _draw_inventory(player: Player):
    """Render the inventory panel."""
    print()
    print(box_top())
    print(box_row(clr("INVENTARIO — lo que cargás", Color.YELLOW), align="center"))
    print(box_separator())
    print(box_row(f"Oro: {clr(str(player.gold), Color.YELLOW)} gp   "
                  f"Objetos: {len(player.inventory)}/{20}"))
    print(box_separator())

    w_name = player.equipped_weapon.name if player.equipped_weapon else "-- vacio --"
    a_name = player.equipped_armor.name  if player.equipped_armor  else "-- vacio --"
    r_name = player.equipped_ring.name   if player.equipped_ring   else "-- vacio --"
    print(box_row(clr("EQUIPADO AHORA:", Color.CYAN)))
    print(box_row(f"  Arma    : {w_name}"))
    print(box_row(f"  Armadura: {a_name}"))
    print(box_row(f"  Anillo  : {r_name}"))
    print(box_separator())

    if not player.inventory:
        print(box_row(clr("  < La mochila está vacía, ni un alfajor >", Color.GREY), align="center"))
    else:
        for i, item in enumerate(player.inventory, 1):
            rarity_color = {
                "common": Color.WHITE,
                "uncommon": Color.GREEN,
                "rare": Color.CYAN,
                "legendary": Color.YELLOW,
            }.get(item.rarity, Color.WHITE)
            name_str = clr(item.name, rarity_color)
            type_str = clr(f"[{item.item_type}]", Color.GREY)
            val_str  = clr(f"{item.value}gp", Color.YELLOW)
            print(box_row(f"  {i:2}. {name_str}  {type_str}  {val_str}"))

    print(box_bottom())


def _item_action_menu(player: Player, item: Item):
    """Show actions for a selected item."""
    print()
    print(box_top(40))
    print(box_row(clr(item.name, Color.YELLOW), width=40, align="center"))
    print(box_separator(40))
    print(box_row(item.description, width=40))
    if item.attack_bonus:
        print(box_row(f"  ATK: +{item.attack_bonus}", width=40))
    if item.defense_bonus:
        print(box_row(f"  DEF: +{item.defense_bonus}", width=40))
    if item.heal_hp:
        print(box_row(f"  Cura: {item.heal_hp} HP", width=40))
    if item.heal_mp:
        print(box_row(f"  Mana: +{item.heal_mp} MP", width=40))
    print(box_row(f"  Rareza: {item.rarity.upper()}", width=40))
    print(box_bottom(40))

    actions = []
    if item.item_type == "potion":
        actions.append("Usar ahora")
    if item.item_type in ("weapon", "armor") or item.slot == "ring":
        actions.append("Equipar")
    actions.append("Tirar (y chau)")
    actions.append("Cancelar")

    choice = prompt_choice(actions, "¿Qué hacés con esto?")
    selected_action = actions[choice]

    if selected_action == "Usar ahora":
        ok, msg = player.use_potion(item)
        print_message(msg, "good" if ok else "bad")
        press_enter()

    elif selected_action == "Equipar":
        ok, msg = player.equip_item(item)
        print_message(msg, "good" if ok else "bad")
        press_enter()

    elif selected_action == "Tirar (y chau)":
        player.remove_from_inventory(item)
        print_message(f"Tiraste el {item.name}. Decisión tomada.", "system")
        press_enter()
