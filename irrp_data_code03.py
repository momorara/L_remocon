#!/usr/bin/env python

# irrp.py
# 2015-12-21
# Public Domain

"""
irrp_data_code03.py

リモコンコマンド受信

プログラム一本化 使用

2020/07/27  irrp.pyを改造して、以下の機能を実現する。irrp_r_data.py
            *1.受信データからrawデータを保存する。
               'python3 irrp_r_data.py -r -g4 -f receive r_data --no-confirm --post 130'
               起動後、receiveファイルがあれば、なくなるまで待って
               無ければ、受信待ちに入る。
               リモコンを受信したらファイルを作って、最初に戻る。
                - 一回めはちゃんと受信データができるが、2回めからは0,がついてしまう。
2020/08/14      初期化ルーチンを繰り返しループに入れたらうまく行きました。論理はわからんけど....
            *1-2 高速化のためrawデータをそのまま保存せずにコード化して保存する。

            irrp_data_code01.py
            削除 2.保存されたrawデータを01コードに変換する。
            *3.リモコンのrawデータを事前に01コードにして保存しておく
               ファイルを読み込み、01コードにして持っておく
               複数ファイル対応とした。2020/08/17
            *4. 01コードと受信01コードを比較して、合致するものがあれば、そのボタンを押されたと判定する。
               receiveファイルを監視して、なければ、出来るまで待つ。
               receiveファイルが出来れば、01コードに変換して、oso 01コードと比較して、合致すれば
               そのコマンド名を取得する。
               receiveファイルは読み込み後削除する。
               4の最初に戻り繰り返す。
               取得したコマンド名は後着優先として上書きする。
            5.リモコンコマンドを処理するプログラムは、コマンドを待ち、あれば処理して削除を繰り返す。

2020/08/16  プログラム名だけで起動する様にした。  
2020/08/19  プログラム一本化
2020/09/11  iR GPIOを変数設定とした。
2020/09/18  ユーザー名変更に対応
2020/10/11  iR受信時にピープ音を鳴らす
2021/03/14  LED,LED1のgpio設定が抜けていた
2021/04/11  リモコンfileを自動選定する デフォルトは ali-w



pigpiod のインストール
sudo apt-get install pigpio

コピースクリプト
scp -r remocon/irrp_data_code03.py pi@192.168.68.135:/home/pi/remocon
scp -r aircontrol pi@192.168.68.131:/home/pi
scp -r aircontrol tk@192.168.68.124:/home/tk
scp -r L_remocon/irrp_data_code03.py pi@192.168.68.128:/home/pi/L_remocon
scp -r L_remocon pi@192.168.68.126:/home/pi
python3 irrp_data_code03.py
"""

import time
import json
import os
import argparse
import datetime
# from nobu_LIB import Lib_OLED
# disp_size = 'SSD1306_128_32'
import pigpio # http://abyz.co.uk/rpi/pigpio/python.html
import getpass


# ユーザー名を取得
user_name = getpass.getuser()
print('user_name',user_name)
path = '/home/' + user_name + '/L_remocon/' # cronで起動する際には絶対パスが必要
# path = '/home/' + 'tk' + '/L_remocon/' # systemdで起動する際にはrootになり絶対パスが必要

disp_size = 32 # or 64
iR_LED = '22'
LED = '12'
LED1 = '5'
iR_sensor = '4'
beep = '6'
beep2 = '18'

# FILE=[path + 'oso'] # Car mp3 と表記のあるリモコン
# FILE=[path + 'ali'] # 黒地のaliリモコン
FILE=[path + 'ali-w'] # 白地のaliリモコン

# リモコンfileを自動選定
if os.path.exists(path + 'ali-w'):
    FILE = [path + 'ali-w'] # 白地のaliリモコン
else:
    if os.path.exists(path + 'oso'):
        FILE = [path + 'oso'] # osoのaliリモコン
    else:
        if os.path.exists(path + 'ali'):
            FILE = [path + 'ali'] # 黒地のaliリモコン


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

GPIO       = int(iR_sensor)     #args.gpio
# FILE       = 'プログラムで決定'  #args.file
GLITCH     = 100    #args.glitch
PRE_MS     = 200    #args.pre
POST_MS    = 130    #args.post
FREQ       = 38     #args.freq
VERBOSE    = False  #args.verbose
SHORT      = 20     #args.short
GAP_MS     = 100    #args.gap
NO_CONFIRM = True   #args.no_confirm
TOLERANCE  = 15     #args.tolerance

