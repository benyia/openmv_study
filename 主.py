

import sensor, image, time, lcd, json, struct
from pyb import UART, Timer,LED

sensor.reset()
sensor.set_pixformat(sensor.RGB565)#设置图像为彩色
sensor.set_framesize(sensor.QQVGA)#图像大小为160*120
sensor.set_auto_gain(False)#自动增益关闭
sensor.set_auto_exposure(False)#白平衡关闭
sensor.set_hmirror(True)#水平方向翻转
sensor.set_vflip(True)#垂直方向翻转
sensor.skip_frames(time=2000)#跳过2000毫秒
clock = time.clock()
#进行视野补光
LED(1).off()#red

LED(2).off()#green
LED(3).off()#blue

uart = UART(3, 115200,timeout_char = 1000)#串口为3，波特率为115200，如果UART繁忙， 在发送字符之间等待最多1秒
uart.init(115200, bits=8, parity=None, stop=1)#初始化串口


black_threshold = (0, 21, -8, 34, -20, 41)#黑色线的阈值
def find_max(blobs):    #定义寻找色块面积最大的函数
    max_size=0  # 初始化最大面积为0
    for blob in blobs:  # 遍历所有的色块
        if blob.pixels() > max_size:  # 如果当前色块的面积大于最大面积
            max_blob=blob  # 将当前色块赋值给max_blob
            max_size = blob.pixels()  # 更新最大面积为当前色块的面积
    return max_blob  # 返回面积最大的色块

while True:
    clock.tick()#开始追踪运行时间。
    img = sensor.snapshot().lens_corr(1.8)#获取摄像头拍摄到的图像，并进行镜头校正。
    blobs = img.find_blobs([black_threshold])#在图像中查找黑色矩形，并返回一个包含所有找到的矩形对象的列表。
    cx = 0
    cy = 0
    if blobs:
            max_b = find_max(blobs)
            #获取最大矩形对象的中心点坐标。
            cx = max_b.cx()
            cy = max_b.cy()
            #获取最大矩形对象的宽度和高度
            cw = max_b.w()
            ch = max_b.h()
            img.draw_rectangle(max_b.rect(),color=(250,0,0))#在图像上绘制最大矩形对象的边框
            img.draw_cross(max_b.cx(), max_b.cy(),color=(0,0,250))#在最大矩形对象的中心点上绘制一个十字线
            #img.draw_circle(max_b.cx(),max_b.cy())
            FH = bytearray([0x2C,0x12,cx,cy,cw,ch,0x5B])

            #sending_data(cx,cy,cw,ch)
            uart.write(FH)#将最大矩形对象的中心点坐标、宽度和高度发送出去
            #time.sleep_ms(100)
            print(cx, cy,cw,ch)#打印最大矩形对象的中心点坐标、宽度和高度。


