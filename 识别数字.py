import sensor,image,lcd,time
import KPU as kpu
from machine import UART
from fpioa_manager import fm

lcd.init(freq=15000000)
sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.set_hmirror(0)
sensor.run(1)
#加载yolov5模型
task = kpu.load("/sd/yolov5.kmodel")
f=open("anchors.txt","r")
anchor_txt=f.read()
L=[]
for i in anchor_txt.split(","):
    L.append(float(i))
anchor=tuple(L)
f.close()
f=open("lable.txt","r")
lable_txt=f.read()
lable = lable_txt.split(",")
f.close()
#设置RX、RT引脚
fm.register(9, fm.fpioa.UART1_TX, force=True)
fm.register(10, fm.fpioa.UART1_RX, force=True)
#设置串口通信
uart_A = UART(UART.UART1, 115200, 8, 1, 0, timeout=1000, read_buf_len=4096)
anchor = (0.1766, 0.1793, 0.4409, 0.3797, 0.6773, 0.5954, 1.0218, 0.9527, 2.158, 1.6841)
sensor.set_windowing((224, 224))
a = kpu.init_yolo2(task, 0.5, 0.3, 5, anchor)
classes=["9","1","4","2","3","8","5","6","7" ]

#全局变量，保存初始化识别的数字
intnum = 0
#初始化识别函数
def begin(intnum):
    TF = 1
    #得分序列，放1-8识别的次数，每一帧识别成哪个，对应的位置加一，1-8哪个先到10即最终识别为哪个
    List_score01 = [0]*8
    while(TF):
         img = sensor.snapshot()
         #code是yolov5返回的每个矩形框的参数
         #例图中出现两个目标区域的时候：[{"x":9, "y":99, "w":55, "h":82, "value":0.697979, "classid":8, "index":0, "objnum":2}, {"x":137, "y":105, "w":56, "h":67, "value":0.939132, "classid":4, "index":1, "objnum":2}]
         code = kpu.run_yolo2(task, img)
         #print(code)
         if code:
             for i in code:
                #画目标区域矩形框
                a = img.draw_rectangle(i.rect())
                a = lcd. display(img)
                list1=list(i.rect())
                #print(classes[i.classid()])
                #识别到的加1
                List_score01[int(classes[i.classid()])-1] += 1
                #print(List_score01)
                if(List_score01[0] >= 10):
                    intnum = 1
                    #给下位机通信传指令
                    uart_A.write('1')
                    #print(1)
                    #退出初始化循环
                    TF = 0
                if(List_score01[1] >= 10):
                    intnum = 2
                    uart_A.write('2')
                    #print(2)
                    TF = 0
                if(List_score01[2] >= 10):
                    intnum = 3
                    uart_A.write('3')
                    #print(3)
                    TF = 0
                if(List_score01[3] >= 10):
                    intnum = 4
                    uart_A.write('4')
                    #print(4)
                    TF = 0
                if(List_score01[4] >= 10):
                    intnum = 5
                    uart_A.write('5')
                    #print(5)
                    TF = 0
                if(List_score01[5] >= 10):
                    intnum = 6
                    uart_A.write('6')
                    #print(6)
                    TF = 0
                if(List_score01[6] >= 10):
                    intnum = 7
                    uart_A.write('7')
                    #print(7)
                    TF = 0
                if(List_score01[7] >= 10):
                    intnum = 8
                    uart_A.write('8')
                    print(8)
                    TF = 0
         else:
             a = lcd.display(img)
    return intnum

#34道路识别函数
def threefour(intnum):
    #设置二维矩阵，存放每一个矩形框中不同数字识别的次数
    List_score02 = [[0]*8] * 6
    intnum02 = [0]*6
    TF = 1
    while(TF):
         #加载一帧图像
         img = sensor.snapshot()
         code = kpu.run_yolo2(task, img)
         if code:
             int_i = 0
             for i in code:
                 int_i +=1
                 a=img.draw_rectangle(i.rect())
                 a = lcd. display(img)
                 list1=list(i.rect())
                 b=(list1[0]+list1[2])/2
                 #对应的矩阵值加一
                 List_score02[int_i][int(classes[i.classid()])-1] += 1
                 print(List_score02[int_i])
                 #该目标框逐个数字分析是否出现次数到达10，即为该目标区域中的数字
                 for ii in range(8):
                    if(List_score02[int_i][ii] >= 10):
                        intnum02[int_i] = ii+1
                 #该目标区域中的数字是否是初始化识别的数字
                 if(intnum == intnum02[int_i]):
                 #判断位置，从而判断先做向右转
                    if(b < 75):
                        uart_A.write("l")
                        print("l")
                        TF = 0
                    if(b > 75):
                        uart_A.write("r")
                        print("r")
                        TF = 0
         else:
             a = lcd.display(img)
    return 0

#5678道路识别函数
def fivesixseveneight(intnum):
    #设置二维矩阵，存放每一个矩形框中不同数字识别的次数，一帧中最多有四个目标区域，但这里设置六个，防止有误识别的造成有很多矩形框程序暴死
    List_score02 = [[0]*8] * 6
    intnum02 = [0]*6
    TF = 2
    #5678道路识别要识别两次，传两次指令，两次直接通过延时函数断开
    while(TF):
         img = sensor.snapshot()
         code = kpu.run_yolo2(task, img)
         if code:
             int_i = 0
             for i in code:
                 int_i +=1
                 a=img.draw_rectangle(i.rect())
                 a = lcd. display(img)
                 list1=list(i.rect())
                 b=(list1[0]+list1[2])/2
                 List_score02[int_i][int(classes[i.classid()]) -1] += 1
                 print(List_score02[int_i])
                 for ii in range(8):
                    if(List_score02[int_i][ii] >= 10):
                        intnum02[int_i] = ii+1
                 if(intnum == intnum02[int_i]):
                    if(b < 75):
                        uart_A.write("l")
                        print("l")
                        TF -= 1
                        List_score02 = [[0]*8] * 6
                        intnum02 = [0]*6
                        time.sleep(3)
                    if(b > 75):
                        uart_A.write("r")
                        print("r")
                        TF -= 1
                        List_score02 = [[0]*8] * 6
                        intnum02 = [0]*6
                        time.sleep(3)
         else:
             a = lcd.display(img)
    return 0

#执行程序
intnum = begin(intnum)
time.sleep(3)
if(intnum == 3 or intnum == 4):
    threefour(intnum)
if(intnum == 5 or intnum == 6 or intnum ==7 or intnum == 8):
    fivesixseveneight(intnum)
uart_A.deinit()
del uart_A
a = kpu.deinit(task)

