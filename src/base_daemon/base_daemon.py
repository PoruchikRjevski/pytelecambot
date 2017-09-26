import os
import configparser

from logger import *
from base_daemon.base_defs import *

__all__ = ['init_base', 'get_viewers', 'add_viewer', 'rem_viewer']

DB_PATH = ""
config_h = None


def init_base():
    global config_h
    global DB_PATH

    print("path: {:s}".format(DB_PATH))

    config_h = configparser.ConfigParser()
    config_h.read(DB_PATH)


def get_viewers():
    global config_h
    global DB_PATH

    if config_h.has_section(VIEWERS_BLK):
        return config_h._sections[VIEWERS_BLK]
    return {}


def write_cfg():
    global config_h
    global DB_PATH

    with open(DB_PATH, 'w') as cfg_f:
        config_h.write(cfg_f)


def add_viewer(t_id, t_name):
    global config_h
    global DB_PATH

    viewers = {}

    if config_h.has_section(VIEWERS_BLK):
        viewers = config_h._sections[VIEWERS_BLK]

    viewers[t_id] = t_name
    config_h._sections[VIEWERS_BLK] = viewers

    write_cfg()


def rem_viewer(t_id):
    global config_h
    global DB_PATH

    if config_h.has_section(VIEWERS_BLK):
        viewers = config_h._sections[VIEWERS_BLK]

        if t_id in viewers.keys():
            del viewers[t_id]
            config_h._sections[VIEWERS_BLK] = viewers
            write_cfg()
