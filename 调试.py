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

    print("Thresholds learned...")
    print("Tracking colors...")
    return threshold

clock = time.clock()
#串口
uart = UART(3,115200)   #定义串口3变量
uart.init(115200, bits=8, parity=None, stop=1)
#设置感兴趣区
#ROI = [(20, 160, 260, 60) ,(20, 80, 260, 60), (20, 0, 260, 60)]
ROI=[(0,160,320,80),(0,80,320,80),(0,0,320,80)]#,(10,150,300,40),(10,50,300,40)
def find_max(blobs):    #定义寻找色块面积最大的函数
    max_size=0
    for blob in blobs:
        if blob.pixels() > max_size:
            max_blob=blob
            max_size = blob.pixels()
    return max_blob

'''
def sending_data(cx,cy,cw,ch):
    global uart;
    #frame=[0x2C,18,cx%0xff,int(cx/0xff),cy%0xff,int(cy/0xff),0x5B];
    #data = bytearray(frame)
    data = ustruct.pack("<bbhhhhb",      #格式为俩个字符俩个短整型(2字节)
                   0x2C,                      #帧头1
                   0x12,                      #帧头2
                   int(cx), # up sample by 4   #数据1
                   int(cy), # up sample by 4    #数据2
                   int(cw), # up sample by 4    #数据1
                   int(ch), # up sample by 4    #数据2
                   0x5B)
    uart.write(data);   #必须要传入一个字节数组
'''
black_threshold=auto_get_colour()
while(True):
    clock.tick()
    img = sensor.snapshot().lens_corr(1.8)
    cx = cy = cw = ch = 0


     # 将当前帧缓冲区的图像捕获到一个图像对象中
    #cframe = img.compressed(quality=35)

    # 定义HTTP响应头，包括内容类型和响应长度
    #header = "\r\n--openmv\r\n" \
             #"Content-Type: image/jpeg\r\n"\
             #"Content-Length:"+str(cframe.size())+"\r\n\r\n"

    # 将HTTP响应头编码为字节串，以便通过串口发送
    #uart.write(header.encode())  # 将header编码为字节串，以便通过串口发送

    # 通过串口发送压缩后的照片数据
    #uart.write(img)  # 通过串口发送压缩后的照片数据
    #client.send(header)
    #client.send(cframe)
    uart.write(bytes([0x2c,0x12]))
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
                    #img.draw_rectangle(ROI[ROI_Index],color=(255,0,0))
                    img.draw_rectangle(max_b[0:4],color=(0,0,255)) # rect
                    img.draw_cross(max_b[5], max_b[6]) # cx, cy
                    #FH = bytearray([0x34, 0x12, cx, cy, cw, ch, 0x56]) #将一个包含7个元素的字节数组赋值给变量 FH
                    #对 FH 的前6个元素进行求和，并使用按位与运算符 & 将其与 0xFF 进行按位与操作，得到校验和。
                    #checksum = sum(FH[:-1]) & 0xFF
                    #将校验和添加到 FH 的末尾，形成一个新的字节数组 data,其中前6个元素与原来的 FH 相同，第7个元素为校验和
                    #bytes([checksum])将校验和转换为一个字节序列，然后将其添加到FH的末尾形成新的字节数组data。
                    #data = FH[:-1] + bytes([checksum])
                    #uart.write(data)#将字节数组 data 通过串口发送出去
                    #last_byte = data[-1]#将字节数组 data 的最后一个元素赋值给变量 last_byte,即校验和。
                    #uart.write(bytes([last_byte]))#将校验和通过串口发送出去。
                    uart.write(bytes([0x34,0x12]))
                    if 0 < cx < 100:
                        uart.write(bytes([0x01]))
                    elif 110 < cx < 210:
                        uart.write(bytes([0x02]))
                    elif 220 < cx < 320:
                        uart.write(bytes([0x03]))
                    print(cx,cy,cw,ch)
                    #time.sleep_ms(100)
                    print(black_threshold)






