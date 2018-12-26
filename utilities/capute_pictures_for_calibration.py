"""
Captures 20 pictures pictures for callibration (or any) purpose
save to data directory
"""
from pyueye import ueye
import numpy as np
import time
import cv2
import math
from skimage import util
import cmd
import markers
import transformation

def cap():
    frame = ueye.get_data(mem_ptr, width, height, bitspixel, lineinc, copy=True)
    return np.reshape(frame, (height, width, 3))

def display(wait=1000):
    src = cap()
    cv2.imshow("ueye", src)
    cv2.waitKey(wait)


if __name__=="__main__":
    #Clear error
    cmd.event("clr", 1)
    time.sleep(0.1)

    #Initialize camera
    hcam = ueye.HIDS(0)
    ueye.is_InitCamera(hcam, None)

    #Set color mode
    ueye.is_SetColorMode(hcam, ueye.IS_CM_BGR8_PACKED)

    #Set camera resolution
    width = 1280
    height = 720

    #Allocate memory
    mem_ptr = ueye.c_mem_p()
    mem_id = ueye.int()

    #For colormode = IS_CM_BGR8_PACKED
    bitspixel = ueye.INT(24)
    ueye.is_AllocImageMem(hcam, width, height, bitspixel, mem_ptr, mem_id)

    #Set active memory region
    ueye.is_SetImageMem(hcam, mem_ptr, mem_id)

    #Continuous capture to memory
    ueye.is_CaptureVideo(hcam, ueye.IS_DONT_WAIT)

    #Get data from camera
    lineinc = width * int((bitspixel + 7) / 8)

    count = 0
    while(count < 5):
        cv2.waitKey(100)
        count+=1

    img = cap()
    cv2.imshow('ueye', img)
    cv2.waitKey(0)

    cmd.event("init_pos")


    count = 0
    while(count < 20):
        cv2.waitKey(100)
        count+=1
        img = cap()
        cv2.imshow('ueye', img)
        cv2.imwrite('../../calib/'+str(count)+'.jpg',img)
        cv2.waitKey(0)

    cv2.destroyAllWindows()
    
    # cleanup
    ueye.is_FreeImageMem(hcam, mem_ptr, mem_id)
    ueye.is_StopLiveVideo(hcam, ueye.IS_FORCE_VIDEO_STOP)
    ueye.is_ExitCamera(hcam)