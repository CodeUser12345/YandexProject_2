import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import pygame
import time
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

        self.animations_rotation = []  # поворот для каждой анимации
        self.animations_rotation_flag = []  # спиcок флагов уже измененных/неизмененных rotation frame для каждой анимации
        self.animations_rotation_frames = []  # повернутые изображения
        self.animations_rotation_frames_sizes = []  # размер повернутых изображений по высоте и ширине для каждой анимации

        self.animations_scale = []  # масштаб для каждой анимации
        self.animations_scale_flag = []  # спиcок флагов уже измененных/неизмененных scale frame для каждой анимации
        self.animations_scale_frames = []  # готовые кадры для отрисовки анимаций
        self.animations_scale_frames_sizes = []  # размер frame по высоте и ширине для каждой анимации

        self.animations_position_politic = []  # политика синхронизации frames для каждой анимации
        self.animations_position_politic_flag = []  # список флагов измененных/неизмененных position politic frame для каждой анимации
        self.animations_position_add = []  # добавочные значения x и y в соответствии с политикой синхронизации
        self.last_add_x, self.last_add_y = 0, 0  # прошлые добавочные значения (нужны для отката прошлого сложения)

        self.vector, self.speed = None, 0  # переменные для перемещения спрайта
        self.vx, self.vy = 0, 0  # преобразованный вектор в x и y
        self.step_x, self.step_y = 0, 0  # переменные перемещения спрайта
        self.vector_flag, self.speed_flag = False, False  # флаги наличия или отсутствия параметров

    def add_animation(self, images, speed=0.01, loop=False, width=1, height=1, rotation=0,
                      position_politic_x=0, position_politic_y=0, activate=False):
        index = self.get_animations_len()
        self.animations_images.append(None)
        self.animations_images_sizes.append(None)
        self.animations_len.append(None)
        self.set_animation_images(index, images)

        self.animations_speed.append(None)
        self.set_animation_speed(index, speed)

        self.animations_loop.append(None)
        self.set_animation_loop(index, loop)

        self.animations_mask.append(None)
        self.animations_mask_flag.append(None)

        self.animations_rotation.append(None)
        self.animations_rotation_flag.append(None)
        self.animations_rotation_frames.append([None] * self.animations_len[index])
        self.animations_rotation_frames_sizes.append([None] * self.animations_len[index])
        self.set_animation_rotation(index, rotation)

        self.animations_scale.append(None)
        self.animations_scale_flag.append(None)
        self.animations_scale_frames.append([None] * self.animations_len[index])
        self.animations_scale_frames_sizes.append([None] * self.animations_len[index])
        self.set_animation_scale(index, width, height)

        self.animations_position_politic.append(None)
        self.animations_position_politic_flag.append(None)
        self.animations_position_add.append([None] * self.animations_len[index])
        self.set_animation_position_politic(index, position_politic_x, position_politic_y)

        if activate:
            self.set_animation_activate(index)

        self.update(0)

    def delete_animation(self, index):
        if self.animation_index == index and self.animation_flag:
            self.set_animation_frame_index(self.get_animation_len(index) - 1)
            self.set_animation_deactivate()

        self.animations_images.pop(index)
        self.animations_images_sizes.pop(index)
        self.animations_len.pop(index)

        self.animations_speed.pop(index)

        self.animations_loop.pop(index)

        self.animations_mask.pop(index)
        self.animations_mask_flag.pop(index)

        self.animations_rotation.pop(index)
        self.animations_rotation_flag.pop(index)
        self.animations_rotation_frames.pop(index)
        self.animations_rotation_frames_sizes.pop(index)

        self.animations_scale.pop(index)
        self.animations_scale_flag.pop(index)
        self.animations_scale_frames.pop(index)
        self.animations_scale_frames_sizes.pop(index)

        self.animations_position_politic.pop(index)
        self.animations_position_politic_flag.pop(index)
        self.animations_position_add.pop(index)

    def set_positions(self, x=None, y=None):
        index = int(self.get_animation_frame_index())
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
        index = int(self.get_animation_frame_index())
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

    def set_animation_rotation(self, index, rotation):
        self.animations_rotation[index] = rotation
        self.animations_rotation_flag[index] = True

    def get_animation_rotation(self, index):
        return self.animations_rotation[index]

    def get_animation_rotation_frames_sizes(self, index):
        return self.animations_rotation_frames_sizes[index]

    def set_animation_scale(self, index, width=1.0, height=1.0):
        self.animations_scale[index] = [width, height]
        self.animations_scale_flag[index] = True

    def get_animation_scale(self, index):
        return self.animations_scale[index]

    def get_animation_scale_frames_sizes(self, index):
        return self.animations_scale_frames_sizes[index]

    def get_animations_len(self):
        return len(self.animations_images)

    def set_animation_frame_index(self, index):
        self.animation_frame_index = index

    def get_animation_frame_index(self):
        if self.animation_frame_index < self.animations_len[self.animation_index]:
            return self.animation_frame_index
        else:
            return self.animations_len[self.animation_index] - 1

    def set_animation_activate(self, index):
        self.animation_flag = True
        self.animation_index = index

    def set_animation_deactivate(self):
        self.animation_flag = False

    def get_animation_activate(self):
        return self.animation_flag

    def get_animation_index(self):
        return self.animation_index

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

    def get_intersections(self, list_objects):
        new_list = []
        for n in list_objects:
            if pygame.sprite.collide_mask(self, n):
                new_list.append(n)
        return new_list

    def _rotation_frames_update(self):
        if self.animations_rotation_flag[self.animation_index]:
            images = self.animations_images[self.animation_index]
            rotation = self.animations_rotation[self.animation_index]
            for index in range(self.animations_len[self.animation_index]):
                self.animations_rotation_frames[self.animation_index][index] = \
                    pygame.transform.rotate(images[index], rotation)
                width = self.animations_rotation_frames[self.animation_index][index].get_width()
                height = self.animations_rotation_frames[self.animation_index][index].get_height()
                self.animations_rotation_frames_sizes[self.animation_index][index] = [width, height]
            self.animations_rotation_flag[self.animation_index] = False
            self.animations_scale_flag[self.animation_index] = True
            return True
        return False

    def _scale_frames_update(self):
        if self.animations_scale_flag[self.animation_index]:
            images = self.animations_rotation_frames[self.animation_index]
            sizes = self.animations_rotation_frames_sizes[self.animation_index]
            scale = self.animations_scale[self.animation_index]
            for index in range(self.animations_len[self.animation_index]):
                width = int(sizes[index][0] * scale[0])
                height = int(sizes[index][1] * scale[1])
                self.animations_scale_frames[self.animation_index][index] = \
                    pygame.transform.scale(images[index], (width, height))
                self.animations_scale_frames_sizes[self.animation_index][index] = [width, height]
            self.animations_scale_flag[self.animation_index] = False
            self.animations_position_politic_flag[self.animation_index] = True
            self.animations_mask_flag[self.animation_index] = True
            return True
        return False

    def _position_politic_frames_update(self):
        if self.animations_position_politic_flag[self.animation_index]:
            sizes = self.animations_scale_frames_sizes[self.animation_index]
            positions_politic = self.animations_position_politic[self.animation_index]
            for index in range(self.animations_len[self.animation_index]):
                add_x = -sizes[index][0] * ((positions_politic[0] + 1) / 2)
                add_y = sizes[index][1] * ((positions_politic[1] + 1) / 2)
                self.animations_position_add[self.animation_index][index] = [add_x, add_y]
            self.animations_position_politic_flag[self.animation_index] = False
            return True
        return False

    def _mask_update(self):
        if self.animations_mask_flag[self.animation_index]:
            self.animations_mask[self.animation_index] = \
                [pygame.mask.from_surface(frame) for frame in self.animations_scale_frames[self.animation_index]]
            self.animations_mask_flag[self.animation_index] = False

    def _frame_update(self, index):
        if index is None:
            index = -1
        self.image = self.animations_scale_frames[self.animation_index][index]
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
                    self.set_animation_frame_index(0)
                    self.set_animation_activate(self.animation_index)
                else:
                    self.set_animation_frame_index(self.get_animation_len(self.animation_index) - 1)
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

    def update(self, number):
        frame_index = self._animation_frame_index_update(number)  # вычисляем текущий индекс анимации
        self._rotation_frames_update()  # поворачиваем изображение
        self._scale_frames_update()  # меняем масштаб frames
        self._position_politic_frames_update()  # устанавливаем значения сдвигов на основе politic position
        self._mask_update()  # обновляем маску
        self._frame_update(frame_index)  # обновляем frame
        self._animation_update(frame_index)  # активируем/переактивируем/деактивируем анимацию
        self._run_update(number)  # вычисляем положение объекта


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


