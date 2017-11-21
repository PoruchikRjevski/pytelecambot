import os
import sys
import threading
import queue
import logging
import time

import telebot
import telebot.types

import common
from tele_bot.bot_def import *
import version as ver

__all__ = ['TelegramBot']


logger = logging.getLogger("{:s}.TelegramBot".format(common.SOLUTION))


class TelegramBot(telebot.TeleBot):
    def __init__(self, token, u_model, m_daemon):
        super().__init__(token)

        logger.info("bot created with token: {:s}".format(token))

        bot = self

        self.__stop_f = False

        self.__model = u_model
        self.__machine_daemon = m_daemon
        self.__machine_daemon.set_alerts(self.__model.alerts)

        self.__reg_state = ''
        self.__reg_pos = None
        self.__reg_item = None

        self.__cam_sel_id = None
        self.__cam_sel_state = None
        self.__cam_sel_state_str = None

        self.__now_requester = None

        self.__create_cam_menu()

        @bot.message_handler(commands=[C_START, C_HELP])
        def handle_start(msg):
            logger.info("Rx \"{:s}\" by {:s} : {:s}".format(msg.text,
                                                            str(msg.chat.id),
                                                            msg.chat.first_name))
            self.__show_m(msg)

        @bot.message_handler(content_types=["text"])
        def handle_text(msg):
            t_comm = msg.text

            logger.info("Rx \"{:s}\" by {:s} : {:s}".format(t_comm,
                                                        str(msg.chat.id),
                                                        msg.chat.first_name))

            if t_comm == C_A_RES: self.__restart_bot(msg)
            elif t_comm == C_A_STOP: self.__stop_bot(msg)
            elif t_comm == C_CAMS: self.__show_cams_m(msg)
            elif t_comm in [C_A_WHO_ARE, C_A_WHO_R, C_A_WHO_UR]: self.__show_who_are(msg)
            elif t_comm == C_A_SYS_INFO: self.__get_system_info(msg)
            elif t_comm in [C_R_ACC, C_R_KICK]: self.__do_reg(msg)
            elif t_comm == C_R_NEXT: self.__show_next_reg(msg)
            elif t_comm == C_U_REG: self.__add_req_reg(msg)
            elif t_comm == C_V_UREG: self.__add_req_ureg(msg)
            elif t_comm in [C_MENU, C_BACK, C_UPD]: self.__show_m(msg)
            elif t_comm in [C_C_ON, C_C_OFF]: self.__cam_switch_state(msg)
            elif t_comm in [C_MD_ON, C_MD_OFF]: self.__cam_switch_md_state(msg)
            elif t_comm == C_C_LAST: self.__get_last_frame(msg)
            elif t_comm == C_C_NOW: self.__get_now_frame(msg)
            elif t_comm == C_C_NOW_ALL: self.__get_now_frame_all(msg)
            elif t_comm in CAM_M_L: self.__show_cam_m(msg)

    def __create_cam_menu(self):
        cams_n = self.__model.get_cameras_len()

        for n in range(cams_n):
            cam_name_tmp = self.__model.get_camera_by_i(n).cam_name
            CAM_M_L.append(cam_name_tmp)
            CAM_KB.row(*[cam_name_tmp])

        CAM_KB.row(*[C_MENU])

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
        common.reset_app()

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
    def __show_cams_m(self, msg):
        self.send_message(msg.chat.id, TO_RULE, reply_markup=CAM_KB)

    @mid_protect
    def __show_viewer_m(self, msg):
        self.send_message(msg.chat.id, TO_RULE, reply_markup=VIEWERS_KB)

    def __show_undef_m(self, msg):
        self.send_message(msg.chat.id, TO_RULE, reply_markup=UNDEF_KB)

    @hi_protect
    def __show_admin_m(self, _):
        self.send_message(ADMIN_ID, TO_RULE, reply_markup=ADMIN_KB)

    def __show_reg_m(self):
        self.send_message(ADMIN_ID, TO_RULE, reply_markup=REG_KB)

    def __show_kick_m(self):
        self.send_message(ADMIN_ID, TO_RULE, reply_markup=KICK_KB)

    def __switch_sel_cam_state(self, state):
        self.__cam_sel_state = state
        self.__cam_sel_stat_str = "работает" if state else "не работает"

    @hm_protect
    def __show_cam_m(self, msg):
        self.__cam_sel_id = CAM_M_L.index(msg.text)
        self.__switch_sel_cam_state(self.__model.get_camera_by_i(self.__cam_sel_id).state)

        CAM_CTRL_KB = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)

        if self.__model.get_camera_by_i(self.__cam_sel_id).state:
            CAM_CTRL_KB.row(*[C_C_OFF])
        else:
            CAM_CTRL_KB.row(*[C_C_ON])

        if self.__model.get_camera_by_i(self.__cam_sel_id).motion_detect:
            CAM_CTRL_KB.row(*[C_MD_OFF])
        else:
            CAM_CTRL_KB.row(*[C_MD_ON])

        for row in CAM_CTRL_M_L:
            CAM_CTRL_KB.row(*row)

        self.send_message(msg.chat.id, TO_RULE, reply_markup=CAM_CTRL_KB)

    def __show_bot_started(self):
        msg = BOT_START.format(ver.V_FULL)
        self.send_message(ADMIN_ID, msg)
        self.send_message(ADMIN_ID, TO_RULE, reply_markup=GET_KB)

        for i in range(0, self.__model.get_viewers_len()):
            (s_id, s_name) = self.__model.get_viewer_by_i(i)
            self.send_message(s_id, msg)
            self.send_message(s_id, TO_RULE, reply_markup=GET_KB)

            logger.info(msg)

    def __show_bot_stopped(self):
        self.send_message(ADMIN_ID, BOT_STOP)

        # for i in range(0, self.__model.get_viewers_len()):
        #     (s_id, s_name) = self.__model.get_viewer_by_i(i)
        #     self.send_message(s_id, BOT_STOP)

        logger.info(BOT_STOP)

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
            self.__show_admin_m(_)

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

            if t_comm == C_A_WHO_ARE:
                self.__show_kick_m()
            else:
                self.__show_reg_m()
            self.__show_next_reg(msg)

    def __show_who_are_viewer(self):
        if self.__model.get_viewers_len() > 0:
            self.send_message(ADMIN_ID, "There are viewers:\n{:s}".format(self.__model.get_viewers_list_str()))
            return True

        return False

    def __show_who_are_w_reg(self):
        if self.__model.get_reg_req_len() > 0:
            self.send_message(ADMIN_ID, "There are want's to reg:\n{:s}".format(self.__model.get_reg_req_list_str()))
            return True

        return False

    def __show_who_are_w_ureg(self):
        if self.__model.get_ureg_req_len() > 0:
            self.send_message(ADMIN_ID, "There are want's to unreg:\n{:s}".format(self.__model.get_ureg_req_list_str()))
            return True

        return False

    def __show_alert(self):
        if self.__model.is_alerts_exists():
            alert = self.__model.get_alert()

            if alert.type == common.T_CAM_NOW_PHOTO:
                self.send_photo(int(alert.who), photo=open(alert.img, 'rb'))
            elif alert.type == common.T_CAM_MOVE_PHOTO:
                photo_f = open(alert.img, 'rb')

                logger.error("Alert: {:s} saved photo in {:s}".format(alert.msg,
                                                                      alert.img))
                self.send_photo(ADMIN_ID, photo=photo_f)

                for i in range(0, self.__model.get_viewers_len()):
                    (s_id, s_name) = self.__model.get_viewer_by_i(i)
                    self.send_photo(s_id, photo=photo_f)

            elif alert.type in (common.T_SYS_NOW_INFO, common.T_SYS_ALERT):
                self.send_message(chat_id=ADMIN_ID, text=alert.msg, parse_mode="markdown")
            elif alert.type == common.T_CAM_SW:
                chat = telebot.types.Chat(ADMIN_ID, 'private')
                msg = telebot.types.Message(0, 0, 0, chat, 0, [])
                msg.text = alert.cam

                if alert.cam is not None:
                    self.__show_cam_m(msg)
                self.send_message(chat_id=ADMIN_ID, text=alert.msg, parse_mode="markdown")

                for i in range(0, self.__model.get_viewers_len()):
                    (s_id, s_name) = self.__model.get_viewer_by_i(i)
                    if alert.cam is not None:
                        msg.chat.id = s_id
                        self.__show_cam_m(msg)

                    self.send_message(s_id, alert.msg)

            # if alert.type == common.T_CAM_MOVE_PHOTO:
            #     self.send_photo(ADMIN_ID, photo=open(alert.img, 'rb'))
            #     out_log(alert.msg)
            # elif alert.type == common.T_CAM_MOVE_MP4:
            #     self.send_video(ADMIN_ID, data=open(alert.img, 'rb'))
            #     out_log(alert.msg)
            # elif alert.type == common.T_CAM_SW:
            #     if not alert.cam is None:
            #         chat = telebot.types.Chat(ADMIN_ID, 'private')
            #         msg = telebot.types.Message(0, 0, 0, chat, 0, [])
            #         msg.text = alert.cam
            #         self.__show_cam_m(msg)
            #
            #     self.send_message(ADMIN_ID, alert.msg)
            # elif alert.type == common.T_CAM_NOW_PHOTO:
            #     self.send_photo(ADMIN_ID, photo=open(alert.img, 'rb'))
            #     out_log(alert.msg)

            # do for all viewers

    @hi_protect
    def __do_reg(self, msg):
        t_comm = msg.text

        pred = False

        if t_comm == C_R_ACC:
            pred = self.__do_acc()
        elif t_comm == C_R_KICK:
            pred = self.__do_kick()

        if pred:
            self.__show_next_reg(msg)

    def __add_req_reg(self, msg):
        t_id = str(msg.chat.id)
        t_name = msg.chat.first_name

        self.__model.add_reg_req(t_id, t_name)
        self.send_message(ADMIN_ID, "User \"{:s} : {:s}\" want to register".format(t_id,
                                                                                   t_name))

    @mid_protect
    def __add_req_ureg(self, msg):
        t_id =str(msg.chat.id)
        t_name = msg.chat.first_name

        self.__model.add_ureg_req(t_id, t_name)
        self.send_message(ADMIN_ID, "User \"{:s} : {:s}\" want to unregister".format(t_id,
                                                                                     t_name))

    @hm_protect
    def __cam_switch_state(self, msg):
        state = True if msg.text == C_C_ON else False

        if state != self.__cam_sel_state:
            self.__switch_sel_cam_state(state)
            self.__model.camera_switch_state(self.__cam_sel_id, state)

    @hm_protect
    def __cam_switch_md_state(self, msg):
        state = True if msg.text == C_MD_ON else False

        if state != self.__model.get_camera_by_i(self.__cam_sel_id).motion_detect:
            self.__model.camera_switch_md_state(self.__cam_sel_id, state)

    @hm_protect
    def __get_last_frame(self, msg):
        last_f_p = self.__model.get_camera_last_f(self.__cam_sel_id)
        if os.path.exists(last_f_p):
            self.send_photo(msg.chat.id, photo=open(last_f_p, 'rb'))

    @hm_protect
    def __get_now_frame(self, msg):
        self.__model.get_now_photo(self.__cam_sel_id, msg.chat.id)

    @hm_protect
    def __get_now_frame_all(self, msg):
        cams_n = self.__model.get_cameras_len()

        for n in range(cams_n):
            self.__model.get_now_photo(n, msg.chat.id)

    @hi_protect
    def __get_system_info(self, _):
        self.__machine_daemon.get_now_status()

    def __do_acc(self):
        if not self.__reg_item is None:
            (a_id, a_name) = self.__reg_item

            chat = telebot.types.Chat(a_id, 'private')
            msg = telebot.types.Message(0, 0, 0, chat, 0, [])

            if self.__reg_state == C_A_WHO_R:
                self.__model.add_viewer(a_id)
                self.send_message(ADMIN_ID, "User \"{:s} : {:s}\" was added to viewers".format(a_id,
                                                                                               a_name))
                self.send_message(a_id, "You are added to viewers")
            elif self.__reg_state == C_A_WHO_UR:
                self.__model.kick_viewer(a_id)
                self.send_message(ADMIN_ID, "User \"{:s} : {:s}\" was kicked from viewers".format(a_id,
                                                                                                  a_name))
                self.send_message(a_id, "You are kicked from viewers")

            self.__show_m(msg)

            return True

        self.send_message(ADMIN_ID, "Bad try add viewer")
        return False

    def __do_kick(self):
        if not self.__reg_item is None:
            (k_id, k_name) = self.__reg_item

            if self.__reg_state == C_A_WHO_R:
                self.__model.kick_reg_req(k_id)
                self.send_message(ADMIN_ID, "User \"{:s} : {:s}\" was kicked from register requests".format(k_id,
                                                                                                            k_name))
            elif self.__reg_state == C_A_WHO_UR:
                self.__model.kick_ureg_req(k_id)
                self.send_message(ADMIN_ID, "User \"{:s} : {:s}\" was kicked from unregister requests".format(k_id,
                                                                                                              k_name))
            elif self.__reg_state == C_A_WHO_ARE:
                self.__model.kick_viewer(k_id)
                self.send_message(ADMIN_ID, "User \"{:s} : {:s}\" was kicked from viewers".format(k_id,
                                                                                                  k_name))
            return True

        self.send_message(ADMIN_ID, "Bad try kick viewer")
        return False

    def __get_updates(self):
        total = 0
        updates = self.get_updates(offset=self.last_update_id, timeout=UPD_TMT)
        while updates:
            total += len(updates)
            for update in updates:
                if update.update_id > self.last_update_id:
                    self.last_update_id = update.update_id

            self.process_new_updates(updates)
            updates = self.get_updates(offset=self.last_update_id + 1, timeout=UPD_TMT)
        return total

    def __skip_updates_m(self):
        total = 0
        updates = self.get_updates(offset=self.last_update_id, timeout=UPD_TMT)
        while updates:
            total += len(updates)
            for update in updates:
                if update.update_id > self.last_update_id:
                    self.last_update_id = update.update_id
            updates = self.get_updates(offset=self.last_update_id + 1, timeout=UPD_TMT)
        return total

    def do_work(self):
        logger.info("skipped: {:s}".format(str(self.__skip_updates_m())))
        self.__show_bot_started()

        self.__model.check_cameras()
        self.__machine_daemon.start_work()

        while not self.__stop_f:
            upds_num = self.__get_updates()
            if upds_num:
                logger.info("rx updates: {:s}".format(str(upds_num)))
            else:
                time.sleep(common.WAIT_TIMEOUT)
            self.__show_alert()

        self.__model.switch_off_cameras()
        self.__machine_daemon.stop_work()

        self.__show_bot_stopped()

    def stop_bot(self):
        self.__stop_f = True
