import telebot.types

# main defs
ADMIN_ID                = '74810100' # 74810100
TOKEN                   = '364842219:AAEl03t9yKk0qxz0afTWDLwVaPRIzWpYRZc'
UPD_TMT                 = 1

# commands
C_START                 = 'start'
C_STOP                  = 'stop'
C_HELP                  = 'help'

C_V_UREG                = 'unreg'

C_U_REG                 = 'reg'

C_CTRL                  = 'control'
C_BACK                  = 'back'
C_LAST_F                = 'last_f'
C_UPD                   = 'upd'

C_A_RES                 = 'restart'
C_A_STOP                = 'stop'
C_A_WHO_R               = 'who_reg'
C_A_WHO_UR              = 'who_ureg'
C_A_WHO_ARE             = 'who_are'

C_R_ADD                 = 'add'
C_R_NEXT                = 'next'
C_R_KICK                = 'kick'

# keyboards
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



# ---------------------------------------------


HEAD_MSG            = ("PyTeleCamBot v{:s}\n"
                       "To control me use next commands:\n"
                       "/start or /help - получить еще раз это сообщение\n{:s}")

REG_MSG             = ("/reg - подписаться к рассылке алертов\n"
                       "/unreg - отписаться от рассылки алертов")

WORK_MSG            = ("/last_f - получить последний снятый кадр\n"
                       "...")


REG_A = 'REG'
UNREG_A = 'UNREG'
MOVE_A = 'MOVE'





A_D_ADD         = 'ADD'
A_D_KICK        = 'KICK'
A_D_WHO_REG     = 'WHO_W'
A_D_WHO_UREG    = 'WHO_U'
A_D_WHO_ARE     = 'WHO_A'
A_D_CONRTOL     = 'CONTROL'

# ADMIN_M             = [A_D_ADD, A_D_KICK, A_D_WHO_REG, A_D_WHO_ARE]


NEXT_M      = 'NEXT'
UPD_M       = 'UPD_M'

N_R_REG     = 'REGISTER'

BACK_M      = 'BACK'


R_UNREG     = 'UNREGISTER'
R_LAST_F    = 'LAST_F'