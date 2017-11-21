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

    def __process_img_rec(self, img):
        img = self.__decrease_img(img, LO_W, LO_H)

        return img

    def __compare_imgs(self, img_1, img_2):
        return cv2.subtract(img_1, img_2).any()

    def __write_frame(self, frame):
        frame = self.__add_timestamp(frame)

        self.__last_frame_p = os.path.join(self.__path_d, "{:s}.jpg".format(self.__time_stamp))

        cv2.imwrite(self.__last_frame_p, frame, [cv2.IMWRITE_JPEG_QUALITY, LAST_F_JPG_Q])

    def __add_to_buf(self, frame):
        if not self.__f_rec:
            if self.__rec_buff.__len__() > self.__pre_rec_buff_sz:
                self.__rec_buff.pop()
        else:
            if not self.__f_wr_mp4:
                if self.__rec_buff.__len__() >= self.__full_rec_buff_sz:
                    self.__f_wr_mp4 = True
                    s_t = time.time()
                    cp_buf = copy.copy(self.__rec_buff)
                    # todo detach to other process
                    # proc = multiprocessing.Process(target=self.__write_mp4())
                    # proc.start()
                    self.__write_mp4()

                    s_t = time.time() - s_t
                    out_log("detach writing videos t: {:s}".format(str(s_t)))

                    return
            else:
                return

        self.__rec_buff.append(self.__add_timestamp(frame))

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

    def __add_frame_to_pre_buf(self, frame, buff):
        if buff.__len__() >= PRE_REC_BUF_SZ:
            buff.get_nowait()

        buff.put_nowait(frame)

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


                # if recording:
                #     if rec_f.Value:
                #         rec_buf.put_nowait(frame_ts)
                #         rec_fr_cntr += 1
                #
                #         if rec_fr_cntr >= FULL_REC_BUF_SZ:
                #             rec_buf.put_nowait(None)
                #             rec_buf.put_nowait(mv_detected_ts)
                #             recording = False
                    # else:
                        # self.__add_frame_to_pre_buf(frame_ts, rec_buf)

                # if rec_fr_cntr >= FULL_REC_BUF_SZ:
                #     rec_buf.put_nowait()

                obs_t_c = cur_t - obs_t
                if obs_t_c >= OBSERVING_TMT:
                    obs_t = obs_t_c

                    # todo add selecting area for detect move

                    # if self.__check_moving(frame, last_frame):
                    #     pass
                        # rec_f.value = True
                        # recording = True
                        # mv_detected_ts = ts_p

                    # if not rec_f.value and not recording:
                    #     if last_frame is not None:
                    #         if self.__check_moving(frame, last_frame):
                    #             rec_f.value = True
                    #             recording = True
                    #             mv_detected_ts = ts_p

                    detected, frame_rs_mv = Camera.__is_differed(last_frame, frame_rs)
                    frame_ts_mv = self.__add_frame_timestamp(frame_rs_mv, ts_fr)

                    if detected:
                        file_d_mv = self.__write_frame_to_file(frame_ts_mv, ts_p, SUFF_TIMELAPSE)
                        out.put_nowait(cmn.Alert(cmn.T_CAM_MOVE_PHOTO,
                                                 cmn.MOVE_ALERT.format(str(self.__c_id),
                                                                       self.__c_name,
                                                                       ts_fr),
                                                 file_d_mv,
                                                 self.__c_name))

                frame_ts = self.__add_frame_timestamp(frame_rs, ts_fr)
                last_frame = frame_rs

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
    def __is_differed(last, cur):
        detected_diff = False

        # some prepares
        frame_last = Camera.__proc_for_detect(last)
        frame_cur = Camera.__proc_for_detect(cur)

        # get diff
        delta = cv2.absdiff(frame_last, frame_cur)
        # 25, 255
        thresh = cv2.threshold(delta, 5, 255, cv2.THRESH_BINARY)[1]
        thresh = cv2.dilate(thresh, None, iterations=1)
        im, cnts, hir = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for c in cnts:
            if cv2.contourArea(c) < 2000 or cv2.contourArea(c) > 30000:
                continue

            detected_diff = True
            (x, y, w, h) = cv2.boundingRect(c)
            cv2.rectangle(frame_cur, (x, y), (x + w, y + h), (0, 255, 0), 2)

        return detected_diff, frame_cur

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

    def __detect_move_test_proc(self):
        print("start move detect")
        last_f = cv2.imread(os.path.join(os.getcwd(), cmn.LAST_D_P, "img_6.jpg"))
        cur_f = cv2.imread(os.path.join(os.getcwd(), cmn.LAST_D_P, "img_7.jpg"))

        cur_t = time.time()

        last_f_pr = Camera.__proc_for_detect(last_f)
        cur_f_pr = Camera.__proc_for_detect(cur_f)

        delta = cv2.absdiff(last_f_pr, cur_f_pr)

        # 25, 255
        thresh = cv2.threshold(delta, 5, 255, cv2.THRESH_BINARY)[1]

        thresh = cv2.dilate(thresh, None, iterations=1)

        im, cnts, hir = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # todo need to add setting by admin contours range with callback inline menu

        for c in cnts:
            if cv2.contourArea(c) < 2000 or cv2.contourArea(c) > 30000:
                continue

            (x, y, w, h) = cv2.boundingRect(c)
            cv2.rectangle(cur_f, (x, y), (x + w, y + h), (0, 255, 0), 2)

        print("finish move detect, {:s}".format(str(time.time() - cur_t)))
        cv2.imwrite(os.path.join(os.getcwd(), cmn.LAST_D_P, "post.jpg"), cur_f, [cv2.IMWRITE_JPEG_QUALITY, LAST_F_JPG_Q])

    @staticmethod
    def __proc_for_detect(frame):
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        frame = cv2.GaussianBlur(frame, (21, 21), 0)

        return frame

    def __write_move_photo(self, frame):
        frame = self.__add_timestamp(frame)

        move_ph_p = os.path.join(self.__path_d, "{:s}_MOVE.jpg".format(self.__time_stamp))

        cv2.imwrite(move_ph_p, frame, [cv2.IMWRITE_JPEG_QUALITY, LAST_F_JPG_Q])

        self.__out_deq.append(cmn.Alert(cmn.T_CAM_MOVE_PHOTO,
                                        cmn.MOVE_ALERT.format(str(self.__c_id),
                                                                self.__c_name,
                                                                self.__time_stamp),
                                        move_ph_p))

    def __do_work_test(self):
        once = True
        obs_t = time.time()

        while self.__work_f:
            rec_t = time.time()
            frame = self.__get_test_frame()
            ret = True

            if ret:
                cur_t = time.time()
                self.__time_stamp = datetime.datetime.now().strftime('%y%m%d_%H%M%S')

                frame = self.__process_img(frame)

                # self.__add_to_buf(frame)

                if not self.__f_rec:
                    if (cur_t - obs_t) >= OBSERVING_TMT:
                        # if not self.__last_frame is None:
                        #     if self.__compare_imgs(frame, self.__last_frame):
                        #         self.__write_move_photo(frame)
                        #         self.__f_rec = True
                        #         self.__move_time_stamp = self.__time_stamp

                        # todo detach to other process
                        self.__write_frame(frame)
                        self.__last_frame = frame
                        obs_t = cur_t


            rec_t = time.time() - rec_t
            if rec_t < self.__frame_rec_half_tmt:
                time.sleep(self.__frame_rec_half_tmt - rec_t)
            else:
                print("bad: {:s}".format(str(rec_t)))

        self.state = False

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
        # self.__proc_test = Process(target=self.__detect_move_test_proc)
        # self.__proc_test.start()
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
