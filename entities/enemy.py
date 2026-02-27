import random
from entities.character import Character
from data.enemies import EnemyTemplate
from data.items import ALL_ITEMS, Item


class Enemy(Character):
    """
    A combat instance of an enemy, built from an EnemyTemplate.
    Handles AI turn logic and loot generation.
    """

    def __init__(self, template: EnemyTemplate, level_modifier: int = 0):
        self.template = template

        scale = 1.0 + (level_modifier * 0.08)
        hp   = int(template.hp * scale)
        atk  = int(template.attack * scale)
        defn = int(template.defense * (1 + level_modifier * 0.05))

        super().__init__(
            name=template.name,
            max_hp=hp, max_mp=template.mp,
            strength=template.str_stat,
            dexterity=template.dex_stat,
            intelligence=template.int_stat,
            wisdom=8, charisma=6, constitution=10,
            attack_power=atk,
            defense=defn,
        )

        self.xp_reward   = int(template.xp_reward * scale)
        self.gold_reward = random.randint(template.gold_min, template.gold_max)
        self.abilities   = template.abilities
        self.art_key     = template.art_key
        self.is_boss     = template.is_boss
        self.is_undead   = template.is_undead
        self.attack_phrases = template.attack_phrases

        self.ability_cooldowns: dict[str, int] = {}


    def choose_action(self) -> dict:
        """
        Simple AI: decides between basic attack and ability use.
        Returns an action dict with type and relevant data.
        """
        if self.has_status("stun"):
            self.remove_status("stun")
            return {"type": "stunned"}

        available = [
            ab for ab in self.abilities
            if self.ability_cooldowns.get(ab[0], 0) <= 0
            and self.current_mp >= ab[3]
        ]

        if available and (random.random() < 0.35 or self.template.tier >= 3):
            ability = random.choice(available)
            name, mult, effect, cost = ability
            self.current_mp = max(0, self.current_mp - cost)
            if self.template.tier >= 3:
                cooldown = 2
            else:
                cooldown = 1
            self.ability_cooldowns[name] = cooldown
            return {
                "type": "ability",
                "ability_name": name,
                "multiplier": mult,
                "effect": effect,
            }

        phrase = random.choice(self.attack_phrases) if self.attack_phrases else f"{self.name} attacks!"
        return {
            "type": "attack",
            "phrase": phrase,
        }

    def tick_cooldowns(self):
        """Reduce AI cooldowns each turn."""
        for key in list(self.ability_cooldowns.keys()):
            self.ability_cooldowns[key] = max(0, self.ability_cooldowns[key] - 1)


    def generate_loot(self) -> list[Item]:
        """
        Generate item drops from the loot table.
        Bosses always drop; normal enemies have a chance.
        """
        drops = []
        for item_key in self.template.loot_table:
            if item_key == "gold_coin":
                continue
            drop_chance = 0.60 if self.is_boss else 0.25
            if random.random() < drop_chance:
                item = ALL_ITEMS.get(item_key)
                if item:
                    drops.append(item)
        return drops


    @property
    def display_description(self) -> str:
        return self.template.description

    @property
    def tier_label(self) -> str:
        labels = {1: "WEAK", 2: "MODERATE", 3: "DANGEROUS", 4: "BOSS"}
        return labels.get(self.template.tier, "???")
