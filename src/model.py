import collections
import queue
from multiprocessing import Queue

import base_daemon.base_daemon as b_d
from observer.camera import *

__all__ = ['UserModel']


class UserModel:
    def __init__(self, path):
        self.__admins = []
        self.__reg_req = collections.OrderedDict()
        self.__ureg_req = collections.OrderedDict()

        self.__bd_dmn = b_d.BD_INI_DMN(path)
        self.__viewers = self.__bd_dmn.get_viewers()
        self.__cameras = []

        self.__alerts = Queue()

    def __set_alert_deq(self):
        for cam in self.__cameras:
            cam.set_alert_deq(self.__alerts)

    @property
    def alerts(self):
        return self.__alerts

    def get_viewers_len(self):
        return len(self.__viewers)

    def get_viewers_list_str(self):
        return "\n".join(["{:s} : {:s}".format(str(k), name) for (k, name) in self.__viewers.items()])

    def get_viewer_by_i(self, t_i):
        tmp_l = list(self.__viewers.items())

        if len(tmp_l) > t_i:
            return tmp_l[t_i]

        return '', ''

    def is_viewer(self, t_id):
        return t_id in self.__viewers.keys()

    def add_viewer(self, t_id):
        if t_id in self.__reg_req.keys():
            name = self.__reg_req[t_id]
            self.__viewers[t_id] = name

            self.__bd_dmn.accept_changes()

            self.kick_reg_req(t_id)

    def kick_viewer(self, t_id):
        if t_id in self.__viewers.keys():
            del self.__viewers[t_id]

            self.__bd_dmn.accept_changes()

            self.kick_ureg_req(t_id)

    def add_reg_req(self, t_id, t_name):
        self.__reg_req[t_id] = t_name

    def get_reg_req_len(self):
        return len(self.__reg_req)

    def get_reg_req_list_str(self):
        return "\n".join(["{:s} : {:s}".format(str(k), name) for (k, name) in self.__reg_req.items()])

    def get_reg_req_by_i(self, t_i):
        tmp_l = list(self.__reg_req.items())

        if len(tmp_l) > t_i:
            return tmp_l[t_i]

        return '', ''

    def kick_reg_req(self, t_id):
        if t_id in self.__reg_req.keys():
            del self.__reg_req[t_id]

    def add_ureg_req(self, t_id, t_name):
        self.__ureg_req[t_id] = t_name

    def get_ureg_req_len(self):
        return len(self.__ureg_req)

    def get_ureg_req_list_str(self):
        return "\n".join(["{:s} : {:s}".format(str(k), name) for (k, name) in self.__ureg_req.items()])

    def get_ureg_req_by_i(self, t_i):
        tmp_l = list(self.__ureg_req.items())

        if len(tmp_l) > t_i:
            return tmp_l[t_i]

        return '', ''

    def kick_ureg_req(self, t_id):
        if t_id in self.__ureg_req.keys():
            del self.__ureg_req[t_id]

    def add_cameras(self, cam_list):
        self.__cameras = cam_list
        self.__set_alert_deq()

    def check_cameras(self):
        for cam in self.__cameras:
            cam.autostart()

    def switch_off_cameras(self):
        for cam in self.__cameras:
            cam.state = False

    def get_cameras_len(self):
        return len(self.__cameras)

    def camera_switch_state(self, t_i, state):
        self.get_camera_by_i(t_i).state = state

    def camera_switch_md_state(self, t_i, state):
        self.get_camera_by_i(t_i).motion_detect = state

    def get_camera_by_i(self, t_i):
        if len(self.__cameras) > t_i:
            return self.__cameras[t_i]

        return None

    def get_camera_last_f(self, t_i):
        return self.get_camera_by_i(t_i).last_frame

    def is_alerts_exists(self):
        return True if self.__alerts.qsize() > 0 else False

    def get_alert(self):
        return self.__alerts.get_nowait()

    def get_now_photo(self, t_i, who):
        self.get_camera_by_i(t_i).now_frame(who)