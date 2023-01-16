import os
import random

import pygame
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


class Animation:
    # возможность загрузить анимацию (список изображений)/выгрузить/изменить/запустить/остановить и т. д.
    def __init__(self, *args, **kwargs):
        self.frame_index, self.activate = 0, False
        self.images = []  # список исходных изображений
        self.images_sizes = []  # список размеров исходных изображений

        self.len = None  # количество image/frame/mask
        self.speed = None  # скорость смены кадров
        self.loop = None  # флаги цикличности анимации (повторять ли анимацию после ее завершения)

        self.mask = []  # маски кадров
        self.mask_flag = None  # нужно ли обновить masks для frames

        self.rotation = None  # поворот
        self.rotation_flag = None  # флаг уже измененной/неизмененной rotation frame

        self.rotation_frames = []  # повернутые изображения
        self.rotation_frames_sizes = []  # размер повернутых изображений по высоте и ширине

        self.scale = [None, None]  # масштаб по x и y
        self.scale_flag = None  # флаг уже измененной/неизмененной scale frame

        self.scale_frames = []  # готовые кадры для отрисовки анимации
        self.scale_frames_sizes = []  # размер scale frame по высоте и ширине

        self.politic = [None, None]  # политика синхронизации frames
        self.politic_flag = None  # флаг уже измененной/неизмененной politic frame

        self.politic_add = []  # добавочные значения x и y в соответствии с политикой синхронизации

        self.set_animation(*args, **kwargs)

    def load_animation(self, path):
        with open(path, "r", encoding="utf-8") as file:
            text = file.read().split("\n")
            len_text = len(text)
            data_object = []
            images = []
            index = 1
            while index < len_text:
                string = text[index].replace(" ", "").split(",")
                index += 1
                if string == ["parameters:"]:
                    break
                string[0] = string[0][1:-1].replace("\\\\", "\\")
                if len(string) > 1:
                    string[1] = int(string[1])
                else:
                    string = string[0]
                images.append(string)
            data_object.append(["images", images])

            while index < len_text:
                data = text[index].replace(" ", "").split(",")
                identificator, data = data[0], ", ".join(data[1:])
                if data[:6] == "random":
                    data = [int(n) for n in data[7:-1].replace(" ", "").split(",")]
                    data = random.randrange(data[0], data[1], data[2])
                elif identificator in ["speed", "width", "height", "rotation", "politic_x", "politic_y"]:
                    data = float(data)
                elif identificator in ["loop", "activate"]:
                    if data in ["False", "0"]:
                        data = False
                    else:
                        data = True
                else:
                    print(f"Ошибка, идентификатор {identificator} не определен")
                    sys.exit()
                data_object.append([identificator, data])
                index += 1

            identificators = ["images", "speed", "loop", "width", "height",
                              "rotation", "politic_x", "politic_y", "activate"]
            data = [[None], 100, False, 1.0, 1.0, 0.0, 0.0, 0.0, True]
            for n in data_object:
                data[identificators.index(n[0])] = n[1]

            self.set_animation(data[0], speed=data[1], loop=data[2], width=data[3], height=data[4],
                               rotation=data[5], politic_x=data[6], politic_y=data[7], activate=data[8])

    def set_animation(self, images, speed=0.01, loop=False, width=1.0, height=1.0, rotation=0.0,
                      politic_x=0.0, politic_y=0.0, activate=False):
        self.set_speed(speed)
        self.set_loop(loop)

        self.set_rotation(rotation)
        self.set_scale(width, height)
        self.set_politic(politic_x, politic_y)

        if activate:
            self.set_activate()

        self.set_images(images)

    def set_images(self, images):
        self.images = [get_image(n) for n in images]
        self.images_sizes = [[n.get_width(), n.get_height()] for n in self.images]
        self.len = len(self.images)

        self.rotation_frames = [None] * self.len
        self.rotation_frames_sizes = [None] * self.len
        self.scale_frames = [None] * self.len
        self.scale_frames_sizes = [None] * self.len
        self.politic_add = [None] * self.len

        self.update(0)

    def get_images(self):
        return self.images

    def get_images_sizes(self):
        return self.images_sizes

    def get_len(self):
        return self.len

    def set_speed(self, speed):
        self.speed = speed

    def get_speed(self):
        return self.speed

    def set_loop(self, loop=True):
        self.loop = loop

    def get_loop(self):
        return self.loop

    def set_rotation(self, rotation):
        self.rotation = rotation
        self.rotation_flag = True

    def get_rotation(self):
        return self.rotation

    def get_rotation_frames(self):
        return self.rotation_frames

    def get_rotation_frames_sizes(self):
        return self.rotation_frames_sizes

    def set_scale(self, width=1.0, height=1.0):
        self.scale = [width, height]
        self.scale_flag = True

    def get_scale(self):
        return self.scale

    def get_scale_frames(self):
        return self.scale_frames

    def get_scale_frames_sizes(self):
        return self.scale_frames_sizes

    def set_frame_index(self, frame_index):
        self.frame_index = frame_index

    def get_frame_index(self):
        if self.frame_index < self.len:
            return self.frame_index
        else:
            return self.len - 1

    def set_activate(self):
        self.activate = True

    def set_deactivate(self):
        self.activate = False

    def get_activate(self):
        return self.activate

    def set_politic(self, x=0.0, y=0.0):
        self.politic = [x, y]
        self.politic_flag = True

    def get_politic(self):
        return self.politic

    def get_politic_add(self):
        return self.politic_add

    def get_mask(self):
        return self.mask

    def _rotation_frames_update(self):
        if self.rotation_flag:
            images = self.images
            rotation = self.rotation
            for index in range(self.len):
                self.rotation_frames[index] = \
                    pygame.transform.rotate(images[index], rotation)
                width = self.rotation_frames[index].get_width()
                height = self.rotation_frames[index].get_height()
                self.rotation_frames_sizes[index] = [width, height]
            self.rotation_flag = False
            self.scale_flag = True

    def _scale_frames_update(self):
        if self.scale_flag:
            images = self.rotation_frames
            sizes = self.rotation_frames_sizes
            scale = self.scale
            for index in range(self.len):
                width = int(sizes[index][0] * scale[0])
                height = int(sizes[index][1] * scale[1])
                self.scale_frames[index] = \
                    pygame.transform.scale(images[index], (width, height))
                self.scale_frames_sizes[index] = [width, height]
            self.scale_flag = False
            self.politic_flag = True
            self.mask_flag = True

    def _politic_frames_update(self):
        if self.politic_flag:
            for index in range(self.len):
                add_x = self.scale_frames_sizes[index][0] * self.politic[0]
                add_y = self.scale_frames_sizes[index][1] * self.politic[1]
                self.politic_add[index] = [add_x, add_y]
            self.politic_flag = False

    def _mask_update(self):
        if self.mask_flag:
            self.mask = [pygame.mask.from_surface(frame) for frame in self.scale_frames]
            self.mask_flag = False

    def _frame_update(self, number):
        if self.activate:
            last_frame_index = int(self.frame_index)
            self.frame_index += number * self.speed
            now_frame_index = int(self.frame_index)
            if now_frame_index > last_frame_index:
                if now_frame_index == self.len:
                    if self.loop:
                        self.set_frame_index(0)
                        self.set_activate()
                    else:
                        self.set_deactivate()

    def update(self, number):
        self._frame_update(number)  # вычисляем текущий индекс анимации
        self._rotation_frames_update()  # поворачиваем изображение
        self._scale_frames_update()  # меняем масштаб frames
        self._politic_frames_update()  # устанавливаем значения сдвигов на основе politic position
        self._mask_update()  # обновляем маску


