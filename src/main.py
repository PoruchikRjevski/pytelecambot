#!/usr/bin/sudo python3

import os

import config as cfg
import version as ver
from tele_bot.bot import *
from logger import *
from git_man import *
from model import *
# from sql_daemon import *


def update_ver():
    ver.V_COMM = get_commits_num()
    ver.V_FULL = "{:s}.{:s}.{:s}.{:s}".format(ver.V_MAJ,
                                              ver.V_MIN,
                                              ver.V_COMM,
                                              ver.V_BRANCH)

if __name__ == '__main__':
    log_set_mt(cfg.MULTITHREAD)
    log_set_q(cfg.QUIET)
    log_init(os.path.join(os.getcwd(), cfg.LOG_P))

    update_ver()

    user_mod = UserModel(os.path.join(os.getcwd(), cfg.INI_PATH))
    tele_bot = Tele_Bot(user_mod)

    tele_bot.do_work()

    if cfg.MULTITHREAD:
        log_out_deffered()

