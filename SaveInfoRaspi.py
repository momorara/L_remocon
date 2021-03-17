#main function
#!/usr/bin/python

"""
###########################################################################
ラズパイの情報を収集し、ファィルに書き込む
cpu_temp_data.txt
cpu_rate_data.txt にデータを上書きする。
それを、node-redで表示する

#Filename      :SaveInfoRaspi.py
#Description   :CPU温度、CPU使用率
#Update        :2021/01/17  作成開始
                2021/02/08  修正、整理

                
scp -r GPIO/*.py tk@192.168.68.100:/home/tk/GPIO
scp -r GPIO/*.py pi@172.20.10.6:/home/pi/GPIO
scp -r L_remocon pi@172.20.10.6:/home/pi
scp -r L_remocon/*.py pi@172.20.10.6:/home/pi/L_remocon
############################################################################
"""
# ライブラリの読み込み
import subprocess
import time 
import datetime
import os

# ユーザー名を取得
import getpass
user_name = getpass.getuser()
print('user_name',user_name)
path = '/home/' + user_name + '/L_remocon/' # cronで起動する際には絶対パスが必要

###################log print#####################
# 自身のプログラム名からログファイル名を作る
import sys
args = sys.argv
logFileName = args[0].strip(".py") + "_log.csv"
# ログファイルにプログラム起動時間を記録
import csv
# 日本語文字化けするので、Shift_jisやめてみた。
f = open(logFileName, 'a')
csvWriter = csv.writer(f)
#csvWriter.writerow([datetime.datetime.now(),'  program start!!'])
f.close()
#----------------------------------------------
def log_print(msg1="",msg2="",msg3=""):
    # エラーメッセージなどをプリントする際に、ログファイルも作る
    # ３つまでのデータに対応
    print(msg1,msg2,msg3)
    # f = open(logFileName, 'a',encoding="Shift_jis") 
    # 日本語文字化けするので、Shift_jisやめてみた。
    f = open(logFileName, 'a')
    csvWriter = csv.writer(f)
    csvWriter.writerow([datetime.datetime.now(),msg1,msg2,msg3])
    f.close()
################################################

#ラズパイ情報取得
def RaspiInfo():
    p = subprocess.Popen(
        "cat /proc/cpuinfo|grep Model",
        #stdin=subprocess.PIPE
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, 
        env={'LANG':'C'},
        shell=True
        )
    out, err = p.communicate()
    # b'Model\t\t: Raspberry Pi 3 Model B Plus Rev 1.3\n'
    # Piから1.3までを切り出す。
    str_out = out.decode("ascii", "ignore")
    # print(str_out)
    # Piを見つける
    fd1 = str_out.find('Pi')
    # print(fd1)
    str_out1 = str_out[fd1:-1]
    # Revを見つける
    fd2 = str_out1.find('Rev')
    str_out2 = str_out1[:fd2]
    # print(str_out2)
    str_out3 = str_out2.replace(" ", "")
    str_out4 = str_out3.replace("Model", "")
    str_out5 = str_out4.replace("Plus", "+")
    # 全てのラズパイの文字数を合わせる
    if len(str_out5) == 4: str_out5 = str_out5 + ' '
    return str_out5

#cpu情報取得
def CpuInfo():
    CpuRateList = gCpuUsage.get()
    CpuRate     = CpuRateList[0]
    CpuRate_str = " %3d" % CpuRate
    del CpuRateList[0]
    CpuTemp     = GetCpuTemp()
    Info_str =  CpuTemp + CpuRate_str + "% "
    CpuTemp = float(CpuTemp[5:9])
    return CpuTemp,CpuRate_str,Info_str.replace(": ", ":")

