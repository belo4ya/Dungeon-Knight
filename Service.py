import pygame
import random
import yaml
import os
import Objects


OBJECT_TEXTURE = os.path.join("texture", "objects")
ENEMY_TEXTURE = os.path.join("texture", "enemies")
ALLY_TEXTURE = os.path.join("texture", "ally")
AREA = (40, 40)


def create_sprite(img, sprite_size):
    icon = pygame.image.load(img).convert_alpha()
    icon = pygame.transform.scale(icon, (sprite_size, sprite_size))
    sprite = pygame.Surface((sprite_size, sprite_size), pygame.HWSURFACE)
    sprite.blit(icon, (0, 0))
    return sprite


def reload_game(engine, hero, gameover=None):
    global level_list
    level_list_max = len(level_list) - 1
    engine.level += 1
    if gameover:
        engine.level = level_list_max
        engine.notify("† "*9)
        engine.notify("†  Game Over  †")
        engine.notify("† "*9)
    else:
        engine.notify("Go to Next Floor")
        if engine.level >= level_list_max:
            engine.notify("Win!")
    hero.position = [1, 1]
    engine.objects = []
    generator = level_list[min(engine.level, level_list_max)]
    _map = generator['map'].get_map()
    engine.load_map(_map)
    engine.add_objects(generator['obj'].get_objects(_map))
    engine.add_hero(hero)


def restore_hp(engine, hero):
    engine.score += 0.1
    hero.hp = hero.max_hp
    engine.notify("HP restored")


def apply_blessing(engine, hero):
    if hero.gold >= int(20 * 1.5**engine.level) - 2 * hero.stats["intelligence"]:
        engine.score += 0.2
        hero.gold -= int(20 * 1.5**engine.level) - \
            2 * hero.stats["intelligence"]
        rnd = random.randint(0,5)
        if rnd <= 1:
            engine.hero = Objects.Blessing(hero)
            engine.notify("Blessing applied")
        elif rnd <= 4:
            engine.hero = Objects.Berserk(hero)
            engine.notify("Berserk applied")
        else:
            engine.hero = Objects.Amnesia(hero)
            engine.notify("Amnesia applied")
    else:
        engine.score -= 0.1
        engine.notify("Not enough gold")


def remove_effect(engine, hero):
    if hero.gold >= int(10 * 1.5**engine.level) - 2 * hero.stats["intelligence"] and "base" in dir(hero):
        hero.gold -= int(10 * 1.5**engine.level) - \
            2 * hero.stats["intelligence"]
        engine.hero = hero.base
        engine.hero.calc_max_HP()
        engine.notify("Effect removed")
    else:
        engine.notify("Nothing removing")


def add_gold(engine, hero):
    if random.randint(1, 10) == 1:
        engine.score -= 0.05
        engine.hero = Objects.Weakness(hero)
        engine.notify("You were cursed")
    else:
        engine.score += 0.1
        gold = int(random.randint(10, 1000) * (1.1**(engine.hero.level - 1)))
        hero.gold += gold
        engine.notify(f"{gold} gold added")


def double_exp(engine, hero):
    engine.score += 0.1
    hero.exp *= 2
    engine.notify("Exp doubled")
    if hero.level_up(): engine.notify("Level Up!")


class MapFactory(yaml.YAMLObject):

    @classmethod
    def from_yaml(cls, loader, node):
        _map = cls.Map()
        _obj = cls.Objects()
        data = loader.construct_mapping(node)
        _obj.config = data
        return {'map': _map, 'obj': _obj}


