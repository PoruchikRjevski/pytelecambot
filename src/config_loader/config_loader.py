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
        pass

    @staticmethod
    def load_config(c_path):
        cfg = configparser.ConfigParser()
        cfg.read(c_path)

        if cfg.has_section(common.BOT_SECTION):
            if cfg.has_option(common.BOT_SECTION, common.REAL_TOKEN_OPTION):
                g_v.REAL_TOKEN = str(cfg[common.BOT_SECTION][common.REAL_TOKEN_OPTION])
                logger.info("real token: {:s}".format(g_v.REAL_TOKEN))
            if cfg.has_option(common.BOT_SECTION, common.TEST_TOKEN_OPTION):
                g_v.TEST_TOKEN = str(cfg[common.BOT_SECTION][common.TEST_TOKEN_OPTION])
                logger.info("test token: {:s}".format(g_v.TEST_TOKEN))

    @staticmethod
    def load_cameras(c_path):
        cfg = configparser.ConfigParser()
        cfg.read(c_path)

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
            c_t_min = 0
            c_t_max = 100
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
                elif opt == CAM_THRESH_MIN:
                    c_t_min = int(cfg.get(block, opt))
                elif opt == CAM_THRESH_MAX:
                    c_t_max = int(cfg.get(block, opt))

            cams_l.append(Camera(c_id, c_name, out_d, c_as, c_md, c_c_min, c_c_max, c_t_min, c_t_max))

        return cams_l

    @staticmethod
    def save_cameras(cameras_list, c_path):
        do_write = True
        cfg = configparser.ConfigParser()
        cfg.read(c_path)

        for cam in cameras_list:
            c_id = str(cam.cam_id)
            c_name = str(cam.cam_name)
            c_as = "True" if cam.cam_autostart else "False"
            c_md = c_as = "True" if cam.motion_detect else "False"
            c_c_min, c_c_max = cam.contours
            c_c_min = str(c_c_min)
            c_c_max = str(c_c_max)
            c_t_min, c_t_max = cam.threshold
            c_t_min = str(c_t_min)
            c_t_max = str(c_t_max)

            if cfg.has_section(c_id):
                cfg[c_id][CAM_NAME] = c_name
                cfg[c_id][CAM_AUTOSTART] = c_as
                cfg[c_id][CAM_MOTION_DETECT] = c_md
                cfg[c_id][CAM_CONT_MIN] = c_c_min
                cfg[c_id][CAM_CONT_MAX] = c_c_max
                cfg[c_id][CAM_THRESH_MIN] = c_t_min
                cfg[c_id][CAM_THRESH_MAX] = c_t_max
            else:
                do_write = False

        if do_write:
            with open(c_path, 'w') as cfg_f:
                cfg.write(cfg_f)
        else:
            print("Cameras.ini was changed. Cancelled.")
