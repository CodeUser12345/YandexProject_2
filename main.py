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
        self.animations_images = []  # список исходных изображений для каждой анимации
        self.animations_images_sizes = []  # список размеров исходных изображений для каждой анимации
        self.animations_len = []  # количество image/frame/mask для каждой анимации
        self.animations_speed = []  # скорость смены кадров для каждой анимации
        self.animations_loop = []  # флаги цикличности анимаций (повторять ли анимацию после ее завершения)
        self.animations_mask = []  # маски кадров для каждой анимации
        self.animations_mask_flag = []  # нужно ли обновить masks для frames
        self.animations_frames = []  # готовые кадры для отрисовки анимаций
        self.animations_frames_sizes = []  # размер frame по высоте и ширине для каждой анимации

        self.animations_scale = []  # масштаб для каждой анимации
        self.animations_scale_flag = []  # спиcок флагов уже измененных/неизмененных scale frame для каждой анимации

        self.animations_position_politic = []  # политика синхронизации frames для каждой анимации
        self.animations_position_politic_flag = []  # список флагов измененных/неизмененных position politic frame для каждой анимации
        self.animations_position_add = []  # добавочные значения x и y в соответствии с политикой синхронизации
        self.last_add_x, self.last_add_y = 0, 0  # прошлые добавочные значения (нужны для отката прошлого сложения)

    def add(self, group):
        group.add(self)

    def add_animation(self, images, speed=0.01, loop=False, width=1, height=1,
                      position_politic_x=0, position_politic_y=0, activate=False):
        self.animations_images.append(None)
        self.animations_images_sizes.append(None)
        self.animations_len.append(None)
        self.set_animation_images(-1, images)

        self.animations_speed.append(None)
        self.set_animation_speed(-1, speed)

        self.animations_loop.append(None)
        self.set_animation_loop(-1, loop)

        self.animations_mask.append(None)
        self.animations_mask_flag.append(None)

        self.animations_frames.append(None)
        self.animations_frames_sizes.append(None)

        self.animations_scale.append(None)
        self.animations_scale_flag.append(None)
        self.set_animation_scale(-1, width, height)

        self.animations_position_politic.append(None)
        self.animations_position_politic_flag.append(None)
        self.animations_position_add.append(None)
        self.set_animation_position_politic(-1, position_politic_x, position_politic_y)

        if activate:
            self.set_animation_activate(-1)

    def delete_animation(self, index):
        self.animations_images.pop(index)
        self.animations_images_sizes.pop(index)
        self.animations_len.pop(index)

        self.animations_speed.pop(index)

        self.animations_loop.pop(index)

        self.animations_mask.pop(index)
        self.animations_mask_flag.pop(index)

        self.animations_frames.pop(index)
        self.animations_frames_sizes.pop(index)

        self.animations_scale.pop(index)
        self.animations_scale_flag.pop(index)

        self.animations_position_politic.pop(index)
        self.animations_position_politic_flag.pop(index)
        self.animations_position_add.pop(index)

        if self.animation_index == index and self.animation_flag:
            self.set_animation_deactivate()

    def set_animation_images(self, index, images):
        self.animations_images[index] = [get_image(n) for n in images]
        self.animations_images_sizes[index] = [[n.get_width(), n.get_height()] for n in self.animations_images[index]]
        self.animations_len[index] = len(self.animations_images[index])

    def get_animation_images(self, index):
        return self.animations_images[index]

    def get_animation_images_sizes(self, index):
        return self.animations_images_sizes[index]

    def get_animation_len(self, index):
        return self.animations_len[index]

    def set_animation_speed(self, index, speed):
        self.animations_speed[index] = speed

    def get_animation_speed(self, index):
        return self.animations_speed[index]

    def set_animation_loop(self, index, loop=True):
        self.animations_loop[index] = loop

    def get_animation_loop(self, index):
        return self.animations_loop[index]

    def set_animation_scale(self, index, width=1, height=1):
        self.animations_scale[index] = [width, height]
        self.animations_scale_flag[index] = True

    def get_animation_scale(self, index):
        return self.animations_scale[index]

    def get_animation_frames_sizes(self, index):
        return self.animations_frames_sizes[index]

    def set_animation_activate(self, index):
        self.animation_flag = True
        self.animation_index = index
        self.animation_frame_index = 0

    def set_animation_deactivate(self):
        self.animation_flag = False
        self.animation_frame_index = self.animations_len[self.animation_index] - 1

    def get_animation_index(self):
        return self.animation_index

    def get_animation_frame_index(self):
        if self.animation_frame_index < self.animations_len[self.animation_index]:
            return int(self.animation_frame_index)
        else:
            return self.animations_len[self.animation_index] - 1

    def get_animation_activate(self):
        return self.animation_flag

    def set_animation_position_politic(self, index, x=0, y=0):
        self.animations_position_politic[index] = [x, y]
        self.animations_position_politic_flag[index] = True

    def get_animation_position_politic(self, index):
        return self.animations_position_politic[index]

    def _lists_update(self):
        if self.animations_frames[self.animation_index] is None:
            self.animations_frames[self.animation_index] = [None] * self.animations_len[self.animation_index]
            self.animations_frames_sizes[self.animation_index] = [None] * self.animations_len[self.animation_index]
            self.animations_position_add[self.animation_index] = [None] * self.animations_len[self.animation_index]
            return True
        return False

    def _scale_frames_update(self):
        if self.animations_scale_flag[self.animation_index]:
            images = self.animations_images[self.animation_index]
            sizes = self.animations_images_sizes[self.animation_index]
            scale = self.animations_scale[self.animation_index]
            for index in range(self.animations_len[self.animation_index]):
                width = int(sizes[index][0] * scale[0])
                height = int(sizes[index][1] * scale[1])
                self.animations_frames[self.animation_index][index] = \
                    pygame.transform.scale(images[index], (width, height))
                self.animations_frames_sizes[self.animation_index][index] = [width, height]
            self.animations_scale_flag[self.animation_index] = False
            self.animations_position_politic_flag[self.animation_index] = True
            self.animations_mask_flag[self.animation_index] = True
            return True
        return False

    def _position_politic_frames_update(self):
        if self.animations_position_politic_flag[self.animation_index]:
            sizes = self.animations_frames_sizes[self.animation_index]
            for index in range(self.animations_len[self.animation_index]):
                if self.animations_position_politic[self.animation_index][0] == 1:
                    add_x = -sizes[index][0]
                elif self.animations_position_politic[self.animation_index][0] == -1:
                    add_x = 0
                else:
                    add_x = -sizes[index][0] // 2

                if self.animations_position_politic[self.animation_index][1] == 1:
                    add_y = 0
                elif self.animations_position_politic[self.animation_index][1] == -1:
                    add_y = -sizes[index][1]
                else:
                    add_y = -sizes[index][1] // 2

                self.animations_position_add[self.animation_index][index] = [add_x, add_y]
            self.animations_position_politic_flag[self.animation_index] = False
            return True
        return False

    def _mask_update(self):
        if self.animations_mask_flag[self.animation_index]:
            self.animations_mask[self.animation_index] = \
                [pygame.mask.from_surface(frame) for frame in self.animations_frames[self.animation_index]]
            self.animations_mask_flag[self.animation_index] = False

    def _frame_update(self, index):
        if index is None:
            index = -1
        self.image = self.animations_frames[self.animation_index][index]
        self.mask = self.animations_mask[self.animation_index][index]

        self.rect.x -= self.last_add_x
        self.rect.y -= self.last_add_y
        self.rect.x += self.animations_position_add[self.animation_index][index][0]
        self.rect.y += self.animations_position_add[self.animation_index][index][1]
        self.last_add_x = self.animations_position_add[self.animation_index][index][0]
        self.last_add_y = self.animations_position_add[self.animation_index][index][1]

    def _animation_frame_index_update(self, number):
        last_animation_frame_index = int(self.animation_frame_index)
        self.animation_frame_index += number * self.animations_speed[self.animation_index]
        now_animation_frame_index = int(self.animation_frame_index)
        if now_animation_frame_index > last_animation_frame_index:
            if now_animation_frame_index < self.animations_len[self.animation_index]:
                return now_animation_frame_index
            elif last_animation_frame_index < self.animations_len[self.animation_index]:
                return self.animations_len[self.animation_index] - 1
            else:
                return None
        else:
            if last_animation_frame_index < self.animations_len[self.animation_index]:
                return last_animation_frame_index
            else:
                return None

    def _animation_update(self, index):
        if self.animation_flag:
            if index is None:
                if self.animations_loop[self.animation_index]:
                    self.set_animation_activate(self.animation_index)
                else:
                    self.set_animation_deactivate()
            return True
        return False

    def _intersections(self, list_objects):
        new_list = []
        for n in list_objects:
            if pygame.sprite.collide_mask(self, n):
                new_list.append(n)
        return new_list

    def update(self, number, list_objects=()):
        self._lists_update()  # добавляем None в списки новых animations
        frame_index = self._animation_frame_index_update(number)  # вычисляем текущий индекс анимации
        self._scale_frames_update()  # меняем масштаб frames
        self._position_politic_frames_update()  # устанавливаем значения сдвигов на основе politic position
        self._mask_update()  # обновляем маску
        self._frame_update(frame_index)  # обновляем frame
        self._animation_update(frame_index)  # активируем/переактивируем/деактивируем анимацию
        self._intersections(list_objects)  # вычисляем объекты с которыми было пересечение


