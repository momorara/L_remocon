"""
ip_check.py　

2022/01/04　start
2022/01/07  ipgetにてipアドレスを取得
            wpsはしない


ipアドレスをipgetにて取得、5秒5回試してダメならあきらめる。
ライブラリと使用する。
返り値は　ipアドレス or  in not


scp -r ip_che*.py pi@192.168.68.107:/home/pi/L_remocon
"""

import subprocess
import sys
import os
import time
import getpass


# sudo ifconfig wlan0 down
# sudo ifconfig wlan0 up
os.system('sudo ifconfig wlan0 up')
time.sleep(5)

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
                pass
                # print('00',ip_adr)
            else:
                ip_adr = ip_adr.replace('/24','')
                ip_adr = ip_adr.replace('/28','')
                # print('01 ip_adr:',ip_adr)
        except :
            pass
            # print('02',ip_adr)
        count = count +1
        # print('1',count,ip_adr)
        if count >5 or ('not' in ip_adr) == False:
            return ip_adr
        else:
            os.system('sudo ifconfig wlan0 up')
            time.sleep(5)

    # print('2',ip_adr)
    return ip_adr

def main():
    ip_adr = ip_check()
    print('ip_adr:',ip_adr)

if __name__ == '__main__':
    main()
