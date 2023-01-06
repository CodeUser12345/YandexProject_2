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
        self.rect = pygame.Rect(x, -y, width, height)
        self.image = get_image(None)

        self.animation_frame_index, self.animation_index, self.animation_flag = 0, 0, False
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

        self.vector, self.speed = None, 0  # переменные для перемещения спрайта
        self.vx, self.vy = 0, 0  # преобразованный вектор в x и y
        self.step_x, self.step_y = 0, 0  # переменные перемещения спрайта
        self.vector_flag, self.speed_flag = False, False  # флаги наличия или отсутствия параметров

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

        self.animations_frames.append([None] * self.animations_len[self.animation_index])
        self.animations_frames_sizes.append([None] * self.animations_len[self.animation_index])

        self.animations_scale.append(None)
        self.animations_scale_flag.append(None)
        self.set_animation_scale(-1, width, height)

        self.animations_position_politic.append(None)
        self.animations_position_politic_flag.append(None)
        self.animations_position_add.append([None] * self.animations_len[self.animation_index])
        self.set_animation_position_politic(-1, position_politic_x, position_politic_y)

        if activate:
            self.set_animation_activate(-1)

        self.update(0)

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

    def set_positions(self, x=None, y=None):
        index = self.get_animation_frame_index()
        if x is not None:
            self.step_x = x + self.animations_position_add[self.animation_index][index][0]
            self.rect.x = 0
        if y is not None:
            self.step_y = y + self.animations_position_add[self.animation_index][index][1]
            self.rect.y = 0

    def add_positions(self, x=None, y=None):
        if x is not None:
            self.step_x += x
        if y is not None:
            self.step_y += y

    def get_positions(self):
        index = self.get_animation_frame_index()
        return self.rect.x - self.animations_position_add[self.animation_index][index][0] + self.step_x, \
               -self.rect.y - self.animations_position_add[self.animation_index][index][1] - self.step_y

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

    def get_animations_len(self):
        return len(self.animations_images)

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

    def set_vector(self, degrees):
        self.vector = degrees
        if self.vector is not None:
            self.vector_flag = True
            self.vector %= 360
            radians = math.radians(self.vector)
            self.vx = math.sin(radians) if self.vector != 0 and self.vector != 180 else 0
            self.vy = math.cos(radians) if self.vector != 90 and self.vector != 270 else 0
        else:
            self.vector_flag = False

    def get_vector(self):
        return self.vector

    def set_speed(self, speed):
        if speed is not None and speed != 0:
            self.speed_flag = True
            self.speed = speed
        else:
            self.speed_flag = False

    def get_speed(self):
        return self.speed

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
                    add_y = sizes[index][1]
                else:
                    add_y = sizes[index][1] // 2

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

        self.step_x -= self.last_add_x
        self.step_y -= self.last_add_y
        self.step_x += self.animations_position_add[self.animation_index][index][0]
        self.step_y += self.animations_position_add[self.animation_index][index][1]
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

    def _run_update(self, number):
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
            self.rect.y -= number

    def _intersections(self, list_objects):
        new_list = []
        for n in list_objects:
            if pygame.sprite.collide_mask(self, n):
                new_list.append(n)
        return new_list

    def update(self, number, list_objects=()):
        frame_index = self._animation_frame_index_update(number)  # вычисляем текущий индекс анимации
        self._scale_frames_update()  # меняем масштаб frames
        self._position_politic_frames_update()  # устанавливаем значения сдвигов на основе politic position
        self._mask_update()  # обновляем маску
        self._frame_update(frame_index)  # обновляем frame
        self._animation_update(frame_index)  # активируем/переактивируем/деактивируем анимацию
        self._run_update(number)
        self._intersections(list_objects)  # вычисляем объекты с которыми было пересечение


class Entity(Sprite):
    def __init__(self, x, y, path_image):
        super().__init__(x, y, 1, 1)
        self.add_animation([[path_image, -1], "data\\frames_2\\Spider_1 — копия (6) (1) (1).png"], 0.001,
                           loop=True, activate=True)

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


class Object(Sprite):
    def __init__(self):
        pass


class Font:
    def __init__(self, *args, **kwargs):
        self.font = pygame.font.SysFont(*args, **kwargs)

    def render(self, *args, **kwargs):
        return self.font.render(*args, **kwargs)


