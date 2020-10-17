from abc import ABC, abstractmethod
import pygame
import random
from Service import reload_game


def create_sprite(img, sprite_size):
    icon = pygame.image.load(img).convert_alpha()
    icon = pygame.transform.scale(icon, (sprite_size, sprite_size))
    sprite = pygame.Surface((sprite_size, sprite_size), pygame.HWSURFACE)
    sprite.blit(icon, (0, 0))
    return sprite


class AbstractObject(ABC):
    @abstractmethod
    def __init__(self):
        pass

    def draw(self, surface, offset, sprite_size):
        surface.blit(self.sprite,
                     ((self.position[0] - offset[0]) * sprite_size,
                      (self.position[1] - offset[1]) * sprite_size))


class Interactive(ABC):

    @abstractmethod
    def interact(self, engine, hero):
        pass


class Ally(AbstractObject, Interactive):

    def __init__(self, icon, action, position):
        self.sprite = icon
        self.action = action
        self.position = position

    def interact(self, engine, hero):
        self.action(engine, hero)


class Creature(AbstractObject):

    def __init__(self, icon, stats, position):
        self.sprite = icon
        self.stats = stats
        self.position = position
        self.hp = 0
        self.calc_max_HP()
        self.hp = self.max_hp

    def calc_max_HP(self):
        self.max_hp = 5 + self.stats["endurance"] * 2
        if self.hp > self.max_hp: self.hp = self.max_hp


class Enemy(Creature, Interactive):
    def __init__(self, icon, stats, xp, position):
        super().__init__(icon, stats, position)
        self.exp = xp

    def interact(self, engine, hero):
        delta_strength = hero.stats["strength"]*(-0.5 + random.random()) - self.stats["strength"]*(-0.5 + random.random())
        delta_endurance = hero.stats["endurance"]*(-0.5 + random.random()) - self.stats["endurance"]*(-0.5 + random.random())
        delta_luck = hero.stats["luck"]*(-0.5 + random.random()) - 2*self.stats["luck"]*(-0.5 + random.random())
        delta_exp = hero.exp*(-0.5 + random.random()) - self.exp*(-0.5 + random.random())

        delta = delta_strength + delta_endurance + delta_luck + delta_exp
        engine.score += delta + 5

        hero.exp += int(0.5 * self.exp * (-0.1 + random.random()))
        hero.hp += -5 + int(delta / 5) if delta < 0 else 0
        if hero.exp < 0: hero.exp = 0
        if engine.hero.level_up(): engine.notify("Level Up!")

        if hero.hp < 1:
            hero.hp = 0
            reload_game(engine, hero, gameover=True)


class Hero(Creature):

    def __init__(self, stats, icon):
        pos = [1, 1]
        self.level = 1
        self.exp = 0
        self.gold = 0
        super().__init__(icon, stats, pos)

    def level_up(self):
        while self.exp >= 100 * (2 ** (self.level - 1)):
            self.level += 1
            self.stats["strength"] += 2
            self.stats["endurance"] += 2
            self.calc_max_HP()
            self.hp = self.max_hp
            if self.exp < 100 * (2 ** (self.level - 1)):
                return True


class Effect(Hero):

    def __init__(self, base):
        self.base = base
        self.stats = self.base.stats.copy()
        self.apply_effect()

    @property
    def position(self):
        return self.base.position

    @position.setter
    def position(self, value):
        self.base.position = value

    @property
    def level(self):
        return self.base.level

    @level.setter
    def level(self, value):
        self.base.level = value

    @property
    def gold(self):
        return self.base.gold

    @gold.setter
    def gold(self, value):
        self.base.gold = value

    @property
    def hp(self):
        return self.base.hp

    @hp.setter
    def hp(self, value):
        self.base.hp = value

    @property
    def max_hp(self):
        return self.base.max_hp

    @max_hp.setter
    def max_hp(self, value):
        self.base.max_hp = value

    @property
    def exp(self):
        return self.base.exp

    @exp.setter
    def exp(self, value):
        self.base.exp = value

    @property
    def sprite(self):
        return self.base.sprite

    @abstractmethod
    def apply_effect(self):
        pass


class Berserk(Effect):
    def __init__(self, base):
        super().__init__(base)

    def apply_effect(self):
        self.stats["strength"] += 20


class Blessing(Effect):
    def __init__(self, base):
        super().__init__(base)

    def apply_effect(self):
        self.stats["luck"] += 10


class Weakness(Effect):
    def __init__(self, base):
        super().__init__(base)

    def apply_effect(self):
        self.stats["strength"] -= 20
        self.stats["luck"] -= 10


class Amnesia(Effect):
    def __init__(self, base):
        super().__init__(base)

    def apply_effect(self):
        self.stats["strength"] = 0
        self.stats["luck"] = 0
