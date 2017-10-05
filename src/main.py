#!/usr/bin/sudo python3

import os
import sys
import time
import datetime
import threading
import multiprocessing
import queue

import common as cmn
import version as ver
from tele_bot.bot import *
from logger import *
from git_man import *
from model import *
from observer import *
from config_loader import *
from time_checker import *
from machine_daemon import *


def update_ver():
    ver.V_COMM = get_commits_num()
    ver.V_FULL = "{:s}.{:s}.{:s}.{:s}".format(ver.V_MAJ,
                                              ver.V_MIN,
                                              ver.V_COMM,
                                              ver.V_BRANCH)


if __name__ == '__main__':
    # PREPROCESS
    log_set_mt(cmn.MULTITHREAD)
    log_set_q(cmn.QUIET)

    # create log dir
    log_init(os.path.join(os.getcwd(), cmn.LOG_P))

    # create out dir
    cmn.make_dir(os.path.join(os.getcwd(), cmn.OUT_P))

    # check version
    update_ver()

    # CREATE OBJECTS
    cfg_loader = ConfigLoader()
    cfg_loader.set_cameras_path(os.path.join(os.getcwd(), cmn.CAMS_F_PATH))
    cameras_l = cfg_loader.load_cameras()

    user_mod = UserModel(os.path.join(os.getcwd(), cmn.INI_PATH))
    user_mod.add_cameras(cameras_l)

    machine_daemon = MachineDaemon()

    tele_bot = Tele_Bot(user_mod, machine_daemon)
    # tb_t = threading.Thread(target=tele_bot.do_work)

    # main cycle
    # START
    # tb_t.start()
    tele_bot.do_work()
    # user_mod.check_cameras()

    # FINISH
    # tb_t.join()

    # POSTPROCESS
    if cmn.MULTITHREAD:
        log_out_deffered()

