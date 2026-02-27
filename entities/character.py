from dataclasses import dataclass, field
from typing import Optional


@dataclass
class StatusEffect:
    """A temporary status effect on a character."""
    name: str
    duration: int
    value: int = 0
    description: str = ""


class Character:
    """
    Base class for all combatants.
    Holds stats, HP/MP tracking, and status effect management.
    """

    def __init__(
        self,
        name: str,
        max_hp: int,
        max_mp: int,
        strength: int,
        dexterity: int,
        intelligence: int,
        wisdom: int,
        charisma: int,
        constitution: int,
        attack_power: int,
        defense: int,
    ):
        self.name = name

        self.max_hp = max_hp
        self.max_mp = max_mp
        self.strength = strength
        self.dexterity = dexterity
        self.intelligence = intelligence
        self.wisdom = wisdom
        self.charisma = charisma
        self.constitution = constitution
        self.base_attack = attack_power
        self.base_defense = defense

        self.current_hp = max_hp
        self.current_mp = max_mp

        self.status_effects: list[StatusEffect] = []


    @property
    def is_alive(self) -> bool:
        return self.current_hp > 0

    @property
    def hp_percent(self) -> float:
        return self.current_hp / max(1, self.max_hp)

    def take_damage(self, amount: int) -> int:
        """Apply damage after defense reduction. Returns actual damage taken."""
        if self.has_status("evade"):
            self.remove_status("evade")
            return 0

        if self.has_status("shield"):
            shield = self.get_status("shield")
            absorbed = min(shield.value, amount)
            amount -= absorbed
            shield.value -= absorbed
            if shield.value <= 0:
                self.remove_status("shield")

        actual = max(1, amount - self.effective_defense)
        self.current_hp = max(0, self.current_hp - actual)
        return actual

    def heal(self, amount: int) -> int:
        """Restore HP. Returns actual HP restored."""
        before = self.current_hp
        self.current_hp = min(self.max_hp, self.current_hp + amount)
        return self.current_hp - before

    def restore_mp(self, amount: int) -> int:
        """Restore MP. Returns actual MP restored."""
        before = self.current_mp
        self.current_mp = min(self.max_mp, self.current_mp + amount)
        return self.current_mp - before

    def spend_mp(self, amount: int) -> bool:
        """Spend MP. Returns False if not enough."""
        if self.current_mp < amount:
            return False
        self.current_mp -= amount
        return True


    @property
    def effective_attack(self) -> int:
        """Attack power, accounting for rage or other modifiers."""
        atk = self.base_attack
        if self.has_status("rage"):
            atk = int(atk * 1.5)
        if self.has_status("empower"):
            atk = int(atk * 2.0)
        if self.has_status("mark"):
            atk = int(atk * 1.3)
        return atk

    @property
    def effective_defense(self) -> int:
        """Defense, lowered by rage, raised by aura."""
        defense = self.base_defense
        if self.has_status("rage"):
            defense = int(defense * 0.8)
        if self.has_status("aura"):
            defense = int(defense * 1.3)
        return max(0, defense)

    def stat_by_name(self, stat: str) -> int:
        """Return a stat value by string name."""
        mapping = {
            "str": self.strength, "dex": self.dexterity,
            "int": self.intelligence, "wis": self.wisdom,
            "cha": self.charisma, "con": self.constitution,
        }
        return mapping.get(stat, self.strength)


    def add_status(self, name: str, duration: int, value: int = 0, description: str = ""):
        """Add or refresh a status effect."""
        existing = self.get_status(name)
        if existing:
            existing.duration = max(existing.duration, duration)
            return
        self.status_effects.append(StatusEffect(name, duration, value, description))

    def has_status(self, name: str) -> bool:
        return any(s.name == name for s in self.status_effects)

    def get_status(self, name: str) -> Optional[StatusEffect]:
        return next((s for s in self.status_effects if s.name == name), None)

    def remove_status(self, name: str):
        self.status_effects = [s for s in self.status_effects if s.name != name]

    def tick_status_effects(self) -> list[str]:
        """
        Advance all status effects by one turn.
        Returns a list of narrative messages describing what happened.
        """
        messages = []
        expired = []

        for effect in self.status_effects:
            if effect.name == "poison":
                dmg = max(1, int(self.max_hp * 0.05))
                self.current_hp = max(0, self.current_hp - dmg)
                messages.append(f"  Poison courses through {self.name}'s veins! -{dmg} HP")
            elif effect.name == "burn":
                dmg = max(1, int(self.max_hp * 0.06))
                self.current_hp = max(0, self.current_hp - dmg)
                messages.append(f"  {self.name} writhes in magical fire! -{dmg} HP")
            elif effect.name == "curse":
                dmg = max(1, int(self.max_hp * 0.04))
                self.current_hp = max(0, self.current_hp - dmg)
                messages.append(f"  The curse gnaws at {self.name}'s soul! -{dmg} HP")

            effect.duration -= 1
            if effect.duration <= 0:
                expired.append(effect.name)
                messages.append(f"  [{effect.name.upper()} fades from {self.name}]")

        self.status_effects = [s for s in self.status_effects if s.name not in expired]
        return messages

    def clear_all_status(self):
        """Remove all status effects (used after combat ends)."""
        self.status_effects.clear()


    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} '{self.name}' HP:{self.current_hp}/{self.max_hp}>"
