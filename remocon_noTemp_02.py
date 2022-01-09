"""
汎用学習リモコン

air_set03 -> remocon_mode03_02.py-> remocon_mode03_03.py -> remocon_noTemp_01.py

制御は基本的に全てnode-redで行います。


2021/01/19  開発開始
2021/02/13  タイマー予約対応
            node-redで作ったタイマー予約ファィルを読み込み、時間が来たらIRを送出する。
            ファィルリロードはnode-redが'reload'をiR_comandに書いた時
2021/02/14  もくもく会にて、組み込み一応完成、あとはテストなり整理たね。
2021/02/16  node-redでreloadを書いていたが、反応が遅いので、
            node-redでyoyaku_reloadを起動して整理したのち、yoyaku_reloadがreloadをiR_comandに書くこととした
            それによる修正
2021/02/20  destroy_stopが無かったで関数名の修正
2021/02/23  UI予約活殺導入による改造
    02
2021/03/01  node-redでの処理を最小限にして、後はpythonに任せる。
    03
2021/03/04  UI連打の時 reloadがたくさん出る場合があり、すぐにフィァルをみにいくとタイミングにより
            正常にデータを弓込めない場合がある。排他処理をすれば良いけれど、time.sleep(15)で逃げる。
2021/03/17  「irrp」を「irrp_long」に統一する。
----------
2021/12/24  温度センサーを使わないバージョンとして再開発
2021/12/26  node-red2.1のフローが混じりエラーで悩んだ。
            modeFile.txtで快眠制御をコントロールするため、モード追記になっているのを
            現在モードのみファィルに記録する形に変更
2022/01/07  wifiだけでなく有線LANもipアドレス取得できるようにする。 


scp -r *.py pi@192.168.68.126:/home/pi/L_remocon

scp -r L_remocon pi@192.168.68.126:/home/pi
scp -r L_remocon tk@192.168.68.100:/home/tk
scp -r L_remocon/*.py tk@192.168.68.126:/home/tk/L_remocon
scp -r L_remocon/*.py pi@192.168.68.131:/home/pi/L_remocon
scp -r L_remocon tk@192.168.68.100:/home/tk

scp -r L_remocon/*.py pi@192.168.68.123:/home/pi/L_remocon
scp -r L_remocon pi@192.168.68.100:/home/pi

scp -r L_remocon/*.py pi@172.20.10.6:/home/pi/L_remocon
scp -r L_remocon pi@172.20.10.6:/home/pi
scp -r remocon*.py pi@192.168.68.107:/home/pi/L_remocon
"""
import RPi.GPIO as GPIO
import time
import subprocess
import sys
import datetime
import os
from nobu_LIB import Lib_OLED
# import Lib_OLED
import timeout_decorator
import unicodedata # 半角、全角の判定
import getpass

import ip_check_noOLED




# ユーザー名を取得
user_name = getpass.getuser()
print('user_name',user_name)
path = '/home/' + user_name + '/L_remocon/' # cronで起動する際には絶対パスが必要
# path = '/home/' + 'tk' + '/L_remocon/' # systemdで起動する際にはrootになり絶対パスが必要

disp_size = 32 # or 64
iR_LED = '22'
iR_sensor = '4'

# 表示用LED
LED = 12
LED1 = 5
GPIO.setwarnings(False)
#set the gpio modes to BCM numbering
GPIO.setmode(GPIO.BCM)
GPIO.setup(LED,GPIO.OUT,initial=GPIO.LOW)
GPIO.setup(LED1,GPIO.OUT,initial=GPIO.LOW)

###################log print#####################
# 自身のプログラム名からログファイル名を作る
import sys
args = sys.argv
logFileName = args[0].strip(".py") + "_log.csv"
print(logFileName)
# ログファイルにプログラム起動時間を記録
import csv
# 日本語文字化けするので、Shift_jisやめてみた。
f = open(logFileName, 'a')
csvWriter = csv.writer(f)
csvWriter.writerow([datetime.datetime.now(),'  program start!!'])
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

