#!/usr/bin/sudo python3

import os
import sys
import time
import datetime
import threading
import queue

import config as cfg
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


def reset_app():
    os.execl(sys.executable, sys.executable, *sys.argv)


def check_dir(dir):
    if not os.path.exists(dir):
        os.mkdir(dir)


if __name__ == '__main__':
    # preprocess
    log_set_mt(cfg.MULTITHREAD)
    log_set_q(cfg.QUIET)
    log_init(os.path.join(os.getcwd(), cfg.LOG_P))

    check_dir(os.path.join(os.getcwd(), cfg.OUT_P))

    date = datetime.date.today().__str__()
    out_d = os.path.join(os.getcwd(), cfg.OUT_P, date)
    check_dir(out_d)

    update_ver()

    # todo optionsparser read config, create cameras and return list of thats
    test_camera = Camera(0, "main", False)

    # create essence
    alert_queue = queue.Queue()

    cfg.FULL_P = os.path.join(os.getcwd(), cfg.LAST_D_P, cfg.LAST_F)

    user_mod = UserModel(os.path.join(os.getcwd(), cfg.INI_PATH))
    user_mod.add_camera(test_camera)

    tele_bot = Tele_Bot(user_mod)
    tele_bot.set_reset_f(reset_app)
    tele_bot.set_queue(alert_queue)


    cam_ids = [0]

    # observ = Observer()

    # create threads
    tb_t = threading.Thread(target=tele_bot.do_work)
    # obs_t = threading.Thread(target=observ.do_work_test)
    # tele_bot.do_work()

    # start work
    tb_t.start()
    # obs_t.start()

    # test

    # time.sleep(5)
    # tele_bot.stop_bot()
    # time.sleep(5)
    # alert_queue.put(open(os.path.join(os.getcwd(), cfg.LAST_D_P, cfg.LAST_F_T), 'rb'))
    # test

    # wait threads
    tb_t.join()
    # obs_t.join()

    # postprocess
    if cfg.MULTITHREAD:
        log_out_deffered()

