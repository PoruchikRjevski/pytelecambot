import psutil
import time
import datetime
from multiprocessing import Value, Queue, Process

import common as cmn

__all__ = ['MachineDaemon']


UPDATE_TMT = 2
UPDATE_TMT_HALF = UPDATE_TMT/2

CPU_INTERVAL = 0

CRIT_CPU_LOAD = 15
CRIT_CPU_TEMP = 50
CRIT_MEM_LOAD = 50


class MachineDaemon:
    def __init__(self):
        self.__alerts = None

        self.__working_f = Value("i", 1)
        self.__working_f.value = False

        self.__now_status_f = Value("i", 1)
        self.__now_status_f.value = False

    def __get_battery_info(self):
        m_bat = psutil.sensors_battery()
        if not m_bat is None:
            return m_bat[0], m_bat[2]

        return None, None

    def __get_cpu_load(self):
        return psutil.cpu_percent(CPU_INTERVAL)

    def __get_cpu_mid_temp(self):
        return psutil.sensors_temperatures()['coretemp'][0][1]

    def __get_mem_load(self):
        return psutil.virtual_memory()[2]

    def __get_system_status_info(self):
        msg = "System status"
        m_load_cpu = str(self.__get_cpu_load())
        m_load_mem = str(self.__get_mem_load())

        # get common cpu temp
        m_cpu_temp = str(self.__get_cpu_mid_temp())

        # get battery info
        m_bat_str = ""
        b_perc, b_plug = self.__get_battery_info()
        if not b_perc is None or not b_plug is None:
            m_bat_str = "{:s}%, {:s}".format(str(b_perc),
                                                  "Plugged" if b_plug else "Unplugged")

        msg = "CPU load: {:s} \nCPU temp: {:s} \nMEM load: {:s} \nBat: {:s}".format(m_load_cpu,
                                                                                    m_cpu_temp,
                                                                                    m_load_mem,
                                                                                    m_bat_str)

        return msg

    def __check_cpu_load(self):
        cur_cpu_load = self.__get_cpu_load()
        return "CPU load {:s} {:d}".format(str(cur_cpu_load),
                                                  CRIT_CPU_LOAD) if cur_cpu_load > CRIT_CPU_LOAD else ""

    def __check_cpu_temp(self):
        cur_cpu_temp = self.__get_cpu_mid_temp()
        return "CPU temp {:s} {:d}".format(str(cur_cpu_temp),
                                                  CRIT_CPU_TEMP) if cur_cpu_temp > CRIT_CPU_TEMP else ""

    def __check_mem_load(self):
        cur_mem_load = self.__get_mem_load()
        return "MEM load {:s} {:d}".format(str(cur_mem_load),
                                                  CRIT_MEM_LOAD) if cur_mem_load > CRIT_MEM_LOAD else ""

    def __do_check_system_status(self, alerts_q):
        msg = ""

        cpu_load_str = self.__check_cpu_load()
        cpu_temp_str = self.__check_cpu_temp()
        mem_load_str = self.__check_mem_load()

        msgs_list = [cpu_load_str, cpu_temp_str, mem_load_str]

        msgs_list = [msg for msg in msgs_list if msg]

        if msgs_list:
            timestamp = datetime.datetime.now()
            ts_fr = timestamp.strftime(cmn.TIMESTAMP_FRAME_STR)

            msg = "\n".join(msgs_list)
            msg = "EXCEED at {:s}\n{:s}".format(ts_fr,
                                                msg)

            alerts_q.put_nowait(cmn.Alert(cmn.T_SYS_ALERT,
                                          msg))


    def __main_loop(self, work_f, now_stat_f, alerts_q):
        cur_t = time.time()
        cur_t_tmp = 0

        while work_f.value:
            if now_stat_f.value:
                alerts_q.put_nowait(cmn.Alert(cmn.T_SYS_NOW_INFO,
                                              self.__get_system_status_info()))
                # todo do get system info
                now_stat_f.value = False

            cur_t_tmp = time.time() - cur_t

            if cur_t_tmp >= UPDATE_TMT:
                self.__do_check_system_status(alerts_q)

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