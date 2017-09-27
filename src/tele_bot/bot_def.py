import telebot.types

# main defs
ADMIN_ID                = '74810100' # 74810100
TOKEN                   = '364842219:AAEl03t9yKk0qxz0afTWDLwVaPRIzWpYRZc'
UPD_TMT                 = 1

# messages
BOT_START               = "Бусинко-наблюдатель({:s}) запущен"
BOT_STOP                = "Бусинко-наблюдатель остановлен"
TO_RULE                 = "Командуй"

# commands
C_START                 = 'start'
C_HELP                  = 'help'

C_V_UREG                = 'Удалиться'

C_U_REG                 = 'Зарегистрироваться'

C_CTRL                  = 'Управление'
C_BACK                  = 'Назад'
C_LAST_F                = 'Последний кадр'
C_UPD                   = 'Обновить'
C_GET                   = 'Меню'

C_A_RES                 = 'restart'
C_A_STOP                = 'stop'
C_A_WHO_R               = 'who_reg'
C_A_WHO_UR              = 'who_ureg'
C_A_WHO_ARE             = 'who_are'

C_R_ADD                 = 'add'
C_R_NEXT                = 'next'
C_R_KICK                = 'kick'

# keyboards
GET_M                   = [[C_GET]]
GET_MARK = telebot.types.ReplyKeyboardMarkup()
for row in GET_M:
    GET_MARK.row(*row)


ADMIN_M                 = [[C_A_STOP, C_A_RES],
                           [C_A_WHO_R, C_A_WHO_UR, C_A_WHO_ARE],
                           [C_CTRL],
                           [C_UPD]]
ADMIN_MARK = telebot.types.ReplyKeyboardMarkup()
for row in ADMIN_M:
    ADMIN_MARK.row(*row)

REG_M                   = [[C_R_ADD, C_R_KICK],
                           [C_R_NEXT],
                           [C_BACK]]
REG_MARK = telebot.types.ReplyKeyboardMarkup()
for row in REG_M:
    REG_MARK.row(*row)

CTRL_M                  = [[C_LAST_F],
                           [C_BACK]]
CTRL_MARK = telebot.types.ReplyKeyboardMarkup()
for row in CTRL_M:
    CTRL_MARK.row(*row)

VIEWERS_M               = [[C_V_UREG],
                           [C_CTRL],
                           [C_UPD]]
VIEWERS_MARK = telebot.types.ReplyKeyboardMarkup()
for row in VIEWERS_M:
    VIEWERS_MARK.row(*row)

UNDEF_M                 = [[C_U_REG],
                           [C_UPD]]
UNDEF_MARK = telebot.types.ReplyKeyboardMarkup()
for row in VIEWERS_M:
    UNDEF_MARK.row(*row)

