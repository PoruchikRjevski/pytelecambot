import os
import time
import datetime
import threading
from multiprocessing import Value, Queue, Process
import queue
import copy
from operator import itemgetter

import common as cmn
from logger import *
from observer.cam_defs import *
from git_man import cmd_executor as cmd_ex

import numpy as np
import cv2


class Camera:
    def __init__(self, c_id, c_name,
                 out_d, work_f=True, m_detect=False,
                 cont_min=0, cont_max=100, thresh_min = 0, thresh_max = 100):
        self.__c_id = c_id
        self.__c_name = c_name
        self.__autostart = work_f
        self.__motion_detection = m_detect
        self.__contours_min = cont_min
        self.__contours_max = cont_max
        self.__thresh_min = thresh_min
        self.__thresh_max = thresh_max

        self.__out_deq = Queue()

        self.__path_d = os.path.join(out_d, "{:s}_{:s}".format(str(c_id),
                                                               c_name))

        self.__move_time_stamp = ""

        # multiprocessing variables
        self.__working_f = Value("i", 1)
        self.__working_f.value = False
        self.__now_frame_q = Queue()
        self.__motion_detect_f = Value("i", 1)
        self.__motion_detect_f.value = m_detect

    @property
    def cam_id(self):
        return self.__c_id

    @property
    def cam_name(self):
        return self.__c_name

    @property
    def state(self):
        return self.__working_f.value

    @property
    def cam_autostart(self):
        return self.__autostart

    @state.setter
    def state(self, state):
        if state != self.__working_f.value:
            self.__working_f.value = state

            msg_t = ""

            if state:
                self.__start_procs()
                msg_t = cmn.CAM_STARTED.format(self.__c_name,
                                               str(True))
            else:
                msg_t = cmn.CAM_STOPPED.format(self.__c_name,
                                               str(False))

            self.__out_deq.put_nowait(cmn.Alert(cmn.T_CAM_SW,
                                                msg_t,
                                                None,
                                                self.__c_name))

    @property
    def motion_detect(self):
        return self.__motion_detect_f.value

    @motion_detect.setter
    def motion_detect(self, state):
        if state != self.__motion_detect_f.value:
            self.__motion_detect_f.value = state

            msg_t = ""

            if state:
                msg_t = cmn.CAM_MD_STARTED.format(self.__c_name,
                                                  str(True))
            else:
                msg_t = cmn.CAM_MD_STOPPED.format(self.__c_name,
                                                  str(False))

            self.__out_deq.put_nowait(cmn.Alert(cmn.T_CAM_SW,
                                                msg_t,
                                                None,
                                                self.__c_name))

    @property
    def contours(self):
        return self.__contours_min, self.__contours_max

    @contours.setter
    def contours(self, conts):
        self.__contours_min, self.__contours_max = conts

    @property
    def threshold(self):
        return self.__thresh_min, self.__thresh_max

    @threshold.setter
    def threshold(self, threshes):
        self.__thresh_min, self.__thresh_max = threshes

    def __accept_gray_filter(self, frame):
        return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    def __resize_frame(self, frame, p_w, p_h):
        h, w, _ = frame.shape

        if h > p_h and w > p_w:
            frame = cv2.resize(frame, (p_w, p_h))

        return frame

    def __mirroring_img(self, frame):
        return cv2.flip(frame, 0)

    def __process_img(self, img):
        img = self.__resize_frame(img, HI_W, HI_H)

        # img = self.__mirroring_img(img)

        # img = self.__accept_gray_filter(img)

        return img

    def __write_frame_to_file(self, frame, ts_p, suffix):
        path = os.path.join(self.__path_d, "{:s}_{:s}.jpg".format(ts_p,
                                                                  suffix))

        cv2.imwrite(path, frame, [cv2.IMWRITE_JPEG_QUALITY, LAST_F_JPG_Q])

        return path

    def __add_frame_timestamp(self, frame, ts):
        cv2.putText(frame,
                    "{:s}_{:s} {:s}".format(str(self.__c_id),
                                            self.__c_name,
                                            ts),
                    (12, frame.shape[0] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    LAST_F_SIZE,
                    LAST_F_TXT_CLR,
                    1)

        return frame

    def __init_cam(self):
        cam_h = cv2.VideoCapture(int(self.__c_id))
        # res_x, res_y = cam_h.set_format(HI_W, HI_H)
        cam_h.set(3, HI_W)
        cam_h.set(4, HI_H)
        # cam_h.set(cv2.CAP_PROP_AUTOFOCUS, 0)
        print("CAM {:s} FPS {:s}".format(str(self.__c_id),
                                         str(cam_h.get(cv2.CAP_PROP_FPS))))

        return cam_h

    def __deinit_cam(self, cam):
        cam.release()

    def __do_work_proc(self, working_f, md_f, now_frame_q, out):
        cam_h = self.__init_cam()

        out_big = None
        out_small = None
        out_big = None
        pre_buf_small = queue.deque()
        pre_buf_big = queue.deque()

        recording = False
        recorded_frames = 0
        recorded_small = 0
        mv_detected_ts = None
        recorded_main_frame = FULL_REC_BUF_SZ

        detected_in_last_part = False

        rec_t = time.time()
        obs_t = rec_t
        wrt_t = rec_t
        file_p = ""

        check_t = 0
        timestamp = ''
        last_frame = None
        last_frame_p = ''
        frame_ts = last_frame
        file_d_mv_small = ""
        file_d_mv_big = ""

        # while working_f.value and cam_work:
        while working_f.value and cam_h.isOpened():
            cur_t = time.time()
            # check_t = cur_t
            rec_t_c = cur_t - rec_t

            if rec_t_c >= REC_TMT:
                rec_t = rec_t_c
                # get_f_t = time.time()
                ret, frame = cam_h.read()
                # get_f_t = time.time() - get_f_t
                # print("get frame t: {:f}".format(get_f_t))

                if not ret:
                    time.sleep(REC_TMT_SHIFT)
                    continue

                # process frame
                frame_rs = self.__resize_frame(frame, LO_W, LO_H)

                timestamp = datetime.datetime.now()
                ts_fr = timestamp.strftime(cmn.TIMESTAMP_FRAME_STR)
                ts_p = timestamp.strftime(cmn.TIMESTAMP_PATH_STR)
                frame_ts = self.__add_frame_timestamp(frame_rs, ts_fr)

                obs_t_c = cur_t - obs_t
                if obs_t_c >= OBSERVING_TMT:
                    # det_t = time.time()
                    detected, frame_rs_mv = self.__is_differed(last_frame, frame_rs)
                    # det_t = time.time() - det_t
                    # print("detect t: {:f}".format(det_t))

                    if detected:
                        detected_in_last_part = detected

                    if not recording:
                        if detected:
                            frame_ts_mv = self.__add_frame_timestamp(frame_rs_mv, ts_fr)
                            file_d_mv = self.__write_frame_to_file(frame_ts_mv, ts_p, SUFF_MOVE)
                            out.put_nowait(cmn.Alert(cmn.T_CAM_MOVE_PHOTO,
                                                     cmn.MOVE_ALERT.format(str(self.__c_id),
                                                                           self.__c_name,
                                                                           ts_fr),
                                                     file_d_mv,
                                                     self.__c_name))

                            file_d_mv_small = file_d_mv.replace(".jpg", "_small.mp4")
                            out_small = cv2.VideoWriter(file_d_mv_small,
                                                        cv2.VideoWriter_fourcc(*'H264'),
                                                        VIDEO_REC_FPS,
                                                        (PREV_W, PREV_H))
                            file_d_mv_big = file_d_mv.replace(".jpg", "_big.mp4")
                            out_big = cv2.VideoWriter(file_d_mv_big,
                                                      cv2.VideoWriter_fourcc(*'H264'),
                                                      VIDEO_REC_FPS,
                                                      (HI_W, HI_H))

                            while pre_buf_small:
                                out_small.write(pre_buf_small.popleft())

                            while pre_buf_big:
                                out_big.write(pre_buf_big.popleft())

                            recorded_main_frame = 0
                            recording = True

                    obs_t = obs_t_c

                if recording:
                    if recorded_main_frame >= FULL_REC_BUF_SZ:
                        if not detected_in_last_part:
                            out_small.release()
                            out_small = None
                            out_big.release()
                            out_big = None
                            out.put_nowait(cmn.Alert(cmn.T_CAM_MOVE_MP4,
                                                     cmn.MOVE_ALERT.format(str(self.__c_id),
                                                                           self.__c_name,
                                                                           ts_fr),
                                                     file_d_mv_small,
                                                     self.__c_name))

                            recording = False

                        recorded_main_frame = 0
                    else:
                        small_rec_frame = self.__resize_frame(frame_ts, PREV_W, PREV_H)
                        big_rec_frame = self.__resize_frame(frame_ts, HI_W, HI_H)

                        out_small.write(small_rec_frame)
                        out_big.write(big_rec_frame)

                        recorded_main_frame += 1
                else:
                    small_rec_frame = self.__resize_frame(frame_ts, PREV_W, PREV_H)
                    big_rec_frame = self.__resize_frame(frame_ts, HI_W, HI_H)

                    if len(pre_buf_small) >= PRE_REC_BUF_SZ:
                        pre_buf_small.popleft()
                        pre_buf_big.popleft()

                    pre_buf_small.append(small_rec_frame)
                    pre_buf_big.append(big_rec_frame)

                last_frame = frame_rs

                cur_wrt_t = time.time() - wrt_t
                if cur_wrt_t >= TIMELAPSE_TMT:
                    wrt_t = cur_wrt_t
                    file_p = self.__write_frame_to_file(frame_ts, ts_p, SUFF_TIMELAPSE)

                while not now_frame_q.empty():
                    file_p = self.__write_frame_to_file(frame_ts, ts_p, SUFF_NOW)
                    out.put_nowait(cmn.Alert(cmn.T_CAM_NOW_PHOTO,
                                             cmn.NOW_ALERT.format(str(self.__c_id),
                                                                  self.__c_name,
                                                                  ts_fr),
                                             file_p,
                                             self.__c_name,
                                             str(now_frame_q.get_nowait())))
            else:
                if rec_t_c <= REC_TMT_SHIFT:
                    time.sleep(REC_TMT_SHIFT)

            # loop_t = time.time() - cur_t
            # print("loop t: {:f}".format(loop_t))

        if recording and out_small is not None:
            recording = False
            out_small.release()
            out_small = None
            out.put_nowait(cmn.Alert(cmn.T_CAM_MOVE_MP4,
                                     cmn.MOVE_ALERT.format(str(self.__c_id),
                                                           self.__c_name,
                                                           ts_fr),
                                     file_d_mv_small,
                                     self.__c_name))

            out_big.release()
            out_big = None

        self.__deinit_cam(cam_h)
        self.state = False

    @staticmethod
    def process_denoise(frame):
        return cv2.fastNlMeansDenoisingColored(frame, None, 10, 10, 7, 21)

    @staticmethod
    def process_for_detect(frame, kw, kh):
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        frame = cv2.GaussianBlur(frame, (kw, kh), 0)

        return frame

    @staticmethod
    def accept_threshold(delta, min, max):
        return cv2.threshold(delta, min, max, cv2.THRESH_BINARY)[1]

    @staticmethod
    def get_dilate(thresh):
        return cv2.dilate(thresh, None, iterations=1)

    @staticmethod
    def check_contours(thresh, out, c_min, c_max):
        detected = False
        im, cnts, hir = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        true_cont = [c for c in cnts if cv2.contourArea(c) < c_min or cv2.contourArea(c) > c_max]

        if len(true_cont) > 0:
            detected = True

            if len(true_cont) > 1:
                coords = []
                for c in true_cont:
                    (x, y, w, h) = cv2.boundingRect(c)
                    coords.append((x, y, w, h))

                l_l = min(coords, key=lambda item: item[0])
                # l_l = max(coords, key=itemgetter(1))
                l_u = min(coords, key=lambda item: item[1])
                # l_u = max(coords, key=itemgetter(2))
                r_r = max(coords, key=lambda item: item[2])
                # r_r = max(coords, key=itemgetter(3))
                r_b = max(coords, key=lambda item: item[3])
                # r_b = max(coords, key=itemgetter(4))

                cv2.rectangle(out, (l_l[0], l_u[1]), (r_r[0] + r_r[2], r_b[1] + r_b[3]), (0, 255, 0), 2)
            else:
                for c in true_cont:
                    (x, y, w, h) = cv2.boundingRect(c)
                    cv2.rectangle(out, (x, y), (x + w, y + h), (0, 255, 0), 2)

        return detected, out

    def __is_differed(self, last, cur):
        if last is None or cur is None:
            return False, None

        # some prepares
        frame_last = Camera.process_for_detect(last, GAUSS_BLUR_KERN_SIZE, GAUSS_BLUR_KERN_SIZE)
        frame_cur = Camera.process_for_detect(cur, GAUSS_BLUR_KERN_SIZE, GAUSS_BLUR_KERN_SIZE)

        # get diff
        delta = cv2.absdiff(frame_last, frame_cur)
        thresh = Camera.accept_threshold(delta, self.__thresh_min, self.__thresh_max)
        thresh = Camera.get_dilate(thresh)

        # draw contours
        detected, cur = Camera.check_contours(thresh, cur, self.__contours_min, self.__contours_max)

        return detected, cur

    def autostart(self):
        if self.__autostart:
            self.__working_f.value = True
            self.__start_procs()
            self.__out_deq.put_nowait(cmn.Alert(cmn.T_CAM_SW,
                                                cmn.CAM_STARTED.format(self.__c_name,
                                                                       str(True)),
                                                None,
                                                None))

    def __start_procs(self):
        self.__proc_rx = Process(target=self.__do_work_proc,
                                 args=(self.__working_f,
                                       self.__motion_detect_f,
                                       self.__now_frame_q,
                                       self.__out_deq, ))
        self.__proc_rx.start()

    def set_alert_deq(self, a_deq):
        self.__out_deq = a_deq

    def now_frame(self, who):
        self.__now_frame_q.put_nowait(who)
