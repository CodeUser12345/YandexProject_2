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
        self.image = get_image(None)

        self.animation_frame_index, self.animation_index, self.animation_flag, self.animations_len = 0, 0, False, 0
        self.animations_image = []  # список исходных изображений для каждой анимации
        self.animations_image_sizes = []  # список размеров исходных изображений для каждой анимации
        self.animations_len = []  # количество image/frame/mask для каждой анимации
        self.animations_speed = []  # скорость смены кадров для каждой анимации
        self.animations_loop = []  # флаги цикличности анимаций (повторять ли анимацию после ее завершения)
        self.animations_frames = []  # готовые кадры для отрисовки анимаций
        self.animations_mask = []  # маски кадров для каждой анимации
        self.animations_frame_size = []  # размер frame по высоте и ширине для каждой анимации
        self.animations_frame_size_flag = []  # спиcок флагов уже измененных/неизмененных frame для каждой анимации

    def add(self, group):
        group.add(self)

    def add_animation(self, frames, speed=0.01, loop=False, size=1, activate=False):
        self.animations_image.append(None)
        self.animations_image_sizes.append(None)
        self.animations_len.append(None)
        self.set_animation_image(-1, frames)

        self.animations_speed.append(None)
        self.set_animation_speed(-1, speed)

        self.animations_loop.append(None)
        self.set_animation_loop(-1, loop)

        self.animations_frames.append(None)
        self.animations_mask.append(None)

        self.animations_frame_size.append(None)
        self.animations_frame_size_flag.append(None)
        self.set_animation_size(-1, size)

        if activate:
            self.set_animation_activate(-1)

    def set_animation_image(self, index, frames):
        self.animations_image[index] = [get_image(n) for n in frames]
        self.animations_image_sizes[index] = [[n.get_width(), n.get_height()] for n in self.animations_image[index]]
        self.animations_len[index] = len(self.animations_image[index])

    def set_animation_speed(self, index, speed):
        self.animations_speed[index] = speed

    def set_animation_loop(self, index, loop=True):
        self.animations_loop[index] = loop

    def set_animation_size(self, index, size=1):
        self.animations_frame_size[index] = size
        self.animations_frame_size_flag[index] = True
        print(self.animations_frame_size, self.animations_frame_size_flag)

    def delete_animation(self, index):
        self.animations_image.pop(index)
        self.animations_image_sizes.pop(index)
        self.animations_len.pop(index)

        self.animations_speed.pop(index)

        self.animations_loop.pop(index)

        self.animations_frames.pop(index)
        self.animations_mask.pop(index)

        self.animations_frame_size.pop(index)
        self.animations_frame_size_flag.pop(index)

        if self.animation_index == index and self.animation_flag:
            self.set_animation_deactivate()

    def set_animation_activate(self, index):
        self.animation_flag = True
        self.animation_index = index
        self.animation_frame_index = 0

    def set_animation_deactivate(self):
        self.animation_flag = False

    def _set_frame_and_mask(self):
        if self.animations_frame_size_flag[self.animation_index]:
            if self.animations_frames[self.animation_index] is None:
                self.animations_frames[self.animation_index] = [None] * self.animations_len[self.animation_index]

            size = self.animations_frame_size[self.animation_index]
            images = self.animations_image[self.animation_index]
            images_sizes = self.animations_image_sizes[self.animation_index]
            for index in range(self.animations_len[self.animation_index]):
                self.animations_frames[self.animation_index][index] = \
                    pygame.transform.scale(images[index], (int(images_sizes[index][0] * size),
                                                           int(images_sizes[index][1] * size)))

            self.animations_mask[self.animation_index] = \
                [pygame.mask.from_surface(frame) for frame in self.animations_frames[self.animation_index]]

            self.animations_frame_size_flag[self.animation_index] = False

    def _set_image(self, index):
        self._set_frame_and_mask()
        self.image = self.animations_frames[self.animation_index][index]
        self.mask = self.animations_mask[self.animation_index][index]

    def _animation(self, number):
        if self.animation_flag:
            last_animation_frame_index = int(self.animation_frame_index)
            self.animation_frame_index += number * self.animations_speed[self.animation_index]
            now_animation_frame_index = int(self.animation_frame_index)
            if now_animation_frame_index > last_animation_frame_index:
                if now_animation_frame_index < self.animations_len[self.animation_index]:
                    self._set_image(now_animation_frame_index)
                elif last_animation_frame_index < self.animations_len[self.animation_index]:
                    self._set_image(-1)
                else:
                    if self.animations_loop[self.animation_index]:
                        self.set_animation_activate(self.animation_index)
                    else:
                        self.set_animation_deactivate()

    def _intersections(self, list_objects):
        for n in list_objects:
            if pygame.sprite.collide_mask(self, n):
                pass  # print(True)
            else:
                pass  # print(False)

    def update(self, number, list_objects=()):
        self._animation(number)
        self._intersections(list_objects)


