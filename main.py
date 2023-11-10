import math
import random

import pygame
import pygame as pg
import os

pg.init()
pg.font.init()

FPS = 60
clock = pg.time.Clock()

SCREEN_HEIGHT = pygame.display.get_desktop_sizes()[0][1] * 0.9
HEIGHT = SCREEN_HEIGHT * (7/8)
WIDTH = HEIGHT

font = pg.font.Font("assets/antiqua.ttf", round(WIDTH/15))

screen = pg.display.set_mode((WIDTH, SCREEN_HEIGHT), pygame.NOFRAME)
pg.display.set_caption("quack")

# level             0           1            2            3            4            5            6            7            8            9
board_level = [     7,          7,           8,           8,           10,          8,           10,          9,           10,          12 ]
obstacle_level = [  (3, 0),     (4, 0),      (3, 0),      (3, 3),      (3, 5),      (0, 8),      (5, 5),      (3, 6),      (0, 0),      (7, 0)]
enemy_level = [     (2, 0, 0),  (4, 0, 0),   (3, 1, 0),   (4, 2, 0),   (2, 4, 0),   (0, 6, 0),   (3, 3, 1),   (3, 4, 2),   (0, 0, 4),   (3, 3, 3)]
level = -1
level_text = font.render(f"level: {level+1}/10", True, (0, 0, 0))

width = 1
size = 1

bgsurface = pg.Surface((1, 1))
walls = pg.Surface((1, 1))
walls.set_colorkey((100, 100, 100))
playarea = pg.Surface((1, 1))
enemiesarea = pg.Surface((1, 1))
enemiesarea.set_colorkey((100, 100, 100))
playerarea = pg.Surface((1, 1))
playerarea.set_colorkey((100, 100, 100))
hud = pg.Surface((WIDTH, SCREEN_HEIGHT * (1/8)))

turns = 3
action = None
ammo = 3
ammo_text = font.render(f"{ammo}", True, (0, 0, 0))
arrows = []

highlight = pg.transform.scale(pg.image.load(os.path.join('assets/ground', "highlight.png")), (size, size))
arrow = pg.transform.scale(pg.image.load(os.path.join('assets', "arrow.png")), (size, size))
fly_arrow = pg.transform.scale(pg.image.load(os.path.join('assets', "arrowfly.png")), (size, size))
exit_button = pg.transform.scale(pg.image.load(os.path.join('assets/buttons', "exit.png")), (size, size))
heart = pg.transform.scale(pg.image.load(os.path.join('assets', "heart.png")), (SCREEN_HEIGHT * (1/8) * 0.7, (SCREEN_HEIGHT * (1/8)) * 0.7))
turn_counter = pg.transform.scale(pg.image.load(os.path.join('assets', "turns.png")), (SCREEN_HEIGHT * (1/8) * 0.25, (SCREEN_HEIGHT * (1/8)) * 0.25))
board = []

NEW_LEVEL = pg.USEREVENT + 1


def update_background():
    global board
    board = [[4 for x in range(width+2)] for x in range(width+2)]
    for i in range(1, width+1):
        for j in range(1, width+1):
            board[i][j] = 0

    while sum([board[x].count(1) for x in range(len(board))]) < obstacle_level[level][0]:
        try_position = (random.randint(1, width-2), random.randint(1, width-2))
        place = True
        for i in range(-1, 2):
            for j in range(-1, 2):
                if board[try_position[0]-i+1][try_position[1]-j+1] == 1:
                    place = False
        if place:
            board[try_position[0]+1][try_position[1]+1] = 1

    while sum([board[x].count(2) for x in range(len(board))]) < obstacle_level[level][1]:
        try_position = (random.randint(1, width-2), random.randint(1, width-2))
        place = True
        for i in range(-1, 2):
            for j in range(-1, 2):
                if board[try_position[0]-i+1][try_position[1]-j+1] == 2 or board[try_position[0]-i+1][try_position[1]-j+1] == 1:
                    place = False
        if place:
            board[try_position[0]+1][try_position[1]+1] = 2

    tiles = []
    for number in range(6):
        tile = pg.transform.scale(pg.image.load(os.path.join('assets/ground', str(number) + ".png")), (size, size))
        tiles.append(tile)

    wall = pg.transform.scale(pg.image.load(os.path.join('assets/ground', "wall.png")), (size, size*1.5))
    walls.fill((100, 100, 100))

    lava = pg.transform.scale(pg.image.load(os.path.join('assets/ground', "lava.png")), (size, size))

    for sor in range(width):
        for oszlop in range(width):
            if board[sor+1][oszlop+1] == 0:
                bgsurface.blit(random.choice(tiles), (sor * size, oszlop * size))
            if board[sor+1][oszlop+1] == 1:
                walls.blit(wall, (sor * size, (oszlop * size)-(size*0.5)))
            if board[sor+1][oszlop+1] == 2:
                bgsurface.blit(lava, (sor * size, oszlop * size))


