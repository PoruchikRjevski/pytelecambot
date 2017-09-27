import os
import sys
import queue

import telebot
import telebot.types

import config as cfg
from tele_bot.bot_def import *

__all__ = ['Tele_Bot']


class Tele_Bot(telebot.TeleBot):
    def __init__(self, u_model):
        super().__init__(TOKEN)
        bot = self

        self.__stop_f = False

        self.__model = u_model

        self.__reg_state = ''
        self.__reg_pos = None
        self.__reg_item = None

        @bot.message_handler(commands=[C_START, C_HELP])
        def handle_start(msg):
            self.__show_m(msg)

        @bot.message_handler(content_types=["text"])
        def handle_text(msg):
            t_comm = msg.text

            if t_comm == C_A_RES:
                self.__restart_bot(msg)
            elif t_comm == C_A_STOP:
                self.__stop_bot(msg)
            elif t_comm == C_CTRL:
                self.__show_ctrl_m(msg)
            elif t_comm == C_A_WHO_ARE or t_comm == C_A_WHO_R or t_comm == C_A_WHO_UR:
                self.__show_who_are(msg)
            elif t_comm == C_R_ADD or t_comm == C_R_KICK:
                self.__do_reg(msg)
            elif t_comm == C_R_NEXT:
                self.__show_next_reg(msg)
            elif t_comm == C_BACK or t_comm == C_UPD:
                self.__show_m(msg)

    def __def_reg(self):
        self.__reg_state = ''
        self.__reg_pos = None
        self.__reg_item = None

    def hi_protect(func):
        def wrapped(s, msg, *args, **kwargs):
            c_id = str(msg.chat.id)
            if c_id == ADMIN_ID:
                return func(s, msg)
        return wrapped

    def mid_protect(func):
        def wrapped(s, msg, *args, **kwargs):
            c_id = str(msg.chat.id)
            if s.__model.is_viewer(c_id):
                return func(s, msg)
        return wrapped

    def hm_protect(func):
        def wrapped(s, msg, *args, **kwargs):
            c_id = str(msg.chat.id)
            if s.__model.is_viewer(c_id) or c_id == ADMIN_ID:
                return func(s, msg)
        return wrapped

    @hi_protect
    def __restart_bot(self, msg):
        self.send_message(ADMIN_ID, "Rebooting...")
        os.execl(sys.executable, sys.executable, *sys.argv)

    @hi_protect
    def __stop_bot(self, msg):
        self.send_message(ADMIN_ID, "Stopping...")
        self.__stop_f = True

    def __show_m(self, msg):
        t_id = str(msg.chat.id)

        if t_id == ADMIN_ID:
            self.__show_admin_m()
        elif self.__model.is_viewer(t_id):
            self.__show_viewer_m(msg)
        else:
            self.__show_undef_m(msg)

        self.__def_reg()

    @hm_protect
    def __show_ctrl_m(self, msg):
        self.send_message(msg.chat.id, "You rules:", reply_markup=CTRL_MARK)

    @mid_protect
    def __show_viewer_m(self, msg):
        self.send_message(msg.chat.id, "You rules:", reply_markup=VIEWERS_MARK)

    def __show_undef_m(self, msg):
        self.send_message(msg.chat.id, "You rules:", reply_markup=UNDEF_MARK)

    def __show_admin_m(self):
        self.send_message(ADMIN_ID, "You rules:", reply_markup=ADMIN_MARK)

    def __show_reg_m(self):
        self.send_message(ADMIN_ID, "You rules:", reply_markup=REG_MARK)

    @hi_protect
    def __show_next_reg(self, _):
        c_len = 0

        if self.__reg_state == C_A_WHO_UR:
            c_len = self.__model.get_ureg_req_len()
        elif self.__reg_state == C_A_WHO_R:
            c_len = self.__model.get_reg_req_len()
        elif self.__reg_state == C_A_WHO_ARE:
            c_len = self.__model.get_viewers_len()

        if c_len <= 0:
            self.__def_reg()
            self.send_message(ADMIN_ID, "No more users")
            self.__show_admin_m()

            return

        if self.__reg_pos is None:
            self.__reg_pos = 0
        else:
            if c_len > (self.__reg_pos + 1):
                self.__reg_pos += 1
            else:
                self.__reg_pos = 0

        item = None

        if self.__reg_state == C_A_WHO_UR:
            item = self.__model.get_ureg_req_by_i(self.__reg_pos)
        elif self.__reg_state == C_A_WHO_R:
            item = self.__model.get_reg_req_by_i(self.__reg_pos)
        elif self.__reg_state == C_A_WHO_ARE:
            item = self.__model.get_viewer_by_i(self.__reg_pos)

        (n_id, n_name) = item
        self.__reg_item = item

        self.send_message(ADMIN_ID, "Selected: \"{:s} : {:s}\"".format(n_name, str(n_id)))

    @hi_protect
    def __show_who_are(self, msg):
        t_comm = msg.text

        pred = False

        if t_comm == C_A_WHO_ARE:
            pred = self.__show_who_are_viewer()
        elif t_comm == C_A_WHO_R:
            pred = self.__show_who_are_w_reg()
        elif t_comm == C_A_WHO_UR:
            pred = self.__show_who_are_w_ureg()

        if pred:
            self.__reg_state = t_comm
            self.__show_reg_m()
            self.__show_next_reg(msg)

    def __show_who_are_viewer(self):
        if self.__model.get_viewers_len() > 0:
            self.send_message(ADMIN_ID, "There are viewers:\n{:s}".format(self.__model.get_viewers_list_str()))
            return True

        self.send_message(ADMIN_ID, "Nobody")
        return False

    def __show_who_are_w_reg(self):
        if self.__model.get_reg_req_len() > 0:
            self.send_message(ADMIN_ID, "There are want's to reg:\n{:s}".format(self.__model.get_reg_req_list_str()))
            return True

        self.send_message(ADMIN_ID, "Nobody")
        return False

    def __show_who_are_w_ureg(self):
        if self.__model.get_ureg_req_len() > 0:
            self.send_message(ADMIN_ID, "There are want's to unreg:\n{:s}".format(self.__model.get_ureg_req_list_str()))
            return True

        self.send_message(ADMIN_ID, "Nobody")
        return False

    @hi_protect
    def __do_reg(self, msg):
        t_comm = msg.text

        pred = False

        if t_comm == C_R_ADD:
            pred = self.__do_add()
        elif t_comm == C_R_KICK:
            pred = self.__do_kick()

        if pred:
            self.__show_next_reg(msg)

    def __do_add(self):
        if not self.__reg_item is None:
            (a_id, a_name) = self.__reg_item

            self.__model.add_viewer(a_id)
            self.send_message(ADMIN_ID, "User \"{:s} : {:s}\" was added to viewers".format(a_id,
                                                                                           a_name))
            return True

        self.send_message(ADMIN_ID, "Bad try add viewer")
        return False

    def __do_kick(self):
        if not self.__reg_item is None:
            (k_id, k_name) = self.__reg_item

            self.__model.kick_viewer(k_id)
            self.send_message(ADMIN_ID, "User \"{:s} : {:s}\" was kicked from viewers".format(k_id,
                                                                                              k_name))
            return True

        self.send_message(ADMIN_ID, "Bad try kick viewer")
        return False

    def start_loop(self):
        self.send_message(ADMIN_ID, "Bot was started")
        self.__show_admin_m()

        offset = None

        while not self.__stop_f:
            updates = self.get_updates(offset, timeout=UPD_TMT)

            # process msgs
            if len(updates) > 0:
                offset = updates[-1].update_id + 1
                self.process_new_updates(updates)

        self.send_message(ADMIN_ID, "Bot was stopped")

