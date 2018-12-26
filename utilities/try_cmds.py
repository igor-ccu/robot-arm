"""
Move this file to Execute directory and run as 
python3 -i try_cmds.py 
or
python -i try_cmds.py

This will move the robot into initial position and let you try the commands in cmd module
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

if __name__=="__main__":
    print(__doc__)
    #Clear error
    cmd.event("clr", 1)
    time.sleep(0.1)

    cmd.event("init_pos")