def carrier(gpio, frequency, micros):
   #　キャリア方形波を生成します。
   wf = []
   cycle = 1000.0 / frequency
   cycles = int(round(micros/cycle))
   on = int(round(cycle / 2.0))
   sofar = 0
   for c in range(cycles):
      target = int(round((c+1)*cycle))
      sofar += on
      off = target - sofar
      sofar += off
      wf.append(pigpio.pulse(1<<gpio, 0, on))
      wf.append(pigpio.pulse(0, 1<<gpio, off))
   return wf

def normalise(c):
   if VERBOSE:
      print("before normalise", c)
   entries = len(c)
   p = [0]*entries # Set all entries not processed.
   for i in range(entries):
      if not p[i]: # Not processed?
         v = c[i]
         tot = v
         similar = 1.0
         # Find all pulses with similar lengths to the start pulse.
         for j in range(i+2, entries, 2):
            if not p[j]: # Unprocessed.
               if (c[j]*TOLER_MIN) < v < (c[j]*TOLER_MAX): # Similar.
                  tot = tot + c[j]
                  similar += 1.0
         # Calculate the average pulse length.
         newv = round(tot / similar, 2)
         c[i] = newv
         # Set all similar pulses to the average value.
         for j in range(i+2, entries, 2):
            if not p[j]: # Unprocessed.
               if (c[j]*TOLER_MIN) < v < (c[j]*TOLER_MAX): # Similar.
                  c[j] = newv
                  p[j] = 1
   if VERBOSE:
      print("after normalise", c)

def compare(p1, p2):
   if len(p1) != len(p2):
      return False
   for i in range(len(p1)):
      v = p1[i] / p2[i]
      if (v < TOLER_MIN) or (v > TOLER_MAX):
         return False
   for i in range(len(p1)):
       p1[i] = int(round((p1[i]+p2[i])/2.0))
   if VERBOSE:
      print("after compare", p1)
   return True

def tidy_mark_space(records, base):
   ms = {}
   for rec in records:
      rl = len(records[rec])
      for i in range(base, rl, 2):
         if records[rec][i] in ms:
            ms[records[rec][i]] += 1
         else:
            ms[records[rec][i]] = 1
   if VERBOSE:
      print("t_m_s A", ms)
   v = None
   for plen in sorted(ms):
      if v == None:
         e = [plen]
         v = plen
         tot = plen * ms[plen]
         similar = ms[plen]
      elif plen < (v*TOLER_MAX):
         e.append(plen)
         tot += (plen * ms[plen])
         similar += ms[plen]
      else:
         v = int(round(tot/float(similar)))
         # set all previous to v
         for i in e:
            ms[i] = v
         e = [plen]
         v = plen
         tot = plen * ms[plen]
         similar = ms[plen]
   v = int(round(tot/float(similar)))
   # set all previous to v
   for i in e:
      ms[i] = v
   if VERBOSE:
      print("t_m_s B", ms)
   for rec in records:
      rl = len(records[rec])
      for i in range(base, rl, 2):
         records[rec][i] = ms[records[rec][i]]

def tidy(records):
   tidy_mark_space(records, 0) # Marks.
   tidy_mark_space(records, 1) # Spaces.

def end_of_code():
   global code, fetching_code
   if len(code) > SHORT:
      normalise(code)
      fetching_code = False
   else:
      code = []
      print("Short code, probably a repeat, try again")

def cbf(gpio, level, tick):
   global last_tick, in_code, code, fetching_code
   if level != pigpio.TIMEOUT:
      edge = pigpio.tickDiff(last_tick, tick)
      last_tick = tick
      if fetching_code:
         if (edge > PRE_US) and (not in_code): # Start of a code.
            in_code = True
            pi.set_watchdog(GPIO, POST_MS) # Start watchdog.
         elif (edge > POST_US) and in_code: # End of a code.
            in_code = False
            pi.set_watchdog(GPIO, 0) # Cancel watchdog.
            end_of_code()
         elif in_code:
            code.append(edge)
   else:
      pi.set_watchdog(GPIO, 0) # Cancel watchdog.
      if in_code:
         in_code = False
         end_of_code()