def update_playarea():
    global action
    playarea.fill((255, 0, 0))
    playarea.blit(bgsurface, (0, 0))
    for sor in range(1, width + 1):
        for oszlop in range(1, width + 1):
            if check_action(action, (sor, oszlop)):
                playarea.blit(highlight, coord_to_pixel(sor, oszlop))
    for aw in arrows:
        playarea.blit(arrow, coord_to_pixel(aw[0], aw[1]))
    playerarea.fill((100, 100, 100))
    player.draw(playerarea)

    enemiesarea.fill((100, 100, 100))
    enemies.draw(enemiesarea)
    for enemy in enemies:
        for i in range(enemy.hp):
            enemyheart = pg.transform.scale(heart, (size/4, size/4))
            enemiesarea.blit(enemyheart, (enemy.rect.x + i * (size / 3.5), enemy.rect.y))
    playarea.blit(playerarea, (0, 0))
    playarea.blit(enemiesarea, (0, 0))
    playarea.blit(walls, (0, 0))


def update_hud():
    hud.fill((255, 255, 255))
    buttons.draw(hud)
    hud.blit(ammo_text, ((WIDTH/1.9 + (12.4 * round(WIDTH/11))/2) - SCREEN_HEIGHT * (1/8), hud.get_size()[1]/2.2))
    for i in range(duck.hp):
        hud.blit(heart, ((WIDTH/2.1 - (10 * round(WIDTH/11))/2) + (SCREEN_HEIGHT * (1/8) * 0.75)*i, (SCREEN_HEIGHT * (1/8) * 0.3) / 2))
    for i in range(turns):
        hud.blit(turn_counter, ((WIDTH / 2.1 - (10 * round(WIDTH / 11)) / 2) + (SCREEN_HEIGHT * (1 / 8) * 0.75) * 3.2, (SCREEN_HEIGHT * (1 / 8) * 0.2) / 2 * 6.5 - i * SCREEN_HEIGHT * (1 / 8) / 3.5))


def update_enemies():
    for enemy in enemies:
        board[enemy.coord["x"]][enemy.coord["y"]] = 3
    for enemy in enemies:
        enemy.update()


def check_action(act, position):
    legal = False

    if act is None:
        legal = False

    if act == "move":
        #if 0 < abs(duck.coord["x"]-position[0]) + abs(duck.coord["y"]-position[1]) < 3:
        #    legal = True
        if abs(duck.coord["x"] - position[0]) < 3 and abs(duck.coord["y"] - position[1]) < 3:
            legal = True
        for enemy in enemies:
            if enemy.coord["x"] == position[0] and enemy.coord["y"] == position[1]:
                legal = False
        if board[position[0]][position[1]] == 1:
            legal = False
        if board[position[0]][position[1]] == 2:
            legal = False
        if legal:
            if abs(duck.coord["x"]-position[0]) > 1 or abs(duck.coord["y"]-position[1]) > 1:
                if board[int(position[0]+((duck.coord["x"]-position[0])*0.5))][int(position[1]+((duck.coord["y"]-position[1])*0.5))] == 1:
                    legal = False
            if abs(duck.coord["x"]-position[0]) > 1 or abs(duck.coord["y"]-position[1]) > 1:
                if board[int(position[0]+((duck.coord["x"]-position[0])*0.5))][int(position[1]+((duck.coord["y"]-position[1])*0.5))] == 2:
                    legal = False

    if act == "fly":
        if duck.coord["x"] == position[0] or duck.coord["y"] == position[1]:
            legal = True
        if abs(duck.coord["x"] - position[0]) == abs(duck.coord["y"] - position[1]):
            legal = True
        for enemy in enemies:
            if enemy.coord["x"] == position[0] and enemy.coord["y"] == position[1]:
                legal = False
        if board[position[0]][position[1]] == 1:
            legal = False
        if board[position[0]][position[1]] == 2:
            legal = False
        if legal:
            for i in range(max(abs(duck.coord["x"] - position[0]), abs(duck.coord["y"] - position[1]))+1):
                if (duck.coord["x"] - position[0]) > 0:
                    checkpos_x = position[0] + i
                elif (duck.coord["x"] - position[0]) < 0:
                    checkpos_x = position[0] - i
                else:  # (duck.coord["x"] - position[0]) == 0:
                    checkpos_x = duck.coord["x"]

                if (duck.coord["y"] - position[1]) > 0:
                    checkpos_y = position[1] + i
                elif (duck.coord["y"] - position[1]) < 0:
                    checkpos_y = position[1] - i
                else:  # (duck.coord["y"] - position[1]) == 0:
                    checkpos_y = duck.coord["y"]

                if board[checkpos_x][checkpos_y] == 1:
                    legal = False

    if act == "hit":
        for enemy in enemies:
            if (abs(duck.coord["x"]-position[0]) < 2 and abs(duck.coord["y"]-position[1]) < 2) and enemy.coord["x"] == position[0] and enemy.coord["y"] == position[1]:
                legal = True

    if act == "shoot":
        if board[position[0]][position[1]] == 1:
            legal = False
        if board[position[0]][position[1]] == 2:
            legal = False
        for enemy in enemies:
            if (duck.coord["x"] == position[0] or duck.coord["y"] == position[1]) and enemy.coord["x"] == position[0] and enemy.coord["y"] == position[1]:
                legal = True
            if abs(duck.coord["x"] - position[0]) == abs(duck.coord["y"] - position[1]) and enemy.coord["x"] == position[0] and enemy.coord["y"] == position[1]:
                legal = True
            if legal:
                for i in range(max(abs(duck.coord["x"] - position[0]), abs(duck.coord["y"] - position[1]))):
                    if (duck.coord["x"] - position[0]) > 0:
                        checkpos_x = position[0] + i
                    elif (duck.coord["x"] - position[0]) < 0:
                        checkpos_x = duck.coord["x"] + i
                    else:  # (duck.coord["x"] - position[0]) == 0:
                        checkpos_x = duck.coord["x"]

                    if (duck.coord["y"] - position[1]) > 0:
                        checkpos_y = position[1] + i
                    elif (duck.coord["y"] - position[1]) < 0:
                        checkpos_y = duck.coord["y"] + i
                    else:  # (duck.coord["y"] - position[1]) == 0:
                        checkpos_y = duck.coord["y"]

                    if board[checkpos_x][checkpos_y] == 1:
                        legal = False

    return legal


