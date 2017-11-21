import os
import time
import datetime
import threading
from multiprocessing import Value, Queue, Process
import queue
import copy

import common as cmn
from logger import *
from observer.cam_defs import *
from git_man import cmd_executor as cmd_ex

import numpy as np
import cv2


class Camera:
    def __init__(self, c_id, c_name, out_d, work_f=True, m_detect=False, cont_min=0, cont_max=100):
        self.__c_id = c_id
        self.__c_name = c_name
        self.__autostart = work_f
        self.__motion_detection = m_detect
        self.__contours_min = cont_min
        self.__contours_max = cont_max

        self.__work_f = work_f

        self.__last_frame = None
        self.__last_frame_p = ""

        # self.__handle_cam = None
        self.__video_writer = None

        self.__out_deq = Queue()

        self.__path_d = os.path.join(out_d, "{:s}_{:s}".format(str(c_id),
                                                               c_name))

        self.__pre_rec_buff_sz = VIDEO_REC_TIME_PRE * VIDEO_REC_FPS
        self.__full_rec_buff_sz = VIDEO_REC_TIME_FULL * VIDEO_REC_FPS
        # self.__rec_buff = queue.deque()
        self.__frame_rec_half_tmt = 1 / 2 * VIDEO_REC_FPS

        self.__f_rec = False
        self.__f_wr_mp4 = False

        self.__test = True

        self.__procs = []

        self.__move_time_stamp = ""

        cmn.make_dir(self.__path_d)

        # --
        self.__working_f = Value("i", 1)
        self.__working_f.value = False
        self.__now_frame_q = Queue()
        self.__rec_buff_q = Queue()
        self.__rec_f = Value("i", 1)
        self.__rec_f.value = False
        self.__motion_detect_f = Value("i", 1)
        self.__motion_detect_f.value = m_detect

        # self.__now_frame_f = Value("i", 1)
        # self.__now_frame_f.value = False

    def __get_test_frame(self):
        if self.__test:
            self.__test = False
            return cv2.imread(os.path.join(os.getcwd(), cmn.LAST_D_P, "img_0.jpg"))
        else:
            self.__test = True
            return cv2.imread(os.path.join(os.getcwd(), cmn.LAST_D_P, "img_1.jpg"))

    def __accept_gray_filter(self, frame):
        return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    def __add_timestamp(self, frame):
        cv2.putText(frame,
                    "{:s}_{:s} {:s}".format(str(self.__c_id),
                                                   self.__c_name,
                                                   self.__time_stamp),
                    (10, frame.shape[0] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    LAST_F_SIZE,
                    LAST_F_TXT_CLR,
                    1)

        return frame

    def __decrease_img(self, frame, p_w, p_h):
        h, w, _ = frame.shape

        if h > p_h and w > p_w:
            frame = cv2.resize(frame, (p_w, p_h))

        return frame

    def __mirroring_img(self, frame):
        return cv2.flip(frame, 0)

    def __process_img(self, img):
        img = self.__decrease_img(img, HI_W, HI_H)

        # img = self.__mirroring_img(img)

        # img = self.__accept_gray_filter(img)

        return img

    def __free_rec_buff(self, dir_p):
        i_f = 0
        while self.__rec_buff:
            file_t_p = os.path.join(dir_p, "frame_{:s}.jpg".format(str(i_f)))
            cv2.imwrite(file_t_p, self.__rec_buff.pop(), [cv2.IMWRITE_JPEG_QUALITY, LAST_F_JPG_Q])
            i_f += 1

    def __write_mp4(self):
        dir_p = os.path.join(self.__path_d, "temp/")
        cmn.make_dir(dir_p)
        mp4_hi_f = os.path.join(self.__path_d, "{:s}_hi.mp4".format(self.__move_time_stamp))
        mp4_lo_f = os.path.join(self.__path_d, "{:s}_lo.mp4".format(self.__move_time_stamp))

        # write .jpg's to temp
        start_t = time.time()
        size = self.__rec_buff.__len__()

        self.__free_rec_buff(dir_p)

        start_t = time.time() - start_t
        out_log("writed {:s} frames for {:s}".format(str(size),
                                                     str(start_t)))

        # create videos
        start_t = time.time()
        cmd_ex.run_cmd(CMD_FFMPEG_CONVERT.format(dir_p,
                                                 A_SCALE.format(str(LO_W), str(LO_H)),
                                                 mp4_lo_f))

        # send alerts
        self.__out_deq.append(cmn.Alert(cmn.T_CAM_MOVE_MP4,
                                        cmn.MOVE_ALERT.format(str(self.__c_id),
                                                                self.__c_name,
                                                                self.__time_stamp),
                                        mp4_lo_f))

        cmd_ex.run_cmd(CMD_FFMPEG_CONVERT.format(dir_p,
                                                 "",
                                                 mp4_hi_f))
        start_t = time.time() - start_t
        out_log("created videos for {:s}".format(str(start_t)))


        # remove temp
        cmn.rem_dir(dir_p)

        # send alerts
        self.__out_deq.append(cmn.Alert(cmn.T_CAM_MOVE_MP4,
                                        cmn.MOVE_ALERT.format(str(self.__c_id),
                                                                self.__c_name,
                                                                self.__time_stamp),
                                        mp4_lo_f))

        self.__f_rec = False
        self.__f_wr_mp4 = False

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
                    (10, frame.shape[0] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    LAST_F_SIZE,
                    LAST_F_TXT_CLR,
                    1)

        return frame

    def __resize_frame(self, frame, to_w, to_h):
        img = self.__decrease_img(frame, to_w, to_h)

        return img

    def __check_moving(self, cur_fr, l_fr):
        pass

    def __do_work_proc(self, working_f, md_f, now_frame_q, out, rec_f, rec_buf):
        cam_h = cv2.VideoCapture(int(self.__c_id))
        # res_x, res_y = cam_h.set_format(HI_W, HI_H)
        cam_h.set(3, HI_W)
        cam_h.set(4, HI_H)
        cam_h.set(cv2.CAP_PROP_AUTOFOCUS, 1)
        # cam_work = True

        rec_fr_cntr = 0
        recording = False
        mv_detected_ts = None

        rec_t = time.time()
        obs_t = rec_t
        wrt_t = rec_t
        file_p = ""

        check_t = 0
        timestamp = ''
        last_frame = None
        last_frame_p = ''
        frame_ts = last_frame

        # while working_f.value and cam_work:
        while working_f.value and cam_h.isOpened():
            cur_t = time.time()
            # check_t = cur_t
            rec_t_c = cur_t - rec_t

            if rec_t_c >= REC_TMT:
                rec_t = rec_t_c
                ret, frame = cam_h.read()

                if not ret:
                    time.sleep(REC_TMT_SHIFT)
                    continue

                # process frame
                frame_rs = self.__resize_frame(frame, HI_W, HI_H)

                timestamp = datetime.datetime.now()
                ts_fr = timestamp.strftime(cmn.TIMESTAMP_FRAME_STR)
                ts_p = timestamp.strftime(cmn.TIMESTAMP_PATH_STR)

                obs_t_c = cur_t - obs_t
                if obs_t_c >= OBSERVING_TMT:
                    detected, frame_rs_mv = Camera.__is_differed(last_frame, frame_rs)

                    if detected:
                        frame_ts_mv = self.__add_frame_timestamp(frame_rs_mv, ts_fr)
                        file_d_mv = self.__write_frame_to_file(frame_ts_mv, ts_p, SUFF_TIMELAPSE)
                        out.put_nowait(cmn.Alert(cmn.T_CAM_MOVE_PHOTO,
                                                 cmn.MOVE_ALERT.format(str(self.__c_id),
                                                                       self.__c_name,
                                                                       ts_fr),
                                                 file_d_mv,
                                                 self.__c_name))

                    obs_t = obs_t_c

                last_frame = frame_rs
                frame_ts = self.__add_frame_timestamp(frame_rs, ts_fr)

                cur_wrt_t = time.time()
                if (time.time() - wrt_t) >= TIMELAPSE_TMT:
                    wrt_t = cur_wrt_t
                    file_p = self.__write_frame_to_file(frame_ts, ts_p, SUFF_TIMELAPSE)

                if now_frame_q.qsize() > 0:
                    while now_frame_q.qsize() > 0:
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

        self.state = False

    @staticmethod
    def get_thresh(delta, min, max):
        return cv2.threshold(delta, min, max, cv2.THRESH_BINARY)[1]

    @staticmethod
    def get_dilate(thresh):
        return cv2.dilate(thresh, None, iterations=1)

    @staticmethod
    def check_contours(thresh, out, min, max):
        detected = False
        im, cnts, hir = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for c in cnts:
            if cv2.contourArea(c) < min or cv2.contourArea(c) > max:
                continue

            detected = True
            (x, y, w, h) = cv2.boundingRect(c)
            cv2.rectangle(out, (x, y), (x + w, y + h), (0, 255, 0), 1)

        return detected, out

    @staticmethod
    def __is_differed(last, cur):
        if last is None or cur is None:
            return False, None

        # some prepares
        frame_last = Camera.proc_for_detect(last, 21, 21)
        frame_cur = Camera.proc_for_detect(cur, 21, 21)

        # get diff
        delta = cv2.absdiff(frame_last, frame_cur)
        # 25, 255
        # thresh = cv2.threshold(delta, 25, 255, cv2.THRESH_BINARY)[1]
        thresh = Camera.get_thresh(delta, 25, 255)
        # thresh = cv2.dilate(thresh, None, iterations=1)
        thresh = Camera.get_dilate(thresh)

        detected, cur = Camera.check_contours(thresh, cur, 2000, 40000)

        # im, cnts, hir = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        #
        # for c in cnts:
        #     if cv2.contourArea(c) < 3000:
        #         continue
        #
        #     detected_diff = True
        #     (x, y, w, h) = cv2.boundingRect(c)
        #     cv2.rectangle(cur, (x, y), (x + w, y + h), (0, 255, 0), 2)

        return detected, cur

    def __do_write_proc(self, working_f, rec_f, rec_buf):
        while working_f.value:
            if rec_f.value:
                while rec_buf.qsize() > 0:
                    frame = rec_buf.get_nowait()

                    if frame is None:
                        timestamp = rec_buf.get_nowait()
                        # todo finish writing
                        # exe ffmpeg
                        pass

                        rec_f.value = False

                        while not rec_buf.empty():
                            rec_buf.get()

                        continue

                    # write to temp file
                    pass
            else:
                time.sleep(1)

    @staticmethod
    def proc_for_detect(frame, kw, kh):
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        frame = cv2.GaussianBlur(frame, (kw, kh), 0)

        return frame

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
                                       self.__out_deq,
                                       self.__rec_f,
                                       self.__rec_buff_q,))
        self.__proc_rec = Process(target=self.__do_write_proc,
                                 args=(self.__working_f,
                                       self.__rec_f,
                                       self.__rec_buff_q,))

        self.__proc_rec.start()
        self.__proc_rx.start()

    def set_alert_deq(self, a_deq):
        self.__out_deq = a_deq

    @property
    def cam_id(self):
        return self.__c_id

    @property
    def cam_name(self):
        return self.__c_name

    @property
    def state(self):
        return self.__working_f.value

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
    def last_frame(self):
        return self.__last_frame_p

    def now_frame(self, who):
        self.__now_frame_q.put_nowait(who)
