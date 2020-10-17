import pygame
import collections
import Service
import Objects


colors = {
    "black": (0, 0, 0, 255),
    "white": (255, 255, 255, 255),
    "red": (255, 0, 0, 255),
    "green": (0, 255, 0, 255),
    "blue": (0, 0, 255, 255),
    "wooden": (153, 92, 0, 255),
    "help": (255, 208, 123, 255),
    "minimap": (143, 97, 53, 255),
    "gold": (224, 160, 0, 255),
    "wall": (49, 18, 4, 255)
}


class ScreenHandle(pygame.Surface):

    def __init__(self, *args, **kwargs):
        if len(args) > 1:
            self.successor = args[-1]
            self.next_coord = args[-2]
            args = args[:-2]
        else:
            self.successor = None
            self.next_coord = (0, 0)
        super().__init__(*args, **kwargs)
        self.fill(colors["wooden"])
        self.engine = None

    def draw(self, canvas):
        if self.successor is not None:
            canvas.blit(self.successor, self.next_coord)
            self.successor.draw(canvas)

    def connect_engine(self, engine):
        self.engine = engine
        if self.successor is not None:
            self.successor.connect_engine(engine)


class GameSurface(ScreenHandle):

    def connect_engine(self, engine):
        self.game_engine = engine
        self.successor.connect_engine(engine)

    def draw_hero(self, offset, sprite_size):
        self.game_engine.hero.draw(self, offset, sprite_size)

    def draw_map(self, offset):

        min_x, min_y = offset[0], offset[1]

        if self.game_engine.map:
            for i in range(len(self.game_engine.map[0]) - min_x):
                for j in range(len(self.game_engine.map) - min_y):
                    self.blit(self.game_engine.map[min_y + j][min_x + i][
                              0], (i * self.game_engine.sprite_size, j * self.game_engine.sprite_size))
        else:
            self.fill(colors["white"])

    def draw(self, canvas):
        sprite_size = self.game_engine.sprite_size

        min_x, min_y = 0, 0

        view_width, view_height = self.get_width(), self.get_height()

        sprites_in_view_x = int(view_width / sprite_size + 0.5)
        sprites_in_view_y = int(view_height / sprite_size + 0.5)

        sprites_in_area_x = len(self.game_engine.map[0])
        sprites_in_area_y = len(self.game_engine.map)

        center_x = sprites_in_view_x // 2
        center_y = sprites_in_view_y // 2

        if sprites_in_view_x < sprites_in_area_x and self.game_engine.hero.position[0] > center_x:
            min_x = self.game_engine.hero.position[0] - center_x
            if self.game_engine.hero.position[0] > sprites_in_area_x - center_x:
                min_x = sprites_in_area_x - 2*center_x

        if sprites_in_view_y < sprites_in_area_y and self.game_engine.hero.position[1] > center_y:
            min_y = self.game_engine.hero.position[1] - center_y
            if self.game_engine.hero.position[1] > sprites_in_area_y - center_y:
                min_y = sprites_in_area_y - 2*center_y

        self.fill(colors["wooden"])
        self.draw_map((min_x, min_y))
        for obj in self.game_engine.objects:
             self.blit(obj.sprite[0], ((obj.position[0] - min_x) * self.game_engine.sprite_size,
                                       (obj.position[1] - min_y) * self.game_engine.sprite_size))
        self.draw_hero((min_x, min_y), sprite_size)

        canvas.blit(self.successor, self.next_coord)
        self.successor.draw(canvas)


class MiniMap(ScreenHandle):

    def connect_engine(self, engine):
        self.engine = engine
        self.point_size = self.get_width() // len(self.engine.map[0])
        self.stair_color = colors['green']
        self.successor.connect_engine(engine)

    def draw(self, canvas):
        self.fill(colors["wooden"])

        if not self.engine.show_minimap:
            canvas.blit(self.successor, self.next_coord)
            self.successor.draw(canvas)
            return None

        if self.engine.map:
            for i in range(len(self.engine.map)):
                for j in range(len(self.engine.map[0])):
                    if self.engine.map[i][j][1] == 'wall':
                        color = colors['wall']
                    else:
                        color = colors['minimap']
                    pygame.draw.rect(self, color,(j*self.point_size, i*self.point_size, self.point_size, self.point_size))

        for obj in self.engine.objects:
            if obj.sprite[1] == 'stairs':
                green_level = self.stair_color[1]
                green_level = ((green_level - 128 + 2) % 127) + 128
                color = (0, green_level, 0, 255)
                self.stair_color = color
            elif obj.sprite[1] == 'enemies':
                color = colors['red']
            elif obj.sprite[1] == 'ally':
                color = colors['blue']
            elif obj.sprite[1] == 'chest':
                color = colors['gold']
            else:
                color = colors['white']
            pygame.draw.rect(self, color,(obj.position[0]*self.point_size, obj.position[1]*self.point_size, self.point_size, self.point_size))

        hero_x, hero_y = self.engine.hero.position[0], self.engine.hero.position[1]
        pygame.draw.rect(self, colors['white'],(hero_x*self.point_size, hero_y*self.point_size, self.point_size, self.point_size))

        canvas.blit(self.successor, self.next_coord)
        self.successor.draw(canvas)


