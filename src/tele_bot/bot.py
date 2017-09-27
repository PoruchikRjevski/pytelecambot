import os
import sys
import queue

import telebot
import telebot.types

import config as cfg
from tele_bot.bot_def import *
import version as ver

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
            elif t_comm == C_U_REG:
                self.__add_req_reg(msg)
            elif t_comm == C_V_UREG:
                self.__add_req_ureg(msg)
            elif t_comm == C_LAST_F:
                self.__get_last_frame(msg)
            elif t_comm == C_GET or t_comm == C_BACK or t_comm == C_UPD:
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
            self.__show_admin_m(msg)
        elif self.__model.is_viewer(t_id):
            self.__show_viewer_m(msg)
        else:
            self.__show_undef_m(msg)

        self.__def_reg()

    @hm_protect
    def __show_ctrl_m(self, msg):
        self.send_message(msg.chat.id, TO_RULE, reply_markup=CTRL_MARK)

    @mid_protect
    def __show_viewer_m(self, msg):
        self.send_message(msg.chat.id, TO_RULE, reply_markup=VIEWERS_MARK)

    def __show_undef_m(self, msg):
        self.send_message(msg.chat.id, TO_RULE, reply_markup=UNDEF_MARK)

    @hi_protect
    def __show_admin_m(self, _):
        self.send_message(ADMIN_ID, TO_RULE, reply_markup=ADMIN_MARK)

    def __show_reg_m(self):
        self.send_message(ADMIN_ID, TO_RULE, reply_markup=REG_MARK)

    def __show_bot_started(self):
        msg = BOT_START.format(ver.V_FULL)
        self.send_message(ADMIN_ID, msg)
        self.send_message(ADMIN_ID, TO_RULE, reply_markup=GET_MARK)

        for i in range(0, self.__model.get_viewers_len()):
            (s_id, s_name) = self.__model.get_viewer_by_i(i)
            self.send_message(s_id, msg)
            self.send_message(s_id, TO_RULE, reply_markup=GET_MARK)

    def __show_bot_stopped(self):
        self.send_message(ADMIN_ID, BOT_STOP)

        for i in range(0, self.__model.get_viewers_len()):
            (s_id, s_name) = self.__model.get_viewer_by_i(i)
            self.send_message(s_id, BOT_STOP)

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

    def __add_req_reg(self, msg):
        t_id = msg.chat.id
        t_name = msg.chat.first_name

        self.__model.add_reg_req(t_id, t_name)
        self.send_message(ADMIN_ID, "User \"{:s} : {:s}\" want to register".format(t_id,
                                                                                   t_name))

    @mid_protect
    def __add_req_ureg(self, msg):
        t_id = msg.chat.id
        t_name = msg.chat.first_name

        self.__model.add_ureg_req(t_id, t_name)
        self.send_message(ADMIN_ID, "User \"{:s} : {:s}\" want to unregister".format(t_id,
                                                                                     t_name))

    @hm_protect
    def __get_last_frame(self, msg):
        self.send_photo(msg.chat.id, photo=open(os.path.join(os.getcwd(), cfg.LAST_D_P, cfg.LAST_F), 'rb'))

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
        self.__show_bot_started()

        offset = None
        while not self.__stop_f:
            updates = self.get_updates(offset, timeout=UPD_TMT)

            # process msgs
            if len(updates) > 0:
                offset = updates[-1].update_id + 1
                self.process_new_updates(updates)

        self.__show_bot_stopped()