def number_of_1(receive_s,st_start=0):
    # 与えられた文字列の最初の区切りを数字にして返します。
    # 数字にした文字列は与えられた文字列から削除して返します。
    st_end = receive_s.find(", ")
    # print(st_start,st_end)
    result_s = receive_s[st_start:st_end]
    # print(result_s)
    result = int(result_s)
    # print(result)
    receive_s = receive_s[st_end+1:]
    # print(receive_s)
    return result,receive_s

def rawTocode(receive):
   # raw Data 一つ分をcodeに変換します。
   # コマンド名を切り出す
   command = receive[receive.find('"')+1:receive.find("[")-3]
   #  log_print(command) 
   # print('[ ] の間の文字列を切り出す')
   receive_s = receive[receive.find("[")+1:receive.find("]")]
   # print(receive_s) 
   # 数字の数を数える
   n = receive[receive.find("[")+1:receive.find("]")].count(',')+1
   # print(n)

   # 最後の数字を取り出せる様にスペースを追加
   receive_s = receive_s + ' '
   # 文字列の頭から順に数字に変換していく rawデータの取り出し
   number = []
   for i in range(n):
      result,receive_s = number_of_1(receive_s,st_start=0)
      # print(result)
      if result > 400 and result < 800 :number.append(1)
      if result > 1100 and result < 1700 :number.append(3)
   # rawデータからcodeデータに変換する。
   code =''
   err = 0
   if len(number) % 2 != 0:err = -1
   for i in range(0,len(number) + err,2):
      # print(i)
      if number[i] == 1:
            if number[i+1] == 1:code += '0'
            if number[i+1] == 3:code += '1'
      else:
            # print('err')
            pass
   return command , code


# def main():
while True:
   code_data = []
   command = []
   records = {}
   # リモコンデータを結合する。同じコマンド名があると注意が必要
   # FILE=['oso']
   # FILE=['ali']
   # FILE=['oso','ap_remocon','tv','fan']
   # FILE=['ap_remocon']
   records = ''
   for file_name in FILE:
      if  os.path.exists(file_name): #ファイルがあれば追加する。
         with open(file_name) as f:
            receive = f.read()
            # rawデータを足していくのに不要な文字を消す
            receive = receive.replace('{', '')
            receive = receive.replace('}', '')
            receive = receive[:-1] 
            receive = receive + ','
         records += receive
      else:
         log_print(file_name,'が無いです。')
   # print(records) 
   receive = '{' + records + '}'

   # コマンドの数を数える   ": [
   command_n = receive.count('": [')
   log_print('読み込んだコマンドの数 ',command_n)

   # コマンドの数だけ反復
   for i in range(command_n):
      # code変換
      new_command , new_code = rawTocode(receive)
      # リストに追加
      command.append(new_command)
      code_data.append(new_code)
      # 次のコマンドまでを削除  ],
      next_top = receive.find("],") + 2
      receive = receive[next_top:]
      
   for i in range(command_n):
      log_print(code_data[i],command[i],)



   # 受信待ちに入る。