class Entity(Sprite):
    def __init__(self, x, y, path_image):
        super().__init__(x, y, 1, 1)
        self.vx, self.vy, self.speed, self.vector_flag, self.speed_flag = 0, 0, 0, False, False
        self.step_x, self.step_y = 0, 0
        self.add_animation([[path_image, -1], "data\\frames_2\\Spider_1 — копия (6) (1) (1).png"], 0.001, loop=True, activate=True)

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
    def __init__(self, width, height, min_x=0, max_x=1000, now_x=0, min_y=0, max_y=1000, now_y=0,
                 min_scale=0.5, max_scale=1.5, now_scale=1):
        self.sprites, self.index_list = [], []

        self.width, self.height = None, None
        self.set_width(width)
        self.set_height(height)

        self.min_x, self.max_x, self.now_x = None, None, 0
        self.set_min_x(min_x)
        self.set_max_x(max_x)
        self.set_now_x(now_x)

        self.min_y, self.max_y, self.now_y = None, None, 0
        self.set_min_y(min_y)
        self.set_max_y(max_y)
        self.set_now_y(now_y)

        self.min_scale, self.max_scale, self.now_scale = None, None, 1
        self.set_min_scale(min_scale)
        self.set_max_scale(max_scale)
        self.set_now_scale(now_scale)

    def add_sprite(self, sprite):
        self.sprites.append(sprite)
        self.index_list = range(len(self.sprites))

    def delete_sprite(self, index):
        self.sprites.pop(index)
        self.index_list = range(len(self.sprites))

    def set_width(self, width):
        self.width = width

    def set_height(self, height):
        self.height = height

    def set_min_x(self, number):
        self.min_x = number

    def get_min_x(self):
        return self.min_x

    def set_max_x(self, number):
        self.max_x = number

    def get_max_x(self):
        return self.max_x

    def set_now_x(self, number):
        self._x_update(number - self.now_x)

    def get_now_x(self):
        return self.now_x

    def set_min_y(self, number):
        self.min_y = number

    def get_min_y(self):
        return self.min_y

    def set_max_y(self, number):
        self.max_y = number

    def get_max_y(self):
        return self.max_y

    def set_now_y(self, number):
        self._y_update(number - self.now_y)

    def get_now_y(self):
        return self.now_y

    def set_min_scale(self, number):
        self.min_scale = number

    def get_min_scale(self):
        return self.min_scale

    def set_max_scale(self, number):
        self.max_scale = number

    def get_max_scale(self):
        return self.max_scale

    def set_now_scale(self, number):
        self._scale_update(number - self.now_scale)

    def get_now_scale(self):
        return self.now_scale

    def _x_update(self, x):
        if x != 0:
            self.now_x += x
            if self.now_x >= self.min_x and self.now_x <= self.max_x:
                for n in self.index_list:
                    self.sprites[n].rect.x -= x
            else:
                self.now_x -= x

    def _y_update(self, y):
        if y != 0:
            self.now_y += y
            if self.now_y >= self.min_y and self.now_y <= self.max_y:
                for n in self.index_list:
                    self.sprites[n].rect.y -= y
            else:
                self.now_y -= y

    def _scale_update(self, scale):
        if scale != 0:
            new_scale = self.now_scale + scale
            if new_scale >= self.min_scale and new_scale <= self.max_scale:
                for n in self.index_list:
                    index = self.sprites[n].get_animation_index()
                    scale = self.sprites[n].get_animation_scale(index)
                    index_frame = self.sprites[n].get_animation_frame_index()
                    last_sizes = self.sprites[n].get_animation_frames_sizes(index)[index_frame]
                    new_scale_x, new_scale_y = scale[0] / self.now_scale * new_scale, \
                                               scale[1] / self.now_scale * new_scale
                    self.sprites[n].set_animation_scale(index, new_scale_x, new_scale_y)
                    new_sizes = self.sprites[n].get_animation_frames_sizes(index)[index_frame]
                self.now_scale = new_scale

    def update(self, x, y, scale):
        self._x_update(x)
        self._y_update(y)
        self._scale_update(scale)


