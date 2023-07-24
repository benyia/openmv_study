'''
先识别线，再识别数字，巡线识别到路口的时候小车暂停，切换到灰度模式识别数字，
识别完毕后发送数据给单片机，单片机发送指令切换回彩色模式继续巡线。
数字识别采用模版匹配
计数转弯数量
'''
#----------------------------------------------------------
import sensor, image, time, lcd, json, struct
from pyb import UART, Timer,LED
from image import SEARCH_EX, SEARCH_DS
#----------------------------------------------------------
sensor.reset()
sensor.set_pixformat(sensor.GRAYSCALE)
sensor.set_framesize(sensor.HQVGA)#240*160
sensor.skip_frames(20)
sensor.set_auto_gain(False)
sensor.set_auto_whitebal(False)
sensor.set_hmirror(True)
sensor.set_vflip(True)
clock = time.clock()
#----------------------------------------------------------
#LED(1).on()#red
#LED(2).on()#green
LED(3).on()#blue
#----------------------------------------------------------
uart = UART(3, 115200,timeout_char = 1000)#如果UART繁忙， 在发送字符之间等待最多1秒
uart.init(115200, bits=8, parity=None, stop=1)#初始化串口
#----------------------------------------------------------
'''
#自动阈值
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
#----------------------------------------------------------
#模板匹配
templates0 = ["/0_1.pgm","/0_2.pgm","/0_3.pgm","/0_4.pgm","/0_5.pgm","/0_6.pgm","/0_7.pgm","/0_8.pgm","/0_9.pgm","/0_10.pgm","/0_11.pgm"]
templates1 = ["/1_1.pgm","/1_2.pgm","/1_3.pgm","/1_4.pgm","/1_5.pgm","/1_6.pgm","/1_7.pgm","/1_8.pgm","/1_9.pgm","/1_10.pgm","/1_11.pgm"]
'''
template2 = image.Image("/2.pgm")
templates3 = ["/3.pgm","/3_1.pgm","/3_2.pgm","/3_3.pgm","/3_4.pgm","/3_5.pgm","/3_6.pgm","/3_7.pgm","/3_8.pgm"]
templates4 = ["/4.pgm","/4_1.pgm","/4_2.pgm","/4_3.pgm","/4_4.pgm","/4_5.pgm","/4_6.pgm","/4_7.pgm","/4_8.pgm"]
templates5 = ["/5.pgm","/5_1.pgm","/5_2.pgm","/5_3.pgm","/5_4.pgm","/5_5.pgm","/5_6.pgm","/5_7.pgm","/5_8.pgm"]
templates6 = ["/6.pgm","/6_1.pgm","/6_2.pgm","/6_3.pgm","/6_4.pgm","/6_5.pgm","/6_6.pgm","/6_7.pgm","/6_8.pgm"]
templates7 = ["/7.pgm","/7_1.pgm","/7_2.pgm","/7_3.pgm","/7_4.pgm","/7_5.pgm","/7_6.pgm","/7_7.pgm","/7_8.pgm"]
templates8 = ["/8.pgm","/8_1.pgm","/8_2.pgm","/8_3.pgm","/8_4.pgm","/8_5.pgm","/8_6.pgm","/8_7.pgm","/8_8.pgm"]
'''
#----------------------------------------------------------
ROI=[(0,160,320,80),(0,80,320,80),(0,0,320,80)]
#----------------------------------------------------------
def find_max(blobs):    #定义寻找色块面积最大的函数
    max_size=0  # 初始化最大面积为0
    for blob in blobs:  # 遍历所有的色块
        if blob.pixels() > max_size:  # 如果当前色块的面积大于最大面积
            max_blob=blob  # 将当前色块赋值给max_blob
            max_size = blob.pixels()  # 更新最大面积为当前色块的面积
    return max_blob  # 返回面积最大的色块
#----------------------------------------------------------

#----------------------------------------------------------
while True:
    img = sensor.snapshot().lens_corr(1.8)
    r = img.find_template(templates0, 0.70, step=5, search=SEARCH_EX)
    blobs = img.find_blobs([black_threshold], roi=ROI, area_threshold=100)

    # 寻找线并在路口停车
    if r:
        img.draw_rectangle(r)
        print("检测到线")
        # 切换到灰度模式以识别数字
        sensor.set_pixformat(sensor.GRAYSCALE)
        img_gray = sensor.snapshot()  # 获取灰度图像的快照

        # 初始化变量以存储识别到的数字
        detected_numbers = []

        # 循环遍历数字模板
        for template in templates0:
            number_img = image.Image(template)
            res = img_gray.find_template(number_img, 0.70, step=5, search=SEARCH_EX)  # 在灰度图像上进行模板匹配
            if res:
                detected_numbers.append(template[1])  # 从模板文件名中提取数字

        # 通过UART发送识别到的数字给单片机
        data_to_send = json.dumps(detected_numbers)
        uart.write(struct.pack("<H", len(data_to_send)))  # 首先发送数据长度
        uart.write(data_to_send)  # 发送数据
        print("识别到的数字：", detected_numbers)

        # 切换回彩色模式继续巡线
        sensor.set_pixformat(sensor.RGB565)

    else:
        # 未检测到线，继续巡线
        if blobs:
            max_blob = find_max(blobs)
            img.draw_rectangle(max_blob.rect())
            img.draw_cross(max_blob.cx(), max_blob.cy())
            go_straight()  # 不进行拐弯判断，直接直行

    clock.tick()  # 更新FPS时钟
