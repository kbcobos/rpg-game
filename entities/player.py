import math
from entities.character import Character
from data.classes import ClassTemplate, Ability, CLASSES
from data.items import Item, get_starting_weapon, get_starting_armor
from config import MAX_INVENTORY_SIZE, XP_BASE, MAX_LEVEL, STAT_CAP


class Player(Character):
    """
    Represents the player character.
    Extends Character with: class system, leveling, inventory, equipment,
    gold, cooldown tracking, and JSON serialization.
    """

    def __init__(self, name: str, class_template: ClassTemplate):
        self.char_class = class_template
        ct = class_template

        super().__init__(
            name=name,
            max_hp=ct.base_hp,
            max_mp=ct.base_mp,
            strength=ct.base_str,
            dexterity=ct.base_dex,
            intelligence=ct.base_int,
            wisdom=ct.base_wis,
            charisma=ct.base_cha,
            constitution=ct.base_con,
            attack_power=10,
            defense=5,
        )

        self.level = 1
        self.xp = 0
        self.xp_to_next = XP_BASE
        self.gold = 50

        self.inventory: list[Item] = []
        self.equipped_weapon: Item | None = None
        self.equipped_armor: Item | None = None
        self.equipped_ring: Item | None = None

        self.cooldowns: dict[str, int] = {}

        self.kills = 0
        self.floors_cleared = 0
        self.dungeon_floor = 1

        weapon = get_starting_weapon(ct.starting_weapon)
        armor  = get_starting_armor(ct.starting_armor)
        self._equip(weapon)
        self._equip(armor)

        self._recalculate_stats()


    def _recalculate_stats(self):
        """Recompute attack and defense from stats + equipment."""
        ct = self.char_class

        primary = self.stat_by_name(ct.primary_stat)
        weapon_bonus = self.equipped_weapon.attack_bonus if self.equipped_weapon else 0
        self.base_attack = 10 + primary + weapon_bonus

        armor_bonus = self.equipped_armor.defense_bonus if self.equipped_armor else 0
        ring_def = self.equipped_ring.defense_bonus if self.equipped_ring else 0
        self.base_defense = (self.constitution // 3) + armor_bonus + ring_def


    def _equip(self, item: Item):
        """Directly equip an item without adding to inventory (used on init)."""
        if item.item_type == "weapon":
            self.equipped_weapon = item
        elif item.item_type == "armor":
            self.equipped_armor = item
        elif item.slot == "ring":
            self.equipped_ring = item

    def equip_item(self, item: Item) -> tuple[bool, str]:
        """
        Equip an item from inventory.
        Returns (success, message).
        """
        if item.item_type not in ("weapon", "armor") and item.slot != "ring":
            return False, f"{item.name} no se puede equipar, lamentablemente."

        old = None
        if item.item_type == "weapon":
            old = self.equipped_weapon
            self.equipped_weapon = item
        elif item.item_type == "armor":
            old = self.equipped_armor
            self.equipped_armor = item
        elif item.slot == "ring":
            old = self.equipped_ring
            self.equipped_ring = item

        if item in self.inventory:
            self.inventory.remove(item)
        if old:
            self.inventory.append(old)

        self._apply_ring_bonuses(old, equip=False)
        self._apply_ring_bonuses(item, equip=True)

        self._recalculate_stats()
        return True, f"You equip the {item.name}."

    def _apply_ring_bonuses(self, item: Item | None, equip: bool):
        """Apply or remove stat bonuses from ring-type items."""
        if not item or item.slot != "ring":
            return
        sign = 1 if equip else -1
        self.strength     += sign * item.str_bonus
        self.dexterity    += sign * item.dex_bonus
        self.intelligence += sign * item.int_bonus
        self.wisdom       += sign * item.wis_bonus
        self.charisma     += sign * item.cha_bonus
        self.constitution += sign * item.con_bonus

    def add_to_inventory(self, item: Item) -> tuple[bool, str]:
        """Add an item to inventory. Returns (success, message)."""
        if len(self.inventory) >= MAX_INVENTORY_SIZE:
            return False, "La mochila está llena. Tirar algo primero, che."
        self.inventory.append(item)
        return True, f"You pick up: {item.name}"

    def remove_from_inventory(self, item: Item) -> bool:
        if item in self.inventory:
            self.inventory.remove(item)
            return True
        return False

    def use_potion(self, item: Item) -> tuple[bool, str]:
        """Use a consumable from inventory. Returns (used, message)."""
        if item.item_type != "potion":
            return False, f"{item.name} no se puede usar de esa manera."
        messages = []
        if item.heal_hp > 0:
            restored = self.heal(item.heal_hp)
            messages.append(f"You restore {restored} HP.")
        if item.heal_mp > 0:
            restored_mp = self.restore_mp(item.heal_mp)
            messages.append(f"You restore {restored_mp} MP.")
        if item.name == "Antidote":
            self.remove_status("poison")
            messages.append("El veneno se va. Casi no fue.")
        self.remove_from_inventory(item)
        return True, " ".join(messages)


    def gain_xp(self, amount: int) -> list[str]:
        """
        Award XP. Handles level-up chain.
        Returns a list of narrative messages.
        """
        messages = []
        self.xp += amount
        messages.append(f"  Ganaste {amount} puntos de experiencia. Algo aprendiste.")

        while self.xp >= self.xp_to_next and self.level < MAX_LEVEL:
            self.xp -= self.xp_to_next
            self._level_up()
            messages.append(f"")
            messages.append(f"  *** SUBISTE DE NIVEL, CAMPEÓN! Sos nivel {self.level} ahora! ***")
            messages.append(f"  HP: +{self.char_class.hp_per_level}  |  "
                            f"MP: +{self.char_class.mp_per_level}  |  Te sentís posta.")
            messages.append(f"  Tu poder creció. La oscuridad retrocede. Por ahora. Disfrutalo.")
            self.xp_to_next = int(XP_BASE * (self.level ** 1.4))

        return messages

    def _level_up(self):
        ct = self.char_class
        self.level += 1

        hp_gain = ct.hp_per_level
        mp_gain = ct.mp_per_level
        self.max_hp += hp_gain
        self.max_mp += mp_gain
        self.current_hp = min(self.max_hp, self.current_hp + hp_gain // 2)
        self.current_mp = min(self.max_mp, self.current_mp + mp_gain // 2)

        primary = ct.primary_stat
        secondary = ct.secondary_stat
        self._grow_stat(primary, 2)
        self._grow_stat(secondary, 1)
        if self.level % 3 == 0:
            for stat in ("str", "dex", "int", "wis", "cha", "con"):
                if stat not in (primary, secondary):
                    self._grow_stat(stat, 1)

        self._recalculate_stats()

    def _grow_stat(self, stat: str, amount: int):
        attr_map = {
            "str": "strength", "dex": "dexterity", "int": "intelligence",
            "wis": "wisdom", "cha": "charisma", "con": "constitution",
        }
        attr = attr_map.get(stat)
        if attr:
            current = getattr(self, attr)
            setattr(self, attr, min(STAT_CAP, current + amount))


    def get_available_abilities(self) -> list[Ability]:
        """Return abilities not currently on cooldown."""
        available = []
        for ability in self.char_class.abilities:
            if self.cooldowns.get(ability.name, 0) <= 0:
                available.append(ability)
        return available

    def use_ability(self, ability: Ability) -> tuple[bool, str]:
        """Spend MP and set cooldown. Returns (ok, reason)."""
        if not self.spend_mp(ability.mp_cost):
            return False, f"Not enough MP! (need {ability.mp_cost}, have {self.current_mp})"
        if ability.cooldown > 0:
            self.cooldowns[ability.name] = ability.cooldown
        return True, ""

    def tick_cooldowns(self):
        """Reduce all ability cooldowns by 1 at end of turn."""
        for key in list(self.cooldowns.keys()):
            self.cooldowns[key] = max(0, self.cooldowns[key] - 1)


    def earn_gold(self, amount: int):
        self.gold += amount

    def spend_gold(self, amount: int) -> bool:
        if self.gold < amount:
            return False
        self.gold -= amount
        return True


    def to_dict(self) -> dict:
        """Serialize player to JSON-compatible dictionary."""
        return {
            "name": self.name,
            "class_key": self.char_class.key,
            "level": self.level,
            "xp": self.xp,
            "xp_to_next": self.xp_to_next,
            "gold": self.gold,
            "current_hp": self.current_hp,
            "current_mp": self.current_mp,
            "max_hp": self.max_hp,
            "max_mp": self.max_mp,
            "strength": self.strength,
            "dexterity": self.dexterity,
            "intelligence": self.intelligence,
            "wisdom": self.wisdom,
            "charisma": self.charisma,
            "constitution": self.constitution,
            "base_attack": self.base_attack,
            "base_defense": self.base_defense,
            "kills": self.kills,
            "floors_cleared": self.floors_cleared,
            "dungeon_floor": self.dungeon_floor,
            "inventory": [item.key for item in self.inventory],
            "equipped_weapon": self.equipped_weapon.key if self.equipped_weapon else None,
            "equipped_armor": self.equipped_armor.key if self.equipped_armor else None,
            "equipped_ring": self.equipped_ring.key if self.equipped_ring else None,
            "cooldowns": self.cooldowns,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Player":
        """Restore player from saved dictionary."""
        from data.items import ALL_ITEMS

        class_template = CLASSES[data["class_key"]]
        player = cls.__new__(cls)

        Character.__init__(
            player,
            name=data["name"],
            max_hp=data["max_hp"],
            max_mp=data["max_mp"],
            strength=data["strength"],
            dexterity=data["dexterity"],
            intelligence=data["intelligence"],
            wisdom=data["wisdom"],
            charisma=data["charisma"],
            constitution=data["constitution"],
            attack_power=data["base_attack"],
            defense=data["base_defense"],
        )

        player.char_class = class_template
        player.level = data["level"]
        player.xp = data["xp"]
        player.xp_to_next = data["xp_to_next"]
        player.gold = data["gold"]
        player.current_hp = data["current_hp"]
        player.current_mp = data["current_mp"]
        player.kills = data.get("kills", 0)
        player.floors_cleared = data.get("floors_cleared", 0)
        player.dungeon_floor = data.get("dungeon_floor", 1)
        player.cooldowns = data.get("cooldowns", {})
        player.status_effects = []

        player.inventory = []
        for key in data.get("inventory", []):
            item = ALL_ITEMS.get(key)
            if item:
                player.inventory.append(item)

        player.equipped_weapon = ALL_ITEMS.get(data.get("equipped_weapon"))
        player.equipped_armor  = ALL_ITEMS.get(data.get("equipped_armor"))
        player.equipped_ring   = ALL_ITEMS.get(data.get("equipped_ring"))

        return player
