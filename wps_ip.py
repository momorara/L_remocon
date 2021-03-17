"""
ラズパイをwpsで無線LANに加入させます

wps_set.py

2021/01/11  作成開始
2021/03/14  LED1対応

test1test2
scp -r wifi/*.py tk@192.168.68.122:/home/tk/wifi
scp -r wifi/*.py pi@192.168.68.121:/home/pi/wifi
scp -r wifi pi@192.168.68.107:/home/pi
scp -r wifi tk@192.168.68.107:/home/tk
scp -r aircontrol pi@192.168.68.131:/home/pi
"""
import RPi.GPIO as GPIO
import time
import subprocess
import sys
import os
from nobu_LIB import Lib_OLED

LED = 5
LED1 = 12
disp_size = 32 # or 64

def setup():
    GPIO.setwarnings(False)
    #set the gpio modes to BCM numbering
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(LED,GPIO.OUT,initial=GPIO.LOW)
    GPIO.setup(LED1,GPIO.OUT,initial=GPIO.LOW)
    return

#print message at the begining ---custom function
def print_message():
    print ('|********************************|')
    print ('|      wps_ip.py         2       |')
    print ('|********************************|')
    # print ('Program is running...')
    # print ('Please press Ctrl+C to end the program...')
    pass

def LedFlash(j,k):
    for i in range(j):
        GPIO.output(LED,GPIO.HIGH)
        time.sleep(0.1*k)
        GPIO.output(LED,GPIO.LOW)
        time.sleep(0.05*k)
        GPIO.output(LED1,GPIO.HIGH)
        time.sleep(0.1*k)
        GPIO.output(LED1,GPIO.LOW)
        time.sleep(0.05*k)

def wps_cmd(cmd):
    STATUS = subprocess.Popen(cmd, shell=True,  stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    out, err = STATUS.communicate()
    return out.rstrip('\n') , err

def OLED_disp(OLED_disp_text,timer=0):
    Lib_OLED.SSD1306(OLED_disp_text,disp_size)
    time.sleep(timer)

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
    
    print('step2')
    LedFlash(3,1)
    STATUS, err = wps_cmd(wlan0_wpa_state)
    if STATUS != 'COMPLETED':
        print(STATUS,'no conect')
        OLED_disp('no conect',5) 
        # LedFlash(3,1)
        sys.exit(0)
    LedFlash(3,1)
    ip, err = wps_cmd(wlan0_ip_address)
    print()
    print(ip)
    print('step3')
    try:
        OLED_disp(ip,10) # 10秒 ipを表示
    except:
        pass

# if run this script directly ,do:
if __name__ == '__main__':
    setup()
    try:
        main()
    #when 'Ctrl+C' is pressed,child program destroy() will be executed.
    except KeyboardInterrupt:
        print(e)
    except ValueError as e:
        print(e)
