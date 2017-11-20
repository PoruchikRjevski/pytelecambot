import os
import sys

SOLUTION                    = "pytelecambot"

# COMMON
LOG_TIMESTAMP               = "%Y-%m-%d %H:%M"
BOT_SECTION                 = "BOT"
TEST_TOKEN_OPTION           = "test_token"
REAL_TOKEN_OPTION           = "real_token"

# LOGGER
LOG_TIME                    = '%(asctime)s'
LOG_LEVEL                   = '%(levelname)-8s'
LOG_THREAD                  = '%(threadName)-15s'
LOG_FUNC                    = '%(funcName)-30s'
LOG_LINE                    = "%(lineno)-4d"
LOG_CALL                    = '%(module)s:%(funcName)s():%(lineno)d'
LOG_MSG                     = '%(message)s'
LOG_NAME                    = '%(name)-30s'

# PATHES
CONFIG_DIR_PATH             = "../config/"
CAMERAS_FILE                = "cameras.ini"
CONFIG_FILE                 = "config.ini"
DB_FILE                     = "main.ini"
LOG_DIR_PATH                = "../log/"
OUT_DIR_PATH                = "../out/"


# ALERTS
T_CAM_MOVE_MP4              = 0
T_CAM_MOVE_PHOTO            = 1
T_CAM_SW                    = 2
T_CAM_NOW_PHOTO             = 3
T_SYS_NOW_INFO              = 4
T_SYS_ALERT                 = 5

TO_ALL                      = -1

CAM_STOPPED                 = "Камера {:s} выключена"
CAM_STARTED                 = "Камера {:s} включена"
CAM_MD_STARTED              = "{:s} Детектирование включено"
CAM_MD_STOPPED              = "{:s} Детектирование выключено"
MOVE_ALERT                  = "Камера: {:s}_{:s}\nДвижение в {:s}!"
NOW_ALERT                   = "Камера: {:s}_{:s}\nФото в {:s}!"


# COMMON FUNCS
def reset_app():
    os.execl(sys.executable, sys.executable, *sys.argv)


def make_dir(dir):
    if not os.path.exists(dir):
        os.mkdir(dir)


def rem_dir(dir):
    if not os.path.exists(dir):
        os.rmdir(dir)


class Alert:
    def __init__(self, t, m, im=None, cam=None, who=TO_ALL):
        self.type = t
        self.msg = m
        self.cam = cam
        self.img = im
        self.who = who









LOG_P           = "../../LOG/"
OUT_P           = "../../OUT/"
LAST_D_P        = "../../OUT/L_F/"
LAST_F          = "last_frame.jpg" # photo_2017-09-25_14-21-59.jpg
LAST_F_T        = "photo_2017-09-25_14-21-59.jpg"


# DB
DB_PATH         = "../misc/main"
INI_PATH        = "../misc/main.ini"

# cameras config path
CAMS_F_PATH        = "../misc/cameras.ini"

TIMESTAMP_FRAME_STR         = '%d %B %y %H:%M:%S'
TIMESTAMP_PATH_STR          = '%d%m%y_%H%M%S'

# alert types

# alert msgs