class Entity(Sprite):
    def __init__(self, x, y, path_image):
        super().__init__(x, y, 1, 1)
        self.vx, self.vy, self.speed, self.vector_flag, self.speed_flag = 0, 0, 0, False, False
        self.step_x, self.step_y = 0, 0
        self.add_animation([get_image([path_image, -1])], 100, activate=True)

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

    def update(self, number, list_objects=()):
        self._animation(number)
        if self.speed_flag and self.vector_flag:
            self._run(number)
        self._intersections(list_objects)


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


class Camera:
    def __init__(self):
        self.sprites = []
        self.sprites_sizes = []
        self.sprites_len = 0

    def add_sprite(self, sprite):
        self.sprites.append(sprite)
        self.sprites_sizes.append(1)
        self.sprites_len = len(self.sprites)

    def delete_sprite(self, index):
        self.sprites.pop(index)

    def update(self, x, y, up_and_down):
        for n in range(self.sprites_len):
            self.sprites[n].rect.x -= x
            self.sprites[n].rect.y -= y
            if up_and_down == -1 or up_and_down == 1:
                self.sprites_sizes[n] += up_and_down * 0.01
                if self.sprites_sizes[n] > 0:
                    self.sprites[n].set_animation_size(0, self.sprites_sizes[n])
                    self.sprites[n].set_animation_activate(0)
            # width, height = n.image.get_rect().size
            # n.image = pygame.transform.scale(n.image, (width + up_and_down, height + up_and_down))


class MainWindow:
    def __init__(self):
        pygame.init()
        self.window = pygame.display.Info()
        self.width_window, self.height_window = self.window.current_w // 1.5, \
                                                self.window.current_h // 1.5  # деление потом убрать
        self.screen = pygame.display.set_mode((self.width_window, self.height_window))
        self.camera = Camera()

        self.last_time, self.step_time, self.number_frames_time = time.time(), 0.001, 0

        self.all_sprites = pygame.sprite.Group()

        entity = Entity(25, 25, "data\\frames_2\\Spider_1 — копия (5).png")
        entity.add(self.all_sprites)
        entity.set_vector(135)
        entity.set_speed(0.1)
        self.camera.add_sprite(entity)

        entity2 = Entity(425, 25, "data\\frames_2\\Spider_1 — копия (5).png")
        entity2.add(self.all_sprites)
        entity2.set_vector(225)
        entity2.set_speed(0.1)
        self.camera.add_sprite(entity2)
        # button = Button(0, 0)

        self.running = True
        self.mouse_x, self.mouse_y = -1, -1
        self.mouse_left, self.mouse_right = False, False
        self.mouse_middle = False
        self.mouse_up, self.mouse_down = False, False
        self.keyboard_keys = []

        while self.running:
            self._get_data()
            self._get_number_frames_time()

            x = 1 if 7 in self.keyboard_keys else (-1 if 4 in self.keyboard_keys else 0)
            y = 1 if 22 in self.keyboard_keys else (-1 if 26 in self.keyboard_keys else 0)
            up_and_down = 1 if self.mouse_up else (-1 if self.mouse_down else 0)
            self.camera.update(x, y, up_and_down)
            if self.number_frames_time:
                entity.update(self.number_frames_time)
                entity2.update(self.number_frames_time)
            # button.update(self.mouse_x, self.mouse_y, self.mouse_left)

            self._draw_all()
        self._exit()

    def _exit(self):
        pygame.quit()

    def _draw_all(self):
        self.screen.fill((255, 255, 255))
        self.all_sprites.draw(self.screen)
        pygame.display.flip()

    def _get_data(self):
        self.mouse_up, self.mouse_down = False, False

        events = pygame.event.get()
        mouse_focused = pygame.mouse.get_focused()
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False

            if mouse_focused:
                if event.type == pygame.MOUSEMOTION:
                    self.mouse_x, self.mouse_y = pygame.mouse.get_pos()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.mouse_left = True
                    elif event.button == 2:
                        self.mouse_middle = True
                    elif event.button == 3:
                        self.mouse_right = True
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.mouse_left = False
                    elif event.button == 2:
                        self.mouse_middle = False
                    elif event.button == 3:
                        self.mouse_right = False
                elif event.type == pygame.MOUSEWHEEL:
                    if event.y == 1:
                        self.mouse_up = True
                    elif event.y == -1:
                        self.mouse_down = True
            else:
                self.mouse_x, self.mouse_y = -1, -1

        self.keyboard_keys = []
        new_list = list(pygame.key.get_pressed())
        for n in range(len(new_list)):
            if new_list[n]:
                self.keyboard_keys.append(n)

    def _get_number_frames_time(self):
        time_now = time.time()
        step_last_and_now_time = time_now - self.last_time
        number = int(step_last_and_now_time // self.step_time)
        self.last_time = time_now - (step_last_and_now_time - number * self.step_time)
        if number > 30:
            self.number_frames_time = 0
        else:
            self.number_frames_time = number


if __name__ == '__main__':
    main_window = MainWindow()