#print message at the begining ---custom function
def print_message():
    log_print ('|********************************|')
    log_print ('| remocon_noTemp_02.py    1      |')
    log_print ('|********************************|')
    # print('上限温度',temp_uper,'下限温度',temp_lower,'\n')
    print ('Program is running...')
    print ('Please press Ctrl+C to end the program...')

def cmd_read(mode='通常'):
    # リモコンデータを読み取る
    try:
        if mode=='通常':
            time.sleep(0.1)
            if not os.path.exists(path + 'iR_command.txt'):
                return 'no_cmd'
            with open(path + 'iR_command.txt') as f:
                cmd = f.read()
            print('cmd=',cmd)
            if not cmd in ['0','1','2','3','4','5','6','7','8','9','ok','play','reload\n','reload']:
                cmd = 'no_cmd' # 上記 以外は無視
                print('I do not know command')
            os.remove(path + 'iR_command.txt') #ファイルを削除
            return cmd
        else:
            if os.path.exists(path + 'iR_command.txt'):
                os_cmd = 'rm ' + path + 'iR_command.txt'
                os.system(os_cmd)
    except:
        return 'no_cmd'

def OLED_disp(OLED_disp_text,timer=0):
    # print('point0',OLED_disp_text)
    Lib_OLED.SSD1306(OLED_disp_text,disp_size)
    # print('point1')
    time.sleep(timer)

# def temp_read():
#     with open(path + 'temp_data_last.txt') as f:
#         try:
#             temp = float(f.read())
#             log_print('現在温度',temp)
#         except:
#             log_print('温度エラー')
#             temp = 99
#     return temp

def makeModeFile(mode):
    with open(path + 'modeFile.txt', 'w') as f:
        # mode += '\n'
        f.write(mode)
    #makeModeFile('mode選択')

def makeErrFile(mode):
    with open(path + 'errFile.txt', 'a') as f:
        mode += '\n'
        f.write(mode)
    #makeErrFile('mode選択')

@timeout_decorator.timeout(15)
# もし、iR発信し続ける様なことがあると、破損するので、その対策
def iR_send(send_comand):
    try:
        # cronで起動する際には絶対パスが必要
        # send_comand = 'python3 /home/pi/aircontrol/irrp.py -p -g22 -f ' + send_comand
        send_comand = path + send_comand
        send_comand = 'python3 ' + path + 'irrp_long.py -p -g' + iR_LED + ' -f ' + send_comand
        # 設定変更のスタート時間を記憶
        log_print(send_comand)
        # 設定変更の赤外線送出
        os.system(send_comand)
        return
    except:
        OLED_disp('iR送信エラー',2)
        destroy_stop()
        log_print('エラー発生')
        return

def jikan_to_int(jikan):
    # データを読み込み、プログラムで使える形に整えます。時間を文字から数字に変換します。
    print(jikan)
    for i in range(8):
        # print(i,jikan[i],type(jikan[i]))
        if jikan[i] =='':
            jikan[i] = 0
        else:
            jikan[i] = int(jikan[i])
        # print(i,jikan[i],type(jikan[i]))
    return jikan

def yoyaku_file_delete(del_filename):
    try:
        os.remove(path + del_filename)  #ファイルを削除
    except:
        pass  

def yoyaku_file_delete_all():
    yoyaku_file_delete('yoyaku.csv')    #予約データファイルを削除
    yoyaku_file_delete('yoyaku_sw.csv') #予約の活殺ファイルを削除
    yoyaku_file_delete('yoyaku_no.csv') #予約データの数　ファイルを削除
    yoyaku_file_delete('yoyaku_new.csv')#新規の予約データファイルを削除
    yoyaku_file_delete('yoyaku_del.csv')#予約データの削除対象noファイルを削除