class EndMap(MapFactory):
    yaml_tag = "!end_map"

    class Map:
        def __init__(self):
            self.Map = ['0000000000000000000000000000000000000000',
                        '0                                      0',
                        '0                                      0',
                        '0  0   0   000   0   0  00000  0   0   0',
                        '0  0  0   0   0  0   0  0      0   0   0',
                        '0  000    0   0  00000  0000   0   0   0',
                        '0  0  0   0   0  0   0  0      0   0   0',
                        '0  0   0   000   0   0  00000  00000   0',
                        '0                                   0  0',
                        '0                                      0',
                        '0000000000000000000000000000000000000000'
                        ]
            self.Map = list(map(list, self.Map))
            for i in self.Map:
                for j in range(len(i)):
                    i[j] = wall if i[j] == '0' else [floor1, floor2, floor3][random.randint(0, 2)]

        def get_map(self):
            return self.Map

    class Objects:
        def __init__(self):
            self.objects = []
            self.config = {}

        def get_objects(self, _map):
            return self.objects


class RandomMap(MapFactory):
    yaml_tag = "!random_map"

    class Map:
        def __init__(self):
            self.Map = [[0 for _ in range(AREA[0])] for _ in range(AREA[1])]
            for i in range(AREA[0]):
                for j in range(AREA[1]):
                    if i == 0 or j == 0 or i == AREA[0]-1 or j == AREA[1]-1:
                        self.Map[j][i] = wall
                    elif i == 1 and j == 1:
                        self.Map[j][i] = floor1
                    else:
                        self.Map[j][i] = [wall, floor1, floor2, floor3, floor1,
                                          floor2, floor3, floor1, floor2][random.randint(0, 8)]

        def get_map(self):
            return self.Map

    class Objects:
        def __init__(self):
            self.objects = []
            self.config = {}

        def get_objects(self, _map):
            for obj_name in object_list_prob['objects']:
                prop = object_list_prob['objects'][obj_name]
                for i in range(random.randint(prop['min-count'], prop['max-count'])):
                    coord = (random.randint(1, AREA[0]-2),
                             random.randint(1, AREA[1]-2))
                    intersect = True
                    while intersect:
                        intersect = False
                        if _map[coord[1]][coord[0]] == wall:
                            intersect = True
                            coord = (random.randint(1, AREA[0]-2),
                                     random.randint(1, AREA[1]-2))
                            continue
                        for obj in self.objects:
                            if coord == obj.position or coord == (1, 1):
                                intersect = True
                                coord = (random.randint(1, AREA[0]-2),
                                         random.randint(1, AREA[1]-2))

                    self.objects.append(Objects.Ally(
                        prop['sprite'], prop['action'], coord))

            for obj_name in object_list_prob['ally']:
                prop = object_list_prob['ally'][obj_name]
                for i in range(random.randint(prop['min-count'], prop['max-count'])):
                    coord = (random.randint(1, AREA[0]-2),
                             random.randint(1, AREA[1]-2))
                    intersect = True
                    while intersect:
                        intersect = False
                        if _map[coord[1]][coord[0]] == wall:
                            intersect = True
                            coord = (random.randint(1, AREA[0]-2),
                                     random.randint(1, AREA[1]-2))
                            continue
                        for obj in self.objects:
                            if coord == obj.position or coord == (1, 1):
                                intersect = True
                                coord = (random.randint(1, AREA[0]-2),
                                         random.randint(1, AREA[1]-2))
                    self.objects.append(Objects.Ally(
                        prop['sprite'], prop['action'], coord))

            for obj_name in object_list_prob['enemies']:
                prop = object_list_prob['enemies'][obj_name]
                for i in range(random.randint(0, 5)):
                    coord = (random.randint(1, int(0.8*AREA[0])),
                             random.randint(1, int(0.6*AREA[1])))
                    intersect = True
                    while intersect:
                        intersect = False
                        if _map[coord[1]][coord[0]] == wall:
                            intersect = True
                            coord = (random.randint(1, AREA[0]-2),
                                     random.randint(1, AREA[1]-2))
                            continue
                        for obj in self.objects:
                            if coord == obj.position or coord == (1, 1):
                                intersect = True
                                coord = (random.randint(1, AREA[0]-2),
                                         random.randint(1, AREA[1]-2))

                    self.objects.append(Objects.Enemy(
                        prop['sprite'], prop, prop['experience'], coord))

            return self.objects


