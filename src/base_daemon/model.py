import base_daemon.base_daemon as b_d

__all__ = ['UserModel']

class UserModel:
    def __init__(self, path):
        self.__admins = []
        self.__viewers = []
        self.__path = path
        b_d.DB_PATH = path

        self.__load_base()

    def __load_base(self):
        b_d.init_base()
        self.__viewers = b_d.get_viewers()

    @property
    def viewers(self):
        return self.__viewers

    def add_viewer(self, id):
        self.__viewers.append(id)
        b_d.add_viewer(id)

    def rem_viewer(self, id):
        self.__viewers.remove(id)
        b_d.rem_viewer(id)

    def is_viewer(self, id):
        return id in self.__viewers


