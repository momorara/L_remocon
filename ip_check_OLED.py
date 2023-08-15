"""
ip_check.py

2022/01/04 start
2022/01/07  ipgetにてipアドレスを取得
            ipアドレス取得できない場合はwpsを試す
            
pip3 install ipget

wps_set.pyを使って、ipが分かっているか否かを確認する。
ipが分かっていれば、ipを表示して終了。

ip分かっていなければ、
wpsモードに入り5回トライする。

LEDが点灯している間にルーターのwpsボタンを押す。
ip取得に成功すれば、ipを表示して終了。
"""

import subprocess
import sys
import os
import time
import getpass
from nobu_LIB import Lib_OLED


disp_size = 32 # or 64
def OLED_disp(OLED_disp_text,timer=0):
    # print('point0',OLED_disp_text)
    Lib_OLED.SSD1306(OLED_disp_text,disp_size)
    # print('point1')
    time.sleep(timer)

OLED_disp('ipアドレス確認',1)

# sudo ifconfig wlan0 down
# sudo ifconfig wlan0 up
# os.system('sudo ifconfig wlan0 down')
# time.sleep(3)
os.system('sudo ifconfig wlan0 up')
# time.sleep(20)

# ipgetを使って、ipアドレスを取得
import ipget
# ipアドレスをipgetにて取得、5秒5回試してダメならあきらめる。
def ip_check():
    count = 0
    ip_adr = 'not'
    while 'not' in ip_adr:
        try:
            a = ipget.ipget()
            ip_adr = a.ipaddr("eth0")
            if 'not' in ip_adr:
                print('00',ip_adr)
            else:
                ip_adr = ip_adr.replace('/24','')
                ip_adr = ip_adr.replace('/28','')
                print('01 ip_adr:',ip_adr)
        except :
            print('02',ip_adr)
        count = count +1
        print('1',count,ip_adr)
        if ('not' in ip_adr) == False:
            break
        if count >5 :
            ip_adr = 'noconnect'
            break
        os.system('sudo ifconfig wlan0 down')
        time.sleep(3)
        os.system('sudo ifconfig wlan0 up')
        time.sleep(20)
    return ip_adr

ip_adr = ip_check()
print('2',ip_adr)
OLED_disp(ip_adr,0)
if  ip_adr != 'noconnect':
    exit(0)

# ユーザー名を取得
user_name = getpass.getuser()
print('user_name',user_name)
path = '/home/' + user_name + '/L_remocon/' # cronで起動する際には絶対パスが必要
# path = '/home/' + 'tk' + '/L_remocon/' # systemdで起動する際にはrootになり絶対パスが必要

OLED_disp('少々お待ち下さい',2)
OLED_disp('wifi確認します',5)

os.system('sudo ifconfig wlan0 down')
time.sleep(3)
os.system('sudo ifconfig wlan0 up')
time.sleep(20)

# ipアドレス取得状態を確認
wlan0_wpa_state = '/sbin/wpa_cli -i wlan0 status | grep wpa_state= | cut -d = -f 2'
STATUS = subprocess.Popen(wlan0_wpa_state, shell=True,  stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
out, err = STATUS.communicate()
print('1:',out,':', err)

# out = 'COMPLETED' ならipアドレス取得済み それ以外は無効
if out == 'COMPLETED\n' :
    ip_adr = ip_check()
    print('3',ip_adr)
    OLED_disp(ip_adr,0)
    exit(0)

OLED_disp('LED点灯でWPSを押す',2)
while out != 'COMPLETED\n':
    os.system('sudo ifconfig wlan0 down')
    time.sleep(3)
    os.system('sudo ifconfig wlan0 up')
    time.sleep(20)

    # ipアドレス取得状態を確認
    wlan0_wpa_state = '/sbin/wpa_cli -i wlan0 status | grep wpa_state= | cut -d = -f 2'
    STATUS = subprocess.Popen(wlan0_wpa_state, shell=True,  stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    out, err = STATUS.communicate()
    print(out, err)

    if out != 'COMPLETED\n':
        # wpsを実行してipアドレスを取得する
        os_cmd = 'python3 ' + path + 'wps_set.py'
        os.system(os_cmd)
    
    # ipアドレス取得状態を確認
    wlan0_wpa_state = '/sbin/wpa_cli -i wlan0 status | grep wpa_state= | cut -d = -f 2'
    STATUS = subprocess.Popen(wlan0_wpa_state, shell=True,  stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    out, err = STATUS.communicate()
    print(out, err)

ip_adr = ip_check()
print('3',ip_adr)
OLED_disp(ip_adr,0)
exit(0)