class ProgressBar(ScreenHandle):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fill(colors["wooden"])

    def connect_engine(self, engine):
        self.engine = engine
        self.successor.connect_engine(engine)

    def draw(self, canvas):
        self.fill(colors["wooden"])
        pygame.draw.rect(self, colors["black"], (50, 60, 200, 30), 2)
        pygame.draw.rect(self, colors["black"], (50, 100, 200, 30), 2)

        red_hp_color = int(2 * 255 * (self.engine.hero.max_hp - self.engine.hero.hp) / self.engine.hero.max_hp)
        if red_hp_color > 255: red_hp_color = 255
        green_hp_color = int(255 * (self.engine.hero.hp / self.engine.hero.max_hp))
        hp_color = (red_hp_color, green_hp_color, 0, 255)
        pygame.draw.rect(self, hp_color, (53, 62, 196 * self.engine.hero.hp / self.engine.hero.max_hp, 26))
        pygame.draw.rect(self, colors["green"], (53, 102,
                                                 196 * self.engine.hero.exp / (100 * (2**(self.engine.hero.level - 1))), 26))

        font = pygame.font.SysFont("sans", 22)
        self.blit(font.render(f'Hero at {self.engine.hero.position}', True, colors["black"]),
                  (300, 20))

        self.blit(font.render(f'{self.engine.level} floor', True, colors["black"]),
                  (50, 20))

        self.blit(font.render(f'HP', True, colors["black"]),
                  (10, 62))
        self.blit(font.render(f'Exp', True, colors["black"]),
                  (10, 102))

        self.blit(font.render(f'{self.engine.hero.hp}/{self.engine.hero.max_hp}', True, colors["black"]),
                  (60, 62))
        self.blit(font.render(f'{self.engine.hero.exp}/{(100*(2**(self.engine.hero.level-1)))}', True, colors["black"]),
                  (60, 102))

        self.blit(font.render(f'Level', True, colors["black"]),
                  (300, 60))
        self.blit(font.render(f'Gold', True, colors["black"]),
                  (300, 100))

        self.blit(font.render(f'{self.engine.hero.level}', True, colors["black"]),
                  (360, 60))
        self.blit(font.render(f'{self.engine.hero.gold}', True, colors["black"]),
                  (360, 100))

        self.blit(font.render(f'Str', True, colors["black"]),
                  (420, 60))
        self.blit(font.render(f'Luck', True, colors["black"]),
                  (420, 100))

        self.blit(font.render(f'{self.engine.hero.stats["strength"]}', True, colors["black"]),
                  (480, 60))
        self.blit(font.render(f'{self.engine.hero.stats["luck"]}', True, colors["black"]),
                  (480, 100))

        self.blit(font.render(f'SCORE', True, colors["black"]),
                  (550, 60))
        self.blit(font.render(f'{self.engine.score:.2f}', True, colors["black"]),
                  (550, 100))

        canvas.blit(self.successor, self.next_coord)
        self.successor.draw(canvas)


class InfoWindow(ScreenHandle):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.len = 18
        clear = []
        self.data = collections.deque(clear, maxlen=self.len)

    def update(self, value):
        self.data.append(f"> {str(value)}")

    def draw(self, canvas):
        self.fill(colors["wooden"])
        size = self.get_size()

        font = pygame.font.SysFont("sans", 18)
        for i, text in enumerate(self.data):
            self.blit(font.render(text, True, colors["black"]),
                      (15, 20 + 24 * i))

        canvas.blit(self.successor, self.next_coord)
        self.successor.draw(canvas)

    def connect_engine(self, engine):
        self.engine = engine
        engine.subscribe(self)
        self.successor.connect_engine(engine)


class HelpWindow(ScreenHandle):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.len = 30
        clear = []
        self.data = collections.deque(clear, maxlen=self.len)
        self.data.append([" →  ", "Move Right"])
        self.data.append([" ←  ", "Move Left"])
        self.data.append(["  ↑ ", "Move Top"])
        self.data.append(["  ↓ ", "Move Bottom"])
        self.data.append(["", ""])
        self.data.append(["  H ", "Show / Hide Help"])
        self.data.append(["  M ", "Show / Hide Minimap"])
        self.data.append(["", ""])
        self.data.append(["Num +", "Zoom +"])
        self.data.append(["Num -", "Zoom -"])
        self.data.append(["  0 ", "Zoom Default"])
        self.data.append(["", ""])
        self.data.append(["  R ", "Restart Game"])

    def connect_engine(self, engine):
        self.engine = engine
        self.successor.connect_engine(engine)

    def draw(self, canvas):
        alpha = 0
        if self.engine.show_help:
            alpha = 180
        self.fill((0, 0, 0, alpha))
        size = self.get_size()
        font = pygame.font.SysFont("sans", 20)
        if self.engine.show_help:
            for i, text in enumerate(self.data):
                self.blit(font.render(text[0], True, (colors["help"])),
                          (150, 100 + 25 * i))
                self.blit(font.render(text[1], True, (colors["help"])),
                          (250, 100 + 25 * i))
        canvas.blit(self.successor, self.next_coord)
        self.successor.draw(canvas)
