from dataclasses import dataclass, field
from typing import List


@dataclass
class Ability:
    name: str
    description: str
    narrative: str
    mp_cost: int = 0
    damage_base: int = 0
    damage_scale: float = 1.0
    stat_used: str = "str"
    heal_amount: int = 0
    effect: str = ""
    cooldown: int = 0


@dataclass
class ClassTemplate:
    key: str
    name: str
    description: str
    base_hp: int
    base_mp: int
    base_str: int
    base_dex: int
    base_int: int
    base_wis: int
    base_cha: int
    base_con: int
    hp_per_level: int
    mp_per_level: int
    primary_stat: str
    secondary_stat: str
    starting_weapon: str
    starting_armor: str
    lore: str
    abilities: List[Ability] = field(default_factory=list)


CLASSES: dict[str, ClassTemplate] = {}

def _reg(c: ClassTemplate):
    CLASSES[c.key] = c

_reg(ClassTemplate(
    key="guerrero", name="Guerrero", primary_stat="str", secondary_stat="con",
    description="class_desc_guerrero",
    base_hp=120, base_mp=20, base_str=14, base_dex=8,
    base_int=6, base_wis=8, base_cha=8, base_con=14,
    hp_per_level=12, mp_per_level=2,
    starting_weapon="Iron Sword", starting_armor="Chain Mail",
    lore="lore_guerrero",
    abilities=[
        Ability("ab_guerrero_1_name", "ab_guerrero_1_desc",
                "With a savage roar, {name} delivers a crushing blow that splits iron and bone alike!",
                mp_cost=5, damage_base=15, damage_scale=1.5, stat_used="str"),
        Ability("ab_guerrero_2_name", "ab_guerrero_2_desc",
                "{name} grits their teeth against the pain, drawing upon reserves of iron will to endure!",
                mp_cost=8, heal_amount=30, effect=""),
        Ability("ab_guerrero_3_name", "ab_guerrero_3_desc",
                "{name} spins in a deadly arc, their blade singing through the air!",
                mp_cost=12, damage_base=10, damage_scale=1.2, stat_used="str", effect="aoe"),
    ]
))

_reg(ClassTemplate(
    key="mago", name="Mago", primary_stat="int", secondary_stat="wis",
    description="class_desc_mago",
    base_hp=60, base_mp=120, base_str=5, base_dex=8,
    base_int=16, base_wis=12, base_cha=10, base_con=6,
    hp_per_level=5, mp_per_level=14,
    starting_weapon="Oak Staff", starting_armor="Robes",
    lore="lore_mago",
    abilities=[
        Ability("ab_mago_1_name", "ab_mago_1_desc",
                "With a sharp incantation, {name} hurls a roaring sphere of fire that scorches all in its path!",
                mp_cost=15, damage_base=25, damage_scale=2.0, stat_used="int", effect="burn"),
        Ability("ab_mago_2_name", "ab_mago_2_desc",
                "{name} mutters a ward of protection, weaving a shimmering barrier from the aether!",
                mp_cost=10, heal_amount=20, effect="shield"),
        Ability("ab_mago_3_name", "ab_mago_3_desc",
                "{name} channels raw arcane energy into a searing bolt that tears through magical resistance!",
                mp_cost=20, damage_base=30, damage_scale=2.2, stat_used="int"),
    ]
))

_reg(ClassTemplate(
    key="picaro", name="Picaro", primary_stat="dex", secondary_stat="str",
    description="class_desc_picaro",
    base_hp=80, base_mp=40, base_str=10, base_dex=16,
    base_int=10, base_wis=8, base_cha=12, base_con=8,
    hp_per_level=7, mp_per_level=4,
    starting_weapon="Steel Daggers", starting_armor="Leather Armor",
    lore="lore_picaro",
    abilities=[
        Ability("ab_picaro_1_name", "ab_picaro_1_desc",
                "{name} materializes from the darkness, driving twin blades deep into a vital spot!",
                mp_cost=8, damage_base=20, damage_scale=1.8, stat_used="dex"),
        Ability("ab_picaro_2_name", "ab_picaro_2_desc",
                "{name}'s blade drips with foul venom as it finds its mark, promising slow suffering!",
                mp_cost=6, damage_base=8, damage_scale=1.0, stat_used="dex", effect="poison"),
        Ability("ab_picaro_3_name", "ab_picaro_3_desc",
                "{name} becomes a blur of motion, vanishing from sight like smoke in the wind!",
                mp_cost=5, effect="evade"),
    ]
))