class Run:
    # возможность установить вектор и скорость передвижения, возможно получить x и y смещения с течением времени
    def __init__(self):
        self.vector, self.speed = None, 0  # переменные для перемещения спрайта
        self.vx, self.vy = 0, 0  # преобразованный вектор в x и y
        self.step_x, self.step_y = 0, 0  # переменные перемещения спрайта
        self.vector_flag, self.speed_flag = False, False  # флаги наличия или отсутствия параметров

        self.x, self.y = 0, 0

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

    def get_shift_x_y(self):
        return self.x, self.y

    def _run_update(self, number):
        for _ in range(number):
            self.step_x += self.vx * self.speed
            self.step_y += self.vy * self.speed

        if self.step_x >= 1 or self.step_x <= -1:
            number = int(self.step_x)
            self.step_x -= number
            self.x += number
        if self.step_y >= 1 or self.step_y <= -1:
            number = int(self.step_y)
            self.step_y -= number
            self.y -= number

    def update(self, number):
        self._run_update(number)


class Sprite(pygame.sprite.Sprite):
    # возможно изменить картинку/маску/позицию, узнать о пересечении с другими объектами
    def __init__(self, x, y, width, height):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = get_image(None)
        self.mask = None

    def set_positions(self, x=None, y=None):
        if x is not None:
            self.rect.x = x
        if y is not None:
            self.rect.y = y

    def add_positions(self, x=None, y=None):
        if x is not None:
            self.rect.x += x
        if y is not None:
            self.rect.y += y

    def get_positions(self):
        return self.rect.x, self.rect.y

    def set_image(self, image):
        self.image = image

    def set_mask(self, mask):
        self.mask = mask

    def get_intersections(self, list_objects):
        new_list = []
        for n in list_objects:
            if pygame.sprite.collide_mask(self, n):
                new_list.append(n)
        return new_list

    def update(self):
        pass
