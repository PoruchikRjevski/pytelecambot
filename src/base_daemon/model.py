import collections

import base_daemon.base_daemon as b_d

__all__ = ['UserModel']

class UserModel:
    def __init__(self, path):
        self.__admins = []
        self.__viewers = collections.OrderedDict()
        self.__reg_req = collections.OrderedDict()
        self.__unreg_req = collections.OrderedDict()
        self.__path = path
        b_d.DB_PATH = path

        self.__load_base()

    def __load_base(self):
        b_d.init_base()
        self.__viewers = b_d.get_viewers()

    @property
    def viewers(self):
        return self.__viewers

    @property
    def reg_req(self):
        return self.__reg_req

    def add_reg_req(self, t_id, t_name):
        self.__reg_req[t_id] = t_name

    @property
    def unreg_req(self):
        return self.__unreg_req

    def add_unreg_req(self, t_id, t_name):
        self.__unreg_req[t_id] = t_name

    def add_viewer(self, t_id):
        name = self.__reg_req[t_id]
        self.__viewers[t_id] = name
        b_d.add_viewer(t_id, name)

        del self.__reg_req[t_id]

    def rem_viewer(self, t_id):
        if t_id in self.__viewers.keys():
            del self.__viewers[t_id]
            b_d.rem_viewer(t_id)

            if t_id in self.__unreg_req.keys():
                del self.__unreg_req[t_id]

    def is_viewer(self, t_id):
        if t_id in self.__viewers.keys():
            return True

        return False