# kiszámolja, hogy egy koordinátának a táblán mi a pixelje
def coord_to_pixel(x, y):
    pixel_x = (size * x) - size
    pixel_y = (size * y) - size
    pixel_position = (pixel_x, pixel_y)
    return pixel_position


# kiszámolja, hogy egy pixel helye, melyik tábla kockára érkezik
def pixel_to_coord(x, y):
    position_x = math.ceil((x-((WIDTH-size*width)/2))/size)  # kis matek
    position_y = math.ceil((y-((HEIGHT-size*width)/2))/size)
    position_coord = (position_x, position_y)
    return position_coord


class Player(pg.sprite.Sprite):
    def __init__(self, pos):
        pg.sprite.Sprite.__init__(self)
        self.hp = 3
        self.image = pg.transform.scale(pg.image.load(os.path.join('assets/characters/duck', "duck.png")), (size, size))
        self.rect = self.image.get_rect()
        self.coord = {"x": pos[0], "y": pos[1]}
        x = (size * self.coord["x"]) - (size/2)  # - (size/2), hogy ne legyen elcsúsztatva
        y = (size * self.coord["y"]) - (size / 2)
        self.rect.center = (x, y)

    def update(self, pos):
        for i in range(11):
            clock.tick(FPS)
            x = ((((size * pos[0]) - (size / 2)) - ((size * self.coord["x"]) - (size/2))) * (i / 10)) + ((size * self.coord["x"]) - (size/2))
            y = ((((size * pos[1]) - (size / 2)) - ((size * self.coord["y"]) - (size/2))) * (i / 10)) + ((size * self.coord["y"]) - (size/2))
            self.rect.center = (x, y)

            update_playarea()
            screen.fill((255, 255, 255))
            screen.blit(hud, (0, SCREEN_HEIGHT * (6.8 / 8)))
            screen.blit(playarea, (WIDTH / 2 - (width * size) / 2, HEIGHT / 2 - (width * size) / 2))
            screen.blit(exit_button, (WIDTH - size / 2, 0))
            screen.blit(level_text, (WIDTH / 300, WIDTH / 300))
            pg.display.update()

        self.coord = {"x": pos[0], "y": pos[1]}
        x = (size * self.coord["x"]) - (size / 2)
        y = (size * self.coord["y"]) - (size / 2)
        self.rect.center = (x, y)


