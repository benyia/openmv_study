import sensor, image, time,math,pyb
from pyb import UART,LED
import json,network
import ustruct
import struct

sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)#320*240
sensor.skip_frames(20)
sensor.set_auto_gain(False) # must be turned off for color tracking
sensor.set_auto_whitebal(False) # must be turned off for color tracking
sensor.set_hmirror(True)
sensor.set_vflip(True)
clock = time.clock()
#LED(1).on()red
#LED(2).on()green
LED(3).on()#blue

uart = UART(3,115200)   #定义串口3变量
uart.init(115200, bits=8, parity=None, stop=1) # init with given parameters

#ROI_Index=0
ROI=[(0,160,320,80),(0,80,320,80),(0,0,320,80)]

def find_max(blobs):    #定义寻找色块面积最大的函数
    max_size=0
    for blob in blobs:
        if blob.pixels() > max_size:
            max_blob=blob
            max_size = blob.pixels()
    return max_blob
#black_threshold = (0, 21, -8, 34, -20, 41)
#black_threshold = (6, 72, -14, 20, -20, 18)
#black_threshold = (11, 55, -7, 20, -46, 25)
black_threshold = (19, 0, -8, 37, -37, 8)
#black_threshold=(0,100)
while(True):
    clock.tick()

    img = sensor.snapshot().lens_corr(1.8)
    cx = cy = cw = ch = 0
    uart.write(bytes([0x2C,0x12]))
    for ROI_Index in range(3):
        roi=ROI[ROI_Index]
        blobs = img.find_blobs([black_threshold],roi=roi,area_threshold=100)
    #第一个模块
        #uart.write(bytes([0x2C,0x12]))
        if blobs:
            max_b = find_max(blobs)
            cx=max_b[5]
            cy=max_b[6]
            cw=max_b[2]
            ch=max_b[3]
            img.draw_rectangle(max_b[0:4])
            img.draw_cross(max_b[5], max_b[6])

            if 0 < cx <=105:
                print(01)
                uart.write(bytes([0x01]))
            elif 105 < cx <= 205:
                print(02)
                uart.write(bytes([0x02]))
            elif 205 < cx <= 320:
                print(03)
                uart.write(bytes([0x03]))
            #print(cx,cy,cw,ch)
        else:
            uart.write(bytes([0x00]))
            print(0)
    uart.write(bytes([0x5B]))
    #print(black_threshold)
