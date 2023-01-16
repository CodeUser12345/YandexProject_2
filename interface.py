import pygame
from sprite import Sprite, Animation


class Point(Sprite):
    # создает спрайт точку 1x1, можно задать координаты размещения
    def __init__(self, x, y):
        super().__init__(x, y, 1, 1)
        self.set_image(pygame.Surface((1, 1)))
        self.set_mask(pygame.mask.from_surface(self.image))


class Font:
    # создает объект шрифт, возможно создать текст с параметрами шрифта
    def __init__(self, *args, **kwargs):
        self.font = pygame.font.SysFont(*args, **kwargs)

    def render(self, *args, **kwargs):
        return self.font.render(*args, **kwargs)


class Text:
    # создает текст
    def __init__(self, text, font, x=0, y=0, smooth=True, color=(0, 0, 0)):
        self.text = text
        self.font = font
        self.smooth = smooth
        self.color = color
        self.x, self.y = x, y
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
        self.y = y

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


class Button(Sprite):
    # имеет 3 состояния, для каждой можно задать анимацию, установить тексты с разными параметрами
    def __init__(self, x, y):
        super().__init__(x, y, 1, 1)
        self.animations = [Animation([None]), Animation([None]), Animation([None])]
        font = Font(None, 16)
        self.texts = [Text("", font), Text("", font), Text("", font)]
        self.methods = [None, None, None]
        self.index_now = 0

    def set_passive_animation(self, animation):
        self.animations[0] = animation

    def set_select_animation(self, animation):
        self.animations[1] = animation

    def set_active_animation(self, animation):
        self.animations[2] = animation

    def set_positions_images(self, x, y):
        self.set_positions(x, y)

    def set_passive_text(self, text):
        self.texts[0] = text

    def set_select_text(self, text):
        self.texts[1] = text

    def set_active_text(self, text):
        self.texts[2] = text

    def set_positions_passive_text(self, x, y):
        self.texts[0].set_positions(x, y)

    def set_positions_select_text(self, x, y):
        self.texts[1].set_positions(x, y)

    def set_positions_active_text(self, x, y):
        self.texts[2].set_positions(x, y)

    def set_positions_texts(self, x, y):
        self.set_positions_passive_text(x, y)
        self.set_positions_select_text(x, y)
        self.set_positions_active_text(x, y)

    def set_passive(self):
        self.animations[0].set_frame_index(0)
        self.animations[0].set_activate()
        self.index_now = 0

    def set_select(self):
        self.animations[1].set_frame_index(0)
        self.animations[1].set_activate()
        self.index_now = 1

    def set_active(self):
        self.animations[2].set_frame_index(0)
        self.animations[2].set_activate()
        self.index_now = 2

    def set_passive_method(self, method):
        self.methods[0] = method

    def set_select_method(self, method):
        self.methods[1] = method

    def set_active_method(self, method):
        self.methods[2] = method

    def _choice_image(self, mouse_point, key_down):
        answer = self.get_intersections([mouse_point])
        x, y = mouse_point.get_positions()
        if len(answer) > 0 and x >= 0 and y >= 0:
            if key_down:
                if self.index_now != 2:
                    self.set_active()
            else:
                if self.index_now != 1:
                    self.set_select()
        else:
            if self.index_now != 0:
                self.set_passive()

    def update(self, number, mouse_point, key_down):
        animation = self.animations[self.index_now]
        animation.update(number)
        frame_index = int(animation.get_frame_index())
        self.set_image(animation.get_scale_frames()[frame_index])
        self.set_mask(animation.get_mask()[frame_index])
        self._choice_image(mouse_point, key_down)
        super().update()
        self.texts[self.index_now].update()

    def draw(self, screen):
        self.texts[self.index_now].draw(screen)
        if self.methods[self.index_now] is not None:
            self.methods[self.index_now]()