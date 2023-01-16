from sprite import Sprite


class Object(Sprite):
    def __init__(self):
        super().__init__(0, 0, 1, 1)
        self.types = ["field", "stone_2"]

    def init(self, x, y, animations):
        self.set_positions(x, y)
        self.set_image(animations[0].get_scale_frames()[0])
