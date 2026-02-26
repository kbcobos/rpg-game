from dataclasses import dataclass, field
from typing import List, Optional
import random


@dataclass
class EnemyTemplate:
    key: str
    name: str
    description: str
    hp: int
    mp: int
    attack: int
    defense: int
    speed: int
    xp_reward: int
    gold_min: int
    gold_max: int
    str_stat: int = 8
    dex_stat: int = 8
    int_stat: int = 6
    abilities: list = field(default_factory=list)
    loot_table: list = field(default_factory=list)
    tier: int = 1
    art_key: str = "goblin"
    is_undead: bool = False
    is_boss: bool = False
    attack_phrases: list = field(default_factory=list)


ENEMIES = {

"goblin": EnemyTemplate(
    key="goblin", name="Goblin Scout", tier=1, art_key="goblin",
    description="Un goblin flacucho y verdoso con un cuchillo más oxidado que los caños de tu edificio. Parece que no comió en tres días. Igual te va a atacar.",
    hp=35, mp=0, attack=8, defense=3, speed=12,
    xp_reward=40, gold_min=3, gold_max=12,
    str_stat=7, dex_stat=12, int_stat=5,
    loot_table=["health_potion", "gold_coin"],
    attack_phrases=[
        "The Goblin Scout lunges with its rusty knife!",
        "The Goblin bares its rotten teeth and slashes!",
        "With a shriek, the Goblin drives its blade forward!",
    ]
),

"goblin_shaman": EnemyTemplate(
    key="goblin_shaman", name="Goblin Shaman", tier=1, art_key="goblin",
    description="Un goblin jorobado con huesos colgando por todos lados. Claramente el intelectual del grupo. Eso no lo hace menos peligroso, sí más raro.",
    hp=28, mp=40, attack=6, defense=2, speed=9,
    xp_reward=55, gold_min=5, gold_max=18,
    str_stat=5, dex_stat=9, int_stat=12,
    abilities=[("Hex Bolt", 1.4, "burn", 8)],
    loot_table=["mana_potion", "old_scroll"],
    attack_phrases=[
        "The Goblin Shaman chants in a guttural tongue, hurling dark energy!",
        "Fetishes rattle as the Shaman channels foul magic!",
    ]
),

"giant_rat": EnemyTemplate(
    key="giant_rat", name="Giant Dungeon Rat", tier=1, art_key="goblin",
    description="Una rata del tamaño de un perro mediano. La encontraste en la mazmorra pero podría ser perfectamente del subte de la línea B.",
    hp=25, mp=0, attack=7, defense=2, speed=15,
    xp_reward=25, gold_min=0, gold_max=5,
    str_stat=8, dex_stat=14, int_stat=2,
    abilities=[("Rabid Bite", 1.2, "poison", 0)],
    loot_table=["antidote"],
    attack_phrases=[
        "The Giant Rat snaps its yellowed teeth at your ankles!",
        "With vicious speed, the rat lunges for your throat!",
    ]
),

"skeleton": EnemyTemplate(
    key="skeleton", name="Risen Skeleton", tier=1, art_key="skeleton",
    description="Huesos pegados con magia oscura y ganas de molestar. El cuchillo está más oxidado que una heladera de los 90. Pero igual duele.",
    hp=40, mp=0, attack=9, defense=5, speed=7,
    xp_reward=50, gold_min=2, gold_max=10,
    str_stat=9, dex_stat=6, int_stat=3,
    is_undead=True,
    loot_table=["health_potion"],
    attack_phrases=[
        "The Skeleton swings its corroded blade with mechanical precision!",
        "Bone fingers grip the sword tighter as the Skeleton advances!",
        "The Skeleton's jaw clicks open in a soundless battle cry!",
    ]
),


"orc": EnemyTemplate(
    key="orc", name="Orc Warrior", tier=2, art_key="orc",
    description="Un orco enorme con colmillos y una armadura de hierro que claramente no limpió nunca. Huele a sangre y a algo que preferís no identificar.",
    hp=80, mp=0, attack=14, defense=8, speed=8,
    xp_reward=90, gold_min=10, gold_max=30,
    str_stat=15, dex_stat=7, int_stat=5,
    abilities=[("Brutal Smash", 1.8, "stun", 0)],
    loot_table=["health_potion", "chain_mail", "iron_sword"],
    attack_phrases=[
        "The Orc Warrior bellows a war cry and charges with its iron blade!",
        "Massive arms swing the Orc's weapon in a brutal overhead arc!",
        "The Orc grabs you by the collar and headbutts you savagely!",
    ]
),

"dark_elf": EnemyTemplate(
    key="dark_elf", name="Dark Elf Assassin", tier=2, art_key="goblin",
    description="Una figura elegante de seda negra con dos dagas envenenadas. Vestida mejor que vos. Mucho mejor. Algo que también duele, pero diferente.",
    hp=60, mp=30, attack=15, defense=6, speed=18,
    xp_reward=100, gold_min=15, gold_max=45,
    str_stat=10, dex_stat=16, int_stat=12,
    abilities=[("Shadow Strike", 1.9, "poison", 8), ("Smoke Bomb", 1.0, "evade", 10)],
    loot_table=["steel_daggers", "mana_potion", "ruby"],
    attack_phrases=[
        "The Dark Elf flows like shadow, blades finding every gap in your guard!",
        "With inhuman speed, the assassin vanishes and reappears at your side!",
        "Venom-coated steel traces burning lines across your skin!",
    ]
),

"zombie_knight": EnemyTemplate(
    key="zombie_knight", name="Zombie Knight", tier=2, art_key="skeleton",
    description="Fue noble, ahora es un horror podrido con armadura oxidada. Igual tiene más postura que la mayoría. La muerte no le quitó el porte, lamentablemente.",
    hp=95, mp=0, attack=13, defense=12, speed=5,
    xp_reward=110, gold_min=20, gold_max=50,
    str_stat=14, dex_stat=5, int_stat=2,
    is_undead=True,
    abilities=[("Death Grip", 1.5, "stun", 0)],
    loot_table=["plate_mail", "health_potion", "amulet"],
    attack_phrases=[
        "The Zombie Knight raises its corroded blade with terrible slowness — then strikes like a falling wall!",
        "Rotting fingers grip your arm with the strength of death itself!",
    ]
),

"witch": EnemyTemplate(
    key="witch", name="Dungeon Witch", tier=2, art_key="witch",
    description="Una bruja riéndose sola rodeada de humo verde. El caldero burbujea con algo que definitivamente no es mate. Claramente le va bien en lo suyo.",
    hp=55, mp=80, attack=11, defense=5, speed=10,
    xp_reward=105, gold_min=12, gold_max=40,
    str_stat=6, dex_stat=9, int_stat=15,
    abilities=[("Hex Bolt", 1.6, "curse", 12), ("Poison Brew", 1.3, "poison", 8)],
    loot_table=["mana_potion", "antidote", "old_scroll"],
    attack_phrases=[
        "The Witch points a gnarled finger — dark energy crackles toward you!",
        "A vile laugh precedes the wave of sickly green magic!",
        "The Witch flings a smoking flask of poisonous brew!",
    ]
),


"vampire": EnemyTemplate(
    key="vampire", name="Vampire Lord", tier=3, art_key="vampire",
    description="Pálido, frío y con aires de superioridad. Tiene siglos de experiencia haciéndote sentir inferior. Como ese compañero de trabajo pero con colmillos.",
    hp=130, mp=60, attack=18, defense=10, speed=16,
    xp_reward=200, gold_min=40, gold_max=100,
    str_stat=16, dex_stat=14, int_stat=14,
    is_undead=True,
    abilities=[("Life Drain", 1.7, "drain", 15), ("Hypnotic Gaze", 1.0, "stun", 12)],
    loot_table=["shadowblade", "ruby", "elixir"],
    attack_phrases=[
        "The Vampire Lord moves faster than the eye can follow, fangs at your throat!",
        "Cold fingers close around your life force, drawing it away like candlelight in wind!",
        "The Vampire's eyes blaze crimson — your will bends before its ancient gaze!",
    ]
),

"stone_golem": EnemyTemplate(
    key="stone_golem", name="Stone Golem", tier=3, art_key="orc",
    description="Dos metros y medio de granito animado con runas brillando en el pecho. No corre. No habla. No negocia. Simplemente viene hacia vos. Tranquilamente.",
    hp=160, mp=20, attack=20, defense=18, speed=4,
    xp_reward=220, gold_min=30, gold_max=80,
    str_stat=20, dex_stat=3, int_stat=4,
    abilities=[("Fist of Stone", 2.0, "stun", 0)],
    loot_table=["mithril_shirt", "ruby", "amulet"],
    attack_phrases=[
        "The Golem's massive fist descends like a boulder from a cliff!",
        "With a grinding of ancient stone, the Golem sweeps its arm — you are flung across the room!",
        "The runes on its chest blaze white hot as it slams the ground with titanic force!",
    ]
),

"demon": EnemyTemplate(
    key="demon", name="Lesser Demon", tier=3, art_key="demon",
    description="Una criatura de fuego y odio puro con alas de cuero quemado. Tiene los ojos como brasas y la actitud de alguien a quien le cancelaron el vuelo y perdió las valijas.",
    hp=120, mp=70, attack=19, defense=9, speed=14,
    xp_reward=230, gold_min=35, gold_max=90,
    str_stat=17, dex_stat=13, int_stat=13,
    abilities=[("Hellfire", 1.8, "burn", 18), ("Fear Aura", 1.0, "fear", 12)],
    loot_table=["enchanted_staff", "ruby", "elixir"],
    attack_phrases=[
        "The Demon spreads its wings and unleashes a torrent of hellfire!",
        "Claws of black iron rake across you, trailing fire in their wake!",
        "An aura of pure dread radiates from the Demon — your courage wavers!",
    ]
),


"dragon": EnemyTemplate(
    key="dragon", name="Aethoran Dragon", tier=4, art_key="dragon",
    is_boss=True,
    description="Un dragón enorme. En serio, es GRANDE. No, más grande que eso. Llevás toda la mazmorra pensando que el final iba a ser manejable. Error de cálculo.",
    hp=400, mp=150, attack=30, defense=20, speed=12,
    xp_reward=1000, gold_min=200, gold_max=500,
    str_stat=25, dex_stat=12, int_stat=18,
    abilities=[
        ("Dragon Breath", 2.5, "burn", 20),
        ("Crushing Claw", 2.0, "stun", 0),
        ("Tail Sweep", 1.6, "aoe", 0),
    ],
    loot_table=["dragonslayer", "dragonscale_armor", "ruby", "elixir"],
    attack_phrases=[
        "The Dragon opens its maw — the air glows orange before the inferno erupts!",
        "A claw the size of a cart wheel slams down where you were standing!",
        "The Dragon's tail sweeps the entire chamber in a devastating arc!",
        "Ancient eyes regard you with cold contempt before the Dragon strikes!",
    ]
),

"lich": EnemyTemplate(
    key="lich", name="The Lich Archmage", tier=4, art_key="skeleton",
    is_boss=True, is_undead=True,
    description="Fue el mejor mago del mundo y eligió la inmortalidad. Ahora es un esqueleto con actitud. Morirse hubiera sido más elegante, pero nadie le preguntó.",
    hp=300, mp=300, attack=25, defense=14, speed=10,
    xp_reward=900, gold_min=150, gold_max=400,
    str_stat=8, dex_stat=10, int_stat=22,
    abilities=[
        ("Death Ray", 2.8, "freeze", 25),
        ("Raise Dead", 1.0, "summon", 20),
        ("Soul Drain", 2.0, "drain", 18),
    ],
    loot_table=["enchanted_staff", "mana_potion", "ruby", "old_scroll"],
    attack_phrases=[
        "The Lich raises its phylactery — a beam of pure death tears through reality toward you!",
        "Skeletal fingers weave a sigil of annihilation in the cold air!",
        "The Lich laughs — a sound like a crypt door — and reality darkens around its hands!",
    ]
),

"ancient_demon": EnemyTemplate(
    key="ancient_demon", name="Archfiend Malachar", tier=4, art_key="demon",
    is_boss=True,
    description="El verdadero dueño de la mazmorra. Tres siglos encerrado acá abajo. Está de mal humor, con razón. Vos sos lo primero que va a ver al salir. Mala suerte.",
    hp=500, mp=200, attack=35, defense=22, speed=15,
    xp_reward=2000, gold_min=300, gold_max=800,
    str_stat=22, dex_stat=15, int_stat=20,
    abilities=[
        ("Hellfire Nova", 3.0, "burn", 30),
        ("Void Crush", 2.5, "stun", 25),
        ("Soul Harvest", 2.0, "drain", 20),
    ],
    loot_table=["dragonslayer", "dragonscale_armor", "elixir", "ruby"],
    attack_phrases=[
        "Malachar's laugh is the sound of worlds ending. It raises one hand — reality tears!",
        "The air ignites as the Archfiend channels power that was old before your world had a name!",
        "Your very soul trembles as Malachar turns its full terrible attention upon you!",
    ]
),

}


def get_enemies_by_tier(tier: int) -> list:
    """Return all enemy templates of a given tier."""
    return [e for e in ENEMIES.values() if e.tier == tier and not e.is_boss]

def get_random_enemy(tier: int) -> EnemyTemplate:
    """Return a random non-boss enemy of the given tier."""
    pool = get_enemies_by_tier(tier)
    if not pool:
        pool = get_enemies_by_tier(1)
    return random.choice(pool)

def get_boss(key: str = None) -> EnemyTemplate:
    """Return a boss by key, or a random one."""
    bosses = [e for e in ENEMIES.values() if e.is_boss]
    if key and key in ENEMIES:
        return ENEMIES[key]
    return random.choice(bosses)