_reg(ClassTemplate(
    key="paladin", name="Paladin", primary_stat="str", secondary_stat="cha",
    description="class_desc_paladin",
    base_hp=100, base_mp=70, base_str=12, base_dex=7,
    base_int=8, base_wis=12, base_cha=14, base_con=12,
    hp_per_level=10, mp_per_level=8,
    starting_weapon="Holy Mace", starting_armor="Plate Mail",
    lore="lore_paladin",
    abilities=[
        Ability("ab_paladin_1_name", "ab_paladin_1_desc",
                "{name} calls upon the power of the Light! A blinding radiance erupts from their weapon!",
                mp_cost=12, damage_base=18, damage_scale=1.6, stat_used="cha", effect="holy"),
        Ability("ab_paladin_2_name", "ab_paladin_2_desc",
                "{name} places a gauntleted hand upon their wounds. Golden light flows — flesh knits whole.",
                mp_cost=15, heal_amount=40),
        Ability("ab_paladin_3_name", "ab_paladin_3_desc",
                "{name} radiates a holy aura that drives back shadow and blunts the edge of evil!",
                mp_cost=18, effect="aura"),
    ]
))

_reg(ClassTemplate(
    key="arquero", name="Arquero", primary_stat="dex", secondary_stat="wis",
    description="class_desc_arquero",
    base_hp=75, base_mp=40, base_str=9, base_dex=15,
    base_int=9, base_wis=13, base_cha=10, base_con=9,
    hp_per_level=7, mp_per_level=4,
    starting_weapon="Longbow", starting_armor="Leather Armor",
    lore="lore_arquero",
    abilities=[
        Ability("ab_arquero_1_name", "ab_arquero_1_desc",
                "{name} draws three arrows in a single fluid motion and looses them in a deadly fan!",
                mp_cost=8, damage_base=10, damage_scale=1.3, stat_used="dex", effect="multi"),
        Ability("ab_arquero_2_name", "ab_arquero_2_desc",
                "{name} draws deep, narrows their eye, and fires — the shaft punches through steel plate!",
                mp_cost=10, damage_base=22, damage_scale=1.5, stat_used="dex"),
        Ability("ab_arquero_3_name", "ab_arquero_3_desc",
                "{name} studies their foe with a predator's patience, finding the gap in every guard.",
                mp_cost=7, effect="analyze"),
    ]
))

_reg(ClassTemplate(
    key="barbaro", name="Barbaro", primary_stat="str", secondary_stat="con",
    description="class_desc_barbaro",
    base_hp=140, base_mp=15, base_str=16, base_dex=9,
    base_int=5, base_wis=7, base_cha=7, base_con=16,
    hp_per_level=15, mp_per_level=1,
    starting_weapon="Great Axe", starting_armor="Hide Armor",
    lore="lore_barbaro",
    abilities=[
        Ability("ab_barbaro_1_name", "ab_barbaro_1_desc",
                "{name} lets out a battle cry that shakes the very stones! Blood-rage takes hold!",
                mp_cost=5, effect="rage"),
        Ability("ab_barbaro_2_name", "ab_barbaro_2_desc",
                "{name} heaves their axe in a devastating overhead arc that shakes the earth on impact!",
                mp_cost=8, damage_base=30, damage_scale=2.0, stat_used="str", effect="stun"),
        Ability("ab_barbaro_3_name", "ab_barbaro_3_desc",
                "{name}'s muscles tighten and their skin seems to harden like ancient bark and iron!",
                mp_cost=6, effect="shield"),
    ]
))

_reg(ClassTemplate(
    key="monje", name="Monje", primary_stat="dex", secondary_stat="wis",
    description="class_desc_monje",
    base_hp=85, base_mp=60, base_str=10, base_dex=14,
    base_int=10, base_wis=14, base_cha=9, base_con=10,
    hp_per_level=8, mp_per_level=6,
    starting_weapon="Quarterstaff", starting_armor="Monk Robes",
    lore="lore_monje",
    abilities=[
        Ability("ab_monje_1_name", "ab_monje_1_desc",
                "{name} becomes a whirlwind of fists and feet — five perfect strikes in the span of a breath!",
                mp_cost=10, damage_base=7, damage_scale=1.2, stat_used="dex", effect="multi"),
        Ability("ab_monje_2_name", "ab_monje_2_desc",
                "{name} steadies their breathing, channels inner chi, and closes their wounds through will alone.",
                mp_cost=12, heal_amount=25),
        Ability("ab_monje_3_name", "ab_monje_3_desc",
                "{name} strikes a precise nerve cluster — the enemy's limbs betray them entirely!",
                mp_cost=8, damage_base=12, damage_scale=1.0, stat_used="wis", effect="stun"),
    ]
))