def GetCpuTemp():
    Cmd = 'vcgencmd measure_temp'
    result = subprocess.Popen(Cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    Rstdout ,Rstderr = result.communicate()
    CpuTemp = Rstdout.split()
    # 'c を削る
    # print(CpuTemp[0].replace("C","")[:-1])
    return CpuTemp[0].replace("C","")[:-1]

class CpuUsage:
    def __init__(self):
        self._TckList    = GetCpuStat()
    def get(self):
        TckListPre       = self._TckList
        TckListNow       = GetCpuStat()
        self._TckList    = TckListNow
        CpuRateList = []
        for (TckNow, TckPre) in zip(TckListNow, TckListPre):
            TckDiff = [ Now - Pre for (Now , Pre) in zip(TckNow, TckPre) ]
            TckBusy = TckDiff[0]
            TckAll  = TckDiff[1]
            CpuRate = int(TckBusy*100/TckAll)
            CpuRateList.append( CpuRate )
        return CpuRateList

def GetCpuStat():
    Cmd = 'cat /proc/stat | grep cpu'
    result = subprocess.Popen(Cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    Rstdout ,Rstderr = result.communicate()
    LineList = Rstdout.splitlines()

    TckList = []
    for Line in LineList:
        ItemList = Line.split()
        TckIdle = int(ItemList[4])
        TckBusy = int(ItemList[1])+int(ItemList[2])+int(ItemList[3])
        TckAll  = TckBusy + TckIdle
        TckList.append( [ TckBusy ,TckAll ] )
    return  TckList

def main():
    #イニシャライズ処理 
    # cronで毎分起動するので、毎正分を少しずらす 
    time.sleep(17)      # Receiveミスがたまにあるので、送信を少し早くする。

    #ラズパイ情報取得
    Raspi_info = RaspiInfo()
    print(Raspi_info)

    #cpu情報取得
    # プログラム起動直後にデータ収集すると、大きな負荷率となってしまう
    # なので、一秒程度時間をおくと良い。
    time.sleep(2)    # Receiveミスがたまにあるので、送信を少し早くする。
    cpu_temp,cpu_rate,cpu_info = CpuInfo()
    print('1:',cpu_info)
    print('2:',cpu_temp)
    print('3:',cpu_rate)

    dt_now = datetime.datetime.now()
    # s = "celsius: {0:.3f}, fahrenheit: {1:.3f}"
    s = "摂氏: {0:.1f}"
    temp = cpu_temp
    # print(s.format(*temp))
    # print(s.format(temp),"  :" ,dt_now)
    print(dt_now.strftime("%Y/%m/%d %H:%M"),"  :",s.format(temp))
    #####################################
    # # 最新のデータを一つだけ入れたファイルを作る
    temp_s = dt_now.strftime("%Y/%m/%d %H:%M") + "  :" + s.format(temp) + '\n' 
    with open(path + 'cpu_temp_data.txt', mode='w') as f:
            f.write(temp_s)
    # with open(path + 'temp_data_last.txt', mode='w') as f:
    #     s = "{0:.1f}"
    #     temp_s = s.format(temp)
    #     f.write(temp_s)
        # f.write(dt_now.strftime("%Y/%m/%d %H:%M"))
    # SendInfoRaspi.py に乗せる
    #####################################

    print(dt_now.strftime("%Y/%m/%d %H:%M"),"  :",cpu_rate)
    #####################################
    # # 最新のデータを一つだけ入れたファイルを作る
    temp_s = dt_now.strftime("%Y/%m/%d %H:%M") + "  :" + cpu_rate + '\n' 
    with open(path + 'cpu_rate_data.txt', mode='w') as f:
            f.write(temp_s)
    # with open(path + 'temp_data_last.txt', mode='w') as f:
    #     s = "{0:.1f}"
    #     temp_s = s.format(temp)
    #     f.write(temp_s)
        # f.write(dt_now.strftime("%Y/%m/%d %H:%M"))
    # SendInfoRaspi.py に乗せる
    #####################################

    print(path)



def destroy():
    pass
#
# if run this script directly ,do:
if __name__ == '__main__':

    gCpuUsage = CpuUsage()       # 初期化

    try:
        main()
    #when 'Ctrl+C' is pressed,child program destroy() will be executed.
    except KeyboardInterrupt:
        print('キーボード押されました。')
        destroy()
    except ValueError as e:
        log_print(e)


   
