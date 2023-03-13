main.py
from level import *
from sprites import *


class Game:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        self.rect = self.screen.get_rect()
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        self.playing = True
        self.all_group = pg.sprite.Group()
        self.viewpoint = self.rect

    def new(self):
        self.level_surface = pg.Surface((WIDTH, HEIGHT)).convert()
        self.background = load_image('level.png')
        self.back_rect = self.background.get_rect()
        self.background = pg.transform.scale(self.background,
                                             (int(self.back_rect.width * BACKGROUND_SIZE),
                                              int(self.back_rect.height * BACKGROUND_SIZE))).convert()
        self.level = Level()
        self.all_group.add(self.level.mario)

    def run(self):
        while self.playing:
            self.clock.tick(FPS)
            self.events()
            self.update()
            self.draw()

    def update(self):
        self.all_group.update()
        self.level.update()
        if self.level.mario.pos.x < self.viewpoint.x + 15:
            self.level.mario.pos.x -= self.level.mario.vel.x
        if self.level.mario.vel.x > 0:
            if self.level.mario.pos.x > WIDTH * 0.55 + self.viewpoint.x:
                self.viewpoint.x += int(self.level.mario.vel.x * 1.1)
        if self.level.mario.dead:
            self.playing = False

    def events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.playing = False

    def draw(self):
        pg.display.flip()
        self.background_clean = self.background.copy()
        self.all_group.draw(self.background_clean)
        self.screen.blit(self.background, (0, 0), self.viewpoint)
        self.all_group.draw(self.screen)

    def show_start_screen(self):
        pass

    def show_end_screen(self):
        pass


game = Game()
game.show_start_screen()
game.new()
game.run()
game.show_end_screen()
sprites.py
import random
from tools import *
from settings import *

vec = pg.math.Vector2


class Mario(pg.sprite.Sprite):
    def __init__(self):
        pg.sprite.Sprite.__init__(self)
        self.sheet = load_image('mario.png')
        self.load_from_sheet()
        self.walking_timer = pg.time.get_ticks()
        self.image_index = 4
        self.image = self.frames[0]
        self.rect = self.image.get_rect()
        self.pos = vec(WIDTH * 0.5, GROUND_HEIGHT - 70)
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)
        self.landing = False
        self.dead = False

    def update(self):
        self.acc = vec(0, GRAVITY)
        keys = pg.key.get_pressed()
        if keys[pg.K_RIGHT]:
            self.walk('right')
            if self.vel.x > 0:
                self.acc.x = TURNAROUND
            if self.vel.x <= 0:
                self.acc.x = ACC
            self.pos.x += 5
        elif keys[pg.K_LEFT]:
            self.walk('left')
            if self.vel.x < 0:
                self.acc.x = -TURNAROUND
            if self.vel.x >= 0:
                self.acc.x = -ACC
        else:
            self.image_index = 0
        if abs(self.vel.x) < MAX_SPEED:
            self.vel.x += self.acc.x
        elif keys[pg.K_LEFT]:
            self.vel.x = -MAX_SPEED
        elif keys[pg.K_RIGHT]:
            self.vel.x = MAX_SPEED
        if keys[pg.K_SPACE]:
            if self.landing:
                self.vel.y = -JUMP
        if not self.landing:
            self.image_index = 4
        self.image = self.frames[self.image_index]
        self.acc.x += self.vel.x * FRICTION
        self.vel += self.acc
        self.pos += self.vel + 0.5 * self.acc

        self.rect.midbottom = self.pos

    def calculate_animation_speed(self):
        if self.vel.x == 0:
            animation_speed = 130
        elif self.vel.x > 0:
            animation_speed = 130 - (self.vel.x * 12)
        else:
            animation_speed = 130 - (self.vel.x * 12 * -1)
        return animation_speed

    def walk(self, facing):
        if self.image_index == 0:
            self.image_index += 1
            self.walking_timer = pg.time.get_ticks()
        else:
            if (pg.time.get_ticks() - self.walking_timer >
                    self.calculate_animation_speed()):
                self.image_index += 1
                self.walking_timer = pg.time.get_ticks()
        if facing == 'right':
            if self.image_index > 3:
                self.image_index = 0
        if facing == 'left':
            if self.image_index > 8:
                self.image_index = 5
            if self.image_index < 5:
                self.image_index = 5

    def load_from_sheet(self):
        self.right_frames = []
        self.left_frames = []

        self.right_frames.append(
            self.get_image(178, 32, 12, 16))
        self.right_frames.append(
            self.get_image(80, 32, 15, 16))
        self.right_frames.append(
            self.get_image(96, 32, 16, 16))
        self.right_frames.append(
            self.get_image(112, 32, 16, 16))
        self.right_frames.append(
            self.get_image(144, 32, 16, 16))

        for frame in self.right_frames:
            new_image = pg.transform.flip(frame, True, False)
            self.left_frames.append(new_image)

        self.frames = self.right_frames + self.left_frames

    def get_image(self, x, y, width, height):
        image = pg.Surface([width, height])
        rect = image.get_rect()
        image.blit(self.sheet, (0, 0), (x, y, width, height))
        image.set_colorkey(BLACK)
        image = pg.transform.scale(image,
                                   (int(rect.width * MARIO_SIZE),
                                    int(rect.height * MARIO_SIZE)))
        return image


