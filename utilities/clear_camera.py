"""
Tries to reinitialize camera in case you get errors.
This happens sometimes when you don't close your camera properly.
Usually replugging USB is enough.
"""
from pyueye import ueye
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

ueye.is_FreeImageMem(hcam, mem_ptr, mem_id)
ueye.is_StopLiveVideo(hcam, ueye.IS_FORCE_VIDEO_STOP)
ueye.is_ExitCamera(hcam)