class EmptyMap(MapFactory):
    yaml_tag = "!empty_map"

    class Map:
        def __init__(self):
            self.Map = [[0 for _ in range(AREA[0])] for _ in range(AREA[1])]
            for i in range(AREA[0]):
                for j in range(AREA[1]):
                    if i == 0 or j == 0 or i == AREA[0]-1 or j == AREA[1]-1:
                        self.Map[j][i] = wall
                    elif i == 1 and j == 1:
                        self.Map[j][i] = floor1
                    else:
                        self.Map[j][i] = [wall, floor1, floor2, floor3, floor1,
                                          floor2, floor3, floor1, floor2][random.randint(0, 8)]

        def get_map(self):
            return self.Map

    class Objects:
        def __init__(self):
            self.objects = []
            self.config = {}

        def get_objects(self, _map):
            for obj_name in object_list_prob['objects']:
                prop = object_list_prob['objects'][obj_name]
                for i in range(random.randint(prop['min-count'], prop['max-count'])):
                    coord = (random.randint(1, AREA[0]-2),
                             random.randint(1, AREA[1]-2))
                    intersect = True
                    while intersect:
                        intersect = False
                        if _map[coord[1]][coord[0]] == wall:
                            intersect = True
                            coord = (random.randint(1, AREA[0]-2),
                                     random.randint(1, AREA[1]-2))
                            continue
                        for obj in self.objects:
                            if coord == obj.position or coord == (1, 1):
                                intersect = True
                                coord = (random.randint(1, AREA[0]-2),
                                         random.randint(1, AREA[1]-2))
                    self.objects.append(Objects.Ally(
                        prop['sprite'], prop['action'], coord))

            return self.objects


class SpecialMap(MapFactory):
    yaml_tag = "!special_map"

    class Map:
        def __init__(self):
            self.Map = [[0 for _ in range(AREA[0])] for _ in range(AREA[1])]
            for i in range(AREA[0]):
                for j in range(AREA[1]):
                    if i == 0 or j == 0 or i == AREA[0]-1 or j == AREA[1]-1:
                        self.Map[j][i] = wall
                    elif i == 1 and j == 1:
                        self.Map[j][i] = floor1
                    else:
                        self.Map[j][i] = [wall, floor1, floor2, floor3, floor1,
                                          floor2, floor3, floor1, floor2][random.randint(0, 8)]

        def get_map(self):
            return self.Map

    class Objects:
        def __init__(self):
            self.objects = []
            self.config = {}

        def get_objects(self, _map):
            for obj_name in object_list_prob['objects']:
                prop = object_list_prob['objects'][obj_name]
                for i in range(random.randint(prop['min-count'], prop['max-count'])):
                    coord = (random.randint(1, AREA[0]-2),
                             random.randint(1, AREA[1]-2))
                    intersect = True
                    while intersect:
                        intersect = False
                        if _map[coord[1]][coord[0]] == wall:
                            intersect = True
                            coord = (random.randint(1, AREA[0]-2),
                                     random.randint(1, AREA[1]-2))
                            continue
                        for obj in self.objects:
                            if coord == obj.position or coord == (1, 1):
                                intersect = True
                                coord = (random.randint(1, AREA[0]-2),
                                         random.randint(1, AREA[1]-2))

                    self.objects.append(Objects.Ally(
                        prop['sprite'], prop['action'], coord))

            for obj_name in object_list_prob['ally']:
                prop = object_list_prob['ally'][obj_name]
                for i in range(random.randint(prop['min-count'], prop['max-count'])):
                    coord = (random.randint(1, AREA[0]-2),
                             random.randint(1, AREA[1]-2))
                    intersect = True
                    while intersect:
                        intersect = False
                        if _map[coord[1]][coord[0]] == wall:
                            intersect = True
                            coord = (random.randint(1, AREA[0]-2),
                                     random.randint(1, AREA[1]-2))
                            continue
                        for obj in self.objects:
                            if coord == obj.position or coord == (1, 1):
                                intersect = True
                                coord = (random.randint(1, AREA[0]-2),
                                         random.randint(1, AREA[1]-2))
                    self.objects.append(Objects.Ally(
                        prop['sprite'], prop['action'], coord))

            for obj_name in self.config:
                prop = object_list_prob['enemies'][obj_name]
                for i in range(self.config[obj_name]):
                    coord = (random.randint(1, int(0.8*AREA[0])),
                             random.randint(1, int(0.6*AREA[1])))
                    intersect = True
                    while intersect:
                        intersect = False
                        if _map[coord[1]][coord[0]] == wall:
                            intersect = True
                            coord = (random.randint(1, AREA[0]-2),
                                     random.randint(1, AREA[1]-2))
                            continue
                        for obj in self.objects:
                            if coord == obj.position or coord == (1, 1):
                                intersect = True
                                coord = (random.randint(1, AREA[0]-2),
                                         random.randint(1, AREA[1]-2))

                    self.objects.append(Objects.Enemy(
                        prop['sprite'], prop, prop['experience'], coord))

            return self.objects