class Enemy(pg.sprite.Sprite):
    def __init__(self, pos, variant):
        pg.sprite.Sprite.__init__(self)
        self.variant = variant
        self.hp = int
        if variant == 1:
            self.hp = 2
        if variant == 2:
            self.hp = 1
        if variant == 3:
            self.hp = 1
        self.image = pg.transform.scale(pg.image.load(os.path.join('assets/characters/goose', str(self.variant)+".png")), (size, size))  # fajtától függ a képe
        self.rect = self.image.get_rect()
        self.coord = {"x": pos[0], "y": pos[1]}
        x = (size * self.coord["x"]) - (size / 2)  # - (size/2), hogy ne legyen elcsúsztatva
        y = (size * self.coord["y"]) - (size / 2)
        self.rect.center = (x, y)

    def update(self):
        global board
        # fajtától függően viselkednek
        if self.variant == 1:
            if abs(duck.coord["x"]-self.coord["x"]) < 2 and abs(duck.coord["y"]-self.coord["y"]) < 2:
                duck.hp -= 1

            else:
                best = (0, 0)
                for i in range(-1, 2):
                    for j in range(-1, 2):
                        if board[self.coord["x"]+i][self.coord["y"]+j] != 1 and board[self.coord["x"]+i][self.coord["y"]+j] != 2 and board[self.coord["x"]+i][self.coord["y"]+j] != 3 and board[self.coord["x"] + i][self.coord["y"] + j] != 4:
                            if math.sqrt((duck.coord["x"]-(self.coord["x"]+best[0]))**2 + (duck.coord["y"]-(self.coord["y"]+best[1]))**2) > math.sqrt((duck.coord["x"]-(self.coord["x"]+i))**2 + (duck.coord["y"]-(self.coord["y"]+j))**2):
                                best = (i, j)
                board[self.coord["x"]][self.coord["y"]] = 0
                pos = [0, 0]
                pos[0] = self.coord["x"] + best[0]
                pos[1] = self.coord["y"] + best[1]
                for i in range(11):
                    clock.tick(FPS)
                    x = ((((size * pos[0]) - (size / 2)) - ((size * self.coord["x"]) - (size / 2))) * (i / 10)) + ((size * self.coord["x"]) - (size / 2))
                    y = ((((size * pos[1]) - (size / 2)) - ((size * self.coord["y"]) - (size / 2))) * (i / 10)) + ((size * self.coord["y"]) - (size / 2))
                    self.rect.center = (x, y)

                    update_playarea()
                    screen.fill((255, 255, 255))
                    screen.blit(hud, (0, SCREEN_HEIGHT * (6.8 / 8)))
                    screen.blit(playarea, (WIDTH / 2 - (width * size) / 2, HEIGHT / 2 - (width * size) / 2))
                    screen.blit(exit_button, (WIDTH - size / 2, 0))
                    screen.blit(level_text, (WIDTH / 300, WIDTH / 300))
                    pg.display.update()

                self.coord["x"] = pos[0]
                self.coord["y"] = pos[1]
                board[self.coord["x"]][self.coord["y"]] = 3
                x = (size * self.coord["x"]) - (size / 2)
                y = (size * self.coord["y"]) - (size / 2)
                self.rect.center = (x, y)
        if self.variant == 2:
            can_shoot = duck.coord["x"] == self.coord["x"] or duck.coord["y"] == self.coord["y"]
            if can_shoot:
                if duck.coord["x"] == self.coord["x"]:
                    for i in range(abs(duck.coord["y"]-self.coord["y"])):
                        if duck.coord["y"] > self.coord["y"]:
                            if board[self.coord["x"]][self.coord["y"] + i] == 1:
                                can_shoot = False
                        if duck.coord["y"] < self.coord["y"]:
                            if board[self.coord["x"]][duck.coord["y"] + i] == 1:
                                can_shoot = False
                else:
                    for i in range(abs(duck.coord["x"] - self.coord["x"])):
                        if duck.coord["x"] > self.coord["x"]:
                            if board[self.coord["x"]+i][self.coord["y"]] == 1:
                                can_shoot = False
                        if duck.coord["x"] < self.coord["x"]:
                            if board[duck.coord["x"]+i][self.coord["y"]] == 1:
                                can_shoot = False
            if can_shoot:
                fly_arrow = pg.transform.scale(pg.image.load(os.path.join('assets', "arrowfly.png")), (size, size))
                if (self.coord["y"] - duck.coord["y"]) <= 0:
                    fly_arrow = pg.transform.rotate(fly_arrow, -1*math.degrees(math.acos((duck.coord["x"] - self.coord["x"]) / math.sqrt((duck.coord["x"] - self.coord["x"]) ** 2 + (duck.coord["y"] - self.coord["y"]) ** 2))))
                else:
                    fly_arrow = pg.transform.rotate(fly_arrow, math.degrees(math.acos((duck.coord["x"] - self.coord["x"]) / math.sqrt((duck.coord["x"] - self.coord["x"]) ** 2 + (duck.coord["y"] - self.coord["y"]) ** 2))))
                for i in range(11):
                    clock.tick(FPS)
                    x = ((((size * duck.coord["x"]) - (size / 2)) - ((size * self.coord["x"]) - (size / 2))) * (i / 10)) + ((size * self.coord["x"]) - (size / 2))
                    y = ((((size * duck.coord["y"]) - (size / 2)) - ((size * self.coord["y"]) - (size / 2))) * (i / 10)) + ((size * self.coord["y"]) - (size / 2))

                    update_playarea()
                    screen.fill((255, 255, 255))
                    screen.blit(hud, (0, SCREEN_HEIGHT * (6.8 / 8)))
                    screen.blit(playarea, (WIDTH / 2 - (width * size) / 2, HEIGHT / 2 - (width * size) / 2))
                    screen.blit(fly_arrow, (x, y))
                    screen.blit(exit_button, (WIDTH - size / 2, 0))
                    screen.blit(level_text, (WIDTH / 300, WIDTH / 300))
                    pg.display.update()

                duck.hp -= 1

            else:
                best = (0, 0)
                if abs(duck.coord["x"] - self.coord["x"]) < 3 and abs(duck.coord["y"] - self.coord["y"]) < 3:
                    print("menekulok")
                    for i in range(-1, 2):
                        for j in range(-1, 2):
                            if board[self.coord["x"] + i][self.coord["y"] + j] != 1 and board[self.coord["x"] + i][self.coord["y"] + j] != 2 and board[self.coord["x"] + i][self.coord["y"] + j] != 3 and board[self.coord["x"] + i][self.coord["y"] + j] != 4:
                                if math.sqrt((duck.coord["x"] - (self.coord["x"] + best[0])) ** 2 + (duck.coord["y"] - (self.coord["y"] + best[1])) ** 2) < math.sqrt((duck.coord["x"] - (self.coord["x"] + i)) ** 2 + (duck.coord["y"] - (self.coord["y"] + j)) ** 2):
                                    best = (i, j)
                else:
                    print("lepek")
                    if abs(duck.coord["x"]-self.coord["x"]) > abs(duck.coord["y"]-self.coord["y"]):
                        goal = (self.coord["x"], duck.coord["y"])
                    else:
                        goal = (duck.coord["x"], self.coord["y"])
                    print(goal)
                    for i in range(-1, 2):
                        for j in range(-1, 2):
                            if board[self.coord["x"] + i][self.coord["y"] + j] != 1 and board[self.coord["x"] + i][self.coord["y"] + j] != 2 and board[self.coord["x"] + i][self.coord["y"] + j] != 3 and board[self.coord["x"] + i][self.coord["y"] + j] != 4:
                                if math.sqrt((goal[0] - (self.coord["x"] + best[0])) ** 2 + (goal[1] - (self.coord["y"] + best[1])) ** 2) > math.sqrt((goal[0] - (self.coord["x"] + i)) ** 2 + (goal[1] - (self.coord["y"] + j)) ** 2):
                                    best = (i, j)
                board[self.coord["x"]][self.coord["y"]] = 0
                pos = [0, 0]
                pos[0] = self.coord["x"] + best[0]
                pos[1] = self.coord["y"] + best[1]
                for i in range(11):
                    clock.tick(FPS)
                    x = ((((size * pos[0]) - (size / 2)) - ((size * self.coord["x"]) - (size / 2))) * (i / 10)) + ((size * self.coord["x"]) - (size / 2))
                    y = ((((size * pos[1]) - (size / 2)) - ((size * self.coord["y"]) - (size / 2))) * (i / 10)) + ((size * self.coord["y"]) - (size / 2))
                    self.rect.center = (x, y)

                    update_playarea()
                    screen.fill((255, 255, 255))
                    screen.blit(hud, (0, SCREEN_HEIGHT * (6.8 / 8)))
                    screen.blit(playarea, (WIDTH / 2 - (width * size) / 2, HEIGHT / 2 - (width * size) / 2))
                    screen.blit(exit_button, (WIDTH - size / 2, 0))
                    screen.blit(level_text, (WIDTH / 300, WIDTH / 300))
                    pg.display.update()

                self.coord["x"] = pos[0]
                self.coord["y"] = pos[1]
                board[self.coord["x"]][self.coord["y"]] = 3
                x = (size * self.coord["x"]) - (size / 2)
                y = (size * self.coord["y"]) - (size / 2)
                self.rect.center = (x, y)
        if self.variant == 3:
            for i in range(2):
                if abs(duck.coord["x"]-self.coord["x"]) < 2 and abs(duck.coord["y"]-self.coord["y"]) < 2:
                    duck.hp -= 1

                else:
                    best = (0, 0)
                    for i in range(-1, 2):
                        for j in range(-1, 2):
                            if board[self.coord["x"]+i][self.coord["y"]+j] != 1 and board[self.coord["x"]+i][self.coord["y"]+j] != 3 and board[self.coord["x"] + i][self.coord["y"] + j] != 4:
                                if math.sqrt((duck.coord["x"]-(self.coord["x"]+best[0]))**2 + (duck.coord["y"]-(self.coord["y"]+best[1]))**2) > math.sqrt((duck.coord["x"]-(self.coord["x"]+i))**2 + (duck.coord["y"]-(self.coord["y"]+j))**2):
                                    best = (i, j)
                    board[self.coord["x"]][self.coord["y"]] = 0
                    pos = [0, 0]
                    pos[0] = self.coord["x"] + best[0]
                    pos[1] = self.coord["y"] + best[1]
                    for i in range(11):
                        clock.tick(FPS)
                        x = ((((size * pos[0]) - (size / 2)) - ((size * self.coord["x"]) - (size / 2))) * (i / 10)) + ((size * self.coord["x"]) - (size / 2))
                        y = ((((size * pos[1]) - (size / 2)) - ((size * self.coord["y"]) - (size / 2))) * (i / 10)) + ((size * self.coord["y"]) - (size / 2))
                        self.rect.center = (x, y)

                        update_playarea()
                        screen.fill((255, 255, 255))
                        screen.blit(hud, (0, SCREEN_HEIGHT * (6.8 / 8)))
                        screen.blit(playarea, (WIDTH / 2 - (width * size) / 2, HEIGHT / 2 - (width * size) / 2))
                        screen.blit(exit_button, (WIDTH - size / 2, 0))
                        screen.blit(level_text, (WIDTH / 300, WIDTH / 300))
                        pg.display.update()

                    self.coord["x"] = pos[0]
                    self.coord["y"] = pos[1]
                    board[self.coord["x"]][self.coord["y"]] = 3
                    x = (size * self.coord["x"]) - (size / 2)
                    y = (size * self.coord["y"]) - (size / 2)
                    self.rect.center = (x, y)


