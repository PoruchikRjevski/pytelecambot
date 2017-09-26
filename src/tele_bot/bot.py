import telebot

import src.config as cfg
import tele_bot.bot_def as b_d

__all__ = ['start_listen']


bot = telebot.TeleBot(cfg.token)


@bot.message_handler(commands=['start', 'help'])
def handle_start_help(message):
    # if chat id in base show other start msg
    bot.send_message(message.chat.id, b_d.START_MSG)


@bot.message_handler(commands=['reg'])
def handle_reg(message):
    bot.send_message(message.chat.id, b_d.START_MSG)


def start_listen():
    bot.polling(none_stop=True)