#!/usr/bin/python3

import os
import sys
import time
import datetime
import threading
import multiprocessing
import queue
from optparse import OptionParser
import logging

from requests.exceptions import ReadTimeout
from telebot.apihelper import ApiException

import common
import version as ver
from tele_bot.bot import *
from git_man import *
from model import *
from observer import *
from config_loader import *
from time_checker import *
from machine_daemon import *
from logger import init_logging, log_func_name
import global_vars as g_v
import cam_tester


logger = logging.getLogger("{:s}.main".format(common.SOLUTION))


def update_ver():
    ver.V_COMM = get_commits_num()
    ver.V_FULL = "{:s}.{:s}.{:s}.{:s}".format(ver.V_MAJ,
                                              ver.V_MIN,
                                              ver.V_COMM,
                                              ver.V_BRANCH)


def set_options(parser):
    usage = "usage: %prog [options] [args]"

    parser.set_usage(usage)

    parser.add_option("-l", "--log",
                      action="store_true", dest="log",
                      default=False,
                      help="don't write status messages to log-files")
    parser.add_option("-v", "--verbose",
                      action="store_true", dest="verbose",
                      default=False,
                      help="print status messages to stdout")
    parser.add_option("-b", "--bot",
                      action="store_true", dest="bot",
                      default=False,
                      help="enable bot")
    parser.add_option("-t", "--test",
                      action="store_true", dest="test",
                      default=False,
                      help="use test bot")

    parser.add_option("--show",
                      action="store_true", dest="show",
                      default=False,
                      help="show cameras from config")
    parser.add_option("--setup",
                      action="store_true", dest="setup",
                      default=False,
                      help="uses with position of cam in list")


def setup_options(opts):
    if opts.verbose:
        g_v.VERBOSE = True
    if opts.log:
        g_v.LOGGING = True
    if opts.bot:
        g_v.BOT_ENABLED = True
    if opts.test:
        g_v.TEST_ENABLED = True


def load_config(cfg_loader):
    config_path = os.path.join(g_v.PROJECT_PATH, common.CONFIG_DIR_PATH, common.CONFIG_FILE)
    if not os.path.exists(config_path):
        logger.error("config.ini is not exists {:s}".format(config_path))
        true_exit()

    cfg_loader.load_config(config_path)

    cameras_path = os.path.join(g_v.PROJECT_PATH, common.CONFIG_DIR_PATH, common.CAMERAS_FILE)
    if not os.path.exists(cameras_path):
        logger.error("cameras.ini is not exists {:s}".format(cameras_path))
        true_exit()

    return cfg_loader.load_cameras(cameras_path)

@like_trhows
def run_bot(model, system_info_dmn):
    work_token = g_v.TEST_TOKEN if g_v.TEST_ENABLED else g_v.REAL_TOKEN
    telegram_bot = TelegramBot(work_token, model, system_info_dmn)
    telegram_bot.do_work()


def start_work():
    cfg_loader = ConfigLoader()
    cameras_list = load_config(cfg_loader)

    db_path = os.path.join(g_v.PROJECT_PATH, common.CONFIG_DIR_PATH, common.DB_FILE)
    if not os.path.exists(db_path):
        logger.error("Database is not exist {:s}".format(db_path))
        true_exit()

    model = UserModel(db_path)
    model.add_cameras(cameras_list)

    system_info_dmn = MachineDaemon()

    try:
        if g_v.BOT_ENABLED:
            try:
                run_bot(model, system_info_dmn)
            except (ReadTimeout, ApiException) as e:
                logger.error("EXCEPTION: {:s}".format(str(e)))
                run_bot(model, system_info_dmn)
        else:
            model.check_cameras()
            system_info_dmn.start_work()
    except KeyboardInterrupt:
        model.switch_off_cameras()
        system_info_dmn.stop_work()
    finally:
        model.switch_off_cameras()
        system_info_dmn.stop_work()


def true_exit():
    logger.info("{:s} was closed.".format(common.SOLUTION))
    sys.exit(0)


def bad_exit():
    logger.error("{:s} was closed. Because error, ...".format(common.SOLUTION))
    sys.exit(0)


def show_cameras():
    cfg_loader = ConfigLoader()
    cameras_list = load_config(cfg_loader)

    cameras_text = "\n".join(["{:s} - {:s}".format(str(cameras_list.index(cam)), str(cam.cam_name)) for cam in cameras_list])
    print("Cameras:\n{:s}".format(cameras_text))


def try_setup_cam(id):
    cfg_loader = ConfigLoader()
    cameras_list = load_config(cfg_loader)

    if id < len(cameras_list):
        if cam_tester.do_setup(cameras_list[id]):
            cameras_path = os.path.join(g_v.PROJECT_PATH, common.CONFIG_DIR_PATH, common.CAMERAS_FILE)
            cfg_loader.save_cameras(cameras_list, cameras_path)
    else:
        print("bad id")


def main():
    update_ver()

    opt_parser = OptionParser(version=ver.V_FULL)
    set_options(opt_parser)

    (opts, args) = opt_parser.parse_args()

    setup_options(opts)

    g_v.PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))

    init_logging(common.SOLUTION, g_v.VERBOSE, g_v.LOGGING)

    config_path = os.path.join(g_v.PROJECT_PATH, common.CONFIG_DIR_PATH)
    if not os.path.exists(config_path):
        logger.error("Config's dir is not exist {:s}".format(config_path))
        true_exit()

    out_path = os.path.join(g_v.PROJECT_PATH, common.OUT_DIR_PATH)
    common.make_dir(out_path)

    if opts.setup and not opts.show:
        if args:
            id = -1
            try:
                id = int(args[0])
                try_setup_cam(id)
            except ValueError:
                logger.error("bad args")
    elif opts.show and not opts.setup:
        show_cameras()
    else:
        start_work()

    true_exit()


if __name__ == '__main__':
    main()

