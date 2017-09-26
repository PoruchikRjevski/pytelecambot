import telebot
import queue

import config as cfg
from tele_bot.bot_def import *
import version as ver
import base_daemon.model

__all__ = ['start_listen']


bot = telebot.AsyncTeleBot(cfg.token)
# bot_pid = bot.get_me()

send_l = queue.Queue()
receive_l = []

reg_dict = {} # {id : message}

stop_flag = [True]

user_model = None


def set_model(model):
    global user_model
    user_model = model


@bot.message_handler(commands=['start', 'help'])
def handle_start_help(message):
    markup = telebot.types.ReplyKeyboardMarkup()
    if message.chat.id == ADMIN_ID:
        markup.row(A_D_REG, A_D_UREG)
        markup.row(A_D_WHO_REG, A_D_WHO_ARE)
        markup.row(A_D_CONRTOL)
    elif user_model.is_viewer(message.chat.id):
        markup.row(A_D_CONRTOL)
    else:
        markup.row(N_R_REG)

    bot.send_message(message.chat.id, "You move:", reply_markup=markup)




@bot.message_handler(commands=['who_w_reg'])
def handle_whoo_reg(message):
    msg = "They want to reg: \n{:s}".format("\n".join(["{:s} : {:s}".format(str(key), msg.chat.first_name) for (key, msg) in reg_dict.items()]))

    bot.send_message(ADMIN_ID, msg)


@bot.message_handler(commands=['do_reg'])
def handle_do_reg(message):

    reg_q[message.chat.id] = message
    send_l.put((REG_A, message.chat.id))


@bot.message_handler(commands=['reg'])
def handle_reg(message):
    reg_dict[message.chat.id] = message
    check_regs()


@bot.message_handler(commands=['unreg'])
def handle_reg(message):


    check_regs()
    # delete from base


@bot.message_handler(commands=['stop'])
def handle_stop(message):
    if message.chat.id == ADMIN_ID:
        stop_flag[0] = False


def add_move_alert(msg, path):
    send_q.put(path, msg)


def send_msgs():
    while send_l:
        (type, id) = send_l.get()

        if type == REG_A:
            if id in reg_q.keys():
                msg = reg_q[id]
                bot.send_message(ADMIN_ID, "Ask reg {:s}:{:s}".format(msg.chat.first_name,
                                                                         str(msg.chat.id)))


def check_regs():
    sz = len(reg_dict)
    if sz > 0:
        bot.send_message(ADMIN_ID, "Want to reg {:s}".format(str(sz)))



def start_listen():
    offset = None
    # bot.polling(none_stop=False)

    while stop_flag[0]:
        upds = bot.get_updates(offset, timeout=1)

        # process msgs
        if len(upds) > 0:
            offset = upds[-1].update_id + 1
            bot.process_new_updates(upds)

    bot.send_message(ADMIN_ID, "Service was stopped")