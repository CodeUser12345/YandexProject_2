import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import pygame
import time
import random
import sys
import math


def load_image(path_image, colorkey=None):
    if not os.path.isfile(path_image):
        print(f"Файл с изображением '{path_image}' не найден")
        sys.exit()
    image = pygame.image.load(path_image)

    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


class Sprite(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.set_image(self.load_image(""))
        self.vx, self.vy, self.speed, self.vector_flag, self.speed_flag = 0, 0, 0, False, False
        self.step_x, self.step_y, self.last_time, self.step_time = 0, 0, time.time(), 0.001
        self.animations, self.animation_frame_index, self.animation_index, self.animation_flag = [], 0, 0, False

    def add(self, group):
        group.add(self)

    def load_image(self, path_image, colorkey_image=None):
        if path_image:
            return load_image(path_image, colorkey_image)
        else:
            return pygame.Surface((self.rect.w, self.rect.h))

    def set_image(self, image):
        self.image = image

    def set_vector(self, degrees):
        if degrees is not None:
            self.vector_flag = True
            degrees %= 360
            radians = math.radians(degrees)
            self.vx = math.sin(radians) if degrees != 0 and degrees != 180 else 0
            self.vy = math.cos(radians) if degrees != 90 and degrees != 270 else 0
        else:
            self.vector_flag = False

    def set_speed(self, speed):
        if speed is not None and speed != 0:
            self.speed_flag = True
            self.speed = speed
        else:
            self.speed_flag = False

    def set_position_x(self, x):
        self.rect.x = x

    def set_position_y(self, y):
        self.rect.y = y

    def set_positions(self, x, y):
        self.set_position_x(x)
        self.set_position_y(y)

    def set_size_width(self, width):
        self.rect.width = width

    def set_size_height(self, height):
        self.rect.height = height

    def set_sizes(self, width, height):
        self.set_size_width(width)
        self.set_size_height(height)

    def add_animation(self, frames, speed=0.01, activate=False):
        self.animations.append([None, None, None])
        self.set_frames_animation(-1, frames)
        self.set_speed_animation(-1, speed)
        if activate:
            self.set_activate_animation(-1)

    def set_frames_animation(self, index, frames):
        self.animations[index][0] = [self.load_image(n[0], n[1]) if type(n) == list else
                                     (self.load_image(n) if type(n) == str else
                                      self.set_image(n)) for n in frames]
        self.animations[index][1] = len(self.animations[index][0])

    def set_speed_animation(self, index, speed):
        self.animations[index][2] = speed

    def delete_animation(self, index):
        self.animations.pop(index)
        if self.animation_index == index and self.animation_flag:
            self.set_deactivate_animation()

    def set_activate_animation(self, index):
        self.animation_flag = True
        self.animation_index = index
        self.animation_frame_index = 0

    def set_deactivate_animation(self):
        self.animation_flag = False

    def _run(self, number):
        for _ in range(number):
            self.step_x += self.vx * self.speed
            self.step_y += self.vy * self.speed

        if self.step_x >= 1 or self.step_x <= -1:
            number = int(self.step_x)
            self.step_x -= number
            self.rect.x += number
        if self.step_y >= 1 or self.step_y <= -1:
            number = int(self.step_y)
            self.step_y -= number
            self.rect.y += number

    def _animation(self, number):
        last_animation_frame_index = int(self.animation_frame_index)
        self.animation_frame_index += number * self.animations[self.animation_index][2]
        now_animation_frame_index = int(self.animation_frame_index)
        if now_animation_frame_index > last_animation_frame_index:
            if now_animation_frame_index < self.animations[self.animation_index][1]:
                self.set_image(self.animations[self.animation_index][0][now_animation_frame_index])
            else:
                self.set_deactivate_animation()

    def update(self):
        time_now = time.time()
        step_last_and_now_time = time_now - self.last_time
        number = int(step_last_and_now_time // self.step_time)
        self.last_time = time_now - (step_last_and_now_time - number * self.step_time)
        if step_last_and_now_time >= self.step_time:
            if self.animation_flag:
                self._animation(number)
            if self.speed_flag and self.vector_flag:
                self._run(number)


class Entity(Sprite):
    def __init__(self, x, y, path_image):
        super().__init__(x, y, 25, 25)
        self.set_image(self.load_image(path_image, -1))
        self.set_sizes(50, 50)
        self.name = ""
        self.species = ""
        self.level_now, self.level_max = 0, 0
        self.power = 0
        self.protection = 0
        self.speed = 0
        self.intellect = 0
        self.health_points_now, self.health_points_max = 0, 0
        self.mana_points_now, self.mana_points_max = 0, 0
        self.energy_points_now, self.energy_points_max = 0, 0
        self.endurance_points_now, self.endurance_points_max = 0, 0

    def update(self):
        pass


class Button:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.passive_image = 0
        self.select_image = 0
        self.active_image = 0
        self.set_image(self.load_image(""))

    def update(self, x, y, key):
        pass

    def set_passive_image(self, image):
        pass

    def set_select_image(self, image):
        pass

    def set_active_image(self, image):
        pass


class MainWindow:
    def __init__(self):
        pygame.init()
        width, height = 900, 600
        screen = pygame.display.set_mode((width, height))#, pygame.FULLSCREEN)

        all_sprites = pygame.sprite.Group()

        entity = Entity(25, 25, "data\\frames_2\\Spider_1 — копия (5).png")
        entity.add(all_sprites)

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            entity.update()

            screen.fill((255, 255, 255))
            all_sprites.draw(screen)

            pygame.display.flip()
        pygame.quit()


if __name__ == '__main__':
    main_window = MainWindow()