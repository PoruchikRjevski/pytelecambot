import os
import configparser
import logging

from logger import *
from base_daemon.base_defs import *
import common

__all__ = ['BD_INI_DMN']


logger = logging.getLogger("{:s}.BD_INI_DMN".format(common.SOLUTION))


class BD_INI_DMN:
    def __init__(self, c_path):
        self.__bd_path = c_path
        self.__cfg = configparser.ConfigParser()

        self.__init_bd()

    def __set_block(self, t_block, t_dict):
        self.__cfg[t_block] = t_dict

    def __init_bd(self):
        if os.path.exists(self.__bd_path):
            self.__cfg.read(self.__bd_path)
        else:
            logger.error("BD {:s} was not finded.".format(self.__bd_path))

    def accept_changes(self):
        if os.path.exists(self.__bd_path):
            with open(self.__bd_path, 'w') as cfg_f:
                self.__cfg.write(cfg_f)

    def get_viewers(self):
        if self.__cfg.has_section(VIEWERS_BLK):
            return self.__cfg._sections[VIEWERS_BLK]
