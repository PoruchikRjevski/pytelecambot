import os
import datetime
import configparser

import common as cmn
from config_loader.cfgld_defs import *
from observer import *

__all__ = ['ConfigLoader']


class ConfigLoader:
    def __init__(self):
        self.__cameras_p = None
        self.__cfg = configparser.ConfigParser()

    def set_cameras_path(self, c_path):
        self.__cameras_p = c_path

    def load_cameras(self):
        self.__cfg.read(self.__cameras_p)

        out_d = os.path.join(os.getcwd(), cmn.OUT_P, datetime.date.today().__str__())
        cmn.make_dir(out_d)

        cams_l = []

        for block in self.__cfg.sections():
            c_id = block
            c_name = ""
            c_as = False
            c_md = False
            c_c_min = 0
            c_c_max = 100
            for opt in self.__cfg.options(block):
                if opt == CAM_NAME:
                    c_name = self.__cfg.get(block, opt)
                elif opt == CAM_AUTOSTART:
                    c_as = True if self.__cfg.get(block, opt) == "True" else False
                elif opt == CAM_MOTION_DETECT:
                    c_md = True if self.__cfg.get(block, opt) == "True" else False
                elif opt == CAM_CONT_MIN:
                    c_c_min = int(self.__cfg.get(block, opt))
                elif opt == CAM_CONT_MAX:
                    c_c_max = int(self.__cfg.get(block, opt))

            cams_l.append(Camera(c_id, c_name, out_d, c_as, c_md, c_c_min, c_c_max))

        return cams_l