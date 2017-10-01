OBSERVING_TMT               = 0.1 # s
VIDEO_REC_TIME_FULL         = 5
VIDEO_REC_TIME_PRE          = 1 # s
VIDEO_REC_FPS               = 30
VIDEO_REC_TMT               = 0.016

HI_W                        = 1280
HI_H                        = 720

LO_W                        = 640
LO_H                        = 480

LAST_F_SIZE                 = 0.5
LAST_F_TXT_POS              = (15, 15)
LAST_F_TXT_CLR              = (255, 255, 255)

LAST_F_JPG_Q                = 50

CMD_FFMPEG_CONVERT          = "ffmpeg -i {:s}frame_%d.jpg{:s} {:s}" # 1 - full path to jpgs,
                                                                    # 2 - full path to mp4

A_SCALE                     = " -s {:s}x{:s}"                       # 1x2 - wxh