wall = [0]
floor1 = [0]
floor2 = [0]
floor3 = [0]


def service_init(sprite_size, full=True):
    global object_list_prob, level_list

    global wall
    global floor1
    global floor2
    global floor3

    wall[0] = create_sprite(os.path.join("texture", "wall.png"), sprite_size)
    floor1[0] = create_sprite(os.path.join("texture", "Ground_1.png"), sprite_size)
    floor2[0] = create_sprite(os.path.join("texture", "Ground_2.png"), sprite_size)
    floor3[0] = create_sprite(os.path.join("texture", "Ground_3.png"), sprite_size)
    wall.append('wall')
    for floor in [floor1, floor2, floor3]: floor.append('floor')


    file = open("objects.yml", "r")

    object_list_tmp = yaml.load(file.read())
    if full:
        object_list_prob = object_list_tmp

    object_list_actions = {'reload_game': reload_game,
                           'add_gold': add_gold,
                           'apply_blessing': apply_blessing,
                           'remove_effect': remove_effect,
                           'restore_hp': restore_hp,
                           'double_exp': double_exp}

    for obj in object_list_prob['objects']:
        prop = object_list_prob['objects'][obj]
        prop_tmp = object_list_tmp['objects'][obj]
        prop['sprite'][0] = create_sprite(
            os.path.join(OBJECT_TEXTURE, prop_tmp['sprite'][0]), sprite_size)
        prop['sprite'].append(obj)
        prop['action'] = object_list_actions[prop_tmp['action']]

    for ally in object_list_prob['ally']:
        prop = object_list_prob['ally'][ally]
        prop_tmp = object_list_tmp['ally'][ally]
        prop['sprite'][0] = create_sprite(
            os.path.join(ALLY_TEXTURE, prop_tmp['sprite'][0]), sprite_size)
        prop['sprite'].append('ally')
        prop['action'] = object_list_actions[prop_tmp['action']]

    for enemy in object_list_prob['enemies']:
        prop = object_list_prob['enemies'][enemy]
        prop_tmp = object_list_tmp['enemies'][enemy]
        prop['sprite'][0] = create_sprite(
            os.path.join(ENEMY_TEXTURE, prop_tmp['sprite'][0]), sprite_size)
        prop['sprite'].append('enemies')

    file.close()

    if full:
        file = open("levels.yml", "r")
        level_list = yaml.load(file.read())['levels']
        level_list.append({'map': EndMap.Map(), 'obj': EndMap.Objects()})
        file.close()
