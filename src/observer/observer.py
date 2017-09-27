import os
import time

import cv2

import config as cfg

from observer.obs_defs import *

__all__ = ['Observer']

class Observer:
    def __init__(self):
        self.__camera_id = 0
        self.__camera = None
        self.__last_frame = None

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

        del(self.__camera)

    @is_camera
    def __get_frame(self):
        ret, frame = self.__camera.read()

        return frame

    def __filter_gray(self, frame):
        return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    def __main_loop(self):
        frame = self.__get_frame

        frame = self.__filter_gray(frame)

        cv2.imWrite(os.path.join(os.getcwd(), cfg.LAST_D_P, cfg.LAST_F),
                    frame)

        time.sleep(OBSERVING_TMT)

    def do_work(self):
        self.__init_camera()

        self.__main_loop()