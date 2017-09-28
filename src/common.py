import os
import sys

# PATHES
LOG_P           = "../LOG/"
OUT_P           = "../OUT/"
LAST_D_P        = "../OUT/L_F/"
LAST_F          = "last_frame.jpg" # photo_2017-09-25_14-21-59.jpg
LAST_F_T        = "photo_2017-09-25_14-21-59.jpg"

FULL_P          = ""

# VARS
MULTITHREAD     = False
QUIET           = False

# DB
DB_PATH         = "../misc/main"
INI_PATH        = "../misc/main.ini"

# alert types
T_CAM_MOVE               = 0
T_CAM_SW                 = 1

# alert msgs

CAM_STOPPED             = "Камера {:s} выключена"
CAM_STARTED             = "Камера {:s} включена"
MOVE_ALERT              = "Камера: {:s}_{:s}\nДвижение в {:s}!"


# common functions
def reset_app():
    os.execl(sys.executable, sys.executable, *sys.argv)


def make_dir(dir):
    if not os.path.exists(dir):
        os.mkdir(dir)


class Alert:
    def __init__(self, t, m, im=None):
        self.type = t
        self.msg = m
        self.img = im