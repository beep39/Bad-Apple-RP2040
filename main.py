from machine import Pin, I2C
from ssd1306 import SSD1306_I2C
import time, gc

i2c  = I2C(1, scl=Pin(23), sda=Pin(22), freq=40000)
oled = SSD1306_I2C(72, 40, i2c)
oled.fill(0)

with open('movie.bin','rb') as f:
    h = f.read(4)
    fps = h[0]
    frames_count = h[1]+h[2]*256
    frame_time = 1000//fps
    frame_size = h[3]*2
    framebuffer = oled.buffer
    buffer = bytearray(len(framebuffer))
    mvb = memoryview(buffer)
    while True:
        play_time = 0
        t0 = time.ticks_ms()
        for i in range(frames_count):
            f.readinto(mvb[:frame_size+1])
            off = 0
            for j in range(0, frame_size, 2):
                p = buffer[j]
                fr = off
                off += buffer[j+1]
                for k in range(fr, off):
                    framebuffer[k] = p
            frame_size = buffer[frame_size]*2
            play_time += frame_time
            st = (play_time - time.ticks_diff(time.ticks_ms(), t0))
            if st > 0:
                time.sleep_ms(st)
            oled.show()
        f.seek(4)
        gc.collect()