def yoyaku_file_sakusei():
    # yoyakuファイルを作成
    with open(path + 'yoyaku.csv', 'a') as f:
        f.write('\n')
    with open(path + 'yoyaku_sw.csv', 'w') as f:
        f.write("0,0,0,0")
        f.write('\n')
    with open(path + 'yoyaku_no.csv', 'w') as f:
        f.write("0")
        f.write('\n')

def yoyaku_load():
    # yoyakuファィルを読み込み設定をロードする
    with open(path + 'yoyaku.csv', 'r') as csvfile:
        csv_reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        row1 = []
        for row in csv_reader:
            # print('#1=',','.join(row))
            if row == '' :
                print('#2=','non-data')
            pass
            row1 = row1 + row

        # print('#1=',row1)
        # 全ての''を削除した後に、karaを追加、後に数を12個にする
        kara = ['','','','','','','','','','','','','']
        row1 = ([s for s in row1 if s != ''] ) + kara
        # print('#2=',row1)
        row1 = row1[:12]
        # print('#3=',row1)
    return row1
    
def no_load():
    with open(path + 'yoyaku_no.csv', 'r') as csvfile:
        csv_reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        no1 = []
        for no in csv_reader:
            # print('#1=',','.join(row))
            if no == '' :
                print('#2=','non-data')
            pass
            no = no1 + no
        # print('no=',no)
    return no[0]

def sw_load():
    with open(path + 'yoyaku_sw.csv', 'r') as csvfile:
        csv_reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        sw1 = []
        for sw in csv_reader:
            # print('#1=',','.join(row))
            if sw == '' :
                print('#2=','non-data')
            pass
            sw1 = sw1 + sw
        sw1 = sw1[:4]
    print(sw1,len(sw1))
    # なぜかswが要素0になったらもう一度ファィルを読んでみる
    if len(sw1) == 0:
        time.sleep(0.5)
        with open(path + 'yoyaku_sw.csv', 'r') as csvfile:
            csv_reader = csv.reader(csvfile, delimiter=',', quotechar='"')
            sw1 = []
            for sw in csv_reader:
                # print('#1=',','.join(row))
                if sw == '' :
                    print('#2=','non-data')
                pass
                sw1 = sw1 + sw
            sw1 = sw1[:4]
        print(sw1,len(sw1))
    return sw1

