import telebot

import common as c_v


bot = telebot.TeleBot(c_v.token)


@bot.message_handler(commands=['start', 'help'])
def handle_start_help(message):
    show_help(message.chat.id)


@bot.message_handler(content_types=["text"])
def echo(message):
    if message.text == c_v.CONTROL:
        show_keyboard(message.chat.id)
    elif message.text == c_v.TAKE_PHOTO:
        bot.send_message(message.chat.id, "It's photo")
    elif message.text == c_v.TAKE_VIDEO:
        bot.send_message(message.chat.id, "It's video")
    elif message.text == c_v.TAKE_AUDIO:
        bot.send_message(message.chat.id, "It's audio")
    else:
        bot.send_message(message.chat.id, message.text)


def show_help(chat_id):
    bot.send_message(chat_id, c_v.help_msg)


def show_keyboard(chat_id):
    markup = telebot.types.ReplyKeyboardMarkup()
    markup.row(c_v.TAKE_PHOTO, c_v.TAKE_VIDEO, c_v.TAKE_AUDIO)
    bot.send_message(chat_id, "Choose one letter:", reply_markup=markup)


if __name__ == '__main__':
    bot.polling(none_stop=True)