# Grayscale threshold for dark things...
THRESHOLD = (18, 61, 14, 89, -2, 63)

# 导入所需的库和模块
import sensor, image, time, ustruct
from pyb import UART, LED

# 点亮三个LED灯
LED(1).on()
LED(2).on()
LED(3).on()

# 初始化图像传感器
sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QQQVGA)  # 设置图像帧大小为 80x60 像素
sensor.skip_frames(time=2000)
clock = time.clock()

# 初始化串口3，波特率为115200
uart = UART(3, 115200)
uart.init(115200, bits=8, parity=None, stop=1)

# 定义ROI（感兴趣区域）的位置
roi1 = [
    (0, 17, 15, 25),   # 左
    (65, 17, 15, 25),  # 右
    (30, 0, 20, 15),   # 上
    (0, 0, 80, 60)     # 停车
]

# 定义输出函数outuart，用于发送控制指令给其他设备
def outuart(x, a, flag):
    global uart
    f_x = 0
    f_a = 0

    # 根据flag的不同，设置x、a、f_x、f_a的值
    if flag == 0:
        if x < 0:
            x = -x
            f_x = 1
        if a < 0:
            a = -a
            f_a = 1

    if flag == 1:  # 十字
        x, a, f_x, f_a = (0, 0, 0, 1)
    if flag == 2:  # 上左
        x, a, f_x, f_a = (0, 0, 1, 0)
    if flag == 3:  # 上右
        x, a, f_x, f_a = (0, 0, 1, 1)
    if flag == 4:  # 停车
        x, a, f_x, f_a = (1, 1, 1, 2)

    # 将数据打包成字节数组
    data = ustruct.pack("<bbhhhhb", 0x2C, 0x12, int(x), int(a), int(f_x), int(f_a), 0x5B)

    # 根据flag的值判断是否发送数据
    if flag != 1:
        uart.write(data)
    else:
        # 如果flag为1，连续发送数据50次
        for x in range(50):
            uart.write(data)
            time.sleep_ms(1)

# 初始化标志变量
p9_flag = 0
not_stop = 0

# 主循环
while True:
    clock.tick()
    img = sensor.snapshot().binary([THRESHOLD])  # 对图像进行二值化
    line = img.get_regression([(100, 100)], robust=True)  # 检测图像中的直线

    # 初始化三个方向的标志变量
    left_flag, right_flag, up_flag = (0, 0, 0)

    # 在图像上绘制ROI区域
    for rec in roi1:
        img.draw_rectangle(rec, color=(255, 0, 0))

    # 获取P9引脚的状态
    p = pyb.Pin("P9", pyb.Pin.IN)
    print(p.value())

    # 如果P9引脚从低电平变为高电平，将标志变量设置为1
    if p.value() == 0:
        p9_flag = 1
    if p.value() == 1 and p9_flag == 1:
        not_stop = 1
        p9_flag = 0

    # 如果检测到直线
    if line:
        rho_err = abs(line.rho()) - img.width() / 2  # 直线左右偏移的距离
        if line.theta() > 90:
            theta_err = line.theta() - 180
        else:
            theta_err = line.theta()  # 直线角度偏移

        # 在图像上画出直线
        img.draw_line(line.line(), color=127)

        # 如果直线长度大于8个像素
        if line.magnitude() > 8:
            # 根据直线偏移量发送数据
            outdata = [rho_err, theta_err, 0]
            print(outdata)
            outuart(rho_err, theta_err, 0)

            # 在ROI区域内检测左、右、上方向的障碍物
            if img.find_blobs([(96, 100, -13, 5, -11, 18)], roi=roi1[0]):  # 左
                left_flag = 1
            if img.find_blobs([(96, 100, -13, 5, -11, 18)], roi=roi1[1]):  # 右
                right_flag = 1
            if img.find_blobs([(96, 100, -13, 5, -11, 18)], roi=roi1[2]):  # 上
                up_flag = 1

            # 判断障碍物方向，发送相应数据
            if left_flag == 1 and right_flag == 1:
                outuart(0, 0, 1)  # 十字
                continue
            if left_flag == 1 and up_flag == 1:
                outuart(0, 0, 2)  # 上左
                continue
            if right_flag == 1 and up_flag == 1:
                outuart(0, 0, 3)  # 上右
                continue

        else:
            outuart(0, 0, 4)  # 停车
            pass

    else:
        outuart(0, 0, 4)  # 停车

    # 输出帧率
    print(clock.fps())
