import psutil
import time
import datetime
from multiprocessing import Value, Queue, Process
import logging
import socket

import common
from logger import init_logging, log_func_name

__all__ = ['MachineDaemon']

HLDNS_HOST_NAME         = "poruchik_rjevski.hldns.ru"

UPDATE_TMT              = 5
LOG_TMT                 = 3
UPDATE_TMT_HALF         = UPDATE_TMT/2

CPU_INTERVAL            = 0

CRIT_CPU_LOAD           = 80
CRIT_RAM_LOAD           = 90
CRIT_DISK_LOAD          = 99.5
CRIT_BAT_VOL            = 15


class MachineDaemon:
    def __init__(self):
        self.__alerts = None

        self.__working_f = Value("i", 1)
        self.__working_f.value = False

        self.__now_status_f = Value("i", 1)
        self.__now_status_f.value = False

    @staticmethod
    def __get_cpu_load():
        return psutil.cpu_percent(CPU_INTERVAL)

    @staticmethod
    def __get_all_cpus_load():
        return psutil.cpu_percent(CPU_INTERVAL, percpu=True)

    @staticmethod
    def __get_mem_load():
        return psutil.virtual_memory()[2]

    @staticmethod
    def __get_loads():
        do_alert = False

        # cpu load
        cpu_load = MachineDaemon.__get_cpu_load()
        cpu_load_txt = "CPU: {:s}%".format(str(cpu_load))
        if cpu_load >= CRIT_CPU_LOAD:
            do_alert = True
            cpu_load_txt = "*{:s}*".format(cpu_load_txt)

        # ram load
        ram_load = MachineDaemon.__get_mem_load()
        ram_load_txt = "RAM: {:s}%".format(str(ram_load))
        if ram_load >= CRIT_RAM_LOAD:
            do_alert = True
            ram_load_txt = "*{:s}*".format(ram_load_txt)

        # compile
        msg = "{:s}\nLOAD:\n{:s}\n{:s}\n{:s}".format(common.MID_EDGE,
                                                     common.MID_EDGE,
                                                     cpu_load_txt,
                                                     ram_load_txt)

        return do_alert, msg

    @staticmethod
    def __get_temperatures():
        do_alert = False

        msg = "{:s}\nTEMP:\n{:s}".format(common.MID_EDGE,
                                         common.MID_EDGE)

        temps = psutil.sensors_temperatures()

        if temps is None:
            return do_alert, ""

        first = True

        for key, val_l in temps.items():
            if first:
                first = False
            else:
                msg = "{:s}\n{:s}".format(msg,
                                          common.SMALL_EDGE)

            for label, cur, hight, crit in val_l:
                msg = "{:s}\n{:s}: {:s}({:s})°C".format(msg,
                                                        str(label),
                                                        str(cur),
                                                        str(hight))

                if cur >= hight:
                    msg = "*{:s}*".format(msg)
                    do_alert = True

        return do_alert, msg

    @staticmethod
    def __get_disk_usage():
        do_alert = False

        msg = "{:s}\nHDD:\n{:s}".format(common.MID_EDGE,
                                        common.MID_EDGE)

        disk_usage = psutil.disk_usage('/')

        if disk_usage is None:
            return do_alert, ""

        disk_usage_txt = "Main disk: {:s}%".format(str(disk_usage[3]))
        if disk_usage[3] >= CRIT_DISK_LOAD:
            disk_usage_txt = "*{:s}*".format(disk_usage_txt)
            do_alert = True

        msg = "{:s}\n{:s}".format(msg,
                                  disk_usage_txt)

        return do_alert, msg

    @staticmethod
    def __get_battery_info():
        do_alert = False

        msg = "{:s}\nBATTERY:\n{:s}".format(common.MID_EDGE,
                                        common.MID_EDGE)

        bat_info = psutil.sensors_battery()

        if bat_info is None:
            return do_alert, ""

        perc, t_left, plugg = bat_info

        if perc <= CRIT_BAT_VOL and not plugg:
            do_alert = True

        msg = "{:s}\nVolume: {:s}%".format(msg,
                                           str(perc))
        msg = "{:s}\nTime left: {:s}%".format(msg,
                                              str(t_left/3600))
        msg = "{:s}\nAC plugged: {:s}%".format(msg,
                                               str(plugg))

        if do_alert:
            msg = "*{:s}*".format(msg)

        return do_alert, msg

    @staticmethod
    def __get_ip_by_hldns():
        msg = ""

        ip_addr = socket.gethostbyname(HLDNS_HOST_NAME)

        if ip_addr:
            msg = "{:s}\nIP: {:s}\n{:s}".format(common.MID_EDGE,
                                                str(ip_addr),
                                                common.MID_EDGE)

        return False, msg

    @staticmethod
    def __update_system_status_info(do_alert):
        time_stamp = datetime.datetime.now().strftime(common.TIMESTAMP_FRAME_TEMPLATE)

        load_alert, load_msg = MachineDaemon.__get_loads()
        msg = "{:s}\nSystem status:\n{:s}\n{:s}\n{:s}".format(common.BIG_EDGE,
                                                              time_stamp,
                                                              common.BIG_EDGE,
                                                              load_msg)

        temp_alert, temp_msg = MachineDaemon.__get_temperatures()
        msg = "{:s}\n{:s}\n{:s}".format(msg,
                                        common.MID_EDGE,
                                        temp_msg)

        disk_alert, disk_msg = MachineDaemon.__get_disk_usage()
        msg = "{:s}\n{:s}".format(msg,
                                  disk_msg)

        bat_alert, bat_msg = MachineDaemon.__get_battery_info()
        msg = "{:s}\n{:s}".format(msg,
                                  bat_msg)

        _, ip_msg = MachineDaemon.__get_ip_by_hldns()
        msg = "{:s}\n{:s}".format(msg,
                                  ip_msg)

        msg = "{:s}\n{:s}".format(msg,
                                  common.BIG_EDGE)

        return (load_alert or temp_alert or disk_alert or bat_alert), msg

    def __main_loop(self, work_f, now_stat_f, alerts_q):
        cur_t = time.time()
        cur_t_tmp = 0
        log_t = time.time()
        log_t_tmp = 0

        cur_status = ""
        do_alert = False

        logger = init_logging("MachineDaemon", False, True)

        while work_f.value:
            if (now_stat_f.value or do_alert) and cur_status is not "":
                alerts_q.put_nowait(common.Alert(common.T_SYS_NOW_INFO,
                                                 cur_status))

                now_stat_f.value = False
                do_alert = False

            # log system status
            log_t_tmp = time.time() - log_t
            if log_t_tmp >= LOG_TMT:
                if cur_status is not "":
                    logger.info("\n{:s}".format(cur_status))
                log_t = time.time()

            # update system status
            cur_t_tmp = time.time() - cur_t
            if cur_t_tmp >= UPDATE_TMT:
                do_alert, cur_status = MachineDaemon.__update_system_status_info(do_alert)

                cur_t = time.time()
            else:
                time.sleep(UPDATE_TMT_HALF)

    def set_alerts(self, alerts):
        self.__alerts = alerts

    def get_now_status(self):
        self.__now_status_f.value = True

    def start_work(self):
        self.__working_f.value = True
        self.__proc_worker = Process(target=self.__main_loop,
                                     args=(self.__working_f,
                                           self.__now_status_f,
                                           self.__alerts, ))
        self.__proc_worker.start()

    def stop_work(self):
        self.__working_f.value = False