class MainWindow:
    def __init__(self):
        pygame.init()
        self.window = pygame.display.Info()
        self.width_window, self.height_window = self.window.current_w, self.window.current_h
        self.screen = pygame.display.set_mode((self.width_window // 1.5, self.height_window // 1.5))
        self.camera = Camera(self.width_window, self.height_window, min_x=-500, max_x=500, min_y=-500, max_y=500)

        self.last_time, self.step_time, self.number_frames_time = time.time(), 0.001, 0

        self.all_sprites = pygame.sprite.Group()

        entity = Entity(25, 25, "data\\frames_2\\Spider_1 — копия (5).png")
        entity.add(self.all_sprites)
        entity.set_vector(135)
        entity.set_speed(0)
        self.camera.add_sprite(entity)

        entity2 = Entity(425, 25, "data\\frames_2\\Spider_1 — копия (5).png")
        entity2.add(self.all_sprites)
        entity2.set_vector(225)
        entity2.set_speed(0)
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

            x = 1 * self.number_frames_time if 7 in self.keyboard_keys else \
                (-1 * self.number_frames_time if 4 in self.keyboard_keys else 0)
            y = 1 * self.number_frames_time if 22 in self.keyboard_keys else \
                (-1 * self.number_frames_time if 26 in self.keyboard_keys else 0)
            up_and_down = 0.05 * self.number_frames_time \
                if self.mouse_up else (-0.05 * self.number_frames_time if self.mouse_down else 0)
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
        if number > 30:
            self.number_frames_time = 0
        else:
            self.number_frames_time = number
        self.last_time = time_now - (step_last_and_now_time - number * self.step_time)


if __name__ == '__main__':
    main_window = MainWindow()
