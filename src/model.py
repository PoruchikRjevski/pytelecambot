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


