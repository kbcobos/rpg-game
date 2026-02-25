from dataclasses import dataclass, field
from typing import List


@dataclass
class Ability:
    """A special ability or skill belonging to a class."""
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
    """Blueprint for a player class."""
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
    description="Maestro del combate cuerpo a cuerpo. Resistente y poderoso.",
    base_hp=120, base_mp=20, base_str=14, base_dex=8,
    base_int=6, base_wis=8, base_cha=8, base_con=14,
    hp_per_level=12, mp_per_level=2,
    starting_weapon="Iron Sword", starting_armor="Chain Mail",
    lore="Nació peleando y nunca paró. Tiene más cicatrices que el auto del tío de un amigo. "
         "No estudió mucho, pero lo que sabe lo sabe con el cuerpo. Especialmente el dolor ajeno.",
    abilities=[
        Ability("Golpe Poderoso", "Ataque devastador que ignora parte de la armadura.",
                "With a savage roar, {name} delivers a crushing blow that splits iron and bone alike!",
                mp_cost=5, damage_base=15, damage_scale=1.5, stat_used="str"),
        Ability("Segunda Oportunidad", "Te recuperas con 30 HP cuando estas cerca de morir.",
                "{name} grits their teeth against the pain, drawing upon reserves of iron will to endure!",
                mp_cost=8, heal_amount=30, effect=""),
        Ability("Golpe Torbellino", "Atacas a todos los enemigos en el turno.",
                "{name} spins in a deadly arc, their blade singing through the air!",
                mp_cost=12, damage_base=10, damage_scale=1.2, stat_used="str", effect="aoe"),
    ]
))

_reg(ClassTemplate(
    key="mago", name="Mago", primary_stat="int", secondary_stat="wis",
    description="Wielder of arcane forces. Fragile but devastatingly powerful.",
    base_hp=60, base_mp=120, base_str=5, base_dex=8,
    base_int=16, base_wis=12, base_cha=10, base_con=6,
    hp_per_level=5, mp_per_level=14,
    starting_weapon="Oak Staff", starting_armor="Robes",
    lore="Pasó veinte años estudiando en la Torre Arcana. No consiguió laburo en su especialidad. "
         "Ahora tira bolas de fuego en una mazmorra. Algo es algo.",
    abilities=[
        Ability("Bola de Fuego", "Lanza una esfera de fuego que quema al enemigo.",
                "With a sharp incantation, {name} hurls a roaring sphere of fire that scorches all in its path!",
                mp_cost=15, damage_base=25, damage_scale=2.0, stat_used="int", effect="burn"),
        Ability("Rayo Arcano", "Un rayo de energia pura de maximo poder.",
                "{name} channels raw arcane energy into a searing bolt that tears through magical resistance!",
                mp_cost=20, damage_base=30, damage_scale=2.2, stat_used="int"),
        Ability("Escudo Magico", "Crea un escudo que absorbe dano por 2 turnos.",
                "{name} mutters a ward of protection, weaving a shimmering barrier from the aether!",
                mp_cost=10, heal_amount=20, effect="shield"),
    ]
))

_reg(ClassTemplate(
    key="picaro", name="Picaro", primary_stat="dex", secondary_stat="str",
    description="Shadow and blade. Strikes fast, strikes first, strikes deadly.",
    base_hp=80, base_mp=40, base_str=10, base_dex=16,
    base_int=10, base_wis=8, base_cha=12, base_con=8,
    hp_per_level=7, mp_per_level=4,
    starting_weapon="Steel Daggers", starting_armor="Leather Armor",
    lore="Creció en el barrio bravo y aprendió rápido que el que pega primero, pega dos veces. "
         "Opera desde las sombras, básicamente lo mismo que hacer las cosas a último momento pero con más dramatismo.",
    abilities=[
        Ability("Ataque Furtivo", "Golpe critico desde las sombras. Alto dano.",
                "{name} materializes from the darkness, driving twin blades deep into a vital spot!",
                mp_cost=8, damage_base=20, damage_scale=1.8, stat_used="dex"),
        Ability("Veneno", "Envenena al enemigo, causando dano a lo largo del tiempo.",
                "{name}'s blade drips with foul venom as it finds its mark, promising slow suffering!",
                mp_cost=6, damage_base=8, damage_scale=1.0, stat_used="dex", effect="poison"),
        Ability("Evasion", "Evades the next attack completely (1 turn).",
                "{name} becomes a blur of motion, vanishing from sight like smoke in the wind!",
                mp_cost=5, effect="evade"),
    ]
))

