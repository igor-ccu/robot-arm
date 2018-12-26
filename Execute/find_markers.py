from pyueye import ueye
import numpy as np
import time
import cv2
import math
from skimage import util
import cmd
import markers
import transformation


mtx = np.loadtxt("data/mtx.numpy",dtype=float)
dist = np.loadtxt("data/dist.numpy",dtype=float)
def cap():
    frame = ueye.get_data(mem_ptr, width, height, bitspixel, lineinc, copy=True)
    return calib(np.reshape(frame, (height, width, 3)))

def display(wait=1000):
    src = cap()
    cv2.imshow("ueye", src)
    cv2.waitKey(wait)
    return

def calib(image):
    h,  w = image.shape[:2]
    newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w,h), 1, (w,h))
    return cv2.undistort(image, mtx, dist, None, newcameramtx)


def markers_cycle_horizontal(start=30, end=50, step=10, fct=display):
    blue_lower, blue_higher = markers.parameters('orange')
    green_lower, green_higher = markers.parameters('green')
    blue_circles = None
    green_circles = None
    while ((blue_circles is  None) or (green_circles is  None)):
        for angle in range(start, end+step, step):
            cmd.mv_deg(str(angle)+" 15 50 25 90 0",3)
            img = cap()
            if blue_circles is None: 
                blue_circles = markers.detect_circle(img, blue_lower, blue_higher)
                blue_angle = str(angle)+" 15 50 25 90 0"
                if blue_circles is not None: 
                    None
                    markers.draw_circles(blue_circles, img)
            if green_circles is None: 
                green_circles = markers.detect_circle(img, green_lower, green_higher)
                green_angle = str(angle)+" 15 50 25 90 0"
                if green_circles is not None: 
                    markers.draw_circles(green_circles, img)
            cv2.imshow("ueye", img)
            cv2.waitKey(100)
            cv2.imshow("ueye", cv2.inRange(cv2.cvtColor(img, cv2.COLOR_BGR2HSV), green_lower, green_higher))
            cv2.waitKey()
            if (blue_circles is not None) and (green_circles is not None):
                print(blue_circles)
                print(green_circles)
                break
        if blue_circles is None:
            print("Blue circle not found!")
        if green_circles is None:
            print("Green circle not found!")
        if cv2.waitKey(1000) & 0xFF == ord('q'):
            return
        cmd.mv_deg(str(start)+" 15 50 25 90 0",3)
        cv2.waitKey(0)
    return blue_circles[0], blue_angle, green_circles[0], green_angle


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

    count = 0
    while(count < 5):
        cv2.waitKey(100)
        count+=1
    
    display()
    display()

    (blue_xiyi, blue_angle, green_xiyi, green_angle) = markers_cycle_horizontal()

    

    #cmd.mv_deg("-30 15 50 25 90 0")
    #img = cap()

    cv2.destroyAllWindows()



    # cleanup
    ueye.is_FreeImageMem(hcam, mem_ptr, mem_id)
    ueye.is_StopLiveVideo(hcam, ueye.IS_FORCE_VIDEO_STOP)
    ueye.is_ExitCamera(hcam)