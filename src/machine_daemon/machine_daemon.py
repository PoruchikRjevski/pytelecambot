import psutil
import time
from multiprocessing import Value, Queue, Process

import common as cmn

__all__ = ['MachineDaemon']


UPDATE_TMT = 2
UPDATE_TMT_HALF = UPDATE_TMT/2


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

    def __get_system_status_info(self):
        msg = "System status"
        m_load_cpu = str(psutil.cpu_percent(0))
        m_load_mem = str(psutil.virtual_memory()[2])

        # get battery info
        m_bat_str = ""
        b_perc, b_plug = self.__get_battery_info()
        if not b_perc is None or not b_plug is None:
            m_bat_str = "{:s}%, {:s}".format(str(b_perc),
                                                  "Plugged" if b_plug else "Unplugged")

        # get common cpu temp
        m_cpu_temp = str(psutil.sensors_temperatures()['coretemp'][0][1])

        msg = "CPU load: {:s} \nCPU temp: {:s} \nMEM load: {:s} \nBat: {:s}".format(m_load_cpu,
                                                                                    m_cpu_temp,
                                                                                    m_load_mem,
                                                                                    m_bat_str)

        return msg

    def __main_loop(self, work_f, now_stat_f, alerts_q):
        while work_f.value:
            cur_t = time.time()
            if now_stat_f.value:
                alerts_q.put_nowait(cmn.Alert(cmn.T_SYS_NOW_INFO,
                                              self.__get_system_status_info()))
                # todo do get system info
                now_stat_f.value = False

            cur_t = time.time() - cur_t

            if cur_t < UPDATE_TMT_HALF:
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