_reg(ClassTemplate(
    key="explorador", name="Explorador", primary_stat="dex", secondary_stat="wis",
    description="class_desc_explorador",
    base_hp=78, base_mp=45, base_str=9, base_dex=14,
    base_int=11, base_wis=14, base_cha=10, base_con=9,
    hp_per_level=7, mp_per_level=5,
    starting_weapon="Short Sword + Dagger", starting_armor="Studded Leather",
    lore="lore_explorador",
    abilities=[
        Ability("ab_explorador_1_name", "ab_explorador_1_desc",
                "{name} brands their quarry with a hunter's mark — every blow will find its way true!",
                mp_cost=6, damage_base=5, damage_scale=0.8, stat_used="wis", effect="mark"),
        Ability("ab_explorador_2_name", "ab_explorador_2_desc",
                "{name} flows through a practiced dual-strike — blade and dagger in perfect sequence!",
                mp_cost=8, damage_base=12, damage_scale=1.4, stat_used="dex", effect="multi"),
        Ability("ab_explorador_3_name", "ab_explorador_3_desc",
                "{name} studies their foe with a predator's patience, finding the gap in every guard.",
                mp_cost=7, effect="analyze"),
    ]
))

_reg(ClassTemplate(
    key="hechicero", name="Hechicero", primary_stat="int", secondary_stat="cha",
    description="class_desc_hechicero",
    base_hp=65, base_mp=100, base_str=5, base_dex=9,
    base_int=15, base_wis=10, base_cha=14, base_con=7,
    hp_per_level=5, mp_per_level=12,
    starting_weapon="Arcane Focus", starting_armor="Mage Robes",
    lore="lore_hechicero",
    abilities=[
        Ability("ab_hechicero_1_name", "ab_hechicero_1_desc",
                "{name} releases a torrent of raw chaos! The air cracks and reality screams!",
                mp_cost=14, damage_base=20, damage_scale=2.1, stat_used="int", effect="chaos"),
        Ability("ab_hechicero_2_name", "ab_hechicero_2_desc",
                "{name} twists the weave of magic itself, bending the laws of the arcane to their will!",
                mp_cost=16, effect="empower"),
        Ability("ab_hechicero_3_name", "ab_hechicero_3_desc",
                "{name} detonates a pulse of raw magical energy that warps space in a visible shockwave!",
                mp_cost=18, damage_base=22, damage_scale=1.8, stat_used="int", effect="stun"),
    ]
))

_reg(ClassTemplate(
    key="brujo", name="Brujo", primary_stat="cha", secondary_stat="int",
    description="class_desc_brujo",
    base_hp=70, base_mp=85, base_str=6, base_dex=10,
    base_int=13, base_wis=9, base_cha=16, base_con=8,
    hp_per_level=6, mp_per_level=10,
    starting_weapon="Cursed Tome", starting_armor="Dark Robes",
    lore="lore_brujo",
    abilities=[
        Ability("ab_brujo_1_name", "ab_brujo_1_desc",
                "{name}'s eyes go black as they speak syllables from no human tongue — a curse takes root!",
                mp_cost=10, damage_base=18, damage_scale=1.7, stat_used="cha", effect="curse"),
        Ability("ab_brujo_2_name", "ab_brujo_2_desc",
                "{name} reaches across reality itself, fingers touching something that should not exist...",
                mp_cost=14, damage_base=15, damage_scale=1.5, stat_used="cha", effect="drain"),
        Ability("ab_brujo_3_name", "ab_brujo_3_desc",
                "The air turns cold and sulfurous as {name}'s dark patron manifests its terrible attention!",
                mp_cost=22, damage_base=35, damage_scale=2.0, stat_used="cha", cooldown=3),
    ]
))
