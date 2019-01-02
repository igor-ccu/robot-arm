from pyueye import ueye
import numpy as np
import time
import cv2
import math
from skimage import util
import cmd
import sys
import circle_marker_detection as circle
import transformation


mtx = np.loadtxt("data/mtx.numpy",dtype=float)
dist = np.loadtxt("data/dist.numpy",dtype=float)
cameramtx = np.zeros(mtx.shape)

def cap():
    frame = ueye.get_data(mem_ptr, width, height, bitspixel, lineinc, copy=True)
    image = np.reshape(frame, (height, width, 3))
    warped = cv2.undistort(image, mtx, dist, None, cameramtx)
    return warped

def display(wait=1000):
    src = cap()
    cv2.imshow("ueye", src)
    cv2.waitKey(wait)
    return

def calib():
    h,  w = (720, 1280)
    newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w,h), 1, (w,h))
    global cameramtx
    cameramtx = np.copy(newcameramtx) 
    return newcameramtx


def markers_cycle_horizontal(start=-40, end=50, step=10, fct=display, threshold = 0.3, max_counts = 1):
    """Cycle horizontally (increment base angle) and detect circles
    If circle detected mark it on the image
    
    Returns blue_pos, blue_angle, green_pos, green_angle 
    * pos in [px]
    * angle are the angles of robot joints (ready to feed into cmd.mv_deg(angle))
    This function will return None, None if max_counts of cycles (by default 2) are exceeded
    """
    detect_blue = True
    detect_green = True
    count = 0
    while detect_blue or detect_green:
        for angle in range(start, end+step, step):
            cmd.mv_deg(str(angle)+" 15 50 25 90 0",3)
            img = cap()
            if detect_blue: 
                blue_pos, blue_pro = circle.detector_blue(img)
                print(blue_pro)
                if blue_pro > threshold:
                    detect_blue = False
                    blue_angle = str(angle)+" 15 50 25 90 0"
                    img = circle.draw(img, blue_pos)
                else: 
                    blue_pos, blue_pro = None, None
            if detect_green: 
                green_pos, green_pro = circle.detector_green(img)
                print(green_pro)
                if green_pro > threshold:
                    detect_green = False
                    green_angle = str(angle)+" 15 50 25 90 0"
                    print("{}: {}, {}".format("green", green_pos, green_angle))
                    img = circle.draw(img, green_pos)
                else:
                    green_pos, green_pro = None, None
            cv2.imshow("ueye", img)
            cv2.waitKey(100)
            if not detect_blue and not detect_green:
                break
        count += 1
        if blue_pos is None:
            print("Blue circle not found!")
        if green_pos is None:
            print("Green circle not found!")
        if count >= max_counts and (detect_blue or detect_green):
            blue_pos, blue_pro, green_pos, green_pro = None, None, None, None 
            blue_angle, green_angle = None, None
            detect_blue, detect_green = False, False
        cmd.mv_deg(str(start)+" 15 50 25 90 0",3)
        cv2.waitKey(0)
    return blue_pos, blue_angle, green_pos, green_angle


if __name__=="__main__":
    #Clear error
    cmd.event("clr", 1)
    time.sleep(0.1)

    cmd.event("init_pos")

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

    #Calibrate camera
    tmp = calib()
    count = 0
    while(count < 5):
        display(100)
        count+=1
    
    display()
    cv2.waitKey(0)

    (blue_xiyi, blue_angle, green_xiyi, green_angle) = markers_cycle_horizontal()

    if blue_xiyi is None or green_xiyi:
        #Clean-up
        cv2.destroyAllWindows()
        ueye.is_FreeImageMem(hcam, mem_ptr, mem_id)
        ueye.is_StopLiveVideo(hcam, ueye.IS_FORCE_VIDEO_STOP)
        ueye.is_ExitCamera(hcam)
        cmd.event('go_zero')
        sys.exit()


    # (..........)
    # (..........)
    # (..........)
    # (..........)
    # (..........)

    #Clean-up
    cv2.destroyAllWindows()
    ueye.is_FreeImageMem(hcam, mem_ptr, mem_id)
    ueye.is_StopLiveVideo(hcam, ueye.IS_FORCE_VIDEO_STOP)
    ueye.is_ExitCamera(hcam)
    cmd.event('go_zero')

