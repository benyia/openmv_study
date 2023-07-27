import sensor, image, time

from pid import PID
from pyb import Servo

pan_servo=Servo(1)#P7控制左右
tilt_servo=Servo(2)#P8控制上下

pan_servo.calibration(500,2500,500)
tilt_servo.calibration(500,2500,500)

red_threshold  = (19, 0, -8, 37, -37, 8)

pan_pid = PID(p=0.5, i=0, imax=90) #脱机运行或者禁用图像传输，使用这个PID
tilt_pid = PID(p=0.5, i=0, imax=90) #脱机运行或者禁用图像传输，使用这个PID
#pan_pid = PID(p=0.1, i=0, imax=90)#在线调试使用这个PID
#tilt_pid = PID(p=0.1, i=0, imax=90)#在线调试使用这个PID

sensor.reset() # Initialize the camera sensor.
sensor.set_pixformat(sensor.RGB565) # use RGB565.
sensor.set_framesize(sensor.HQVGA) # use QQVGA for speed.
sensor.skip_frames(10) # Let new settings take affect.
sensor.set_auto_whitebal(False) # turn this off.
sensor.set_hmirror(True)
sensor.set_vflip(True)
clock = time.clock() # Tracks FPS.

def find_max(blobs):
    max_size=0
    for blob in blobs:
        if blob[2]*blob[3] > max_size:
            max_blob=blob
            max_size = blob[2]*blob[3]
    return max_blob


while(True):
    clock.tick() # Track elapsed milliseconds between snapshots().
    img = sensor.snapshot() # Take a picture and return the image.

    blobs = img.find_blobs([red_threshold])
    if blobs:
        max_blob = find_max(blobs)

        cx = max_blob[5]
        cy = max_blob[6]
        cw = max_blob[2]
        ch = max_blob[3]
        pan_error = max_blob.cx()-img.width()/2
        tilt_error = max_blob.cy()-img.height()/2
        print(cx,cy,cw,ch)
        print("pan_error: ", pan_error)

        img.draw_rectangle(max_blob.rect()) # rect
        img.draw_cross(max_blob.cx(), max_blob.cy()) # cx, cy

        pan_output=pan_pid.get_pid(pan_error,1)/2
        tilt_output=tilt_pid.get_pid(tilt_error,1)
        print("pan_output",pan_output)
        pan_servo.angle(pan_servo.angle()+pan_output)
        tilt_servo.angle(tilt_servo.angle()-tilt_output)
