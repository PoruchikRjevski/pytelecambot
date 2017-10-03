VIDEO_REC_TIME_FULL         = 5
VIDEO_REC_TIME_PRE          = 1

VIDEO_REC_FPS               = 30
OBSERVE_FPS                 = 10

PRE_REC_BUF_SZ              = VIDEO_REC_TIME_PRE * VIDEO_REC_FPS
FULL_REC_BUF_SZ             = VIDEO_REC_TIME_FULL * VIDEO_REC_FPS

REC_TMT                     = 1 / VIDEO_REC_FPS
REC_TMT_SHIFT               = REC_TMT / 2
OBSERVING_TMT               = 1 / OBSERVE_FPS

TIMESTAMP_FRAME_STR         = '%d %B %y %H:%M:%S'
TIMESTAMP_PATH_STR          = '%d%m%y_%H%M%S'

HI_W                        = 1280
HI_H                        = 720

LO_W                        = 640
LO_H                        = 480

LAST_F_SIZE                 = 0.5
LAST_F_TXT_POS              = (15, 15)
LAST_F_TXT_CLR              = (255, 0, 0)

LAST_F_JPG_Q                = 50

CMD_FFMPEG_CONVERT          = "ffmpeg -i {:s}frame_%d.jpg{:s} {:s}" # 1 - full path to jpgs,
                                                                    # 2 - full path to mp4

A_SCALE                     = " -s {:s}x{:s}"                       # 1x2 - wxh