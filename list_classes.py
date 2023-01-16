import importlib

import dir_classes.grass
import dir_classes.wall
import dir_classes.stone_1
import dir_classes.stone_2
import dir_classes.human

importlib.reload(dir_classes.grass)
importlib.reload(dir_classes.wall)
importlib.reload(dir_classes.stone_1)
importlib.reload(dir_classes.stone_2)
importlib.reload(dir_classes.human)


def create_object_class(index):
    if index == 1:
        return dir_classes.grass.Object()
    elif index == 2:
        return dir_classes.wall.Object()
    elif index == 3:
        return dir_classes.stone_1.Object()
    elif index == 4:
        return dir_classes.stone_2.Object()
    elif index == 5:
        return dir_classes.human.Object()
    else:
        return None
