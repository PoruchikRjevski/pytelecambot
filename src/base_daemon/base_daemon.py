import os
import configparser

from logger import *
from base_daemon.base_defs import *

__all__ = ['init_base', 'get_viewers']

DB_PATH = ""
config_h = configparser.ConfigParser()


def init_base():
    with open(DB_PATH, 'r') as cfg_f:
        config_h.read(cfg_f)


def get_viewers():
    global config_h
    global DB_PATH

    if config_h.has_section(VIEWERS_BLK):
        return config_h[VIEWERS_BLK].items()
        # if config_h.has_option(VIEWERS_BLK, IDS_SECT):
        #     return config_h.get(VIEWERS_BLK, IDS_SECT).split(",")
    return {}


def write_cfg():
    global config_h
    global DB_PATH

    with open(DB_PATH, 'w') as cfg_f:
        config_h.write(cfg_f)


def add_viewer(id, name):
    global config_h
    global DB_PATH

    if config_h.has_section(VIEWERS_BLK):
        viewers = config_h[VIEWERS_BLK].items()
        viewers[id] = name
        config_h[VIEWERS_BLK] = viewers

        write_cfg()


def rem_viewer(id):
    global config_h
    global DB_PATH

    if config_h.has_section(VIEWERS_BLK):
        viewers = config_h[VIEWERS_BLK].items()

        if id in viewers.keys():
            del viewers[id]
            config_h[VIEWERS_BLK] = viewers
            write_cfg()