# -----------------------------------------------------------------------
#
# bot = telebot.AsyncTeleBot(cfg.token)
# # bot_pid = bot.get_me()
#
# send_l = queue.Queue()
# receive_l = []
#
# stop_flag = [True]
#
# user_model = None
#
# cur_item = -1
# cur_action = ''
#
#
# def set_model(model):
#     global user_model
#     user_model = model
#
#
# @bot.message_handler(commands=[C_START, C_HELP])
# def handle_start_help(message):
#     t_id = message.chat.id
#
#     if message.chat.id == ADMIN_ID:
#         show_admin_m()
#     elif user_model.is_viewer(t_id):
#         show_viewer_m(t_id)
#     else:
#         show_unreg_m(t_id)
#
#
# @bot.message_handler(content_types=["text"])
# def handle_text(message):
#     t_comm = message.text
#     t_id = message.chat.id
#     t_name = message.chat.first_name
#     print("text: {:s}".format(t_comm))
#     print("id: {:s}".format(str(t_id)))
#
#     if t_comm == C_HELP or t_comm == C_START:
#         handle_start_help(message)
#         return
#
#     if t_id == ADMIN_ID:
#         if t_comm == A_D_ADD:
#             add_viewer()
#         elif t_comm == A_D_KICK:
#             kick_viewer()
#         elif t_comm == A_D_WHO_REG:
#             show_who_want_reg()
#         elif t_comm == A_D_WHO_UREG:
#             show_who_want_unreg()
#         elif t_comm == A_D_WHO_ARE:
#             show_who_viewer()
#         elif t_comm == A_D_CONRTOL:
#             show_control_m(ADMIN_ID)
#         elif t_comm == BACK_M:
#             show_admin_m()
#         elif t_comm == R_LAST_F:
#             show_last_frame(ADMIN_ID)
#         elif t_comm == NEXT_M:
#             show_next_want_reg()
#     elif user_model.is_viewer(t_id):
#         if t_comm == R_UNREG:
#             unregister_request(t_id, t_name)
#         elif t_comm == A_D_CONRTOL:
#             show_control_m(t_id)
#         elif t_comm == BACK_M or t_comm == UPD_M:
#             show_viewer_m(t_id)
#         elif t_comm == R_LAST_F:
#             show_last_frame(t_id)
#         else:
#             show_viewer_m(t_id)
#     else:
#         if t_comm == N_R_REG:
#             register_request(t_id, t_name)
#         else:
#             show_unreg_m(t_id)
#
#
# def show_next_want_reg():
#     global user_model
#     global cur_item
#     global cur_action
#
#     c_dict = {}
#
#     if cur_action == A_D_WHO_REG:
#         c_dict = user_model.reg_req
#     elif cur_action == A_D_WHO_UREG:
#         c_dict = user_model.unreg_req
#     elif cur_action == A_D_WHO_ARE:
#         c_dict = user_model.viewers
#
#     if cur_item == -1:
#         cur_item = 0
#     else:
#         if len(c_dict) > cur_item:
#             cur_item = 0
#         else:
#             cur_item += 1
#
#     (n_id, n_name) = list(c_dict.items())[cur_item]
#     bot.send_message(ADMIN_ID, "\"{:s} : {:s}\"".format(n_name, str(n_id)))
#
#
# def show_last_frame(id):
#     # bot.send_photo(chat_id=chat_id, photo=open('tests/test.png', 'rb')
#     bot.send_message(id, "There are will be last frame.")
#
#
# def add_viewer():
#     global user_model
#     global cur_item
#     global cur_action
#
#     if cur_item != -1 and cur_action == A_D_WHO_REG:
#         (c_id, c_name) = list(user_model.reg_req.items())[cur_item]
#
#         user_model.add_viewer(c_id)
#         show_viewer_added(c_id, c_name)
#
#         if not check_len():
#             show_admin_m()
#
#
# def show_viewer_added(id, name):
#     bot.send_message(ADMIN_ID, "User \"{:s} : {:s}\" was added to viewers".format(name, str(id)))
#     bot.send_message(id, "You are registered")
#     show_viewer_m(id)
#
#
# def kick_viewer():
#     global user_model
#     global cur_item
#     global cur_action
#
#     if cur_item != -1 and (cur_action == A_D_WHO_UREG or cur_action == A_D_WHO_ARE):
#         (c_id, c_name) = list(user_model.viewers.items())[cur_item]
#
#         user_model.rem_viewer(c_id)
#         show_viewer_kicked(c_id, c_name)
#
#         if not check_len():
#             show_admin_m()
#
#
# def show_viewer_kicked(id, name):
#     bot.send_message(ADMIN_ID, "User \"{:s} : {:s}\" was kicked from viewers".format(name, str(id)))
#     bot.send_message(id, "You are kicked")
#     show_unreg_m(id)
#
#
# def show_unreg_m(t_id):
#     markup = telebot.types.ReplyKeyboardMarkup()
#     markup.row(N_R_REG)
#     markup.row(UPD_M)
#     bot.send_message(t_id, "You move:", reply_markup=markup)
#
#
# def show_viewer_m(t_id):
#     markup = telebot.types.ReplyKeyboardMarkup()
#     markup.row(R_UNREG, A_D_CONRTOL)
#     markup.row(UPD_M)
#     bot.send_message(t_id, "You move:", reply_markup=markup)
#
#
# def show_admin_m():
#     global cur_action
#     global cur_item
#     cur_action = ''
#     cur_item = -1
#
#     markup = telebot.types.ReplyKeyboardMarkup()
#     markup.row(A_D_WHO_REG, A_D_WHO_UREG, A_D_WHO_ARE)
#     markup.row(A_D_CONRTOL)
#     bot.send_message(ADMIN_ID, "You move:", reply_markup=markup)
#
#
# def show_control_m(chat_id):
#     markup = telebot.types.ReplyKeyboardMarkup()
#     markup.row(R_LAST_F)
#     markup.row(BACK_M)
#     bot.send_message(chat_id, "You move:", reply_markup=markup)
#
#
# def unregister_request(id, name):
#     global user_model
#     user_model.add_ureg_req(id, name)
#     alert_want_unreg()
#
#
# def alert_want_unreg():
#     global user_model
#     sz = len(user_model.unreg_req)
#     print("unreg: {:s}".format(str(sz)))
#     if sz > 0:
#         bot.send_message(ADMIN_ID, "Want to unreg {:s}".format(str(sz)))
#
#
# def register_request(id, name):
#     global user_model
#     user_model.add_reg_req(id, name)
#     alert_want_reg()
#
#
# def alert_want_reg():
#     global user_model
#     sz = len(user_model.reg_req)
#     print("reg: {:s}".format(str(sz)))
#     if sz > 0:
#         bot.send_message(ADMIN_ID, "Want to reg {:s}".format(str(sz)))
#
#
# def show_who_want_reg():
#     global user_model
#     global cur_action
#
#     cur_action = A_D_WHO_REG
#
#     if not check_len():
#         cur_action = ''
#         return
#
#     w_reg_s = "\n".join(["{:s} : {:s}".format(str(k), name) for (k, name) in user_model.reg_req.items()])
#     bot.send_message(ADMIN_ID, "They want to reg: \n {:s}".format(w_reg_s))
#     show_select_menu()
#     show_next_want_reg()
#
#
# def show_select_menu():
#     global cur_action
#
#     markup = telebot.types.ReplyKeyboardMarkup()
#     if cur_action == cur_action == A_D_WHO_REG:
#         markup.row(A_D_ADD, NEXT_M)
#     elif cur_action == A_D_WHO_UREG or cur_action == A_D_WHO_ARE:
#         markup.row(A_D_KICK, NEXT_M)
#     markup.row(BACK_M)
#     bot.send_message(ADMIN_ID, "You move:", reply_markup=markup)
#
#
# def check_len():
#     global cur_action
#
#     if cur_action == A_D_WHO_UREG:
#         if len(user_model.unreg_req) == 0:
#             return False
#     elif cur_action == A_D_WHO_REG:
#         if len(user_model.reg_req) == 0:
#             return False
#     elif cur_action == A_D_WHO_ARE:
#         if len(user_model.viewers) == 0:
#             return False
#
#     return True
#
# def show_who_want_unreg():
#     global user_model
#     global cur_action
#
#     cur_action = A_D_WHO_UREG
#
#     if not check_len():
#         cur_action = ''
#         return
#
#     w_ureg_s = "\n".join(["{:s} : {:s}".format(str(k), name) for (k, name) in user_model.unreg_req.items()])
#     bot.send_message(ADMIN_ID, "They want to unreg: \n {:s}".format(w_ureg_s))
#     show_select_menu()
#     show_next_want_reg()
#
#
# def show_who_viewer():
#     global user_model
#     global cur_action
#
#     cur_action = A_D_WHO_ARE
#
#     if not check_len():
#         cur_action = ''
#         return
#
#     w_viewer_s = "\n".join(["{:s} : {:s}".format(str(k), name) for (k, name) in user_model.viewers.items()])
#     bot.send_message(ADMIN_ID, "They want to unreg: \n {:s}".format(w_viewer_s))
#     show_select_menu()
#     show_next_want_reg()
#
#
# def say_who_want_reg():
#     msg = "They want to reg: \n{:s}".format("\n".join(["{:s} : {:s}".format(str(key), msg.chat.first_name) for (key, msg) in reg_dict.items()]))
#
#     bot.send_message(ADMIN_ID, msg)
#
#
# @bot.message_handler(commands=['stop'])
# def handle_stop(message):
#     if message.chat.id == ADMIN_ID:
#         stop_flag[0] = False
#
#
# def add_move_alert(msg, path):
#     send_q.put(path, msg)
#
#
# def send_msgs():
#     while send_l:
#         (type, id) = send_l.get()
#
#         if type == REG_A:
#             if id in reg_q.keys():
#                 msg = reg_q[id]
#                 bot.send_message(ADMIN_ID, "Ask reg {:s}:{:s}".format(msg.chat.first_name,
#                                                                          str(msg.chat.id)))
#
#
#
#
# def start_listen():
#     offset = None
#     # bot.polling(none_stop=False)
#
#     while stop_flag[0]:
#         upds = bot.get_updates(offset, timeout=3)
#
#         # process msgs
#         if len(upds) > 0:
#             offset = upds[-1].update_id + 1
#             bot.process_new_updates(upds)
#
#     bot.send_message(ADMIN_ID, "Service was stopped")