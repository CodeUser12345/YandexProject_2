import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import pygame
import time
import random
import sys
import math


def get_image(data):
    type_data = type(data)
    if type_data is tuple or type_data is list:
        path_image = data[0]
        color_key = data[1]
    elif type_data is str:
        path_image = data
        color_key = None
    elif data is None:
        path_image = None
        color_key = None
    elif type_data is pygame.Surface:
        return data
    else:
        print(f"Ошибка определения параметров, тип '{type_data}' не определен")
        sys.exit()

    if path_image is not None:
        if not os.path.isfile(path_image):
            print(f"Файл с изображением '{path_image}' не найден")
            sys.exit()
        image = pygame.image.load(path_image)

        if color_key is not None:
            image = image.convert()
            if color_key == -1:
                color_key = image.get_at((0, 0))
            image.set_colorkey(color_key)
        else:
            image = image.convert_alpha()
    else:
        image = pygame.Surface((25, 25))
    return image


class Sprite(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.set_image(get_image(None))
        self.last_time, self.step_time = time.time(), 0.001
        self.animations, self.animation_frame_index, self.animation_index, self.animation_flag = [], 0, 0, False

    def add(self, group):
        group.add(self)

    def set_image(self, image):
        self.image = image

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
        self.animations[index][0] = [get_image(n) for n in frames]
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

    def _animation(self, number):
        last_animation_frame_index = int(self.animation_frame_index)
        self.animation_frame_index += number * self.animations[self.animation_index][2]
        now_animation_frame_index = int(self.animation_frame_index)
        if now_animation_frame_index > last_animation_frame_index:
            if now_animation_frame_index < self.animations[self.animation_index][1]:
                self.set_image(self.animations[self.animation_index][0][now_animation_frame_index])
            else:
                self.set_deactivate_animation()

    def _get_steps_last_and_now_time(self, time_now):
        step_last_and_now_time = time_now - self.last_time
        number = int(step_last_and_now_time // self.step_time)
        self.last_time = time_now - (step_last_and_now_time - number * self.step_time)
        if number > 30:
            return 0
        else:
            return number

    def update(self, time_now):
        number = self._get_steps_last_and_now_time(time_now)
        if number:
            if self.animation_flag:
                self._animation(number)


class Entity(Sprite):
    def __init__(self, x, y, path_image):
        super().__init__(x, y, 25, 25)
        self.vx, self.vy, self.speed, self.vector_flag, self.speed_flag = 0, 0, 0, False, False
        self.step_x, self.step_y = 0, 0
        self.set_image(get_image([path_image, -1]))

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

    def set_vector(self, degrees):
        if degrees is not None:
            self.vector_flag = True
            degrees %= 360
            radians = math.radians(degrees)
            self.vx = math.sin(radians) if degrees != 0 and degrees != 180 else 0
            self.vy = math.cos(radians) * -1 if degrees != 90 and degrees != 270 else 0
        else:
            self.vector_flag = False

    def set_speed(self, speed):
        if speed is not None and speed != 0:
            self.speed_flag = True
            self.speed = speed
        else:
            self.speed_flag = False

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

    def update(self, time_now):
        number = self._get_steps_last_and_now_time(time_now)
        if number:
            if self.animation_flag:
                self._animation(number)
            if self.speed_flag and self.vector_flag:
                self._run(number)


class Object(Sprite):
    def __init__(self):
        pass


class Button:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 25, 25)
        self.passive_image = None
        self.select_image = None
        self.active_image = None

        self.sprite = pygame.sprite.Sprite()
        self.sprite.image = get_image(None)

    def set_passive_image(self, image):
        self.passive_image = image

    def set_select_image(self, image):
        self.select_image = image

    def set_active_image(self, image):
        self.active_image = image

    def update(self, x, y, key):
        pass


class MainWindow:
    def __init__(self):
        pygame.init()
        self.window = pygame.display.Info()
        self.width_window, self.height_window = self.window.current_w // 1.5, \
                                                self.window.current_h // 1.5 # деление потом убрать
        self.screen = pygame.display.set_mode((self.width_window, self.height_window))

        self.all_sprites = pygame.sprite.Group()

        entity = Entity(25, 25, "data\\frames_2\\Spider_1 — копия (5).png")
        entity.add(self.all_sprites)
        entity.set_vector(125)
        entity.set_speed(0.1)
        #button = Button(0, 0)

        self.running = True
        self.mouse_x, self.mouse_y = -1, -1
        self.mouse_left, self.mouse_right = False, False
        self.mouse_middle = False
        self.mouse_up, self.mouse_down = False, False
        self.keyboard_keys = []

        self._get_data()

        while self.running:
            self._get_data()

            time_now = time.time()

            entity.update(time_now)

            self.screen.fill((255, 255, 255))
            self.all_sprites.draw(self.screen)
            pygame.display.flip()
        pygame.quit()

    def _get_data(self):
        mouse_focused = pygame.mouse.get_focused()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if mouse_focused:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.mouse_left = True
                    if event.button == 2:
                        self.mouse_middle = True
                    if event.button == 3:
                        self.mouse_right = True
                    if event.button == 4:
                        self.mouse_up = True
                    if event.button == 5:
                        self.mouse_down = True
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.mouse_left = False
                    if event.button == 2:
                        self.mouse_middle = False
                    if event.button == 3:
                        self.mouse_right = False
                    if event.button == 4:
                        self.mouse_up = False
                    if event.button == 5:
                        self.mouse_down = False
                if event.type == pygame.MOUSEMOTION:
                    self.mouse_x, self.mouse_y = pygame.mouse.get_pos()
            else:
                self.mouse_x, self.mouse_y = -1, -1
                self.mouse_left, self.mouse_right = False, False
                self.mouse_middle = False
                self.mouse_up, self.mouse_down = False, False

            self.keyboard_keys = []
            new_list = list(pygame.key.get_pressed())
            for n in range(len(new_list)):
                if new_list[n]:
                    self.keyboard_keys.append(n)
            print(self.keyboard_keys)


if __name__ == '__main__':
    main_window = MainWindow()
