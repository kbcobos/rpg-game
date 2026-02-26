from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Item:
    key: str
    name: str
    item_type: str
    description: str
    value: int
    weight: float
    attack_bonus: int = 0
    defense_bonus: int = 0
    str_bonus: int = 0
    dex_bonus: int = 0
    int_bonus: int = 0
    wis_bonus: int = 0
    cha_bonus: int = 0
    con_bonus: int = 0
    heal_hp: int = 0
    heal_mp: int = 0
    slot: Optional[str] = None
    rarity: str = "common"
    damage_min: int = 0
    damage_max: int = 0


WEAPONS = {
    "iron_sword": Item("iron_sword", "Iron Sword", "weapon",
        "A reliable iron blade, worn but steady.", 50, 3.0,
        attack_bonus=8, slot="main_hand", damage_min=5, damage_max=12),
    "oak_staff": Item("oak_staff", "Oak Staff", "weapon",
        "A gnarled staff of ancient oak. Channels magical energy.", 40, 2.0,
        attack_bonus=4, int_bonus=2, slot="main_hand", damage_min=3, damage_max=8),
    "steel_daggers": Item("steel_daggers", "Steel Daggers", "weapon",
        "Twin steel daggers, perfectly balanced for swift strikes.", 60, 1.5,
        attack_bonus=6, dex_bonus=2, slot="main_hand", damage_min=4, damage_max=10),
    "holy_mace": Item("holy_mace", "Holy Mace", "weapon",
        "A sacred mace blessed by the Temple of Light.", 75, 4.0,
        attack_bonus=7, cha_bonus=1, slot="main_hand", damage_min=6, damage_max=13),
    "longbow": Item("longbow", "Longbow", "weapon",
        "A yew longbow of impressive draw weight.", 55, 2.5,
        attack_bonus=7, dex_bonus=1, slot="main_hand", damage_min=5, damage_max=11),
    "great_axe": Item("great_axe", "Great Axe", "weapon",
        "A massive two-handed axe that cleaves through armor.", 65, 7.0,
        attack_bonus=10, str_bonus=2, slot="main_hand", damage_min=8, damage_max=18),
    "quarterstaff": Item("quarterstaff", "Quarterstaff", "weapon",
        "A perfectly weighted staff for martial arts training.", 30, 1.8,
        attack_bonus=6, dex_bonus=1, slot="main_hand", damage_min=4, damage_max=9),
    "short_sword": Item("short_sword", "Short Sword + Dagger", "weapon",
        "A matched pair — short sword and parrying dagger.", 55, 2.0,
        attack_bonus=7, dex_bonus=1, slot="main_hand", damage_min=5, damage_max=10),
    "arcane_focus": Item("arcane_focus", "Arcane Focus", "weapon",
        "A crystalline orb that amplifies wild magic surges.", 70, 0.5,
        attack_bonus=5, int_bonus=3, slot="main_hand", damage_min=4, damage_max=9),
    "cursed_tome": Item("cursed_tome", "Cursed Tome", "weapon",
        "A book bound in shadow-leather, warm to the touch.", 80, 1.0,
        attack_bonus=5, cha_bonus=3, slot="main_hand", damage_min=4, damage_max=9),

    "steel_sword": Item("steel_sword", "Steel Sword", "weapon",
        "A well-forged steel blade of superior quality.", 120, 3.0,
        attack_bonus=12, slot="main_hand", damage_min=8, damage_max=16,
        rarity="uncommon"),
    "enchanted_staff": Item("enchanted_staff", "Enchanted Staff", "weapon",
        "Crackles with dormant magic.", 200, 2.0,
        attack_bonus=8, int_bonus=4, slot="main_hand", damage_min=10, damage_max=20,
        rarity="rare"),
    "shadowblade": Item("shadowblade", "Shadowblade", "weapon",
        "A dagger that drinks light and bleeds darkness.", 250, 1.2,
        attack_bonus=14, dex_bonus=3, slot="main_hand", damage_min=10, damage_max=22,
        rarity="rare"),
    "dragonslayer": Item("dragonslayer", "Dragonslayer", "weapon",
        "Forged from dragon bone and quenched in its blood.", 500, 8.0,
        attack_bonus=20, str_bonus=3, slot="main_hand", damage_min=18, damage_max=35,
        rarity="legendary"),
}


