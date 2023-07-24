import sensor, image, time,math,pyb
from pyb import UART,LED
import json,network
import ustruct
import struct

sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)#320*240
sensor.skip_frames(time=20)
sensor.set_auto_gain(False) # must be turned off for color tracking
sensor.set_auto_whitebal(False) # must be turned off for color tracking
#sensor.set_hmirror(True)
#sensor.set_vflip(True)

def auto_get_colour():
# Capture the color thresholds for whatever was in the center of the image.
    r = [(320//2)-(50//2), (240//2)-(50//2), 40, 40] # 40x40 center of QVGA.

    for i in range(100):
        img = sensor.snapshot()
        img.draw_rectangle(r)

    print("Learning thresholds...")
    threshold = [50, 50, 0, 0, 0, 0] # Middle L, A, B values.
    for i in range(100):
        img = sensor.snapshot()
        hist = img.get_histogram(roi=r)
        lo = hist.get_percentile(0.01)
        hi = hist.get_percentile(0.99)

        threshold[0] = (threshold[0] + lo.l_value()) // 2
        threshold[1] = (threshold[1] + hi.l_value()) // 2
        threshold[2] = (threshold[2] + lo.a_value()) // 2
        threshold[3] = (threshold[3] + hi.a_value()) // 2
        threshold[4] = (threshold[4] + lo.b_value()) // 2
        threshold[5] = (threshold[5] + hi.b_value()) // 2
        for blob in img.find_blobs([threshold], pixels_threshold=100
        , area_threshold=100, merge=True, margin=10):
            img.draw_rectangle(blob.rect())
            img.draw_cross(blob.cx(), blob.cy())
            img.draw_rectangle(r)
    return threshold

clock = time.clock()
ROI=[(0,160,320,80),(0,80,320,80),(0,0,320,80)]
def find_max(blobs):    #定义寻找色块面积最大的函数
    max_size=0
    for blob in blobs:
        if blob.pixels() > max_size:
            max_blob=blob
            max_size = blob.pixels()
    return max_blob
black_threshold=auto_get_colour()
while(True):
    clock.tick()
    img = sensor.snapshot().lens_corr(1.8)
    cx = cy = cw = ch = 0
    for ROI_Index in range(len(ROI)):
        blobs = img.find_blobs([black_threshold],roi=ROI[ROI_Index],invert=False
        ,area_threshold=2000,pixels_threshold=500)
        if blobs:
                    max_b = find_max(blobs)
                    #如果找到了目标颜色
                    cx=max_b[5]
                    cy=max_b[6]
                    cw=max_b[2]
                    ch=max_b[3]
                    img.draw_rectangle(max_b[0:4],color=(0,0,255)) # rect
                    img.draw_cross(max_b[5], max_b[6])
                    uart.write(bytes([0x34,0x12]))
                    if 0 < cx <= 100:
                    elif 100 < cx <= 220:
                    elif 220 < cx <= 320:
                    #print(cx,cy,cw,ch)
                    print(black_threshold)






