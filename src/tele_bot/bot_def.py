import telebot.types

# main defs
ADMIN_ID                = '74810100' # 74810100
TOKEN                   = '364842219:AAEl03t9yKk0qxz0afTWDLwVaPRIzWpYRZc'
UPD_TMT                 = 1

# messages
BOT_START               = "Бусинко-наблюдатель({:s}) запущен"
BOT_STOP                = "Бусинко-наблюдатель остановлен"
TO_RULE                 = "Select"
NOBODY                  = "Empty"

# commands
C_START                 = 'start'
C_HELP                  = 'help'

C_V_UREG                = 'DISCONNECT'

C_U_REG                 = 'CONNECT'

C_CAMS                  = 'CAMS'
C_BACK                  = 'BACK'
C_UPD                   = 'REFRESH'
C_MENU                  = 'MENU'

C_A_RES                 = 'restart'
C_A_STOP                = 'stop'
C_A_WHO_R               = 'reg l.'
C_A_WHO_UR              = 'unreg l.'
C_A_WHO_ARE             = 'viewers l.'
C_A_SYS_INFO            = "sys. info"

C_R_ACC                 = 'accept.'
C_R_DECL                = 'decl.'
C_R_NEXT                = 'next'
C_R_KICK                = 'kick'

C_C_ON                  = 'ON cam'
C_C_OFF                 = 'OFF cam'
C_MD_ON                 = 'ON detect'
C_MD_OFF                = 'OFF detect'
C_C_LAST                = 'LAST'
C_C_NOW_ALL             = 'PHOTOS'
C_C_NOW                 = 'PHOTO'

NO_DEL_L                = [C_C_NOW, C_R_ACC, C_R_KICK, C_R_NEXT, C_U_REG, C_V_UREG, C_A_WHO_ARE, C_A_WHO_R, C_A_WHO_UR]

# keyboards
GET_M_L                   = [[C_MENU]]
GET_KB = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
for row in GET_M_L:
    GET_KB.row(*row)


ADMIN_M_L                 = [[C_A_STOP, C_A_RES],
                             [C_A_WHO_R, C_A_WHO_UR, C_A_WHO_ARE],
                             [C_CAMS, C_C_NOW_ALL, C_A_SYS_INFO],
                             [C_UPD]]
ADMIN_KB = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
for row in ADMIN_M_L:
    ADMIN_KB.row(*row)

REG_M_L                   = [[C_R_ACC, C_R_KICK],
                             [C_R_NEXT],
                             [C_MENU]]
REG_KB = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
for row in REG_M_L:
    REG_KB.row(*row)

KICK_M_L = [[C_R_KICK],
            [C_R_NEXT],
            [C_MENU]]
KICK_KB = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
for row in KICK_M_L:
    KICK_KB.row(*row)


VIEWERS_M_L               = [[C_V_UREG],
                             [C_CAMS, C_C_NOW_ALL],
                             [C_UPD]]
VIEWERS_KB = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
for row in VIEWERS_M_L:
    VIEWERS_KB.row(*row)

UNDEF_M_L                 = [[C_U_REG],
                             [C_UPD]]
UNDEF_KB = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
for row in UNDEF_M_L:
    UNDEF_KB.row(*row)


CAM_M_L                   = []
CAM_KB = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)

CAM_CTRL_M_L              = [[C_C_NOW],
                             [C_CAMS],
                             [C_MENU]]
# CAM_CTRL_ON_KB = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
# CAM_CTRL_ON_KB.row(*[C_C_ON])
# CAM_CTRL_OFF_KB = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
# CAM_CTRL_OFF_KB.row(*[C_C_OFF])
#
# for row in CAM_CTRL_M_L:
#     CAM_CTRL_ON_KB.row(*row)
#     CAM_CTRL_OFF_KB.row(*row)



