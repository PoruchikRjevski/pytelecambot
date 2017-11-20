import os
import datetime
import configparser
import logging

from config_loader.cfgld_defs import *
from observer import *
import common
import global_vars as g_v

__all__ = ['ConfigLoader']


logger = logging.getLogger("{:s}.ConfigLoader".format(common.SOLUTION))


class ConfigLoader:
    def __init__(self):
        self.__cameras_p = None
        self.__config_p = None

    def set_cameras_path(self, c_path):
        self.__cameras_p = c_path
        logger.info("Cameras path: {:s} ".format(c_path))

    def set_config_path(self, c_path):
        self.__config_p = c_path

    def load_config(self):
        cfg = configparser.ConfigParser()
        cfg.read(self.__config_p)

        if cfg.has_section(common.BOT_SECTION):
            if cfg.has_option(common.BOT_SECTION, common.REAL_TOKEN_OPTION):
                g_v.REAL_TOKEN = cfg[common.BOT_SECTION][common.REAL_TOKEN_OPTION]
                logger.info("real token: {:s}".format(g_v.REAL_TOKEN))
            if cfg.has_option(common.BOT_SECTION, common.TEST_TOKEN_OPTION):
                g_v.TEST_TOKEN = cfg[common.BOT_SECTION][common.TEST_TOKEN_OPTION]
                logger.info("test token: {:s}".format(g_v.TEST_TOKEN))

    def load_cameras(self):
        cfg = configparser.ConfigParser()
        cfg.read(self.__cameras_p)

        out_d = os.path.join(g_v.PROJECT_PATH, common.OUT_DIR_PATH, datetime.date.today().__str__())
        common.make_dir(out_d)

        cams_l = []

        for block in cfg.sections():
            c_id = block
            c_name = ""
            c_as = False
            c_md = False
            c_c_min = 0
            c_c_max = 100
            for opt in cfg.options(block):
                if opt == CAM_NAME:
                    c_name = cfg.get(block, opt)
                elif opt == CAM_AUTOSTART:
                    c_as = True if cfg.get(block, opt) == "True" else False
                elif opt == CAM_MOTION_DETECT:
                    c_md = True if cfg.get(block, opt) == "True" else False
                elif opt == CAM_CONT_MIN:
                    c_c_min = int(cfg.get(block, opt))
                elif opt == CAM_CONT_MAX:
                    c_c_max = int(cfg.get(block, opt))

            cams_l.append(Camera(c_id, c_name, out_d, c_as, c_md, c_c_min, c_c_max))

        return cams_l