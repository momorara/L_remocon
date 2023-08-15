"""
ラズパイをwpsで無線LANに加入させます

wps_set.py

2021/01/11  作成開始
2021/03/14  LED1対応
            ipを取得
2023/01/06  RPi.GPIOを止めた
2023/01/08  pigpioを使用

scp -r wifi/*.py tk@192.168.68.122:/home/tk/wifi
scp -r wifi/*.py pi@192.168.68.121:/home/pi/wifi
scp -r wifi pi@192.168.68.107:/home/pi
scp -r wifi tk@192.168.68.107:/home/tk
scp -r aircontrol pi@192.168.68.131:/home/pi
scp -r L_remocon-noTemp/L_remocon/*.py pi@192.168.68.116:/home/pi/L_remocon
"""
# import RPi.GPIO as GPIO
import pigpio 
import time
import subprocess
import sys
import os
from nobu_LIB import Lib_OLED


LED = 5
LED1 = 12


disp_size = 32 # or 64
def OLED_disp(OLED_disp_text,timer=0):
    # print('point0',OLED_disp_text)
    Lib_OLED.SSD1306(OLED_disp_text,disp_size)
    # print('point1')
    time.sleep(timer)

def setup():
    # GPIO.setwarnings(False)
    # #set the gpio modes to BCM numberiset
    # GPIO.setmode(GPIO.BCM)
    # GPIO.setup(LED,GPIO.OUT,initial=GPIO.LOW)
    # GPIO.setup(LED1,GPIO.OUT,initial=GPIO.LOW)
    pi = pigpio.pi()  # Connect to Pi.
    pi.set_mode(LED, pigpio.OUTPUT)
    pi.set_mode(LED1, pigpio.OUTPUT)
    return

def LED_on():
    pi.write(LED, 1) 
    pi.write(LED1, 1) 

def LED_off():
    pi.write(LED, 0)
    pi.write(LED1, 0)

#print message at the begining ---custom function
def print_message():
    print ('|********************************|')
    print ('|      wps_set.py         2      |')
    print ('|********************************|')
    # print ('Program is running...')
    # print ('Please press Ctrl+C to end the program...')
    pass

def LedFlash(j,k):
    for i in range(j):
        # GPIO.output(LED,GPIO.HIGH)
        # time.sleep(0.1*k)
        # GPIO.output(LED,GPIO.LOW)
        # time.sleep(0.05*k)
        # GPIO.output(LED1,GPIO.HIGH)
        # time.sleep(0.1*k)
        # GPIO.output(LED1,GPIO.LOW)
        time.sleep(0.05*k)

def wps_cmd(cmd):
    STATUS = subprocess.Popen(cmd, shell=True,  stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    out, err = STATUS.communicate()
    return out.rstrip('\n') , err

# *** WPSボタンを押す
# /sbin/wpa_cli -i wlan0 wps_pbc

# *** wlan ステータスを取り出す
# wpa_cli -i wlan0 status | grep wpa_state= | cut -d = -f 2
# COMPLETED or INACTIVE

# *** ip_address を取り出す
# wpa_cli -i wlan0 status | grep ip_address= | cut -d = -f 2
# 192.168.68.120とか

#main function
print_message()
def main():

    wlan0_wps = '/sbin/wpa_cli -i wlan0 wps_pbc'
    wlan0_status = '/sbin/wpa_cli -i wlan0 status'
    wlan0_wpa_state = '/sbin/wpa_cli -i wlan0 status | grep wpa_state= | cut -d = -f 2'
    wlan0_ip_address = '/sbin/wpa_cli -i wlan0 status | grep ip_address= | cut -d = -f 2'

    out, err = wps_cmd(wlan0_status)
    print()
    print(out, err)
    print()
    
    STATUS, err = wps_cmd(wlan0_wpa_state)
    if STATUS == 'COMPLETED':
        print(STATUS,'既に接続できているのでwpsはやめます')
        LedFlash(3,1)
        sys.exit(0)

    out, err = wps_cmd(wlan0_ip_address)
    print()
    print(out, err)

    # wpsを始める合図としてLEDを10回点滅
    # wpsを始めるとLED連続点灯
    LedFlash(10,1)
    # sys.exit(0)

    # 20秒周期でWifi接続が確立したかチェックする
    # 5回やってダメなら諦める
    count= 5
    wps_cmd(wlan0_wps) #wpsボタンを押す
    while True:
        # count_ = 5-count
        # disp = 'wps' + str(count_) + '回目'
        # OLED_disp(disp,0)

        # GPIO.output(LED1,GPIO.HIGH)
        LED_on()
        time.sleep(10) # wpsボタンを押してから10秒待ち確認
        STATUS, err = wps_cmd(wlan0_wpa_state)
        print(STATUS, 6-count)
        # print(type(STATUS),STATUS)
        if STATUS != 'COMPLETED':
            # 接続失敗
            print(6-count,'回 wps失敗')
            # GPIO.output(LED,GPIO.LOW)
            # GPIO.output(LED1,GPIO.LOW)
            LED_off()
            time.sleep(10) # 失敗したら10秒待って再度 wpsボタンを押す
            wps_cmd(wlan0_wps) #wpsボタンを押す
        if STATUS == 'COMPLETED':
            # GPIO.output(LED,GPIO.LOW)
            # GPIO.output(LED1,GPIO.LOW)
            LED_off()
            # 接続成功
            print(STATUS,6-count,'回目でwps成功')
            STATUS, err = wps_cmd(wlan0_ip_address) 
            print(STATUS)
            # wps成功したら10回点滅
            LedFlash(10,1)
            sys.exit(0)
        count = count - 1
        if count < 0 :
            print('wps失敗')
            # GPIO.output(LED,GPIO.LOW)
            # GPIO.output(LED1,GPIO.LOW)
            LED_off()
            sys.exit(0)



# if run this script directly ,do:
if __name__ == '__main__':
    setup()
    try:
        main()
    #when 'Ctrl+C' is pressed,child program destroy() will be executed.
    except KeyboardInterrupt:
        # print(e)
        pass
    except ValueError as e:
        print(e)