class Button(pg.sprite.Sprite):
    def __init__(self, pos, label):
        pg.sprite.Sprite.__init__(self)
        self.image = pg.transform.scale(pg.image.load(os.path.join('assets/buttons', label+".png")), (SCREEN_HEIGHT * (1/8) * 0.9, (SCREEN_HEIGHT * (1/8)) * 0.9))
        self.rect = self.image.get_rect()
        self.coord = {"x": pos[0], "y": pos[1]}
        x = self.coord["x"]
        y = self.coord["y"]
        self.rect.midright = (x, y)
        self.label = label

    def check(self, mouse):
        mouse = (mouse[0], mouse[1] - (SCREEN_HEIGHT * (6.8 / 8)))
        global action
        if self.rect.collidepoint(mouse):

            if self.label == "shoot":
                if ammo > 0:
                    action = self.label

            elif self.label == "fly":
                if turns >= 2:
                    action = self.label

            else:
                action = self.label


# buttons
buttons = pg.sprite.Group()
shoot = Button((WIDTH/1.9 + (10 * round(WIDTH/11))/2, hud.get_size()[1]/2), "shoot")
buttons.add(shoot)
hit = Button(((WIDTH/1.9 + (10 * round(WIDTH/11))/2) - SCREEN_HEIGHT * (1/8), hud.get_size()[1]/2), "hit")
buttons.add(hit)
fly = Button(((WIDTH/1.9 + (10 * round(WIDTH/11))/2) - SCREEN_HEIGHT * (1/8) * 2, hud.get_size()[1]/2), "fly")
buttons.add(fly)
move = Button(((WIDTH/1.9 + (10 * round(WIDTH/11))/2) - SCREEN_HEIGHT * (1/8) * 3, hud.get_size()[1]/2), "move")
buttons.add(move)

