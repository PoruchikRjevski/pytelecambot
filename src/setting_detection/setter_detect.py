#!/usr/bin/python3

import os
import sys
import time
from multiprocessing import Value, Queue, Process

import cv2
import numpy as np

from observer import Camera
from observer.cam_defs import *

CONTROL = "Control"
SOURCE = "Source"
PROCESSED = "Processed"
DELTA = "Delta"
THRESHOLD = "Threshold"
DILATE = "Dilate"
ENDLESS = "Endless"


GAUSS_W = 'Gauss blur kernel width'
GAUSS_H = 'Gauss blur kernel height'

gauss_kern_w = Value("i", 21)
gauss_kern_h = Value("i", 21)

thresh_min = Value("i", 25)
thresh_max = Value("i", 255)

cont_min = Value("i", 2000)
cont_max = Value("i", 30000)

working_f = Value("i", 1)
working_f.value = True


def grabber_loop(frames, working, g_kw, g_kh, t_min, t_max, c_min, c_max):
    # init cam blabla
    last = cv2.imread("../misc/img_0.jpg")
    last = cv2.resize(last, (640, 480))
    cur = cv2.imread("../misc/img_1.jpg")
    cur = cv2.resize(cur, (640, 480))

    rec_t = time.time()
    while working.value:
        cur_t = time.time()
        # check_t = cur_t
        rec_t_c = cur_t - rec_t

        if rec_t_c >= REC_TMT:
            frame_last = Camera.proc_for_detect(last, g_kw.value, g_kh.value)
            frame_cur = Camera.proc_for_detect(cur, g_kw.value, g_kh.value)

            delta = cv2.absdiff(frame_last, frame_cur)

            thresh = Camera.get_thresh(delta, t_min, t_max)

            dilate = Camera.get_dilate(thresh)

            detected, with_contours = Camera.check_contours(thresh, cur, c_min, c_max)

            frames.putnowait((cur, frame_cur, delta, thresh, dilate, with_contours))
        else:
            time.sleep(REC_TMT_SHIFT)


def change_blur_w(x):
    gauss_kern_w.value = x


def change_blur_h(x):
    gauss_kern_h.value = x


def main():
    # init variables

    # start process
    frames = Queue()
    grabber_pr = Process(target=grabber_loop,
                         args=(frames,
                               working_f,
                               gauss_kern_w,
                               gauss_kern_h,
                               thresh_min,
                               thresh_max,
                               cont_min,
                               cont_max))
    # grabber_pr.start() # todo uncomment

    # create elements
    cv2.namedWindow(CONTROL)
    cv2.namedWindow(PROCESSED)

    cv2.createTrackbar(GAUSS_W, CONTROL, 0, 50, change_blur_w)
    cv2.setTrackbarPos(GAUSS_W, CONTROL, gauss_kern_w.value)
    cv2.createTrackbar(GAUSS_H, CONTROL, 0, 50, change_blur_h)
    cv2.setTrackbarPos(GAUSS_H, CONTROL, gauss_kern_h.value)


    while (1):
        if frames.qsize() > 0:
            source, processed, delta, thresh, dilate, with_contours = frames.get_nowait()

            cv2.imshow(CONTROL, source)
            cv2.imshow(PROCESSED, processed)

        k = cv2.waitKey(1) & 0xFF
        if k == 27:
            break

    working_f.value = False
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()