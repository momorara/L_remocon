#!/usr/bin/env python


"""
起動時にシグナル点灯
LED_on.txtファイルがあればLED点灯なければ、消灯

2023/01/08  start

"""

import time
import pigpio  # http://abyz.co.uk/rpi/pigpio/python.html
import getpass
import os


# ユーザー名を取得
user_name = getpass.getuser()
print('user_name', user_name)
path = '/home/' + user_name + '/L_remocon/'  # cronで起動する際には絶対パスが必要
# path = '/home/' + 'tk' + '/L_remocon/' # systemdで起動する際にはrootになり絶対パスが必要

# リモコン基板の表示用LED 現在はGPIO 5
LED = '12'
LED1 = '5'

LED = int(LED)
LED1 = int(LED1)

pi = pigpio.pi()  # Connect to Pi.
pi.set_mode(LED, pigpio.OUTPUT)
pi.set_mode(LED1, pigpio.OUTPUT)

def LED_on():
    pi.write(LED, 1) 
    pi.write(LED1, 1) 

def LED_off():
    pi.write(LED, 0)
    pi.write(LED1, 0)

# 起動時にLEDを点滅
for _ in range(6):
    LED_on()
    time.sleep(0.2)
    LED_off()
    time.sleep(0.1)

try:#ファイルを削除
    os.remove(path + 'LED_on.txt') 
except:
    pass
print('LED_on start')
on_off = 'off'

while True:
    if os.path.exists(path + 'LED_on.txt'):
        if on_off == 'off':
            LED_on()
            on_off = 'on'
            print(on_off)
    if not os.path.exists(path + 'LED_on.txt'):
        if on_off == 'on':
            LED_off()
            on_off = 'off'
            print(on_off)
    time.sleep(0.1)

pi.stop()