run = "story"

pygame.event.post(pygame.event.Event(NEW_LEVEL))

while run == "story":
    for i in range(120):
        clock.tick(FPS)
        image = pg.transform.scale(pg.image.load(os.path.join('assets/story', "house.png")), (WIDTH, SCREEN_HEIGHT*1.1))
        screen.blit(image, (0, 0 - i * SCREEN_HEIGHT * 0.1 / 120))
        pg.display.update()
    for i in range(180):
        clock.tick(FPS)
        image = pg.transform.scale(pg.image.load(os.path.join('assets/story', "inside_before.png")), (SCREEN_HEIGHT*1.5, SCREEN_HEIGHT))
        screen.blit(image, (SCREEN_HEIGHT * -0.5 + i / 120 * SCREEN_HEIGHT * 0.5 / 1.5, 0))
        pg.display.update()
    for i in range(2):
        clock.tick(FPS)
    for i in range(120):
        clock.tick(FPS)
        image = pg.transform.scale(pg.image.load(os.path.join('assets/story', "inside_after.png")), (SCREEN_HEIGHT*1.5, SCREEN_HEIGHT))
        screen.blit(image, (0 - i / 120 * SCREEN_HEIGHT * 0.5, 0))
        pg.display.update()
    for i in range(20):
        clock.tick(FPS)
    for i in range(150):
        clock.tick(FPS)
        image = pg.transform.scale(pg.image.load(os.path.join('assets/story', "letter.png")), (WIDTH, SCREEN_HEIGHT))
        screen.blit(image, (0, 0))
        pg.display.update()
    for i in range(20):
        clock.tick(FPS)
        image = pg.transform.scale(pg.image.load(os.path.join('assets/story', "sword.png")), (WIDTH, SCREEN_HEIGHT))
        screen.blit(image, (0, 0))
        pg.display.update()
    for i in range(20):
        clock.tick(FPS)
        image = pg.transform.scale(pg.image.load(os.path.join('assets/story', "bow.png")), (WIDTH, SCREEN_HEIGHT))
        screen.blit(image, (0, 0))
        pg.display.update()
    for i in range(20):
        clock.tick(FPS)
        image = pg.transform.scale(pg.image.load(os.path.join('assets/story', "end.png")), (WIDTH, WIDTH * 1.5))
        screen.blit(image, (0, SCREEN_HEIGHT * -2.5 / 8))
        pg.display.update()
    for i in range(120):
        clock.tick(FPS)
        image = pg.transform.scale(pg.image.load(os.path.join('assets/story', "end.png")), (WIDTH, WIDTH*1.5))
        screen.blit(image, (0, SCREEN_HEIGHT * -2.5 / 8 + i * SCREEN_HEIGHT * 2.5 / 8 / 120))
        pg.display.update()
    for i in range(60):
        clock.tick(FPS)
    run = "game"

