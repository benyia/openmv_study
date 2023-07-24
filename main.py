import sensor, image, time,math,os, tf
from pyb import UART,LED
import json,network
import ustruct
import struct

sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.skip_frames(20)
sensor.set_auto_gain(False)
sensor.set_auto_whitebal(False)
sensor.set_hmirror(True)
sensor.set_vflip(True)
clock = time.clock()
#-----------------------------------------------------------
#LED(1).on()red
#LED(2).on()green
LED(3).on()#blue
#-----------------------------------------------------------
'''
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
'''
black_threshold = (19, 0, -8, 37, -37, 8)
#-----------------------------------------------------------
ROI=[(0,160,320,80),(0,80,320,80),(0,0,320,80)]
#-----------------------------------------------------------
def find_max(blobs):    #定义寻找色块面积最大的函数
    max_size=0
    for blob in blobs:
        if blob.pixels() > max_size:
            max_blob=blob
            max_size = blob.pixels()
    return max_blob
#-----------------------------------------------------------
uart = UART(3,115200)
uart.init(115200, bits=8, parity=None, stop=1)
#-----------------------------------------------------------
switch_interval = 10  # 切换间隔，单位：秒
last_switch_time = time.time()
#-----------------------------------------------------------
while True:
    clock.tick()
    img = sensor.snapshot().lens_corr(1.8)
    for obj in tf.classify("trained.tflite", img, min_scale=1.0, scale_mul=0.5, x_overlap=0.0, y_overlap=0.0):
        output = obj.output()
        number = output.index(max(output))
        #uart.write(number)
        print('----------------------------')
        print(number)
        print('----------------------------')
    #img = sensor.snapshot().lens_corr(1.8).binary([black_threshold])
    cx = cy = cw = ch = 0
    uart.write(bytes([0x2C, 0x12]))
    for ROI_Index in range(len(ROI)):
         blobs = img.find_blobs([black_threshold], roi=ROI[ROI_Index], area_threshold=1000,invert=True)
         if blobs:
            max_b = find_max(blobs)
            cx = max_b[5]
            cy = max_b[6]
            cw = max_b[2]
            ch = max_b[3]
            img.draw_rectangle(max_b[0:4],color=(255,0,0))
            img.draw_cross(max_b[5], max_b[6],color=(0,255,0))
            '''
            if 0 < cx <= 100:
                uart.write(bytes([0x01]))
                print(1)
                img.draw_string(40, 20, "01")
            elif 100 < cx <= 220:
                uart.write(bytes([0x02]))
                print(2)
                img.draw_string(40, 20, "02")
            elif 220 < cx <= 320:
                uart.write(bytes([0x03]))
                print(3)
                img.draw_string(40, 20, "03")

            '''
            FH = bytearray([0x2C,0x12,cx,cy,cw,ch,0x5B])

            #sending_data(cx,cy,cw,ch)
            uart.write(FH)#将最大矩形对象的中心点坐标、宽度和高度发送出去
            #time.sleep_ms(100)
            print(cx, cy,cw,ch)#打印最大矩形对象的中心点坐标、宽度和高度。
         else:
             uart.write(bytes([0x00]))
             print(0)
    uart.write(bytes([0x5B]))
    #time.sleep_ms(200)

