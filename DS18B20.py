# -*- coding: utf-8 -*-
"""
温度センサーDS18B20のデータ取得
DS18B20.py

step1 
    必要に応じ、raspi-configで1Wireを生かす。
step2 
    sudo nano /boot/config.txt として、次の行を追加
    dtoverlay=w1-gpio-pullup,gpiopin=14
    reboot
step3
    デバイスを接続して、28-があることを確認
    ls -l /sys/bus/w1/devices/
    lrwxrwxrwx 1 root root 0  5月 25 21:05 28-00000a71dc9e -> ../../../devices/w1_bus_master1/28-00000a71dc9e
    lrwxrwxrwx 1 root root 0  5月 25 21:02 w1_bus_master1 -> ../../../devices/w1_bus_master1
    28-00000xxxxxがあれば、OK
step4
    cat /sys/bus/w1/devices/28-00000a71dc9e/w1_slave
    ba 01 4b 46 7f ff 06 10 d0 : crc=d0 YES
    ba 01 4b 46 7f ff 06 10 d0 t=27625 ←これを1000で割ると摂氏になる。

参考hp
https://qiita.com/MagurosanTeam/items/f76a65f7eb4e27d44b5f
https://qiita.com/masato/items/cf5a27af696a27b73b86


2020/05/25  1-Wireやってみた
2020/07/13  赤外線リモコンの一貫で、改造    GPIO #13にした
2020/09/18  ユーザー名変更に対応
2021/01/07  あとで数字を利用する際に小数点以下1桁で表示するようにした


"""
import os
import glob
import time
import subprocess
import datetime
import getpass

# ユーザー名を取得
user_name = getpass.getuser()
print('user_name',user_name)
path = '/home/' + user_name + '/L_remocon/' # cronで起動する際には絶対パスが必要
# path = '/home/' + 'tk' + '/L_remocon/' # systemdで起動する際にはrootになり絶対パスが必要

disp_size = 32 # or 64
iR_LED = 22
iR_sensor = 4

# 1WデバイスのGPIOはconfigで指定すること
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'

def read_temp_raw():
    catdata = subprocess.Popen(['cat',device_file], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out,err = catdata.communicate()
    out_decode = out.decode('utf-8')
    lines = out_decode.split('\n')
    return lines

def read_temp():
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        # temp_f = temp_c * 9.0 / 5.0 + 32.0
        # return temp_c, temp_f
        return temp_c

while True:
    dt_now = datetime.datetime.now()
    # s = "celsius: {0:.3f}, fahrenheit: {1:.3f}"
    s = "摂氏: {0:.1f}"
    temp = read_temp()
    # print(s.format(*temp))
    # print(s.format(temp),"  :" ,dt_now)
    print(dt_now.strftime("%Y/%m/%d %H:%M"),"  :",s.format(temp))

    #####################################
    # # 最新のデータを一つだけ入れたファイルを作る
    temp_s = dt_now.strftime("%Y/%m/%d %H:%M") + "  :" + s.format(temp) + '\n' 
    with open(path + 'temp_data.txt', mode='a') as f:
            f.write(temp_s)
    with open(path + 'temp_data_last.txt', mode='w') as f:
        s = "{0:.1f}"
        temp_s = s.format(temp)
        f.write(temp_s)
        # f.write(dt_now.strftime("%Y/%m/%d %H:%M"))
    # SendInfoRaspi.py に乗せる
    #####################################

    time.sleep(60)
    # テスト 10秒周期
    # time.sleep(10)