while run == "game":
    clock.tick(FPS)
    for event in pg.event.get():
        if event.type == pg.QUIT:
            run = False

        if event.type == NEW_LEVEL:
            level += 1
            level_text = font.render(f"level: {level + 1}/10", True, (0, 0, 0))

            turns = 3
            action = None
            ammo = 3
            ammo_text = font.render(f"{ammo}", True, (0, 0, 0))
            arrows = []

            width = board_level[level]
            size = round(WIDTH / (width + 1))

            bgsurface = pg.Surface((width * size, width * size))
            walls = pg.Surface((width * size, width * size))
            walls.set_colorkey((100, 100, 100))
            enemiesarea = pg.Surface((width * size, width * size))
            enemiesarea.set_colorkey((100, 100, 100))
            playerarea = pg.Surface((width * size, width * size))
            playerarea.set_colorkey((100, 100, 100))
            playarea = pg.Surface((width * size, width * size))

            highlight = pg.transform.scale(pg.image.load(os.path.join('assets/ground', "highlight.png")), (size, size))
            arrow = pg.transform.scale(pg.image.load(os.path.join('assets', "arrow.png")), (size, size))
            fly_arrow = pg.transform.scale(pg.image.load(os.path.join('assets', "arrowfly.png")), (size, size))
            exit_button = pg.transform.scale(pg.image.load(os.path.join('assets/buttons', "exit.png")), (size/2, size/2))

            update_background()

            found = False
            while not found:
                try_x = random.randint(1, width)
                try_y = random.randint(1, width)
                legal1 = True
                if board[try_x][try_y] == 1 or board[try_x][try_y] == 2:
                    legal1 = False
                if legal1:
                    duck = Player((try_x, try_y))
                    player = pg.sprite.GroupSingle()
                    player.add(duck)
                    found = True

            enemies = pg.sprite.Group()
            while len(enemies.sprites()) < enemy_level[level][0]:
                try_x = random.randint(1, width)
                try_y = random.randint(1, width)
                legal1 = True
                if board[try_x][try_y] == 1 or board[try_x][try_y] == 2:
                    legal1 = False
                for enemy in enemies:
                    if enemy.coord["x"] == try_x and enemy.coord["y"] == try_y:
                        legal1 = False
                if abs(duck.coord["x"] - try_x) < 2 or abs(duck.coord["y"] - try_y) < 2:
                    legal1 = False
                if legal1:
                    enemies.add(Enemy((try_x, try_y), 1))

            while len(enemies.sprites()) < enemy_level[level][0] + enemy_level[level][1]:
                try_x = random.randint(1, width)
                try_y = random.randint(1, width)
                legal1 = True
                if board[try_x][try_y] == 1 or board[try_x][try_y] == 2:
                    legal1 = False
                for enemy in enemies:
                    if enemy.coord["x"] == try_x and enemy.coord["y"] == try_y:
                        legal1 = False
                if abs(duck.coord["x"]-try_x) < 2 or abs(duck.coord["y"]-try_y) < 2:
                    legal1 = False
                if legal1:
                    enemies.add(Enemy((try_x, try_y), 2))

            while len(enemies.sprites()) < enemy_level[level][0] + enemy_level[level][1] + enemy_level[level][2]:
                try_x = random.randint(1, width)
                try_y = random.randint(1, width)
                legal1 = True
                if board[try_x][try_y] == 1 or board[try_x][try_y] == 2:
                    legal1 = False
                for enemy in enemies:
                    if enemy.coord["x"] == try_x and enemy.coord["y"] == try_y:
                        legal1 = False
                if abs(duck.coord["x"]-try_x) < 2 or abs(duck.coord["y"]-try_y) < 2:
                    legal1 = False
                if legal1:
                    enemies.add(Enemy((try_x, try_y), 3))

        if event.type == pg.MOUSEBUTTONDOWN:
            mouse_pixel = pg.mouse.get_pos()
            # megnézzük, hogy a táblára kattintott-e
            if turns > 0:
                if (WIDTH/2 - (width * size)/2) < mouse_pixel[0] < (WIDTH/2 + (width * size)/2) and (HEIGHT/2 - (width * size)/2) < mouse_pixel[1] < (HEIGHT/2 + (width * size)/2) and action is not None:
                    mouse_cord = pixel_to_coord(mouse_pixel[0], mouse_pixel[1])

                    if action == "move":
                        if check_action("move", mouse_cord):
                            turns -= 1
                            player.update((mouse_cord[0], mouse_cord[1]))
                            for aw in arrows:
                                if duck.coord["x"] == aw[0] and duck.coord["y"] == aw[1]:
                                    arrows.remove(aw)
                                    ammo += 1
                                    ammo_text = font.render(f"{ammo}", True, (0, 0, 0))
                        else:
                            break

                    if action == "fly":
                        if check_action("fly", mouse_cord):
                            turns -= 2
                            player.update((mouse_cord[0], mouse_cord[1]))
                        else:
                            break

                    if action == "hit":
                        if check_action("hit", mouse_cord):
                            turns -= 1
                            for enemy in enemies:
                                if enemy.coord["x"] == mouse_cord[0] and enemy.coord["y"] == mouse_cord[1]:
                                    enemy.hp -= 1
                                    if enemy.hp < 1:
                                        enemy.kill()
                                        if len(enemies.sprites()) == 0:
                                            if level < 9:
                                                pygame.event.post(pygame.event.Event(NEW_LEVEL))
                                            else:
                                                run = "win"
                        else:
                            break

                    if action == "shoot":
                        if check_action("shoot", mouse_cord):
                            turns -= 1
                            for enemy in enemies:
                                if enemy.coord["x"] == mouse_cord[0] and enemy.coord["y"] == mouse_cord[1]:
                                    fly_arrow = pg.transform.scale(pg.image.load(os.path.join('assets', "arrowfly.png")), (size, size))
                                    if (duck.coord["y"]-enemy.coord["y"]) <= 0:
                                        fly_arrow = pg.transform.rotate(fly_arrow, -1*math.degrees(math.acos((enemy.coord["x"]-duck.coord["x"])/math.sqrt((enemy.coord["x"]-duck.coord["x"])**2+(enemy.coord["y"]-duck.coord["y"])**2))))
                                    else:
                                        fly_arrow = pg.transform.rotate(fly_arrow, math.degrees(math.acos((enemy.coord["x"] - duck.coord["x"]) / math.sqrt((enemy.coord["x"] - duck.coord["x"]) ** 2 + (enemy.coord["y"] - duck.coord["y"]) ** 2))))
                                    for i in range(11):
                                        clock.tick(FPS)
                                        x = ((((size * enemy.coord["x"]) - (size / 2)) - ((size * duck.coord["x"]) - (size / 2))) * (i / 10)) + ((size * duck.coord["x"]) - (size / 2))
                                        y = ((((size * enemy.coord["y"]) - (size / 2)) - ((size * duck.coord["y"]) - (size / 2))) * (i / 10)) + ((size * duck.coord["y"]) - (size / 2))

                                        update_playarea()
                                        screen.fill((255, 255, 255))
                                        screen.blit(hud, (0, SCREEN_HEIGHT * (6.8 / 8)))
                                        screen.blit(playarea, (WIDTH / 2 - (width * size) / 2, HEIGHT / 2 - (width * size) / 2))
                                        screen.blit(fly_arrow, (x, y))
                                        screen.blit(exit_button, (WIDTH - size / 2, 0))
                                        screen.blit(level_text, (WIDTH / 300, WIDTH / 300))
                                        pg.display.update()

                                    enemy.hp -= 1
                                    ammo -= 1
                                    ammo_text = font.render(f"{ammo}", True, (0, 0, 0))
                                    if enemy.hp < 1:
                                        enemy.kill()
                                        if len(enemies.sprites()) == 0:
                                            if level < 9:
                                                pygame.event.post(pygame.event.Event(NEW_LEVEL))
                                            else:
                                                run = "win"
                            arrows.append((mouse_cord[0], mouse_cord[1]))
                        else:
                            break

                    action = None

                else:
                    for i in buttons:
                        i.check(mouse_pixel)
                    if exit_button.get_rect().collidepoint(mouse_pixel[0] - WIDTH + size/2, mouse_pixel[1]):
                        pg.event.post(pg.event.Event(pg.QUIT))

    # frissítjük a képernyőt
    update_playarea()
    update_hud()
    screen.fill((255, 255, 255))
    screen.blit(hud, (0, SCREEN_HEIGHT * (6.8 / 8)))
    screen.blit(playarea, (WIDTH/2 - (width * size)/2, HEIGHT/2 - (width * size)/2))
    screen.blit(exit_button, (WIDTH - size/2, 0))
    screen.blit(level_text, (WIDTH/300, WIDTH/300))
    pg.display.update()

    if turns == 0:
        update_enemies()
        if duck.hp < 1:
            run = "died"
        turns = 3

