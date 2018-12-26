"""Returns circle position and probabilites (feature values)
use as detector(src, obj)

detector(src, obj)
src - image
obj - 'green_cirle' or 'blue_circle'

returns outputPos, outputPro 
"""

import unittest
import glob
import pickle

import numpy as np
import cv2
import imutils
from pylab import *



def closing(src, obj):
    img_inRange = np.zeros(src.shape[:2], src.dtype)
    if obj == 'blue_circle':
        img_inRange = cv2.inRange(src, (160, 95, 40), (190, 110, 65))
    elif obj == 'green_circle':
        img_inRange = cv2.inRange(src, (70, 100, 35), (90, 120, 65))
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    image_closed = cv2.morphologyEx(img_inRange, cv2.MORPH_CLOSE, kernel)
    image_closed = cv2.morphologyEx(image_closed, cv2.MORPH_OPEN, kernel)
    return image_closed

def normpdf(x, mean, sd):
    var = float(sd) ** 2
    pi = 3.1415926
    denom = (2 * pi * var) ** .5
    num = np.math.exp(-(float(x) - float(mean)) ** 2 / (2 * var))
    return num / denom

def feature1(image, closing, obj):
    pos1 = []
    pro1 = []
    m, sd = [], []  
    if obj == 'blue_circle':
        m = [174, 106, 53]
        sd = [4.7, 2.6, 3.3]
    elif obj == 'green_circle':
        m = [80, 108, 49]
        sd = [3, 2.5, 4.6]
    cnts = cv2.findContours(closing, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if imutils.is_cv2() else cnts[1]
    if cnts is not None:
        # loop over the contours
        maxPB = normpdf(m[0], m[0], sd[0])
        maxPG = normpdf(m[1], m[1], sd[1])
        maxPR = normpdf(m[2], m[2], sd[2])
        for c in cnts:
            # compute the center of the contour
            M = cv2.moments(c)
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            pos1.append([cX, cY])

            PB = normpdf(image[cY, cX, 0], m[0], sd[0])
            PG = normpdf(image[cY, cX, 1], m[1], sd[1])
            PR = normpdf(image[cY, cX, 2], m[2], sd[2])
            norPB = PB / maxPB
            norPG = PG / maxPG
            norPR = PR / maxPR
            pro1.append(np.mean([norPB, norPG, norPR]))
    return pos1, pro1


def feature2(image, pos1):
    tempPro2 = []
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (9, 9), 2.0)
    circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, dp=1, minDist=100,
                               param1=100, param2=40, minRadius=10, maxRadius=100)
    if circles is not None:
        for subPos1 in pos1:
            pro = []
            maxPx = normpdf(subPos1[0], subPos1[0], 1)
            maxPy = normpdf(subPos1[1], subPos1[1], 1)
            for (x, y, r) in circles[0, :]:
                Px = normpdf(x, subPos1[0], 1)
                Py = normpdf(y, subPos1[1], 1)
                norPx = Px / maxPx
                norPy = Py / maxPy
                pro.append(np.mean([norPx, norPy]))
            tempPro2.append(max(pro))
    else:
        tempPro2 += [0]
    pro2 = tempPro2
    return pro2

def iou(region):
    mask = np.zeros_like(region)
    edges = cv2.Canny(region, 100, 200)
    indices = np.where(edges != [0])
    a = fitEllipse(indices[0], indices[1])
    center = ellipse_center(a)
    phi = ellipse_angle_of_rotation2(a)
    axes = ellipse_axis_length(a)
    center = (int(center[1]), int(center[0]))
    axes = (int(axes[0]), int(axes[1]))
    cv2.ellipse(mask, center, axes, phi, 0, 360, 255, -1)
    img_bwa1 = cv2.bitwise_and(region, mask)
    img_bwa2 = cv2.bitwise_or(region, mask)
    img_sum1 = sum(img_bwa1)
    img_sum2 = sum(img_bwa2)
    iou = img_sum1 / img_sum2
    return iou

def fitEllipse(x, y):
    x = x[:, np.newaxis]
    y = y[:, np.newaxis]
    D = np.hstack((x * x, x * y, y * y, x, y, np.ones_like(x)))
    S = np.dot(D.T, D)
    C = np.zeros([6, 6])
    C[0, 2] = C[2, 0] = 2
    C[1, 1] = -1
    E, V = eig(np.dot(inv(S), C))
    n = np.argmax(np.abs(E))
    a = V[:, n]
    return a

def ellipse_center(a):
    b, c, d, f, g, a = a[1] / 2, a[2], a[3] / 2, a[4] / 2, a[5], a[0]
    num = b * b - a * c
    x0 = (c * d - b * f) / num
    y0 = (a * f - b * d) / num
    return np.array([x0, y0])

def ellipse_angle_of_rotation2(a):
    b, c, d, f, g, a = a[1] / 2, a[2], a[3] / 2, a[4] / 2, a[5], a[0]
    if b == 0:
        if a > c:
            return 0
        else:
            return np.pi / 2
    else:
        if a > c:
            return np.arctan(2 * b / (a - c)) / 2
        else:
            return np.pi / 2 + np.arctan(2 * b / (a - c)) / 2


def ellipse_axis_length(a):
    b, c, d, f, g, a = a[1] / 2, a[2], a[3] / 2, a[4] / 2, a[5], a[0]
    up = 2 * (a * f * f + c * d * d + g * b * b - 2 * b * d * f - a * c * g)
    down1 = (b * b - a * c) * ((c - a) * np.sqrt(1 + 4 * b * b / ((a - c) * (a - c))) - (c + a))
    down2 = (b * b - a * c) * ((a - c) * np.sqrt(1 + 4 * b * b / ((a - c) * (a - c))) - (c + a))
    res1 = np.sqrt(abs(up / down1))
    res2 = np.sqrt(abs(up / down2))
    return np.array([res1, res2])

def feature3(closing):
    _dummy, contours, _dummy = cv2.findContours(closing, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    ious = []
    if contours is not None:
        for c in contours:
            mask = np.zeros_like(closing)
            cv2.drawContours(mask, [c], -1, (255, 255, 255), thickness=cv2.FILLED)
            ious.append(iou(mask))
    else:
        ious = 0
    return ious

def detector(src, obj):
    """
    src - image
    obj - 'green_cirle' or 'blue_circle'

    returns outputPos, outputPro 
    circle position and probabilites (feature values)
    """
    img_closed = closing(src, obj)

    src.flags.writeable = False
    img_closed.flags.writeable = False

    pos1, pro1 = feature1(src, img_closed, obj)
    pro2 = feature2(src, pos1)
    pro3 = feature3(img_closed)
    if pos1:
            pro = []
            list = {}
            for pr1, pr2, pr3, po1 in zip(pro1, pro2, pro3, pos1):
                pro.append(pr1 * pr2 * pr3)
                list.update({str(po1): str(pr1 + pr2)})
            pro3Index = pro.index(max(pro))
            outputPos = pos1[pro3Index]
            outputPro = pro[pro3Index]
    else:
        pos0 = [0, 30, 45]
        outputPos = pos0
        outputPro = 0

    src.flags.writeable = True
    return outputPos, outputPro 
    
if __name__ == "__main__":
    print(__doc__)
