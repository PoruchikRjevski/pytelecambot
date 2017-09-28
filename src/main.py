#!/usr/bin/sudo python3

import os
import sys
import time
import datetime
import threading
import queue

import common as cmn
import version as ver
from tele_bot.bot import *
from logger import *
from git_man import *
from model import *
from observer import *
from time_checker import *
# from sql_daemon import *


def update_ver():
    ver.V_COMM = get_commits_num()
    ver.V_FULL = "{:s}.{:s}.{:s}.{:s}".format(ver.V_MAJ,
                                              ver.V_MIN,
                                              ver.V_COMM,
                                              ver.V_BRANCH)


if __name__ == '__main__':
    # preprocess
    log_set_mt(cmn.MULTITHREAD)
    log_set_q(cmn.QUIET)
    log_init(os.path.join(os.getcwd(), cmn.LOG_P))

    cmn.make_dir(os.path.join(os.getcwd(), cmn.OUT_P))

    date = datetime.date.today().__str__()
    out_d = os.path.join(os.getcwd(), cmn.OUT_P, date)
    cmn.make_dir(out_d)

    update_ver()

    # todo optionsparser read config, create cameras and return list of thats
    main_camera = Camera(0, "main", out_d, False)
    sec_camera = Camera(1, "sec", out_d, False)

    # create essence
    alert_queue = queue.Queue()

    cmn.FULL_P = os.path.join(os.getcwd(), cmn.LAST_D_P, cmn.LAST_F)

    user_mod = UserModel(os.path.join(os.getcwd(), cmn.INI_PATH))
    user_mod.add_camera(main_camera)
    user_mod.add_camera(sec_camera)

    tele_bot = Tele_Bot(user_mod)
    tele_bot.set_queue(alert_queue)

    # create threads
    tb_t = threading.Thread(target=tele_bot.do_work)

    # start work
    tb_t.start()

    # wait threads
    tb_t.join()

    # postprocess
    if cmn.MULTITHREAD:
        log_out_deffered()

