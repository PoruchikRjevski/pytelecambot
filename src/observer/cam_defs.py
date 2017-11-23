VIDEO_REC_TIME_FULL         = 4
VIDEO_REC_TIME_PRE          = 1

VIDEO_REC_FPS               = 30
OBSERVE_FPS                 = 1

PREVIEW_FPS_PASS            = 5

MAX_PRE_BUFFER_SIZE         = VIDEO_REC_TIME_PRE * VIDEO_REC_FPS
MAX_FULL_BUFFER_SIZE        = VIDEO_REC_TIME_FULL * VIDEO_REC_FPS

MAX_SIZE_OF_FILE            = 30 * VIDEO_REC_FPS

REC_TMT                     = 1 / VIDEO_REC_FPS
REC_TMT_SHIFT               = REC_TMT / 2
OBSERVING_TMT               = 1 / OBSERVE_FPS

TIMELAPSE_TMT               = 10

DEF_GAUSS_BLUR_KERN_SIZE    = 21
DEF_THRESHOLD_MIN           = 25
DEF_THRESHOLD_MAX           = 255
DEF_CONTOURS_MIN            = 2000
DEF_CONTOURS_MAX            = 40000


HI_W                        = 1280
HI_H                        = 720

LO_W                        = 640
LO_H                        = 480

PREV_W                      = 480
PREV_H                      = 320

LAST_F_SIZE                 = 1
LAST_F_TXT_POS              = (15, 15)
LAST_F_TXT_CLR              = (0, 0, 255)

LAST_F_JPG_Q                = 50

CMD_FFMPEG_CONVERT          = "ffmpeg -i {:s}frame_%d.jpg{:s} {:s}" # 1 - full path to jpgs,
                                                                    # 2 - full path to mp4

A_SCALE                     = " -s {:s}x{:s}"                       # 1x2 - wxh

SUFF_NOW                    = "now"
SUFF_MOVE                   = "move"
SUFF_TIMELAPSE              = "timelapse"

SUFF_PREV                   = "preview"
SUFF_FULL                   = "full"