_reg(ClassTemplate(
    key="paladin", name="Paladin", primary_stat="str", secondary_stat="cha",
    description="Holy warrior. Heals allies and smites evil with divine power.",
    base_hp=100, base_mp=70, base_str=12, base_dex=7,
    base_int=8, base_wis=12, base_cha=14, base_con=12,
    hp_per_level=10, mp_per_level=8,
    starting_weapon="Holy Mace", starting_armor="Plate Mail",
    lore="Hizo el juramento solemne de defender la Luz. Lo cumple, en general. "
         "Los no-muertos le tienen pánico. Los vivos también, pero por otras razones. Es un poco intenso en los asados.",
    abilities=[
        Ability("Golpe Divino", "Canaliza la luz divina en un ataque sagrado.",
                "{name} calls upon the power of the Light! A blinding radiance erupts from their weapon!",
                mp_cost=12, damage_base=18, damage_scale=1.6, stat_used="cha", effect="holy"),
        Ability("Imposicion de Manos", "Sana heridas propias con energia divina.",
                "{name} places a gauntleted hand upon their wounds. Golden light flows — flesh knits whole.",
                mp_cost=15, heal_amount=40),
        Ability("Aura Sagrada", "Aura que reduce el dano recibido por 3 turnos.",
                "{name} radiates a holy aura that drives back shadow and blunts the edge of evil!",
                mp_cost=18, effect="aura"),
    ]
))

_reg(ClassTemplate(
    key="arquero", name="Arquero", primary_stat="dex", secondary_stat="wis",
    description="Master of ranged combat. Precise, swift, and deadly from afar.",
    base_hp=75, base_mp=40, base_str=9, base_dex=15,
    base_int=9, base_wis=13, base_cha=10, base_con=9,
    hp_per_level=7, mp_per_level=4,
    starting_weapon="Longbow", starting_armor="Leather Armor",
    lore="Creció en el bosque y nunca más salió. Come frutos silvestres, habla poco y dispara mejor que nadie. "
         "No lo invités a cumpleaños — va a aparecer desde atrás de un árbol.",
    abilities=[
        Ability("Disparo Multiple", "Lanza 3 flechas de una vez.",
                "{name} draws three arrows in a single fluid motion and looses them in a deadly fan!",
                mp_cost=8, damage_base=10, damage_scale=1.3, stat_used="dex", effect="multi"),
        Ability("Flecha Perforadora", "Una flecha que atraviesa la armadura.",
                "{name} draws deep, narrows their eye, and fires — the shaft punches through steel plate!",
                mp_cost=10, damage_base=22, damage_scale=1.5, stat_used="dex"),
        Ability("Trampa", "Coloca una trampa que inmoviliza al enemigo 1 turno.",
                "{name} hurls a spiked snare at their foe's feet — iron teeth snap shut with a crack!",
                mp_cost=6, effect="stun"),
    ]
))

_reg(ClassTemplate(
    key="barbaro", name="Barbaro", primary_stat="str", secondary_stat="con",
    description="Unstoppable force of nature. Rages beyond pain and reason.",
    base_hp=140, base_mp=15, base_str=16, base_dex=9,
    base_int=5, base_wis=7, base_cha=7, base_con=16,
    hp_per_level=15, mp_per_level=1,
    starting_weapon="Great Axe", starting_armor="Hide Armor",
    lore="Viene de un lugar muy frío donde no hay mucho que hacer aparte de enojarse. "
         "No tiene estrategia. No necesita una. Su plan es ir para adelante hasta que algo pare. Generalmente no es él.",
    abilities=[
        Ability("Furia", "Entra en estado de rabia: +50% dano, -20% defensa por 3 turnos.",
                "{name} lets out a battle cry that shakes the very stones! Blood-rage takes hold!",
                mp_cost=5, effect="rage"),
        Ability("Golpe Devastador", "Ataque masivo de un solo golpe. Puede aturdir.",
                "{name} heaves their axe in a devastating overhead arc that shakes the earth on impact!",
                mp_cost=8, damage_base=30, damage_scale=2.0, stat_used="str", effect="stun"),
        Ability("Piel de Piedra", "La furia endurece tu piel: absorbe el siguiente ataque.",
                "{name}'s muscles tighten and their skin seems to harden like ancient bark and iron!",
                mp_cost=6, effect="shield"),
    ]
))

_reg(ClassTemplate(
    key="monje", name="Monje", primary_stat="dex", secondary_stat="wis",
    description="Martial arts master. Combines speed, inner balance, and discipline.",
    base_hp=85, base_mp=60, base_str=10, base_dex=14,
    base_int=10, base_wis=14, base_cha=9, base_con=10,
    hp_per_level=8, mp_per_level=6,
    starting_weapon="Quarterstaff", starting_armor="Monk Robes",
    lore="Meditó diez mil horas para encontrar la paz interior. La encontró. "
         "Resulta que la paz interior se parece mucho a cinco piñas consecutivas en la cara. Filosofía profunda.",
    abilities=[
        Ability("Torrente de Golpes", "Desata 5 golpes rapidos consecutivos.",
                "{name} becomes a whirlwind of fists and feet — five perfect strikes in the span of a breath!",
                mp_cost=10, damage_base=7, damage_scale=1.2, stat_used="dex", effect="multi"),
        Ability("Chi Curativo", "Medita brevemente para recuperar 25 HP.",
                "{name} steadies their breathing, channels inner chi, and closes their wounds through will alone.",
                mp_cost=12, heal_amount=25),
        Ability("Golpe Paralizante", "Un golpe preciso que deja al enemigo aturdido.",
                "{name} strikes a precise nerve cluster — the enemy's limbs betray them entirely!",
                mp_cost=8, damage_base=12, damage_scale=1.0, stat_used="wis", effect="stun"),
    ]
))