if run == "died":
    run = True
    gameover = pg.transform.scale(pg.image.load(os.path.join('assets', "gameover.png")), (WIDTH, SCREEN_HEIGHT))
    screen.fill((255, 255, 255))
    screen.blit(gameover, (0, 0))
    screen.blit(exit_button, (WIDTH - size / 2, 0))
    pg.display.update()
    while run:
        clock.tick(FPS)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                run = False
            if event.type == pg.MOUSEBUTTONDOWN:
                mouse_pixel = pg.mouse.get_pos()
                if exit_button.get_rect().collidepoint(mouse_pixel[0] - WIDTH + size / 2, mouse_pixel[1]):
                    pg.event.post(pg.event.Event(pg.QUIT))

if run == "win":
    run = True
    win = pg.transform.scale(pg.image.load(os.path.join('assets', "win.png")), (WIDTH, SCREEN_HEIGHT))
    screen.fill((255, 255, 255))
    screen.blit(win, (0, 0))
    screen.blit(exit_button, (WIDTH - size / 2, 0))
    pg.display.update()
    while run:
        clock.tick(FPS)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                run = False
            if event.type == pg.MOUSEBUTTONDOWN:
                mouse_pixel = pg.mouse.get_pos()
                if exit_button.get_rect().collidepoint(mouse_pixel[0] - WIDTH + size / 2, mouse_pixel[1]):
                    pg.event.post(pg.event.Event(pg.QUIT))
