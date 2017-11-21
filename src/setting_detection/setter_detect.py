#!/usr/bin/python3

import os
import sys
import time
from multiprocessing import Value, Queue, Process

import cv2
import numpy as np

from observer import Camera
from observer.cam_defs import *

SOURCE = 0
PROCESSED = 1
DELTA = 2
THRESHOLD = 3
DILATE = 4
ENDLESS = 5


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

            frames.putnowait((frame_cur, delta, thresh, dilate, with_contours))

            if type.value == SOURCE:
                frames.putnowait(cur)


            if type.value == PROCESSED:
                frames.putnowait(cur)

            # get diff
            if type.value == DELTA:
                frames.putnowait(cur)

            if type.value == THRESHOLD:
                frames.putnowait(cur)
            thresh = Camera.get_dilate(thresh)
            if type.value == DILATE:
                frames.putnowait(cur)

            detected, cur = Camera.check_contours(thresh, cur, c_min, c_max)
            if type.value == ENDLESS:
                frames.putnowait(cur)

        else:
            time.sleep(REC_TMT_SHIFT)





def nothing(x):
    pass


def main():
    # init variables
    gauss_kern_w = Value("i", 21)
    gauss_kern_h = Value("i", 21)

    thresh_min = Value("i", 25)
    thresh_max = Value("i", 255)

    cont_min = Value("i", 2000)
    cont_max = Value("i", 30000)

    working_f = Value("i", 1)
    working_f.value = True

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
    cv2.namedWindow('Control')

    # when esc - do close all and stop process

    while (1):
        if frames.qsize() > 0:

            cv2.imshow('Control', frames.get_nowait())

        k = cv2.waitKey(1) & 0xFF
        if k == 27:
            break


    working_f.value = False
    cv2.destroyAllWindows()


    last = cv2.imread("../misc/img_0.jpg")
    last = cv2.resize(last, (640, 480))
    cur = cv2.imread("../misc/img_1.jpg")
    cur = cv2.resize(cur, (640, 480))

    frame_last = Camera.__proc_for_detect(last, 21, 21)
    frame_cur = Camera.__proc_for_detect(cur, 21, 21)

    # get diff
    delta = cv2.absdiff(frame_last, frame_cur)
    # 25, 255
    # thresh = cv2.threshold(delta, 25, 255, cv2.THRESH_BINARY)[1]
    thresh = Camera.__get_thresh(delta, 25, 255)
    # thresh = cv2.dilate(thresh, None, iterations=1)
    thresh = Camera.__get_dilate(thresh)

    detected, cur = Camera.__check_contours(thresh, cur, 2000, 10000)


    img = cv2.resize(img, (640, 480))
    # img = np.zeros((300, 512, 3), np.uint8)
    cv2.namedWindow('image')

    # create trackbars for color change
    cv2.createTrackbar('R', 'image', 0, 255, nothing)
    cv2.createTrackbar('G', 'image', 0, 255, nothing)
    cv2.createTrackbar('B', 'image', 0, 255, nothing)

    # create switch for ON/OFF functionality
    switch = '0 : OFF \n1 : ON'
    cv2.createTrackbar(switch, 'image', 0, 1, nothing)

    while (1):
        cv2.imshow('image', img)
        k = cv2.waitKey(1) & 0xFF
        if k == 27:
            break

        # get current positions of four trackbars
        r = cv2.getTrackbarPos('R', 'image')
        g = cv2.getTrackbarPos('G', 'image')
        b = cv2.getTrackbarPos('B', 'image')
        s = cv2.getTrackbarPos(switch, 'image')

        if s == 0:
            img[:] = 0
        else:
            img[:] = [b, g, r]

    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()