class Text:
    def __init__(self, text, font, x=0, y=0, smooth=True, color=(0, 0, 0)):
        self.text = text
        self.font = font
        self.smooth = smooth
        self.color = color
        self.x, self.y = x, -y
        self.flag_obgect = False
        self.object = None

    def set_text(self, text):
        self.text = text
        self.flag_obgect = False

    def get_text(self):
        return self.text

    def set_font(self, font):
        self.font = font
        self.flag_obgect = False

    def get_font(self):
        return self.font

    def set_smooth(self, smooth):
        self.smooth = smooth
        self.flag_obgect = False

    def get_smooth(self):
        return self.smooth

    def set_color(self, color):
        self.color = color
        self.flag_obgect = False

    def get_color(self):
        return self.color

    def set_x(self, x):
        self.x = x

    def set_y(self, y):
        self.y = -y

    def set_positiolns(self, x, y):
        self.set_x(x)
        self.set_y(y)

    def get_x(self):
        return self.x

    def get_y(self):
        return self.y

    def get_positions(self):
        return self.x, self.y

    def _create_object(self):
        self.object = self.font.render(self.text, self.smooth, self.color)
        self.flag_obgect = True

    def draw(self, screen):
        if not self.flag_obgect:
            self._create_object()
        screen.blit(self.object, (self.x, self.y))


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
    def __init__(self, width, height, x=0, y=0, scale=1):
        self.sprites, self.index_list = [], []

        self.x, self.y,  = 0, 0
        self.set_x(x)
        self.set_y(y)

        self.scale = 1
        self.set_scale(scale)

        self.width, self.height = None, None
        self.center_x, self.center_y = None, None
        self.set_width(width)
        self.set_height(height)

    def add_sprite(self, sprite):
        self.sprites.append(sprite)
        self.index_list = range(len(self.sprites))

    def delete_sprite(self, index):
        self.sprites.pop(index)
        self.index_list = range(len(self.sprites))

    def set_width(self, width):
        self.width = width
        self.center_x = self.x + self.width // 2

    def set_height(self, height):
        self.height = height
        self.center_y = self.y - self.height // 2

    def set_sizes(self, width, height):
        self.set_width(width)
        self.set_height(height)

    def get_width(self):
        return self.width

    def get_height(self):
        return self.height

    def get_sizes(self):
        return self.width, self.height

    def set_x(self, x):
        self._x_update(x - self.x)

    def set_y(self, y):
        self._y_update(y - self.y)

    def set_positions(self, x, y):
        self.set_x(x)
        self.set_y(y)

    def get_y(self):
        return self.y

    def get_x(self):
        return self.x

    def get_positions(self):
        return self.x, self.y

    def set_scale(self, scale):
        self._scale_update(scale - self.scale)

    def get_scale(self):
        return self.scale

    def _x_update(self, x):
        if x != 0:
            self.x += x
            self.center_x += x
            for n in self.index_list:
                self.sprites[n].add_positions(-x, None)

    def _y_update(self, y):
        if y != 0:
            self.y += y
            self.center_y += y
            for n in self.index_list:
                self.sprites[n].add_positions(None, -y)

    def _scale_update(self, scale):
        if scale != 0:
            new_scale = self.scale + scale
            if new_scale >= 0:
                for n in self.index_list:
                    for s in range(self.sprites[n].get_animations_len()):
                        scale_x, scale_y = self.sprites[n].get_animation_scale(s)
                        new_scale_x, new_scale_y = scale_x / self.scale * new_scale, scale_y / self.scale * new_scale
                        self.sprites[n].set_animation_scale(s, new_scale_x, new_scale_y)

                    pos_x, pos_y = self.sprites[n].get_positions()
                    x, y = pos_x - self.center_x + self.x, pos_y - self.center_y + self.y
                    new_x, new_y = x / self.scale * new_scale, y / self.scale * new_scale
                    self.sprites[n].add_positions(new_x - x, new_y - y)

                    self.sprites[n].set_speed(self.sprites[n].get_speed() / self.scale * new_scale)
                self.scale = new_scale

    def update(self, x, y, scale):
        self._x_update(x)
        self._y_update(y)
        self._scale_update(scale)


class Group(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.texts = []

    def add(self, *args):
        if len(args) > 0:
            if type(args[0]) == Text:
                self.texts.append(args[0])
            else:
                super().add(*args)
        else:
            super().add(*args)

    def draw(self, *args, **kwargs):
        super().draw(*args, **kwargs)
        for n in self.texts:
            n.draw(args[0])


class MainWindow:
    def __init__(self):
        pygame.init()
        self.window = pygame.display.Info()
        self.width_window, self.height_window = self.window.current_w, self.window.current_h
        self.screen = pygame.display.set_mode((self.width_window // 1.5, self.height_window // 1.5))
        self.camera = Camera(self.width_window // 1.5, self.height_window // 1.5)

        self.last_time, self.step_time, self.number_frames_time = time.time(), 0.001, 0

        self.group = Group()

        self.entity = Entity(0, 0, "data\\frames_2\\Spider_1 — копия (5).png")
        self.entity.set_positions(100, 10)
        self.entity.add_positions(-100, -10)
        self.group.add(self.entity)
        self.entity.set_vector(135)
        self.entity.set_speed(0.1)
        self.camera.add_sprite(self.entity)

        self.entity2 = Entity(500, 0, "data\\frames_2\\Spider_1 — копия (5).png")
        self.group.add(self.entity2)
        self.entity2.set_vector(225)
        self.entity2.set_speed(0)
        self.camera.add_sprite(self.entity2)
        # button = Button(0, 0)

        font = Font(None, 40)
        text = Text("Text", font)
        self.group.add(text)

        self.running = True
        self.mouse_x, self.mouse_y = -1, -1
        self.mouse_left, self.mouse_right = False, False
        self.mouse_middle = False
        self.mouse_up, self.mouse_down = False, False
        self.keyboard_keys = []

        while self.running:
            self._get_data()  # получаем данные от клавиатуры и мышки
            x, y, scale = self._edit_data()  # обрабатываем данные
            self._get_number_frames_time()  # количество итераций за прошедшее время

            self.camera.update(x, y, scale)  # обновляем камеру
            self._updates_sprites()  # обновляем спрайты

            self._draw_all()  # рисуем все
        self._exit()

    def _exit(self):
        pygame.quit()

    def _draw_all(self):
        self.screen.fill((255, 255, 255))
        self.group.draw(self.screen)
        pygame.display.flip()

    def _updates_sprites(self):
        if self.number_frames_time:
            self.entity.update(self.number_frames_time)
            self.entity2.update(self.number_frames_time)

    def _edit_data(self):
        x = 1 * self.number_frames_time if 7 in self.keyboard_keys else \
            (-1 * self.number_frames_time if 4 in self.keyboard_keys else 0)
        y = 1 * self.number_frames_time if 26 in self.keyboard_keys else \
            (-1 * self.number_frames_time if 22 in self.keyboard_keys else 0)
        up_and_down = 0.05 * self.number_frames_time if self.mouse_up else \
            (-0.05 * self.number_frames_time if self.mouse_down else 0)
        return x, y, up_and_down

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
