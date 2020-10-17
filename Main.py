import pygame
import os
import Objects
import ScreenEngine as SE
import Logic
import Service

SCREEN_DIM = (800, 640)
SPRITE_SIZE = 40
GAME_CANVAS = (640, 480)

pygame.init()
gameDisplay = pygame.display.set_mode(SCREEN_DIM)
pygame.display.set_caption("MyRPG")
KEYBOARD_CONTROL = True

if not KEYBOARD_CONTROL:
    import numpy as np
    answer = np.zeros(4, dtype=float)

base_stats = {
    "strength": 20,
    "endurance": 20,
    "intelligence": 5,
    "luck": 5
}


def create_game(sprite_size, is_new):
    global hero, engine, drawer, iteration
    if is_new:
        hero = Objects.Hero(base_stats, Service.create_sprite(
            os.path.join("texture", "Hero.png"), sprite_size))
        engine = Logic.GameEngine()
        Service.service_init(sprite_size)
        Service.reload_game(engine, hero)

        drawer = SE.GameSurface(GAME_CANVAS, pygame.SRCALPHA, (GAME_CANVAS[0], GAME_CANVAS[1]),
                 SE.MiniMap((SCREEN_DIM[0]-GAME_CANVAS[0], SCREEN_DIM[1]-GAME_CANVAS[1]), pygame.SRCALPHA, (0, GAME_CANVAS[1]),
                 SE.ProgressBar((GAME_CANVAS[0], SCREEN_DIM[1]-GAME_CANVAS[1]+40), (GAME_CANVAS[0], 0),
                 SE.InfoWindow((SCREEN_DIM[0]-GAME_CANVAS[0], GAME_CANVAS[1]), (0, 0),
                 SE.HelpWindow(SCREEN_DIM, pygame.SRCALPHA, (0, 0),
                 SE.ScreenHandle((0, 0)
                 ))))))

    else:
        engine.sprite_size = sprite_size
        hero.sprite = Service.create_sprite(
            os.path.join("texture", "Hero.png"), sprite_size)
        Service.service_init(sprite_size, False)

    Logic.GameEngine.sprite_size = sprite_size

    engine.show_minimap = True
    engine.show_help = False

    drawer.connect_engine(engine)

    iteration = 0


size = SPRITE_SIZE
create_game(size, True)

while engine.working:

    if KEYBOARD_CONTROL:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                engine.working = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_h:
                    engine.show_help = not engine.show_help
                if event.key == pygame.K_m:
                    engine.show_minimap = not engine.show_minimap
                if event.key == pygame.K_KP_PLUS:
                    size += 2 if size <64 else 0
                    create_game(size, False)
                if event.key == pygame.K_KP_MINUS:
                    size -= 2 if size >16 else 0
                    create_game(size, False)
                if event.key == pygame.K_0 or event.key == pygame.K_KP0 :
                    size = SPRITE_SIZE
                    create_game(size, False)
                if event.key == pygame.K_r:
                    create_game(size, True)
                if event.key == pygame.K_ESCAPE:
                    engine.working = False
                if engine.game_process:
                    if event.key == pygame.K_UP:
                        engine.move_up()
                        iteration += 1
                    elif event.key == pygame.K_DOWN:
                        engine.move_down()
                        iteration += 1
                    elif event.key == pygame.K_LEFT:
                        engine.move_left()
                        iteration += 1
                    elif event.key == pygame.K_RIGHT:
                        engine.move_right()
                        iteration += 1
                else:
                    if event.key == pygame.K_RETURN:
                        create_game()
    else:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                engine.working = False
        if engine.game_process:
            actions = [
                engine.move_right,
                engine.move_left,
                engine.move_up,
                engine.move_down,
            ]
            answer = np.random.randint(0, 100, 4)
            prev_score = engine.score
            move = actions[np.argmax(answer)]()
            state = pygame.surfarray.array3d(gameDisplay)
            reward = engine.score - prev_score
            print(reward)
        else:
            create_game()

    gameDisplay.blit(drawer, (0, 0))
    drawer.draw(gameDisplay)

    pygame.display.update()

pygame.display.quit()
pygame.quit()
exit(0)