_reg(ClassTemplate(
    key="explorador", name="Explorador", primary_stat="dex", secondary_stat="wis",
    description="Master of terrain and survival. Reads the dungeon like a book.",
    base_hp=78, base_mp=45, base_str=9, base_dex=14,
    base_int=11, base_wis=14, base_cha=10, base_con=9,
    hp_per_level=7, mp_per_level=5,
    starting_weapon="Short Sword + Dagger", starting_armor="Studded Leather",
    lore="Lee la mazmorra como si fuera el subte: sabe exactamente cuándo viene el peligro, "
         "dónde están las salidas y cuál pasillo huele peor. Prefiere ir solo. Los otros hacen ruido.",
    abilities=[
        Ability("Marca del Cazador", "Marca al enemigo, aumentando el dano que recibe.",
                "{name} brands their quarry with a hunter's mark — every blow will find its way true!",
                mp_cost=6, damage_base=5, damage_scale=0.8, stat_used="wis", effect="mark"),
        Ability("Golpe Doble", "Ataca dos veces con ambas manos.",
                "{name} flows through a practiced dual-strike — blade and dagger in perfect sequence!",
                mp_cost=8, damage_base=12, damage_scale=1.4, stat_used="dex", effect="multi"),
        Ability("Sentidos Aguzados", "Detecta el punto debil del enemigo (+30% dano por 2 turnos).",
                "{name} studies their foe with a predator's patience, finding the gap in every guard.",
                mp_cost=7, effect="analyze"),
    ]
))

_reg(ClassTemplate(
    key="hechicero", name="Hechicero", primary_stat="int", secondary_stat="cha",
    description="Wild magic born in the blood. Unpredictable and terrifyingly powerful.",
    base_hp=65, base_mp=100, base_str=5, base_dex=9,
    base_int=15, base_wis=10, base_cha=14, base_con=7,
    hp_per_level=5, mp_per_level=12,
    starting_weapon="Arcane Focus", starting_armor="Mage Robes",
    lore="La magia le salió sola, sin estudiar. A sus compañeros de escuela los ponía nerviosos. "
         "No controla del todo lo que hace. El 65% de las veces sale bien. El otro 35% también es interesante.",
    abilities=[
        Ability("Caos Arcano", "Lanza energia caotica impredecible — alto dano variable.",
                "{name} releases a torrent of raw chaos! The air cracks and reality screams!",
                mp_cost=14, damage_base=20, damage_scale=2.1, stat_used="int", effect="chaos"),
        Ability("Metamagia", "Duplica el poder del siguiente hechizo.",
                "{name} twists the weave of magic itself, bending the laws of the arcane to their will!",
                mp_cost=16, effect="empower"),
        Ability("Pulso de Mana", "Libera mana en explosion que dana y aturde.",
                "{name} detonates a pulse of raw magical energy that warps space in a visible shockwave!",
                mp_cost=18, damage_base=22, damage_scale=1.8, stat_used="int", effect="stun"),
    ]
))

_reg(ClassTemplate(
    key="brujo", name="Brujo", primary_stat="cha", secondary_stat="int",
    description="Bound to a dark patron. Draws power from forbidden pacts.",
    base_hp=70, base_mp=85, base_str=6, base_dex=10,
    base_int=13, base_wis=9, base_cha=16, base_con=8,
    hp_per_level=6, mp_per_level=10,
    starting_weapon="Cursed Tome", starting_armor="Dark Robes",
    lore="Le rezó a algo en la oscuridad y eso le contestó. No sabe bien qué fue. Prefiere no preguntar. "
         "El alquiler no se paga solo y los pactos oscuros tienen mejores condiciones que los bancos.",
    abilities=[
        Ability("Maldicion Eldritch", "Maldice al enemigo con energia oscura.",
                "{name}'s eyes go black as they speak syllables from no human tongue — a curse takes root!",
                mp_cost=10, damage_base=18, damage_scale=1.7, stat_used="cha", effect="curse"),
        Ability("Toque del Vacio", "El vacio drena la vida del enemigo para ti.",
                "{name} reaches across reality itself, fingers touching something that should not exist...",
                mp_cost=14, damage_base=15, damage_scale=1.5, stat_used="cha", effect="drain"),
        Ability("Invocacion del Patron", "Invoca a tu patron para un ataque devastador.",
                "The air turns cold and sulfurous as {name}'s dark patron manifests its terrible attention!",
                mp_cost=22, damage_base=35, damage_scale=2.0, stat_used="cha", cooldown=3),
    ]
))
