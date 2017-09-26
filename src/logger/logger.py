import datetime
import inspect
import os
import threading
from collections import OrderedDict

from logger import log_def as l_d

__all__ = ['log_init', 'out_log', 'out_err', 'log_out_deffered', 'log_set_mt', 'log_set_q']

threads_list = []
threads_list_f = []
threads_logs = OrderedDict()
threads_errs = OrderedDict()


def log_set_mt(mt):
    l_d.MULTITHREAD = mt


def log_set_q(q):
    l_d.QUIET = q


def check_main_dir():
    if not os.path.isdir(l_d.M_LOGS_D):
        os.mkdir(l_d.M_LOGS_D, 0o777)


def check_cur_dir():
    if not os.path.isdir(l_d.C_LOGS_D):
        os.mkdir(l_d.C_LOGS_D, 0o777)


def check_cur_file_size():
    if os.path.getsize(os.path.join(l_d.C_LOGS_D, l_d.LOG_F)) > l_d.MAX_FILE_SIZE:
        check_cur_file()


def check_cur_file():
    reinit_current_dir()

    l_d.CUR_F_TIME = "{:s}".format(datetime.datetime.now().time().__str__())

    l_d.LOG_F = "{:s}_{:s}".format(l_d.LOG_F_D,
                                   l_d.CUR_F_TIME)
    l_d.ERR_F = "{:s}_{:s}".format(l_d.ERR_F_D,
                                   l_d.CUR_F_TIME)

    open(os.path.join(l_d.C_LOGS_D, l_d.LOG_F), 'w')
    open(os.path.join(l_d.C_LOGS_D, l_d.ERR_F), 'w')


def reinit_current_dir():
    l_d.C_LOGS_D = os.path.join(l_d.M_LOGS_D, datetime.datetime.now().date().__str__())

    check_cur_dir()


def log_init(path):
    l_d.M_LOGS_D = path
    check_main_dir()

    check_cur_file()


def log_out_deffered():
    for pid in threads_list:
        if pid in threads_logs.keys():
            if threads_logs[pid]:
                out_msg(gen_log_msg("", l_d.LOG_F, 2), l_d.LOG_F)
                out_msg(gen_log_msg("PID: {:s}".format(pid), l_d.LOG_F, 2), l_d.LOG_F)
                for out in threads_logs[pid]:
                    out_msg(out, l_d.LOG_F)

        if pid in threads_errs.keys():
            if threads_errs[pid]:
                out_msg(gen_log_msg("", l_d.ERR_F, 2), l_d.ERR_F)
                out_msg(gen_log_msg("PID: {:s}".format(pid), l_d.ERR_F, 2), l_d.ERR_F)
                for out in threads_errs[pid]:
                    out_msg(out, l_d.ERR_F)


def write_msg(msg, file_name):
    with open(os.path.join(l_d.C_LOGS_D, file_name), 'a') as f:
        f.write(msg + "\n")


def out_msg(out, place):
    write_msg(out, place)
    show_msg(out)


def check_pid(pid):
    if pid not in threads_list:
        threads_list.append(pid)
        threads_logs[pid] = []
        threads_errs[pid] = []


def out_log(msg):
    pid = str(threading.get_ident())

    out = gen_log_msg(msg, l_d.LOG_F, 3)

    if l_d.MULTITHREAD:
        check_pid(pid)

        threads_logs[pid].append(out)
    else:
        out_msg(out, l_d.LOG_F)


def out_err(msg):
    pid = str(threading.get_ident())

    out = gen_log_msg(msg, l_d.ERR_F, 3)

    if l_d.MULTITHREAD:
        check_pid(pid)

        threads_errs[pid].append(out)
    else:
        out_msg(out, l_d.ERR_F)


def gen_log_msg(msg, type, level):
    (c_name, c_line) = get_caller_info(level)

    c_name += "()" + " " * (l_d.SYMB_CALLER_N - len(c_name))
    c_line = " " * (l_d.SYMB_C_LINE_N - len(c_line)) + c_line

    return "[{:s}] : [{:s}] : [{:s}] : [L: {:s}] : [{:s}] ".format(datetime.datetime.now().__str__(),
                                                                   type,
                                                                   c_name,
                                                                   c_line,
                                                                   msg)


def show_msg(msg):
    if not l_d.QUIET:
        print(msg)


def get_caller_info(level):
    stack = inspect.stack()

    if len(stack) < level:
        return ""

    parent_frame = stack[level][0]

    # get line number
    line_num = str(inspect.getframeinfo(parent_frame).lineno)

    full_name = "{:s}:{:s}"
    module_name = ""

    # get class or module name
    if 'self' in parent_frame.f_locals:
        module_name = parent_frame.f_locals['self'].__class__.__name__
    else:
        module = inspect.getmodule(parent_frame)
        if module:
            module_name = module.__name__

    full_name = full_name.format(module_name,
                                 parent_frame.f_code.co_name)

    return full_name, line_num


def main():
    print("do nothing from there")
    
if __name__ == "__main__":
    main()
