import sensor, image, time,pyb
from pyb import UART,LED
red_threshold = (50, 34, 13, 42, -17, 20)
black_threshold = (0, 32, -28, 22, -6, 26)
sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QQVGA)
sensor.skip_frames(10)
sensor.set_hmirror(True)
sensor.set_vflip(True)
sensor.set_auto_whitebal(False)
clock = time.clock()
#----------------------------------------------------------
uart = UART(3,115200)
uart.init(115200, bits=8, parity=None, stop=1)
Size=100
#----------------------------------------------------------
def find_max(blobs):
    max_size=0
    for blob in blobs:
        if blob.pixels() > max_size:
            max_blob=blob
            max_size = blob.pixels()
    return max_blob
#----------------------------------------------------------
while(True):#找绿色
    clock.tick()
    img = sensor.snapshot()
    LED(3).off()
    LED(2).off()
    LED(1).off()
    blobs = img.find_blobs([red_threshold])
    break
    if uart.any():
       a = uart.readchar()
       if(a==97):
          print(a)
          Size=20
          LED(1).on()
          time.sleep_ms(10)
          break
    if blobs:
        b = find_max(blobs)
        if(b[4]>=Size):
           LED(3).on()
           LED(2).on()
           img.draw_rectangle(b[0:4])
           img.draw_cross(b[5], b[6])
           output_str1="[%d]" % b[5]
           uart.write(output_str1)
           print(b[5])
           time.sleep_ms(10)
while(True):
    clock.tick()
    img = sensor.snapshot()
    LED(3).off()
    LED(2).off()
    LED(1).off()
    blobs = img.find_blobs([black_threshold],roi = [0,20,160,100])
    if blobs:
        b = find_max(blobs)
        if(b[4]>=10):
            LED(3).on()
            LED(2).on()
            img.draw_rectangle(b[0:4])
            img.draw_cross(b[5], b[6])
            output_str1="[%d]" % b[5]
            uart.write(output_str1)
            print(b[5])
            time.sleep_ms(10)
