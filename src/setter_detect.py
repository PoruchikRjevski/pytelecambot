#!/usr/bin/python3

import os
import sys
import time
from multiprocessing import Value, Queue, Process

import cv2
import numpy as np

from observer import Camera
from observer.cam_defs import *

__all__ = ['do_setup']

# keys
KEY_RETURN = 13
KEY_ESC = 27

# windows
CONTROL = "Control"
DELTA = "Delta"
DILATE = "Dilate"

# trackbars
THRESH_MIN = "Thr min"
THRESH_MAX = "Thr max"

CONT_MIN = "Cntr min"
CONT_MAX = "Cntr max"

FOCUS_TB = "Focus"

thresh_min = Value("i", 25)
thresh_max = Value("i", 255)

cont_min = Value("i", 2000)
cont_max = Value("i", 30000)

working_f = Value("i", 1)
working_f.value = True

focus_v = Value("i", 0)


HEIGHT = 480
WIDTH = 640


def grabber_loop(cam_id, frames, working, t_min, t_max, c_min, c_max, focus):
    saved_focus = -1

    cam_h = cv2.VideoCapture(int(cam_id))

    rec_t = time.time()
    last_f = None

    while working.value and cam_h.isOpened():
        if focus.value != saved_focus:
            saved_focus = focus.value
            cam_h.set(cv2.CAP_PROP_FOCUS, saved_focus/100)

        cur_t = time.time()
        # check_t = cur_t
        rec_t_c = cur_t - rec_t

        if rec_t_c >= REC_TMT:
            rec_t = rec_t_c

            ret, frame = cam_h.read()
            if not ret:
                time.sleep(REC_TMT_SHIFT)
                continue

            cur = cv2.resize(frame, (WIDTH, HEIGHT))

            if last_f is not None:
                frame_last = Camera.process_for_detect(last_f, GAUSS_BLUR_KERN_SIZE, GAUSS_BLUR_KERN_SIZE)
                # frame_last = Camera.process_denoise(frame_last)
                frame_cur = Camera.process_for_detect(cur, GAUSS_BLUR_KERN_SIZE, GAUSS_BLUR_KERN_SIZE)
                # frame_cur = Camera.process_denoise(frame_cur)

                delta = cv2.absdiff(frame_last, frame_cur)

                thresh = Camera.accept_threshold(delta, t_min.value, t_max.value)

                dilate = Camera.get_dilate(thresh)

                detected, with_contours = Camera.check_contours(thresh, cur.copy(), c_min.value, c_max.value)

                frames.put_nowait((dilate, with_contours))

            last_f = cur
        else:
            time.sleep(REC_TMT_SHIFT)

    cam_h.release()


def change_thresh_min(x):
    if x < thresh_max.value:
        thresh_min.value = x
    else:
        cv2.setTrackbarPos(THRESH_MIN, CONTROL, thresh_min.value)


def change_thresh_max(x):
    if x > thresh_min.value:
        thresh_max.value = x
    else:
        cv2.setTrackbarPos(THRESH_MAX, CONTROL, thresh_max.value)


def change_cont_min(x):
    if x < cont_max.value:
        cont_min.value = x
    else:
        cv2.setTrackbarPos(CONT_MIN, CONTROL, cont_min.value)


def change_cont_max(x):
    if x > cont_min.value:
        cont_max.value = x
    else:
        cv2.setTrackbarPos(CONT_MAX, CONTROL, cont_max.value)


def change_focus_v(x):
    if x != focus_v.value:
        focus_v.value = x


def init_windows():
    cv2.namedWindow(DILATE)
    cv2.moveWindow(DILATE, 0, 0)
    cv2.namedWindow(CONTROL)
    cv2.moveWindow(CONTROL, 800, 0)


def init_trackbars():
    cv2.createTrackbar(THRESH_MIN, CONTROL, 0, 255, change_thresh_min)
    cv2.setTrackbarMin(THRESH_MIN, CONTROL, 0)
    cv2.setTrackbarMax(THRESH_MIN, CONTROL, 255)
    cv2.setTrackbarPos(THRESH_MIN, CONTROL, thresh_min.value)

    cv2.createTrackbar(THRESH_MAX, CONTROL, 0, 255, change_thresh_max)
    cv2.setTrackbarMin(THRESH_MAX, CONTROL, 0)
    cv2.setTrackbarMax(THRESH_MAX, CONTROL, 255)
    cv2.setTrackbarPos(THRESH_MAX, CONTROL, thresh_max.value)

    cv2.createTrackbar(CONT_MIN, CONTROL, 0, 50000, change_cont_min)
    cv2.setTrackbarMin(CONT_MIN, CONTROL, 0)
    cv2.setTrackbarMax(CONT_MIN, CONTROL, 50000)
    cv2.setTrackbarPos(CONT_MIN, CONTROL, cont_min.value)

    cv2.createTrackbar(CONT_MAX, CONTROL, 0, 50000, change_cont_max)
    cv2.setTrackbarMin(CONT_MAX, CONTROL, 0)
    cv2.setTrackbarMax(CONT_MAX, CONTROL, 50000)
    cv2.setTrackbarPos(CONT_MAX, CONTROL, cont_max.value)

    cv2.createTrackbar(FOCUS_TB, CONTROL, 0, 100, change_focus_v)
    cv2.setTrackbarMin(FOCUS_TB, CONTROL, 0)
    cv2.setTrackbarMax(FOCUS_TB, CONTROL, 100)
    cv2.setTrackbarPos(FOCUS_TB, CONTROL, focus_v.value)


def init_parameters(cam):
    global CONTROL, thresh_max, thresh_min, cont_max, cont_min
    CONTROL = "{:s} - {:s}".format(CONTROL, str(cam.cam_name))

    t_min, t_max = cam.threshold
    c_min, c_max = cam.contours

    if (t_min is None
        or t_max is None
        or c_min is None
        or c_max is None):
        return False

    thresh_min.value = t_min
    thresh_max.value = t_max

    cont_min.value = c_min
    cont_max.value = c_max

    return True


def accept_params(cam):
    global thresh_max, thresh_min, cont_max, cont_min

    cam.threshold = (thresh_min.value, thresh_max.value)
    cam.contours = (cont_min.value, cont_max.value)


def do_setup(cam):
    ret_val = False

    if not init_parameters(cam):
        print("Bad camera parameters.")
        sys.exit(1)

    init_windows()
    init_trackbars()

    # start process
    frames = Queue()
    grabber_pr = Process(target=grabber_loop,
                         args=(cam.cam_id,
                               frames,
                               working_f,
                               thresh_min,
                               thresh_max,
                               cont_min,
                               cont_max,
                               focus_v))
    grabber_pr.start() # todo uncomment

    while (1):
        while not frames.empty():
            dilate, with_contours = frames.get_nowait()

            cv2.imshow(CONTROL, with_contours)
            cv2.imshow(DILATE, dilate)

        k = cv2.waitKey(1) & 0xFF
        if k == KEY_ESC:
            break
        elif k == KEY_RETURN:
            accept_params(cam)
            ret_val = True
            break

    working_f.value = False
    grabber_pr.terminate()

    cv2.destroyAllWindows()

    return ret_val
