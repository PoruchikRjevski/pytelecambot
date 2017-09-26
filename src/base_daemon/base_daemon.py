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
    if config_h.has_section(VIEWERS_BLK):
        if config_h.has_option(VIEWERS_BLK, IDS_SECT):
            return config_h.get(VIEWERS_BLK, IDS_SECT).split(",")
    return []

def write_cfg():
    with open(DB_PATH, 'w') as cfg_f:
        config_h.write(cfg_f)


def add_viewer(id):
    if config_h.has_section(VIEWERS_BLK):
        if config_h.has_option(VIEWERS_BLK, IDS_SECT):
            viewers_l = config_h.get(VIEWERS_BLK, IDS_SECT).split(",")

            if isinstance(viewers_l, list):
                if id not in viewers_l:
                    viewers_l.append(id)
            else:
                if id != viewers_l:
                    viewers_l = [viewers_l, id]

            viewers = ",".join(viewers_l)

            config_h.set(VIEWERS_BLK, IDS_SECT, viewers)
            write_cfg()


def rem_viewer(id):
    if config_h.has_section(VIEWERS_BLK):
        if config_h.has_option(VIEWERS_BLK, IDS_SECT):
            viewers_l = config_h.get(VIEWERS_BLK, IDS_SECT).split(",")

            if isinstance(viewers_l, list):
                if id in viewers_l:
                    viewers_l.remove(id)
            else:
                if id == viewers_l:
                    viewers_l = []

            viewers = ",".join(viewers_l)

            config_h.set(VIEWERS_BLK, IDS_SECT, viewers)
            write_cfg()