class Collider(pg.sprite.Sprite):
    def __init__(self, x, y, width, height):
        pg.sprite.Sprite.__init__(self)
        self.image = pg.Surface((width, height)).convert()
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
level.py
from sprites import *


class Level(pg.sprite.Sprite):
    def __init__(self):
        self.set_mario()
        self.set_ground()
        self.set_pipes()
        self.set_steps()
        self.set_group()

    def set_group(self):
        self.ground_step_pipe_group = pg.sprite.Group(self.ground_group,
                                                      self.pipe_group,
                                                      self.step_group)

    def update(self):
        self.check_collide()
        self.adjust_x()
        self.adjust_y()
        self.check_dead()
        print(self.mario.pos)

    def set_mario(self):
        self.mario = Mario()

    def set_ground(self):
        ground_rect1 = Collider(0, GROUND_HEIGHT, 2953, 60)
        ground_rect2 = Collider(3048, GROUND_HEIGHT, 635, 60)
        ground_rect3 = Collider(3819, GROUND_HEIGHT, 2735, 60)
        ground_rect4 = Collider(6647, GROUND_HEIGHT, 2300, 60)

        self.ground_group = pg.sprite.Group(ground_rect1,
                                            ground_rect2,
                                            ground_rect3,
                                            ground_rect4)

    def set_pipes(self):
        pipe1 = Collider(1202, 452, 83, 80)
        pipe2 = Collider(1631, 409, 83, 140)
        pipe3 = Collider(1973, 366, 83, 170)
        pipe4 = Collider(2445, 366, 83, 170)
        pipe5 = Collider(6989, 452, 83, 82)
        pipe6 = Collider(7675, 452, 83, 82)

        self.pipe_group = pg.sprite.Group(pipe1, pipe2,
                                          pipe3, pipe4,
                                          pipe5, pipe6)

    def set_steps(self):
        step1 = Collider(5745, 495, 40, 44)
        step2 = Collider(5788, 452, 40, 88)
        step3 = Collider(5831, 409, 40, 132)
        step4 = Collider(5874, 366, 40, 176)

        step5 = Collider(6001, 366, 40, 176)
        step6 = Collider(6044, 408, 40, 40)
        step7 = Collider(6087, 452, 40, 40)
        step8 = Collider(6130, 495, 40, 40)

        step9 = Collider(6345, 495, 40, 40)
        step10 = Collider(6388, 452, 40, 40)
        step11 = Collider(6431, 409, 40, 40)
        step12 = Collider(6474, 366, 40, 40)
        step13 = Collider(6517, 366, 40, 176)

        step14 = Collider(6644, 366, 40, 176)
        step15 = Collider(6687, 408, 40, 40)
        step16 = Collider(6728, 452, 40, 40)
        step17 = Collider(6771, 495, 40, 40)

        step18 = Collider(7760, 495, 40, 40)
        step19 = Collider(7803, 452, 40, 40)
        step20 = Collider(7845, 409, 40, 40)
        step21 = Collider(7888, 366, 40, 40)
        step22 = Collider(7931, 323, 40, 40)
        step23 = Collider(7974, 280, 40, 40)
        step24 = Collider(8017, 237, 40, 40)
        step25 = Collider(8060, 194, 40, 40)
        step26 = Collider(8103, 194, 40, 360)

        step27 = Collider(8488, 495, 40, 40)

        self.step_group = pg.sprite.Group(step1, step2,
                                          step3, step4,
                                          step5, step6,
                                          step7, step8,
                                          step9, step10,
                                          step11, step12,
                                          step13, step14,
                                          step15, step16,
                                          step17, step18,
                                          step19, step20,
                                          step21, step22,
                                          step23, step24,
                                          step25, step26,
                                          step27)

    def check_collide(self):
        self.ground_collide = pg.sprite.spritecollideany(self.mario, self.ground_group)
        self.pipe_collide = pg.sprite.spritecollideany(self.mario, self.pipe_group)
        self.step_collide = pg.sprite.spritecollideany(self.mario, self.step_group)

    def adjust_x(self):
        if self.pipe_collide:
            if self.mario.pos.y > self.pipe_collide.rect.y + 10:
                if self.mario.vel.x > 0:
                    self.mario.pos.x -= 5
                    self.mario.vel.x = 0
                if self.mario.vel.x < 0:
                    self.mario.pos.x = 5
                    self.mario.vel.x = 0
        if self.step_collide:
            if self.mario.pos.y > self.step_collide.rect.y + 10:
                if self.mario.vel.x > 0:
                    self.mario.pos.x -= 5
                    self.mario.vel.x = 0
                if self.mario.vel.x < 0:
                    self.mario.pos.x = 5
                    self.mario.vel.x = 0

    def adjust_y(self):
        if self.ground_collide:
            if self.ground_collide.rect.top < self.mario.pos.y:
                self.mario.acc.y = 0
                self.mario.vel.y = 0
                self.mario.pos.y = self.ground_collide.rect.top
            self.mario.landing = True
        else:
            self.mario.landing = False
        if self.pipe_collide:
            if self.mario.vel.y > 0:
                if self.pipe_collide.rect.top < self.mario.pos.y:
                    self.mario.acc.y = 0
                    self.mario.vel.y = 0
                    self.mario.pos.y = self.pipe_collide.rect.top
                self.mario.landing = True
        if self.step_collide:
            if self.mario.vel.y > 0:
                if self.step_collide.rect.top < self.mario.pos.y:
                    self.mario.acc.y = 0
                    self.mario.vel.y = 0
                    self.mario.pos.y = self.step_collide.rect.top
                self.mario.landing = True

    def check_dead(self):
        if self.mario.pos.y > GROUND_HEIGHT + 50:
            self.mario.dead = True
tools.py
import os
import pygame as pg


def load_image(filename):
    src = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(src, 'resources', 'graphics', filename)
    return pg.image.load(path)
settings.py
# 标题和窗口大小
TITLE = 'Mario'
WIDTH = 800
HEIGHT = 600
​
FPS = 60
​
# 定义颜色
GRAY = (100, 100, 100)
BLACK = (0, 0, 0)
​
# 图片缩放比例
MARIO_SIZE = 2.5
BACKGROUND_SIZE = 2.679
​
# Mario 运动系数
ACC = 0.3
GRAVITY = 1
FRICTION = -0.12
JUMP = 20
TURNAROUND = 0.7
MAX_SPEED = 6
​
# 地面高度
GROUND_HEIGHT = HEIGHT - 66