class Points(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((1, 1))
        self.rect = pygame.Rect(x, y, 1, 1)
        self.mask = pygame.mask.from_surface(self.image)

    def set_x(self, x):
        self.rect.x = x

    def set_y(self, y):
        self.rect.y = y

    def set_positions(self, x, y):
        self.set_x(x)
        self.set_y(y)

    def get_x(self):
        return self.rect.x

    def get_y(self):
        return self.rect.y

    def get_positions(self):
        return self.get_x(), self.get_y()


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

    def set_positions(self, x, y):
        self.set_x(x)
        self.set_y(y)

    def get_x(self):
        return self.x

    def get_y(self):
        return self.y

    def get_positions(self):
        return self.x, self.y

    def get_width(self):
        self._create_object()
        return self.object.get_width()

    def get_height(self):
        self._create_object()
        return self.object.get_height()

    def _create_object(self):
        if not self.flag_obgect:
            self.object = self.font.render(self.text, self.smooth, self.color)
            self.flag_obgect = True

    def update(self):
        self._create_object()

    def draw(self, screen):
        screen.blit(self.object, (self.x, self.y))


class Button:
    def __init__(self):
        self.sprite = Sprite(0, 0, 1, 1)
        for _ in range(3):
            self.sprite.add_animation([None])
        self.index_passive_animation, self.index_select_animation, self.index_active_animation = 0, 1, 2
        self.passive_text, self.select_text, self.active_text = None, None, None
        self.index_now_animation = 0
        self.methods = [None, None, None]

    def set_passive_animation(self, *args, **kwargs):
        self.sprite.delete_animation(self.index_passive_animation)
        self.sprite.add_animation(*args, **kwargs)
        if self.index_select_animation > self.index_passive_animation:
            self.index_select_animation -= 1
        if self.index_active_animation > self.index_passive_animation:
            self.index_active_animation -= 1
        self.index_passive_animation = self.sprite.get_animations_len() - 1

    def set_select_animation(self, *args, **kwargs):
        self.sprite.delete_animation(self.index_select_animation)
        self.sprite.add_animation(*args, **kwargs)
        if self.index_passive_animation > self.index_select_animation:
            self.index_passive_animation -= 1
        if self.index_active_animation > self.index_select_animation:
            self.index_active_animation -= 1
        self.index_select_animation = self.sprite.get_animations_len() - 1

    def set_active_animation(self, *args, **kwargs):
        self.sprite.delete_animation(self.index_active_animation)
        self.sprite.add_animation(*args, **kwargs)
        if self.index_passive_animation > self.index_active_animation:
            self.index_passive_animation -= 1
        if self.index_select_animation > self.index_active_animation:
            self.index_select_animation -= 1
        self.index_active_animation = self.sprite.get_animations_len() - 1

    def set_positions_images(self, x, y):
        self.sprite.set_positions(x, y)

    def set_passive_text(self, *args, **kwargs):
        self.passive_text = Text(*args, **kwargs)

    def set_select_text(self, *args, **kwargs):
        self.select_text = Text(*args, **kwargs)

    def set_active_text(self, *args, **kwargs):
        self.active_text = Text(*args, **kwargs)

    def set_positions_texts(self, x, y):
        self.passive_text.set_positions(x, y)
        self.select_text.set_positions(x, y)
        self.active_text.set_positions(x, y)

    def set_passive(self):
        self.sprite.set_animation_frame_index(0)
        self.sprite.set_animation_activate(self.index_passive_animation)
        self.index_now_animation = 0

    def set_select(self):
        self.sprite.set_animation_frame_index(0)
        self.sprite.set_animation_activate(self.index_select_animation)
        self.index_now_animation = 1

    def set_active(self):
        self.sprite.set_animation_frame_index(0)
        self.sprite.set_animation_activate(self.index_active_animation)
        self.index_now_animation = 2

    def set_passive_method(self, method):
        self.methods[0] = method

    def set_select_method(self, method):
        self.methods[1] = method

    def set_active_method(self, method):
        self.methods[2] = method

    def _choice_image(self, mouse_point, key_down):
        answer = self.sprite.get_intersections([mouse_point])
        if mouse_point.get_x() >= 0 and mouse_point.get_y() >= 0 and len(answer) > 0:
            if key_down:
                if self.index_now_animation != 2:
                    self.set_active()
            else:
                if self.index_now_animation != 1:
                    self.set_select()
        else:
            if self.index_now_animation != 0:
                self.set_passive()

    def update(self, number, mouse_point, key_down):
        self._choice_image(mouse_point, key_down)
        self.sprite.update(number)
        if self.passive_text is not None:
            self.passive_text.update()
        if self.select_text is not None:
            self.select_text.update()
        if self.active_text is not None:
            self.active_text.update()

    def draw(self, screen):
        if self.index_now_animation == 0:
            if self.passive_text is not None:
                self.passive_text.draw(screen)
        elif self.index_now_animation == 1:
            if self.select_text is not None:
                self.select_text.draw(screen)
        else:
            if self.active_text is not None:
                self.active_text.draw(screen)
        if self.methods[self.index_now_animation] is not None:
            self.methods[self.index_now_animation]()


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
        self.buttons = []

    def add(self, *args):
        if len(args) > 0:
            type_args = type(args[0])
            if type_args == Text:
                self.texts.append(args[0])
            elif type_args == Button:
                self.buttons.append(args[0])
                self.add(args[0].sprite)
            else:
                super().add(*args)
        else:
            super().add(*args)

    def draw(self, *args, **kwargs):
        super().draw(*args, **kwargs)
        for n in self.texts:
            n.draw(args[0])
        for n in self.buttons:
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

        self.mouse_point = Points(0, 0)
        self.group.add(self.mouse_point)

        self.font = Font(None, 16)

        self.button = Button()
        self.group.add(self.button)
        self.button.set_select_animation(["data\\frames_2\\button_2_1.png"], 100)
        self.button.set_active_animation(["data\\frames_2\\button_3_1.png"], 100)
        self.button.set_passive_animation(["data\\frames_2\\button_1_1.png", "data\\frames_2\\button_1_2.png"],
                                          0.001, activate=True)
        self.button.set_passive_text("Text1", self.font, color=(255, 255, 0))
        self.button.set_select_text("Text2", self.font, color=(0, 255, 255))
        self.button.set_active_text("Text3", self.font, color=(255, 0, 255))
        self.button.set_positions_images(250, -200)
        self.button.set_positions_texts(250, -200)

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

            self.mouse_point.set_positions(self.mouse_x, self.mouse_y)
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
        self.button.update(self.number_frames_time, self.mouse_point, True if self.mouse_left else False)

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