#main function
def main():
    print_message()
    # OLED_disp('welcom remocon',2)
    print(path)

    # OLED_disp('test',2)
    # OLED_disp('point2',2)

    # 設定ファイルの削除
    yoyaku_file_delete_all()
    # 設定ファイルの初期化
    yoyaku_file_sakusei() # yoyaku.csv sw_data.csv yoyaku_no.csv 作成

    # タイマー予約 データを読み込み、プログラムで使える形に整えます。
    send_1,ji_1,fun_1, send_2,ji_2,fun_2, send_3,ji_3,fun_3, send_4,ji_4,fun_4 = yoyaku_load()
    jikan = [ji_1,fun_1, ji_2,fun_2, ji_3,fun_3, ji_4,fun_4]
    ji_1,fun_1, ji_2,fun_2, ji_3,fun_3, ji_4,fun_4 = jikan_to_int(jikan)
    print('yoyaku=',send_1,ji_1,fun_1, send_2,ji_2,fun_2, send_3,ji_3,fun_3, send_4,ji_4,fun_4)
    sw1,sw2,sw3,sw4= sw_load()
    print('sw=',sw1,sw2,sw3,sw4)
    no= no_load()
    print('no=',no)

    # exit(0)

    # モードファィルを初期化
    try:
        os.remove(path + 'modeFile.txt') #ファイルを削除
    except:
        pass
    with open(path + 'modeFile.txt', 'w') as f:
        mode = 'スタート' + '\n'
        f.write(mode)
    makeModeFile('mode選択')

    # エラーファィルを初期化
    try:
        os.remove(path + 'errFile.txt') #ファイルを削除
    except:
        pass
    with open(path + 'errFile.txt', 'w') as f:
        mode = 'スタート' + '\n'
        f.write(mode)
    makeErrFile('  ')

    cmd = ''
    cmd_read('reset')
    dt_now_izen = datetime.datetime.now()
    
    disp_mes_list = ['モードを選択','1:運用','7:WPS','8:IP表示',            '9:終了','選んでください']
    while True:
        for disp_mes in disp_mes_list:
            OLED_disp(disp_mes,2)
            # コマンド読み取り
            cmd = cmd_read()
            if cmd != 'no_cmd':
                break
            
        if cmd == '9':# シャットダウン
            OLED_disp('シャットダウン',2)
            OLED_disp(' ',0)
            log_print('シャットダウン')
            OLED_disp('1:する 9:戻る',2)
            cmd = ' '

            while cmd != '9':
                cmd = cmd_read()
                
                if cmd == '1':
                    OLED_disp('シャットダウン開始',1)
                    OLED_disp('20秒ほどかかります',2)
                    OLED_disp('下のラズパイ基板の',1)
                    OLED_disp('黄緑色LEDが消えたら',2)
                    OLED_disp('電源を切って下さい',1)
                    OLED_disp(' ...... ',1)
                    # 表示用LEDを点灯してみる
                    GPIO.output(LED ,GPIO.HIGH) # LED  on
                    GPIO.output(LED1,GPIO.HIGH) # LED1 on
                    OLED_disp('... ',1)
                    OLED_disp('黄緑LEDが消えたら',0)
                    # シャットダウンする場合は # を削除
                    subprocess.run('sudo shutdown now',shell=True)
                    cmd = 'no_cmd'
                else:
                    if cmd == '0':
                        OLED_disp('** 説明 **',2)
                        OLED_disp('安全に電源を',2)
                        OLED_disp('切るために',2)
                        OLED_disp('シャットダウンを',2)
                        OLED_disp('選んでください。',2)
                        OLED_disp('9で戻ります',2)
                        OLED_disp('1:する 9:戻る',2)
                    if cmd == '5':
                        OLED_disp(' ',0)
                        sys.exit(0)


        if cmd == '1':# 運用モード
            makeModeFile('運用 mode')
            OLED_disp('運用モード 9:戻',2)
            while cmd != '9':
                
                # # 温度表示
                # 現在温度 = str(int(temp_read()*10)/10) + '度'
                # OLED_disp(現在温度,2)


                dt_now = datetime.datetime.now()
                # タイマー予約を実行
                # print(dt_now_izen,dt_now.minute)
                if dt_now.minute != dt_now_izen:
                    print(sw1,sw2,sw3,sw4)
                    if (dt_now.hour == ji_1 and dt_now.minute == fun_1 ) and send_1 != '' and sw1 == "1":
                        iR_send(send_1)
                    if (dt_now.hour == ji_2 and dt_now.minute == fun_2 ) and send_2 != '' and sw2 == "1":
                        iR_send(send_2)
                    if (dt_now.hour == ji_3 and dt_now.minute == fun_3 ) and send_3 != '' and sw3 == "1":
                        iR_send(send_3)
                    if (dt_now.hour == ji_4 and dt_now.minute == fun_4 ) and send_4 != '' and sw4 == "1":
                        iR_send(send_4) 
                    # 同じ分に繰り返さないため
                    print(dt_now_izen,dt_now.minute,"タイマー予約をチェックしました。")
                    dt_now_izen = dt_now.minute


                cmd = cmd_read()
                if cmd == '0':# 運用モード 説明
                    OLED_disp('** 説明 **',2)
                    OLED_disp('運用モードでは',2)
                    # OLED_disp('時間と温度を',2)
                    OLED_disp('時間を',2)
                    OLED_disp('表示します。',2)
                    OLED_disp('制御は',2)
                    OLED_disp('スマホからになります',2)
                    OLED_disp('9で戻ります',2)

                if cmd == '9':
                    makeModeFile('mode選択')
                    break

                # 時間表示
                dt_now = datetime.datetime.now()
                zero = ''
                if len(str(dt_now.minute)) == 1:zero = '0'
                time_s = str(dt_now.hour) + ':' + zero + str(dt_now.minute)
                OLED_disp(time_s,2)

                # タイマー予約 データを読み込み、プログラムで使える形に整えます。
                if cmd == 'reload' or cmd == 'reload\n':
                    time.sleep(15)
                    print('reload受信')
                    send_1,ji_1,fun_1, send_2,ji_2,fun_2, send_3,ji_3,fun_3, send_4,ji_4,fun_4 = yoyaku_load()
                    jikan = [ji_1,fun_1, ji_2,fun_2, ji_3,fun_3, ji_4,fun_4]
                    ji_1,fun_1, ji_2,fun_2, ji_3,fun_3, ji_4,fun_4 = jikan_to_int(jikan)
                    print('yoyaku=',send_1,ji_1,fun_1, send_2,ji_2,fun_2, send_3,ji_3,fun_3, send_4,ji_4,fun_4)
                    sw1,sw2,sw3,sw4= sw_load()
                    print('sw=',sw1,sw2,sw3,sw4)
                    OLED_disp('予約変更完了',5)

        if cmd == '0':# モード 説明
            OLED_disp('** 説明 **',2)
            OLED_disp('先ずは、wifiに入りましょう',2)
            OLED_disp('WPS設定から、よろしく',2)
            OLED_disp('9で戻ります',2)

        if cmd == '7':# wps
            OLED_disp('wps始めます',2)
            OLED_disp('ルーターの',2)
            OLED_disp('WPSボタンを押してね',2)
            os_cmd = 'python3 ' + path + 'wps_set.py'
            os.system(os_cmd)
            cmd = '8'

        # wifi でも 有線でも対応可能 有線が優先です。
        if cmd == '8':# ip表示
            OLED_disp('ipアドレス',0)
            # os_cmd = 'python3 ' + path + 'wps_ip.py'
            # os.system(os_cmd)
            ip_adr = ip_check_noOLED.ip_check()
            print('ip_adr:',ip_adr)
            if ('not' in ip_adr) == False:
                OLED_disp(ip_adr,10)
            else:
                OLED_disp('no connect',5)

        # タイマー予約 データを読み込み、プログラムで使える形に整えます。
        if cmd == 'reload' or cmd == 'reload\n':
            time.sleep(15)
            send_1,ji_1,fun_1, send_2,ji_2,fun_2, send_3,ji_3,fun_3, send_4,ji_4,fun_4 = yoyaku_load()
            jikan = [ji_1,fun_1, ji_2,fun_2, ji_3,fun_3, ji_4,fun_4]
            ji_1,fun_1, ji_2,fun_2, ji_3,fun_3, ji_4,fun_4 = jikan_to_int(jikan)
            print('yoyaku=',send_1,ji_1,fun_1, send_2,ji_2,fun_2, send_3,ji_3,fun_3, send_4,ji_4,fun_4)
            sw1,sw2,sw3,sw4= sw_load()
            print('sw=',sw1,sw2,sw3,sw4)
            OLED_disp('予約変更完了',5)

        cmd = '29'

#define a destroy function for clean up everything after the script finished
def destroy_stop():
    #release resource
    GPIO.cleanup()
#
# if run this script directly ,do:
if __name__ == '__main__':
    # setup()
    try:
        main()
        GPIO.cleanup()
    #when 'Ctrl+C' is pressed,child program destroy() will be executed.
    except KeyboardInterrupt:
        destroy_stop()
    except ValueError as e:
        log_print(e)
        destroy_stop()