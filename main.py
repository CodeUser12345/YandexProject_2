import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import pygame
import time
import sys
from sprite import Sprite, Animation
from interface import Text, Button, Point
from load_classes import ListClasses


class Camera:
    # перемещает "камеру", меняет размер и позицию объектов/сущностей/поля создавая эффект отдаления/приближения
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

    def add(self, object):
        type_object = type(object)
        if type_object == Sprite:
            self.sprites.append(object)
        elif type_object == Map:
            for n in object.passive_objects:
                self.sprites.append(n)
            for n in object.active_objects_ai:
                self.sprites.append(n)
        else:
            print(f"Тип {type_object} не определен")
            sys.exit()
        self.index_list = range(len(self.sprites))

    def delete_sprite(self, index):
        self.sprites.pop(index)
        self.index_list = range(len(self.sprites))

    def set_width(self, width):
        self.width = width
        self.center_x = self.x + self.width // 2

    def set_height(self, height):
        self.height = height
        self.center_y = self.y + self.height // 2

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

    def _scale_update(self, scale):  # пока не работает :)
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
    # группа нескольких объектов/сущностей и др., рисует добавленные объекты на экран
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
                super().add(args[0])
            elif type_args == Map:
                for n in args[0].passive_objects:
                    self.add(n)
                for n in args[0].active_objects_player:
                    self.add(n)
                for n in args[0].active_objects_ai:
                    self.add(n)
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


class Map:
    # добавить описание
    def __init__(self):
        self.passive_objects = []
        self.active_objects_ai = []
        self.active_objects_player = []
        self.animations_objects = []

    def load(self, path, list_classes, width_window, height_window):
        indexes_animations = []
        paths_animations = []
        indexes_objects = []
        paths_objects = []
        positions_objects = []
        flags_objects = []
        animations_objects = []
        with open(path, "r", encoding="utf-8") as file:
            text = file.read().split("\n")
            len_text = len(text)

            index = 1
            while index < len_text:
                string = text[index].replace(" ", "").split(",")
                index += 1
                if string == ["paths_objects:"]:
                    break
                elif string == [""]:
                    continue
                indexes_animations.append(int(string[0]))
                paths_animations.append(string[1][1:-1].replace("\\\\", "\\"))

            while index < len_text:
                string = text[index].replace(" ", "").split(",")
                index += 1
                if string == ["positions:"]:
                    break
                elif string == [""]:
                    continue
                indexes_objects.append(string[0])
                paths_objects.append(string[1][1:-1].replace("\\\\", "\\"))
                list_classes.add_class(paths_objects[-1], indexes_objects[-1])

            while index < len_text:
                string = text[index]
                list_1 = ["width", "height"]
                list_2 = [width_window, height_window]
                for n in range(len(list_1)):
                    if list_1[n] in string:
                        index_element = string.index(list_1[n])
                        string = string[:index_element] + str(list_2[n]) + string[index_element + len(list_1[n]):]
                string = string.replace(" ", "").split(",")
                index += 1
                if string == [""] or string == ["paths_animations:"]:
                    continue
                positions_objects.append([int(string[0]), int(eval(string[1])), int(eval(string[2]))])
                animations_objects.append([int(n) for n in ", ".join(string[3:-1])[1:-1].replace(" ", "").split(",")])
                flags_objects.append(string[-1] if string[-1] == "Player" or string[-1] == "Ai" else "Passive")

        for n in range(len(paths_animations)):
            self.animations_objects.append(Animation([None]))
            self.animations_objects[-1].load_animation(paths_animations[n])

        for n in range(len(positions_objects)):
            animations = []
            for s in animations_objects[n]:
                animations.append(self.animations_objects[indexes_animations.index(s)])
            object_1 = list_classes.get_object_class(positions_objects[n][0])
            object_1.init(positions_objects[n][1], positions_objects[n][2], animations)
            if flags_objects[n] == "Player":
                self.active_objects_player.append(object_1)
            elif flags_objects[n] == "Ai":
                self.active_objects_ai.append(object_1)
            else:
                self.passive_objects.append(object_1)

    def update(self, number, keyboard_keys, mouse_point, mouse_left,
               mouse_right, mouse_middle, mouse_up, mouse_down):
        for n in self.animations_objects:
            n.update(number)
        for n in self.active_objects_player:
            n.update(number, keyboard_keys, mouse_point, mouse_left,
                     mouse_right, mouse_middle, mouse_up, mouse_down)
        for n in self.active_objects_ai:
            n.update(number)


class MainWindow:
    def __init__(self):
        pygame.init()
        self.window = pygame.display.Info()
        self.width_window, self.height_window = self.window.current_w, self.window.current_h
        self.screen = pygame.display.set_mode((self.width_window // 1.5, self.height_window // 1.5))

        self.last_time, self.step_time, self.number_frames_time = time.time(), 0.001, 0

        self.group = Group()
        self.camera = Camera(self.width_window, self.height_window)
        self.list_classes = ListClasses()
        self.mouse_point = Point(0, 0)
        self.group.add(self.mouse_point)

        self.map = Map()
        self.map.load("data_user\\maps\\map_1.txt", self.list_classes, self.width_window, self.height_window)
        self.group.add(self.map)
        self.camera.add(self.map)

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

            self.mouse_point.set_positions(self.mouse_x, self.mouse_y)  # устанавливаем координаты мыши для точки
            self.camera.update(x, y, 0)  # обновляем камеру
            self.map.update(self.number_frames_time, self.keyboard_keys, self.mouse_point, self.mouse_left,
                            self.mouse_right, self.mouse_middle, self.mouse_up, self.mouse_down)  # обновляем карту

            self._draw_all()  # рисуем все
        self._exit()

    def _exit(self):
        pygame.quit()

    def _draw_all(self):
        self.screen.fill((0, 0, 0))
        self.group.draw(self.screen)
        pygame.display.flip()

    def _edit_data(self):
        x = 1 * self.number_frames_time if 7 in self.keyboard_keys else \
            (-1 * self.number_frames_time if 4 in self.keyboard_keys else 0)
        y = -1 * self.number_frames_time if 26 in self.keyboard_keys else \
            (1 * self.number_frames_time if 22 in self.keyboard_keys else 0)
        if x != 0 and y != 0:
            x *= 0.707
            y *= 0.707
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
