import telebot.types

# main defs
ADMIN_ID                = '74810100' # 74810100
TOKEN                   = '364842219:AAEl03t9yKk0qxz0afTWDLwVaPRIzWpYRZc'
UPD_TMT                 = 1

# messages
BOT_START               = "Бусинко-наблюдатель({:s}) запущен"
BOT_STOP                = "Бусинко-наблюдатель остановлен"
TO_RULE                 = "Командуй"
NOBODY                  = "Empty"

# commands
C_START                 = 'start'
C_HELP                  = 'help'

C_V_UREG                = 'Удалиться'

C_U_REG                 = 'Зарегистрироваться'

C_CAMS                  = 'Камеры'
C_BACK                  = 'Назад'
C_UPD                   = 'Обновить меню'
C_MENU                   = 'Меню'

C_A_RES                 = 'Restart'
C_A_STOP                = 'Stop'
C_A_WHO_R               = 'Reg list'
C_A_WHO_UR              = 'Unreg list'
C_A_WHO_ARE             = 'Viewers'

C_R_ACC                 = 'Accept'
C_R_DECL                = 'Decl'
C_R_NEXT                = 'Next'
C_R_KICK                = 'Kick'

C_C_ON                  = 'on'
C_C_OFF                 = 'off'
C_C_LAST                = 'last'

# keyboards
GET_M                   = [[C_MENU]]
GET_MARK = telebot.types.ReplyKeyboardMarkup()
for row in GET_M:
    GET_MARK.row(*row)


ADMIN_M                 = [[C_A_STOP, C_A_RES],
                           [C_A_WHO_R, C_A_WHO_UR, C_A_WHO_ARE],
                           [C_CAMS],
                           [C_UPD]]
ADMIN_MARK = telebot.types.ReplyKeyboardMarkup()
for row in ADMIN_M:
    ADMIN_MARK.row(*row)

REG_M                   = [[C_R_ACC, C_R_KICK],
                           [C_R_NEXT],
                           [C_MENU]]
REG_MARK = telebot.types.ReplyKeyboardMarkup()
for row in REG_M:
    REG_MARK.row(*row)

KICK_M = [[C_R_KICK],
          [C_R_NEXT],
          [C_MENU]]
KICK_MARK = telebot.types.ReplyKeyboardMarkup()
for row in KICK_M:
    KICK_MARK.row(*row)


VIEWERS_M               = [[C_V_UREG],
                           [C_CAMS],
                           [C_UPD]]
VIEWERS_MARK = telebot.types.ReplyKeyboardMarkup()
for row in VIEWERS_M:
    VIEWERS_MARK.row(*row)

UNDEF_M                 = [[C_U_REG],
                           [C_UPD]]
UNDEF_MARK = telebot.types.ReplyKeyboardMarkup()
for row in VIEWERS_M:
    UNDEF_MARK.row(*row)


CAM_M                   = []
CAM_MARKUP = telebot.types.ReplyKeyboardMarkup()

CAM_CTRL_M              = [[C_C_ON, C_C_OFF],
                           [C_C_LAST],
                           [C_CAMS],
                           [C_MENU]]
CAM_CTRL_MARK = telebot.types.ReplyKeyboardMarkup()
for row in CAM_CTRL_M:
    CAM_CTRL_MARK.row(*row)



