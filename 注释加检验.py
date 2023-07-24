

import sensor, image, time, lcd, json, struct
from pyb import UART, Timer,LED

sensor.reset()
sensor.set_pixformat(sensor.RGB565)#设置图像为彩色
sensor.set_framesize(sensor.QVGA)#图像大小为320*240
sensor.set_auto_gain(False)#自动增益关闭
sensor.set_auto_exposure(False)#白平衡关闭
sensor.set_hmirror(True)#水平方向翻转
sensor.set_vflip(True)#垂直方向翻转
sensor.skip_frames(20)#跳过2000毫秒

ROI=[(40,0,240,80), (40,80,240,80),(40,160,240,80)]

#sensor.set_windowing(roi) #取中间的160*80区域
clock = time.clock()
#进行视野补光
LED(1).on()#red

LED(2).on()#green
LED(3).on()#blue

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
'''
def sending_data(cx, cy, cw, ch):#定义发送目标的位置信息
    data = struct.pack("<bbhhhhb",#将目标位置信息打包成二进制数据。
                       0x2C,            #帧头1
                       0x12,            #帧头2
                       int(cx),         #数据1
                       int(cy),         #数据2
                       int(cw),         #数据3
                       int(ch),         #数据3
                       0x00)            #校验数据
    checksum = sum(data) & 0xFF         #得到前六位数据的校验和
    data = data[:-1] + bytes([checksum])#将校验和转换为一个字节对象，并将其添加到原始数据的末尾
    uart.write(data)                    #将数据通过串口发送出去
'''

while True:
    clock.tick()#开始追踪运行时间。
    img = sensor.snapshot().lens_corr(1.8)#获取摄像头拍摄到的图像，并进行镜头校正。
    for ROI_Index in range(0,3):
        blobs = img.find_blobs([black_threshold],roi=ROI[ROI_Index])#在图像中查找黑色矩形，并返回一个包含所有找到的矩形对象的列表。
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
            img.draw_rectangle(ROI[ROI_Index])
            img.draw_rectangle(max_b.rect(),color=(250,0,0))#在图像上绘制最大矩形对象的边框
            img.draw_cross(max_b.cx(), max_b.cy(),color=(0,0,250))#在最大矩形对象的中心点上绘制一个十字线
            #img.draw_circle(max_b.cx(),max_b.cy())
            FH = bytearray([0x2C,0x12,cx,cy,cw,ch,0x5B])

            #sending_data(cx,cy,cw,ch)
            uart.write(FH)#将最大矩形对象的中心点坐标、宽度和高度发送出去
            print(cx, cy,cw,ch)#打印最大矩形对象的中心点坐标、宽度和高度。
            #time.sleep_ms(50)


