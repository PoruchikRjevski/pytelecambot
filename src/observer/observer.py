import os
import time
import datetime

import numpy as np
import cv2

import config as cfg
from time_checker import *

from observer.obs_defs import *

__all__ = ['Observer']

class Observer:
    def __init__(self):
        self.__camera_id = 0
        self.__camera = None
        self.__last_frame = None
        self.__stop_f = False

        self.__capt_last_time = None

        date = datetime.date.today().__str__()
        self.__cur_dir = os.path.join(os.getcwd(), cfg.OUT_P, date)
        self.__check_dir(self.__cur_dir)

    def __check_dir(self, dir):
        if not os.path.exists(dir):
            os.mkdir(dir)

    def is_camera(func):
        def wrapped(s, *args, **kwargs):
            if not s.__camera is None:
                return func(s, *args, **kwargs)
        return wrapped

    def __init_camera(self):
        self.__camera = cv2.VideoCapture(self.__camera_id)

    @is_camera
    def __deinit_camera(self):
        self.__camera.release()

    @is_camera
    def __get_frame(self):
        return self.__camera.read()

    def __filter_gray(self, frame):
        return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    def __compare_imgs(self, im_1, im_2):
        return cv2.subtract(im_1, im_2).any()

    def __main_loop(self):
        ret, frame = self.__get_frame()

        if ret:
            frame = self.__filter_gray(frame)

            if self.__last_frame is None:
                self.__last_frame = frame
            else:
                if self.__compare_imgs(frame, self.__last_frame):
                    print("same as")
                else:
                    print("they are diff")

        cv2.imwrite(cfg.FULL_P, frame)

        time.sleep(OBSERVING_TMT)

    def do_work(self):
        self.__init_camera()

        self.__capt_last_time = time.time()
        while not self.__stop_f:
            self.__main_loop()

        self.__deinit_camera()

    def do_work_test(self):
        t = start()

        im_1 = cv2.imread(os.path.join(os.getcwd(), cfg.LAST_D_P, "im_1.jpg"))
        im_2 = cv2.imread(os.path.join(os.getcwd(), cfg.LAST_D_P, "im_2.jpg"))
        # im_2 = self.__filter_gray(im_1)

        if self.__compare_imgs(im_1, im_2):
            print("a")
        else:
            print("b")

        stop(t)
        print(get_pass_time(t))

        # print(im_3)