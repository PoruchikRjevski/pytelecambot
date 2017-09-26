#!/usr/bin/sudo python3

import os

import config as cfg
import version as ver
import tele_bot.bot as c_b
from logger import *
from git_man import *
from base_daemon import *
# from sql_daemon import *

# bot = telebot.TeleBot(c_v.token)

#
# @bot.message_handler(commands=['start', 'help'])
# def handle_start_help(message):
#     show_help(message.chat.id)
#
#
# @bot.message_handler(content_types=["text"])
# def echo(message):
#     print("chat id: ", message.chat.id)
#     if message.text == c_v.CONTROL:
#         show_keyboard(message.chat.id)
#     elif message.text == c_v.TAKE_PHOTO:
#         bot.send_message(message.chat.id, "It's photo")
#     elif message.text == c_v.TAKE_VIDEO:
#         bot.send_message(message.chat.id, "It's video")
#     elif message.text == c_v.TAKE_AUDIO:
#         bot.send_message(message.chat.id, "It's audio")
#     else:
#         bot.send_message(message.chat.id, message.text)
#
#
# def show_help(chat_id):
#     bot.send_message(chat_id, c_v.help_msg)
#
#
# def show_keyboard(chat_id):
#     markup = telebot.types.ReplyKeyboardMarkup()
#     markup.row(c_v.TAKE_PHOTO, c_v.TAKE_VIDEO, c_v.TAKE_AUDIO)
#     bot.send_message(chat_id, "Choose one letter:", reply_markup=markup)


def update_ver():
    ver.V_COMM = get_commits_num()
    ver.V_FULL = "{:s}.{:s}.{:s}.{:s}".format(ver.V_MAJ,
                                              ver.V_MIN,
                                              ver.V_COMM,
                                              ver.V_BRANCH)

if __name__ == '__main__':
    log_set_mt(cfg.MULTITHREAD)
    log_set_q(cfg.QUIET)
    log_init(os.path.join(os.getcwd(), cfg.LOG_P))

    update_ver()

    user_mod = UserModel(os.path.join(os.getcwd(), cfg.INI_PATH))

    c_b.set_model(user_mod)
    c_b.start_listen()

    if cfg.MULTITHREAD:
        log_out_deffered()