#    pi = pigpio.pi() # Connect to Pi.
   while True:
      POST_US    = POST_MS * 1000
      PRE_US     = PRE_MS  * 1000
      GAP_S      = GAP_MS  / 1000.0
      CONFIRM    = not NO_CONFIRM
      TOLER_MIN =  (100 - TOLERANCE) / 100.0
      TOLER_MAX =  (100 + TOLERANCE) / 100.0
      last_tick = 0
      in_code = False
      code = []
      fetching_code = False

      pi = pigpio.pi() # Connect to Pi.
      if not pi.connected:
         print("GPIO noconnect")
         exit(0)

      # beep音設定
      beep = int(beep)
      pi.set_mode(beep, pigpio.OUTPUT) 
      pi.write(beep, 0) # beep off

      # beep2音設定 音声再生の代わり
      beep2 = int(beep2)
      pi.set_mode(beep2, pigpio.OUTPUT) 
      pi.write(beep2, 0) # beep off

      LED = int(LED)
      LED1 = int(LED1)
      pi.set_mode(LED, pigpio.OUTPUT) 
      pi.set_mode(LED1, pigpio.OUTPUT) 
    #   pi.write(LED, 1) # beep on
    #   time.sleep(0.05)
    #   pi.write(LED, 0) # beep off

      # 赤外線センサーのデータを待ち、くれば読み取る
      records = {}
      pi.set_mode(GPIO, pigpio.INPUT) # IR RX connected to this GPIO.
      pi.set_glitch_filter(GPIO, GLITCH) # Ignore glitches.
      cb = pi.callback(GPIO, pigpio.EITHER_EDGE, cbf)

      for arg in ['r_data']:
         print('Plese Press key ')
         code = []
         fetching_code = True
         while fetching_code:
            time.sleep(0.1)
         print("Okay")
         time.sleep(0.1)
         
         if CONFIRM:
            press_1 = code[:]
            done = False
            tries = 0
            while not done:
                # print("Press key for '{}' to confirm".format(arg))
                print('Plese Press key ')
                code = []
                fetching_code = True
                while fetching_code:
                    time.sleep(0.1)
                press_2 = code[:]
                the_same = compare(press_1, press_2)
                if the_same:
                    done = True
                    records[arg] = press_1[:]
                    print("Okay")
                    time.sleep(0.5)
                else:
                    tries += 1
                    if tries <= 3:
                        print("No match")
                    else:
                        print("Giving up on key '{}'".format(arg))
                        done = True
                    time.sleep(0.1)
         else: # No confirm.
            records[arg] = code[:]

      pi.set_glitch_filter(GPIO, 0) # Cancel glitch filter.
      pi.set_watchdog(GPIO, 0) # Cancel watchdog.

      tidy(records)
      print('command receive!!')
      # intリストを文字列に変換する。
      result = ", ".join(map(str, records['r_data']))
      result = '{"receive": [' + result + '],}'
      R_command , R_code = rawTocode(result)
   
      try:
         R_code = R_code[2:25] #頭8,尻尾2文字削る ap_remocon
         # R_code = R_code[7:-1] #頭8,尻尾2文字削る oso
      except:
         pass
      print(R_command , R_code)
      print()
      j = 0

    #   # -------------------------------------------
    #   try:
    #     # なぜかたまにここでエラーになることがある
    #     pi.stop() # Disconnect from Pi.
    #   except:
    #     log_print('pi.stop() エラー 1 ***********')
    #     time.sleep(1)
    #     try:
    #         pi.stop()
    #     except:
    #         log_print('pi.stop() エラー 2 ************')
    #         time.sleep(1)
    #         pi.stop()
    #   # -------------------------------------------


# -----------------------------
      log_print(R_code)
      j = 0 #コマンド合致で 1
      # 受信したコードの長さをチェック
      #   print(len(R_code))
      if len(R_code) > 15 and len(R_code) < 30: 
         # 読み取ったosoコードの数だけチェックする
         for i in range(command_n):
            # print(i,code_data[i],command[i])
            if R_code in code_data[i]:
                pi.write(beep, 1) # beep on
                time.sleep(0.0005)
                pi.write(beep, 0) # beep off
                log_print('hit-No and CMD ',i,command[i])

                pi.write(LED, 1) # LED on
                pi.write(LED1, 1) # LED on
                time.sleep(0.05)
                pi.write(LED, 0) # LED off
                pi.write(LED1, 0) # LED off

                # 音声再生によるbeep音 背に着せニラと相性が悪い?
                # os_cmd = 'aplay ' + path + 'pi.wav'
                # try:
                #     os.system(os_cmd)
                # except:
                #     pass
                #     # log_print('suiteki.wav がない? ')
                for k in range(10):
                    pi.write(beep2, 1) # beep on
                    time.sleep(0.0000125)
                    pi.write(beep2, 0) # beep off
                    time.sleep(0.00000125)

                j = 1
                break
      if j == 1:# 一致したコードがあったので、コマンド名を保存
         with open(path + 'iR_command.txt', mode='w') as f: #上書き
            f.write(command[i])
         mes = 'CMD=' + command[i]
         print(path,mes,command[i])
        # Lib_OLED.SSD1306(mes,disp_size,24)
      else:
         log_print('not found')

      # -------------------------------------------
      try:
        # なぜかたまにここでエラーになることがある
        pi.stop() # Disconnect from Pi.
      except:
        log_print('pi.stop() エラー 1 ***********')
        time.sleep(1)
        try:
            pi.stop()
        except:
            log_print('pi.stop() エラー 2 ************')
            time.sleep(1)
            pi.stop()
      # -------------------------------------------