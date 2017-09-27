import os
import configparser

from logger import *
from base_daemon.base_defs import *

__all__ = ['BD_INI_DMN']


class BD_INI_DMN:
    def __init__(self, c_path):
        self.__bd_path = c_path
        self.__cfg = configparser.ConfigParser()

        self.__init_bd()

    def __set_block(self, t_block, t_dict):
        self.__cfg[t_block] = t_dict

    def __init_bd(self):
        self.__cfg.read(self.__bd_path)

    def accept_changes(self):
        with open(self.__bd_path, 'w') as cfg_f:
            self.__cfg.write(cfg_f)
