from sprite import Sprite, Run


class Object(Sprite):
    def __init__(self):
        super().__init__(0, 0, 1, 1)
        self.types = ["entity", "human"]
        self.animations = []
        self.index_animation = 0

    def init(self, x, y, animations):
        self.set_positions(x, y)
        self.animations = animations
        self.add_positions(-100, -100)

    def update(self, number, keyboard_keys, mouse_point, mouse_left,
               mouse_right, mouse_middle, mouse_up, mouse_down, ):
        if 26 in keyboard_keys and 7 in keyboard_keys:
            self.index_animation = 1
        elif 7 in keyboard_keys and 22 in keyboard_keys:
            self.index_animation = 3
        elif 4 in keyboard_keys and 22 in keyboard_keys:
            self.index_animation = 5
        elif 4 in keyboard_keys and 26 in keyboard_keys:
            self.index_animation = 7
        elif 26 in keyboard_keys:
            self.index_animation = 0
        elif 7 in keyboard_keys:
            self.index_animation = 2
        elif 22 in keyboard_keys:
            self.index_animation = 4
        elif 4 in keyboard_keys:
            self.index_animation = 6
        frame_index = int(self.animations[self.index_animation].get_frame_index())
        self.set_image(self.animations[self.index_animation].get_scale_frames()[frame_index])
        self.set_mask(self.animations[self.index_animation].get_mask()[frame_index])