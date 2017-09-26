import queue
import telebot

import config as cfg
from tele_bot.bot_def import *
import version as ver
import base_daemon.model

__all__ = ['start_listen']


bot = telebot.AsyncTeleBot(cfg.token)
# bot_pid = bot.get_me()

send_l = queue.Queue()
receive_l = []

stop_flag = [True]

user_model = None


def set_model(model):
    global user_model
    user_model = model


@bot.message_handler(commands=[C_START, C_HELP])
def handle_start_help(message):
    markup = telebot.types.ReplyKeyboardMarkup()
    if message.chat.id == ADMIN_ID:
        show_admin_m()
    elif user_model.is_viewer(message.chat.id):
        show_viewer_m()
    else:
        markup.row(N_R_REG)

    bot.send_message(message.chat.id, "You move:", reply_markup=markup)


@bot.message_handler(content_types=["text"])
def handle_text(message):
    t_comm = message.text
    t_id = message.chat.id
    t_name = message.chat.first_name
    print("text: {:s}".format(t_comm))
    print("id: {:s}".format(str(t_id)))

    if message.chat.id == ADMIN_ID:
        if t_comm == A_D_ADD:
            pass
        elif t_comm == A_D_KICK:
            pass
        elif t_comm == A_D_WHO_REG:
            show_who_want_reg()
        elif t_comm == A_D_WHO_UREG:
            show_who_want_unreg()
        elif t_comm == A_D_WHO_ARE:
            show_who_viewer()
        elif t_comm == A_D_CONRTOL:
            show_control_m(ADMIN_ID)
        elif t_comm == BACK_M:
            show_admin_m()
    elif user_model.is_viewer(t_id):
        if t_comm == R_UNREG:
            unregister_request(t_id, t_name)
        elif t_comm == A_D_CONRTOL:
            show_control_m(t_id)
        elif t_comm == BACK_M:
            show_viewer_m(t_id)
    else:
        if t_comm == N_R_REG:
            register_request(t_id, t_name)


def show_viewer_m():
    markup = telebot.types.ReplyKeyboardMarkup()
    markup.row(R_UNREG, A_D_CONRTOL)
    bot.send_message(ADMIN_ID, "You move:", reply_markup=markup)


def show_admin_m():
    markup = telebot.types.ReplyKeyboardMarkup()
    markup.row(A_D_ADD, A_D_KICK)
    markup.row(A_D_WHO_REG, A_D_WHO_UREG, A_D_WHO_ARE)
    markup.row(A_D_CONRTOL)
    bot.send_message(ADMIN_ID, "You move:", reply_markup=markup)


def show_control_m(chat_id):
    markup = telebot.types.ReplyKeyboardMarkup()
    markup.row(R_LAST_F)
    markup.row(BACK_M)
    bot.send_message(chat_id, "You move:", reply_markup=markup)


def unregister_request(id, name):
    global user_model
    user_model.add_unreg_req(id, name)
    alert_want_unreg()


def alert_want_unreg():
    global user_model
    sz = len(user_model.unreg_req)
    print("unreg: {:s}".format(str(sz)))
    if sz > 0:
        bot.send_message(ADMIN_ID, "Want to unreg {:s}".format(str(sz)))


def register_request(id, name):
    global user_model
    user_model.add_reg_req(id, name)
    alert_want_reg()


def alert_want_reg():
    global user_model
    sz = len(user_model.reg_req)
    print("reg: {:s}".format(str(sz)))
    if sz > 0:
        bot.send_message(ADMIN_ID, "Want to reg {:s}".format(str(sz)))


def show_who_want_reg():
    global user_model
    w_reg_s = "\n".join(["{:s} : {:s}".format(str(k), name) for (k, name) in user_model.reg_req.items()])
    bot.send_message(ADMIN_ID, "They want to reg: \n {:s}".format(w_reg_s))


def show_who_want_unreg():
    global user_model
    w_ureg_s = "\n".join(["{:s} : {:s}".format(str(k), name) for (k, name) in user_model.unreg_req.items()])
    bot.send_message(ADMIN_ID, "They want to unreg: \n {:s}".format(w_ureg_s))


def show_who_viewer():
    global user_model
    w_viewer_s = "\n".join(["{:s} : {:s}".format(str(k), name) for (k, name) in user_model.viewers.items()])
    bot.send_message(ADMIN_ID, "They want to unreg: \n {:s}".format(w_viewer_s))


def say_who_want_reg():
    msg = "They want to reg: \n{:s}".format("\n".join(["{:s} : {:s}".format(str(key), msg.chat.first_name) for (key, msg) in reg_dict.items()]))

    bot.send_message(ADMIN_ID, msg)


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




def start_listen():
    offset = None
    # bot.polling(none_stop=False)

    while stop_flag[0]:
        upds = bot.get_updates(offset, timeout=3)

        # process msgs
        if len(upds) > 0:
            offset = upds[-1].update_id + 1
            bot.process_new_updates(upds)

    bot.send_message(ADMIN_ID, "Service was stopped")