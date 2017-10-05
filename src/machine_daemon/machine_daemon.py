import psutil
from multiprocessing import Value, Queue, Process

__all__ = ['MachineDaemon']


UPDATE_TMT = 1


class MachineDaemon:
    def __init__(self):
        self.__alerts = None

        self.__working_f = Value("i", 1)
        self.__working_f.value = False

    def set_alerts(self, alerts):
        self.__alerts = alerts

    def __main_loop(self, work_f):
        while work_f.value:
            pass

    def start_work(self):
        self.__working_f.value = True
        self.__proc_worker = Process(target=self.__main_loop,
                                     args=(self.__working_f, ))
        self.__proc_worker.start()

    def stop_work(self):
        self.__working_f.value = False