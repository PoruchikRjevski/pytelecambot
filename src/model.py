import collections

import base_daemon.base_daemon as b_d

__all__ = ['UserModel']

class UserModel:
    def __init__(self, path):
        self.__admins = []
        self.__reg_req = collections.OrderedDict()
        self.__ureg_req = collections.OrderedDict()

        self.__bd_dmn = b_d.BD_INI_DMN(path)
        self.__viewers = self.__bd_dmn.get_viewers()

    def get_viewers_len(self):
        return len(self.__viewers)

    def get_viewer_by_i(self, t_i):
        return list(self.__viewers.items())[t_i]

    def is_viewer(self, t_id):
        return t_id in self.__viewers.keys()

    def add_viewer(self, t_id):
        if t_id in self.__reg_req.keys():
            name = self.__reg_req[t_id]
            self.__viewers[t_id] = name

            self.__bd_dmn.accept_changes()

            del self.__reg_req[t_id]

    def kick_viewer(self, t_id):
        if t_id in self.__viewers.keys():
            del self.__viewers[t_id]

            self.__bd_dmn.accept_changes()

            if t_id in self.__ureg_req.keys():
                del self.__ureg_req[t_id]

    def add_reg_req(self, t_id, t_name):
        self.__reg_req[t_id] = t_name

    def get_reg_req_len(self):
        return len(self.__reg_req)

    def get_reg_req_by_i(self, t_i):
        return list(self.__reg_req.items())[t_i]

    def add_ureg_req(self, t_id, t_name):
        self.__ureg_req[t_id] = t_name

    def get_ureg_req_len(self):
        return len(self.__ureg_req)

    def get_ureg_req_by_i(self, t_i):
        return list(self.__ureg_req.items())[t_i]



