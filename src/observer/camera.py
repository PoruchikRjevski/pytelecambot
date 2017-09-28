import os
import time
import datetime
import threading
import queue

import common as cmn
from observer.cam_defs import *

import numpy as np
import cv2

class Camera:
    def __init__(self, c_id, c_name, out_d, work_f=True):
        self.__c_id = c_id
        self.__c_name = c_name
        self.__work_f = work_f

        self.__last_frame = None
        self.__last_frame_p = ""

        self.__handle_cam = None
        self.__video_writer = None

        self.__alert_deq = queue.deque()

        self.__thread = threading.Thread(target=self.__do_work_test)

        self.__path_d = os.path.join(out_d, "{:s}_{:s}".format(str(c_id),
                                                               c_name))

        cmn.make_dir(self.__path_d)

    def __init_camera(self):
        self.__handle_cam = cv2.VideoCapture(self.__c_id)

    def __get_frame(self):
        return self.__handle_cam.read()

    def __get_frame_test(self):
        return cv2.imread(os.path.join(os.getcwd(), cmn.LAST_D_P, "im_{:s}.jpg".format(str(self.__c_id))))

    def __accept_gray_filter(self, frame):
        return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    def __add_timestamp(self, frame):
        cv2.putText(frame,
                    "{:s}_{:s} {:s}".format(str(self.__c_id),
                                                   self.__c_name,
                                                   self.__time_stamp),
                    LAST_F_TXT_POS,
                    cv2.FONT_HERSHEY_SIMPLEX,
                    LAST_F_SIZE,
                    LAST_F_TXT_CLR,
                    1)

        return frame

    def __decrease_img(self, frame):
        h, w, _ = frame.shape

        if h > FRAME_H and w > FRAME_W:
            frame = cv2.resize(frame, (FRAME_W, FRAME_H))

        return frame

    def __process_img(self, img):
        img = self.__decrease_img(img)

        img = self.__accept_gray_filter(img)

        img = self.__add_timestamp(img)

        return img

    def __compare_imgs(self, img_1, img_2):
        return cv2.subtract(img_1, img_2).any()

    def __write_frame(self, frame):
        self.__last_frame_p = os.path.join(self.__path_d, "{:s}.jpg".format(self.__time_stamp))

        cv2.imwrite(self.__last_frame_p, frame, [cv2.IMWRITE_JPEG_QUALITY, LAST_F_JPG_Q])

    def __write_video(self):
        file_p = os.path.join(self.__path_d, "{:s}.avi".format(self.__time_stamp))
        self.__video_writer = cv2.VideoWriter(file_p,
                                              -1,
                                              VIDEO_REC_FPS,
                                              (FRAME_W, FRAME_H))

        frames = VIDEO_REC_FPS * VIDEO_REC_TIME

        start_t = time.time()
        while frames != 0:
            ret, frame = self.__get_frame()

            if ret:
                frame = self.__process_img(frame)

                self.__video_writer.write(frame)

            stop_t = time.time() - start_t

            if stop_t < VIDEO_REC_TMT:
                time.sleep(VIDEO_REC_TMT - stop_t)

            frames -= 1

        self.__video_writer.release()


    def __deinit_camera(self):
        self.__handle_cam.release()

    def __do_work(self):
        self.__init_camera()

        while self.__work_f:
            ret, frame = self.__get_frame()

            if not ret:
                continue

            self.__time_stamp = datetime.datetime.now().__str__()

            frame = self.__process_img(frame)

            self.__write_frame(frame)

            if not self.__last_frame is None:
                if self.__compare_imgs(frame, self.__last_frame):
                    self.__write_video()
                    self.__alert_deq.append(cmn.Alert(cmn.T_CAM_MOVE,
                                                      cmn.MOVE_ALERT.format(str(self.__c_id),
                                                                            self.__c_name,
                                                                            self.__time_stamp),
                                                      self.__last_frame_p))

            self.__last_frame = frame

        self.__deinit_camera()

        self.state = False

    def __do_work_test(self):
        once = True

        while self.__work_f:
            frame = self.__get_frame_test()

            self.__time_stamp = datetime.datetime.now().__str__()

            frame = self.__process_img(frame)

            self.__last_frame = frame

            self.__write_frame(frame)

            if once:
                self.__alert_deq.append(cmn.Alert(cmn.T_CAM_MOVE,
                                                  cmn.MOVE_ALERT.format(str(self.__c_id),
                                                                        self.__c_name,
                                                                        self.__time_stamp),
                                                  self.__last_frame_p))
                once = False
            else:
                time.sleep(OBSERVING_TMT)

    def set_alert_deq(self, a_deq):
        self.__alert_deq = a_deq

    @property
    def cam_id(self):
        return self.__c_id

    @property
    def cam_name(self):
        return self.__c_name

    @property
    def state(self):
        return self.__work_f

    @state.setter
    def state(self, state):
        if state == self.__work_f:
            return False

        self.__work_f = state

        if state:
            self.__alert_deq.append(cmn.Alert(cmn.T_CAM_SW, cmn.CAM_STARTED.format(self.__c_name,
                                                                                   str(state))))
            self.__thread.start()
            al_msg = cmn.CAM_STARTED.format(self.__c_name,
                                            str(state))
        else:
            self.__thread.join()
            self.__alert_deq.append(cmn.Alert(cmn.T_CAM_SW, cmn.CAM_STOPPED.format(self.__c_name,
                                                                                   str(state))))

        return True

    @property
    def last_frame(self):
        return self.__last_frame_p
