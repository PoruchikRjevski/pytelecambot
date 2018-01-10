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
        cmn.make_dir(self.__path_d)

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

    @staticmethod
    def __resize_frame(frame, p_w, p_h):
        h, w, _ = frame.shape

        if h > p_h and w > p_w:
            frame = cv2.resize(frame, (p_w, p_h))

        return frame

    @staticmethod
    def mirroring_img(frame):
        return cv2.flip(frame, 90)

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
                    (10, frame.shape[0] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    LAST_F_SIZE,
                    LAST_F_TXT_CLR,
                    cv2.LINE_4)

        return frame

    def __init_cam(self, out):
        cam_h = cv2.VideoCapture(int(self.__c_id))
        # res_x, res_y = cam_h.set_format(HI_W, HI_H)
        cam_h.set(cv2.CAP_PROP_FOURCC, MJPG_CODEC)
        cam_h.set(cv2.CAP_PROP_FRAME_WIDTH, HI_W)
        cam_h.set(cv2.CAP_PROP_FRAME_HEIGHT, HI_H)
        # cam_h.set(cv2.CAP_PROP_FPS, 30)
        fps = cam_h.get(cv2.CAP_PROP_FPS)
        real_w = cam_h.get(cv2.CAP_PROP_FRAME_WIDTH)
        real_h = cam_h.get(cv2.CAP_PROP_FRAME_HEIGHT)

        out.put_nowait(cmn.Alert(cmn.T_SYS_NOW_INFO,
                                 "CAM {:s}. {:s}x{:s} with FPS {:s}".format(str(self.__c_id),
                                                                            str(real_w),
                                                                            str(real_h),
                                                                            str(fps))))

        return cam_h, fps

    def __deinit_cam(self, cam):
        cam.release()

    @staticmethod
    def __get_current_timestamps():
        current_time = datetime.datetime.now()
        frame_ts = current_time.strftime(cmn.TIMESTAMP_FRAME_TEMPLATE)
        path_ts = current_time.strftime(cmn.TIMESTAMP_PATH_TEMPLATE)

        return frame_ts, path_ts

    def __send_now_photo(self, now_frame_q, out, ts_frame, ts_path, frame_ts):
        now_file_path = self.__write_frame_to_file(frame_ts, ts_path, SUFF_NOW)

        who_ask_list = []
        while not now_frame_q.empty():
            who_ask_list.append(str(now_frame_q.get_nowait()))

        if who_ask_list:
            out.put_nowait(cmn.Alert(cmn.T_CAM_NOW_PHOTO,
                                     cmn.NOW_ALERT.format(str(self.__c_id),
                                                          self.__c_name,
                                                          ts_frame),
                                     now_file_path,
                                     self.__c_name,
                                     who_ask_list))

    def __open_videowriter(self, file_mv_path, fps, timestamp, suffix):
        path = file_mv_path.replace(".jpg", "_{:s}.mp4".format(suffix))
        handler = cv2.VideoWriter(path,
                                  cv2.VideoWriter_fourcc(*'X264'),
                                  # cv2.VideoWriter_fourcc(*'MJPG'),
                                  fps,
                                  (LO_W, LO_H))

        return handler, path, timestamp

    def __close_videowriter(self, handler, path, out, timestamp, length):
        handler.release()
        handler = None
        out.put_nowait(cmn.Alert(cmn.T_CAM_MOVE_MP4,
                                 cmn.MOVE_ALERT.format(str(self.__c_id),
                                                       self.__c_name,
                                                       "{:s}({:s} s.)".format(timestamp,
                                                                              length)),
                                 path,
                                 self.__c_name))

    def __do_work_proc_ex(self, working_f, md_f, now_frame_q, out):
        cam, fps = self.__init_cam(out)

        real_timeout = 1 / fps
        real_timeout_shift = real_timeout / 2
        observing_timeout = 3 / fps
        start_timeout = 3

        prev_frame_detect = None

        print("real tmt: {:s}".format(str(real_timeout)))

        t_rec = time.time()
        t_detect = t_rec

        while working_f.value and cam.isOpened():
            t_start_loop = time.time()

            t_rec_temp = t_start_loop - t_rec
            if t_rec_temp >= real_timeout:
                t_rec = t_rec_temp

                ret, frame = cam.read()

                if not ret:
                    time.sleep(real_timeout_shift)
                    continue

                frame_for_detect = Camera.__resize_frame(frame, PREV_W, PREV_H)

                if md_f.value:
                    t_detec_temp = t_start_loop - t_detect
                    if t_detec_temp >= observing_timeout and prev_frame_detect is not None:
                        t_detect = t_detec_temp

                        is_detected, contoured_frame = self.__is_differed(prev_frame_detect, frame_for_detect)

                        # if is_detected:

                prev_frame_detect = frame_for_detect
            else:
                time.sleep(real_timeout_shift)

        self.__deinit_cam(cam)
        self.state = False

    def __do_work_proc(self, working_f, md_f, now_frame_q, out):
        cam, fps = self.__init_cam(out)

        real_timeout = 1/fps
        observing_timeout = 1/15
        max_pre_buffer_size = VIDEO_REC_TIME_PRE * fps
        max_full_buffer_size = VIDEO_REC_TIME_FULL * fps
        max_size_of_file = 30 * fps

        t_rec = time.time()
        t_timelapse = t_rec
        t_detect = t_rec

        ts_frame = ""
        ts_path = ""

        last_frame = None

        preview_handler = None
        preview_path = ""
        preview_ts = ""
        pre_buffer = queue.deque()

        recording = False
        part_frames = 0
        file_frames = 0
        detected_in_last_part = False
        dilp_path = ""
        dilp_ts = ""
        frame_detect_write = None

        # test timings
        t_test = t_rec
        frames = 0
        av_loop_time = 0

        while working_f.value and cam.isOpened():
            t_start_loop = time.time()

            t_rec_temp = t_start_loop - t_rec
            if t_rec_temp >= real_timeout:
                t_rec = t_rec_temp

                # r_t = time.time()
                ret, frame = cam.read()
                # r_t = time.time() - r_t
                # print("grab: {:s}, ms".format(str(r_t)))

                if not ret:
                    time.sleep(REC_TMT_SHIFT)
                    continue

                ts_frame, ts_path = Camera.__get_current_timestamps()

                frame_for_detect = Camera.__resize_frame(frame, LO_W, LO_H)
                frame_for_detect_ts = self.__add_frame_timestamp(frame_for_detect, ts_frame)

                frame_ts = self.__add_frame_timestamp(frame, ts_frame)

                frame_detect_write = frame_for_detect_ts

                # move detection
                if md_f.value:
                    t_detec_temp = t_start_loop - t_detect
                    if t_detec_temp >= observing_timeout and last_frame is not None:
                        t_detect = t_detec_temp

                        detected, frame_mv = self.__is_differed(last_frame, frame_for_detect)

                        if detected:
                            frame_detect_write = frame_mv
                            frame_mv_ts = self.__add_frame_timestamp(frame_mv, ts_frame)
                            file_mv_path = self.__write_frame_to_file(frame_mv_ts, ts_path, SUFF_MOVE)

                            if not recording:
                                out.put_nowait(cmn.Alert(cmn.T_CAM_MOVE_PHOTO,
                                                         cmn.MOVE_ALERT.format(str(self.__c_id),
                                                                               self.__c_name,
                                                                               ts_frame),
                                                         file_mv_path,
                                                         self.__c_name,
                                                         cmn.TO_ALL))

                                # open video file
                                preview_handler, preview_path, preview_ts = self.__open_videowriter(file_mv_path,
                                                                                                    fps,
                                                                                                    ts_frame,
                                                                                                    SUFF_PREV)

                                file_frames = len(pre_buffer)
                                # flush prebuffer
                                while pre_buffer:
                                    prev_frame = pre_buffer.popleft()
                                    preview_handler.write(prev_frame)

                                recording = True
                                part_frames = 0
                                detected_in_last_part = False
                            else:
                                if not detected_in_last_part:
                                    detected_in_last_part = True
                                    dilp_path = file_mv_path
                                    dilp_ts = ts_frame

                    # preview_rec_frame = self.__resize_frame(frame_detect_write, PREV_W, PREV_H)
                    preview_rec_frame = frame_detect_write

                    # check when file alredy max size
                    if recording:
                        if file_frames >= max_size_of_file and detected_in_last_part:
                            self.__close_videowriter(preview_handler,
                                                     preview_path,
                                                     out,
                                                     preview_ts,
                                                     str(round(file_frames / fps, 4)))
                            preview_handler, preview_path, preview_ts = self.__open_videowriter(dilp_path,
                                                                                                fps,
                                                                                                dilp_ts,
                                                                                                SUFF_PREV)

                            file_frames = 0
                            detected_in_last_part = False
                        elif file_frames >= max_size_of_file and not detected_in_last_part:
                            self.__close_videowriter(preview_handler,
                                                     preview_path,
                                                     out,
                                                     preview_ts,
                                                     str(round(file_frames / fps, 4)))

                            recording = False
                            file_frames = 0
                            part_frames = 0

                    # check when part of file was writed
                    if recording:
                        if part_frames >= max_full_buffer_size and detected_in_last_part:
                            part_frames = 0
                            detected_in_last_part = False
                        elif part_frames >= max_full_buffer_size and not detected_in_last_part:
                            self.__close_videowriter(preview_handler,
                                                     preview_path,
                                                     out,
                                                     preview_ts,
                                                     str(round(file_frames / fps, 4)))

                            recording = False
                            file_frames = 0
                            part_frames = 0

                    if recording:
                        preview_handler.write(preview_rec_frame)
                        part_frames += 1
                        file_frames += 1
                    else:
                        if len(pre_buffer) >= max_pre_buffer_size:
                            pre_buffer.popleft()
                        pre_buffer.append(preview_rec_frame)
                else:
                    t_detect = t_start_loop

                    if recording:
                        self.__close_videowriter(preview_handler,
                                                 preview_path,
                                                 out,
                                                 preview_ts,
                                                 str(round(file_frames / fps, 4)))

                        recording = False
                        file_frames = 0
                        part_frames = 0

                # send requested now photo
                if not now_frame_q.empty():
                    self.__send_now_photo(now_frame_q, out, ts_frame, ts_path, frame_ts)

                # write timelapse photos
                t_timelapse_cur = t_start_loop - t_timelapse
                if t_timelapse_cur >= TIMELAPSE_TMT:
                    t_timelapse = t_timelapse_cur
                    self.__write_frame_to_file(frame_ts, ts_path, SUFF_TIMELAPSE)

                last_frame = frame_for_detect
            else:
                time.sleep(REC_TMT_SHIFT)

            cur_t = time.time() - t_start_loop
            # 
            # t_test_c = time.time() - t_test
            # frames += 1
            # av_loop_time = (av_loop_time + cur_t)/2
            # if t_test_c >= 1:
            #     t_test = time.time()
            #     print("cam: {:s}. fps: {:s}. av_time: {:s}".format(str(self.__c_id),
            #                                                        str(frames),
            #                                                        str(av_loop_time)))
            #     frames = 0
            #     av_loop_time = 0


            # print("cycle: {:s}, ms".format(str(cur_t)))

        if recording:
            self.__close_videowriter(preview_handler,
                                     preview_path,
                                     out,
                                     preview_ts,
                                     str(round(file_frames / fps, 4)))

        self.__deinit_cam(cam)
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
    def accept_threshold(delta, t_min, t_max):
        return cv2.threshold(delta, t_min, t_max, cv2.THRESH_BINARY)[1]

    @staticmethod
    def get_dilate(thresh):
        return cv2.dilate(thresh, None, iterations=2)

    @staticmethod
    def check_contours(thresh, out, c_min, c_max):
        detected = False
        im, cnts, hir = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        true_cont = [c for c in cnts if c_min <= cv2.contourArea(c) <= c_max]

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
                    cv2.rectangle(out, (x, y), (x + w, y + h), (0, 255, 0), 1)

        return detected, out

    def __is_differed(self, last, cur):
        if last is None or cur is None:
            return False, None

        # some prepares
        frame_last = Camera.process_for_detect(last, DEF_GAUSS_BLUR_KERN_SIZE, DEF_GAUSS_BLUR_KERN_SIZE)
        frame_cur = Camera.process_for_detect(cur, DEF_GAUSS_BLUR_KERN_SIZE, DEF_GAUSS_BLUR_KERN_SIZE)

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