ARMORS = {
    "robes": Item("robes", "Robes", "armor",
        "Simple cloth robes offering minimal protection.", 20, 1.0,
        defense_bonus=2, slot="body"),
    "leather_armor": Item("leather_armor", "Leather Armor", "armor",
        "Cured leather armor — light and flexible.", 40, 3.0,
        defense_bonus=4, slot="body"),
    "monk_robes": Item("monk_robes", "Monk Robes", "armor",
        "Specially woven robes that do not hinder movement.", 35, 1.5,
        defense_bonus=3, dex_bonus=1, slot="body"),
    "studded_leather": Item("studded_leather", "Studded Leather", "armor",
        "Leather reinforced with iron rivets.", 60, 4.0,
        defense_bonus=5, slot="body"),
    "hide_armor": Item("hide_armor", "Hide Armor", "armor",
        "Thick beast-hide stitched into crude but effective armor.", 45, 5.0,
        defense_bonus=5, con_bonus=1, slot="body"),
    "mage_robes": Item("mage_robes", "Mage Robes", "armor",
        "Arcane-threaded robes with minor magical resistance.", 50, 1.5,
        defense_bonus=3, int_bonus=1, slot="body"),
    "dark_robes": Item("dark_robes", "Dark Robes", "armor",
        "Shadow-woven garments that seem to absorb light.", 55, 1.5,
        defense_bonus=3, cha_bonus=1, slot="body"),
    "chain_mail": Item("chain_mail", "Chain Mail", "armor",
        "Interlocking steel rings provide solid protection.", 80, 8.0,
        defense_bonus=8, slot="body"),
    "plate_mail": Item("plate_mail", "Plate Mail", "armor",
        "Full plate armor. Glorious and unyielding.", 150, 15.0,
        defense_bonus=12, str_bonus=1, slot="body"),
    "mithril_shirt": Item("mithril_shirt", "Mithril Shirt", "armor",
        "Incredibly light — feels like silk, stops steel.", 300, 2.0,
        defense_bonus=10, slot="body", rarity="rare"),
    "dragonscale_armor": Item("dragonscale_armor", "Dragonscale Armor", "armor",
        "Scales from the great wyrm, nigh-impenetrable.", 600, 10.0,
        defense_bonus=18, con_bonus=2, slot="body", rarity="legendary"),
}


POTIONS = {
    "health_potion": Item("health_potion", "Health Potion", "potion",
        "A vial of crimson liquid. Smells of copper and iron.", 30, 0.2,
        heal_hp=50),
    "greater_health_potion": Item("greater_health_potion", "Greater Health Potion", "potion",
        "A large flask of potent healing draught.", 70, 0.3,
        heal_hp=120, rarity="uncommon"),
    "mana_potion": Item("mana_potion", "Mana Potion", "potion",
        "Shimmering blue liquid. Tingles on the tongue.", 35, 0.2,
        heal_mp=50),
    "elixir": Item("elixir", "Elixir of Life", "potion",
        "Restores both body and soul.", 100, 0.4,
        heal_hp=80, heal_mp=80, rarity="uncommon"),
    "antidote": Item("antidote", "Antidote", "potion",
        "Cures poison and venom. Clears the poisoned status.", 25, 0.1),
}


MISC_ITEMS = {
    "gold_coin": Item("gold_coin", "Gold Coins", "misc",
        "The language everyone speaks.", 1, 0.01),
    "dungeon_key": Item("dungeon_key", "Iron Key", "misc",
        "Opens a heavy dungeon door somewhere below.", 0, 0.1),
    "old_scroll": Item("old_scroll", "Tattered Scroll", "misc",
        "Ancient writings — illegible but valuable to scholars.", 15, 0.05),
    "ruby": Item("ruby", "Rough Ruby", "misc",
        "An uncut gemstone of deep crimson.", 80, 0.1),
    "amulet": Item("amulet", "Amulet of Fortitude", "misc",
        "A carved stone amulet that radiates enduring energy.",
        120, 0.2, con_bonus=2, slot="ring", rarity="uncommon"),
}


ALL_ITEMS: dict[str, Item] = {**WEAPONS, **ARMORS, **POTIONS, **MISC_ITEMS}

def get_item(key: str) -> Optional[Item]:
    return ALL_ITEMS.get(key)

def get_starting_weapon(weapon_name: str) -> Item:
    """Find a weapon by display name for class setup."""
    weapon_name_lower = weapon_name.lower().replace(" ", "_")
    if weapon_name_lower in WEAPONS:
        return WEAPONS[weapon_name_lower]
    for item in WEAPONS.values():
        if item.name.lower() == weapon_name.lower():
            return item
    return list(WEAPONS.values())[0]

def get_starting_armor(armor_name: str) -> Item:
    """Find armor by display name for class setup."""
    armor_name_lower = armor_name.lower().replace(" ", "_")
    if armor_name_lower in ARMORS:
        return ARMORS[armor_name_lower]
    for item in ARMORS.values():
        if item.name.lower() == armor_name.lower():
            return item
    return list(ARMORS.values())[0]
