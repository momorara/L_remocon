"""
汎用学習リモコン

remocon_mode03_01.py -> yoyaku_reload_03.py


node-redで作ったyoyaku.csvをnode-redのui用にすばやくリロードします。
実際のyoyakuデータの取り込みはremocon_mode03_03.pyで行います。


2021/02/16  node-redでiR_cmmand.txtにreloaadを入れる方法ではuiの反応がおそいので、
            yoyaku_reload.pyとして開発開始
2021/03/01  remocon_mode03_03.py対応として改造
    03
2021/03/03  デバック
2021/03/04  エラー処理のためにファィルがない場合は初期化してファイルを作る


scp -r L_remocon/*.py tk@192.168.68.100:/home/tk/L_remocon
scp -r L_remocon/*.py pi@192.168.68.100:/home/pi/L_remocon
scp -r L_remocon pi@192.168.68.100:/home/pi

scp -r L_remocon/*.py pi@172.20.10.6:/home/pi/L_remocon
scp -r L_remocon pi@172.20.10.6:/home/pi
"""
import csv
import getpass
import os
import datetime

# ユーザー名を取得
user_name = getpass.getuser()
print('user_name',user_name)
path = '/home/' + user_name + '/L_remocon/' # cronで起動する際には絶対パスが必要
# path = '/home/' + 'tk' + '/L_remocon/' # systemdで起動する際にはrootになり絶対パスが必要

"""
初期値はremocon_mode03_03.pyにて作成する
(path + 'yoyaku.csv')     #予約データ              ファイルを作るが初期値は不要
(path + 'yoyaku_sw.csv')  #予約の活殺              初期値 0,0,0,0でファイル作成
(path + 'yoyaku_no.csv')  #予約データの数          初期値 0でファイル作成
(path + 'yoyaku_new.csv') #新規の予約データ        ファイル作らない
(path + 'yoyaku_del.csv') #予約データの削除対象no  ファイル作らない
"""
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
    # return
    # f = open(logFileName, 'a',encoding="Shift_jis") 
    # 日本語文字化けするので、Shift_jisやめてみた。
    f = open(logFileName, 'a')
    csvWriter = csv.writer(f)
    csvWriter.writerow([datetime.datetime.now(),msg1,msg2,msg3])
    f.close()
################################################

def yoyaku_file_sakusei():
    # 関係ファィルを全削除
    yoyaku_file_delete_all()
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
    # yoyakuファィルを読み込み整理して保存
    # 予約名,時,分が 最大４つ、ない場合もある
    if not os.path.exists(path + 'yoyaku.csv'):
        yoyaku_file_sakusei()
    with open(path + 'yoyaku.csv', 'r') as csvfile:

        csv_reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        row1 = []
        for row in csv_reader:
            # print('#1=',','.join(row))
            if row == '' :
                # print('#2=','non-data')
                pass
            row1 = row1 + row

        # print('#1=',row1)
        # 全ての''を削除した後に、karaを追加、後に数を12個にする
        kara = ['','','','','','','','','','','','','']
        row1 = ([s for s in row1 if s != ''] ) + kara
        # print('#2=',row1)
        row1 = row1[:12]
        # print('#3=',row1)

        # 整理したデータでyoyakuを上書き
        with open(path + 'yoyaku.csv', 'w') as f:
            for row in row1:
                f.write(row)
                f.write(',')
    return row1

def no_load():
    if not os.path.exists(path + 'yoyaku_no.csv'):
        yoyaku_file_sakusei()
    # 予約の数 0,1,2,3,
    with open(path + 'yoyaku_no.csv', 'r') as csvfile:
        csv_reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        no1 = []
        for no in csv_reader:
            # print('#1=',','.join(row))
            if no == '' :
                print('#2=','non-data')
            pass
            no = no1 + no
        log_print('no=',no)
    # 間違いで4が入った場合の処理
    if no[0] == '4':
        log_print('noが4になっていたので、3にしたよ')
        no[0] == '3'
    return no[0]

def sw_load():
    if not os.path.exists(path + 'yoyaku_sw.csv'):
        yoyaku_file_sakusei()
    # 予約の活殺　1:使用 0:未使用 ファイルがないことはない
    with open(path + 'yoyaku_sw.csv', 'r') as csvfile:
        csv_reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        sw1 = []
        for sw in csv_reader:
            # print('#1=',','.join(row))
            if sw == '' :
                print('#2=','non-data')
            pass
            sw1 = sw1 + sw
    return sw1

def del_no_load():
    # 削除するno 1,2,3,4  or 9:全て削除 or 0:ファイル無
    if os.path.exists(path + 'yoyaku_del.csv'):
        with open(path + 'yoyaku_del.csv', 'r') as csvfile:
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
    else:
        return '0' #ファイルがない場合は削除対象が0

def yoyaku_new_load():
    # 新規予約 予約名,時,分 or '':ファイルなし
    if  os.path.exists(path + 'yoyaku_new.csv'):
        with open(path + 'yoyaku_new.csv', 'r') as csvfile:

            csv_reader = csv.reader(csvfile, delimiter=',', quotechar='"')
            row1 = []
            for row in csv_reader:
                # print('#1=',','.join(row))
                if row == '' :
                    # print('#2=','non-data')
                    pass
                row1 = row1 + row
            # print('#1=',row1)
        return row1
    else:
        print('新規予約はなし')
        return ['','','']

def yoyaku_file_delete(del_filename):
    try:
        os.remove(path + del_filename)  #ファイルを削除
    except:
        pass  

def yoyaku_file_delete_all():
    print('ファィル全削除')
    yoyaku_file_delete('yoyaku.csv')    #予約データファイルを削除
    yoyaku_file_delete('yoyaku_sw.csv') #予約の活殺ファイルを削除
    yoyaku_file_delete('yoyaku_no.csv') #予約データの数　ファイルを削除
    yoyaku_file_delete('yoyaku_new.csv')#新規の予約データファイルを削除
    yoyaku_file_delete('yoyaku_del.csv')#予約データの削除対象noファイルを削除

def yoyaku_file_sakusei():
    print('ファィル作成')
    with open(path + 'yoyaku.csv', 'a') as f:
        f.write('\n')
    with open(path + 'yoyaku_sw.csv', 'w') as f:
        f.write("0,0,0,0")
        f.write('\n')
    with open(path + 'yoyaku_no.csv', 'w') as f:
        f.write("0")
        f.write('\n')


#main function
def main():
    print(path)
    print('---------0----------')
    # タイマー予約 データを読み込み、
    yoyaku = yoyaku_load()
    sw= sw_load()
    no= int(no_load())
    del_no= int(del_no_load())
    yoyaku_new = yoyaku_new_load()

    log_print('--------1-----------')
    # log_print('yoyaku=',yoyaku)
    # log_print('sw=',sw)
    # log_print('no=',no)
    # log_print('del_no=',del_no)
    # log_print('new=',yoyaku_new)

    # # 新規予約がある場合で予約数が4未満
    if yoyaku_new[0] != '' and  (no in [0,1,2,3]):
        no = no +1
        pos = (no -1 )*3
        del yoyaku[pos:]
        yoyaku.append(yoyaku_new[0])
        yoyaku.append(yoyaku_new[1])
        yoyaku.append(yoyaku_new[2])
        kara = ['','','','','','','','','','','','','']
        yoyaku = yoyaku + kara
        yoyaku = yoyaku[:12]
        sw[no-1] = '1'
        yoyaku_file_delete('yoyaku_new.csv')
    else: # 予約が４あり新規があった場合はファイルを消してキャンセル
        if yoyaku_new[0] != '':
            yoyaku_file_delete('yoyaku_new.csv')
            log_print('end 1',yoyaku_new[0])
            exit(0)

    # 削除がある場合
    if del_no != 0 and del_no != 9:
        if (del_no in [1,2,3,4]) and (no in [1,2,3,4]):
            pos = (del_no - 1)*3   # 削除する先頭を計算
            del yoyaku[pos:pos+3]
            kara = ['','','','','','','','','','','','','']
            yoyaku = yoyaku + kara
            yoyaku = yoyaku[:12]
            pos = (del_no - 1)     # 削除する先頭を計算
            sw.pop(pos)
            sw[3] = '0'
            no = no -1
            yoyaku_file_delete('yoyaku_del.csv')
        else:#del_noが 1,2,3,4,9以外の場合はおかしいのでキャンセル
            yoyaku_file_delete('yoyaku_del.csv')
            log_print('end 2',del_no,no)
            exit(0)

    # swに変更がある場合 なにも変更しないがリロードのみ実行
    print()
    log_print('--------2-----------')
    # log_print('yoyaku=',yoyaku)
    # log_print('sw=',sw)
    # log_print('no=',no)
    # log_print('del_no=',del_no)
    # log_print('new=',yoyaku_new)

    yoyaku_file_delete('yoyaku.csv')
    yoyaku_file_delete('yoyaku_sw.csv')
    yoyaku_file_delete('yoyaku_no.csv')
    with open(path + 'yoyaku.csv', 'a') as f:
        for i in range(12):
            f.write(yoyaku[i])
            f.write(',')
    with open(path + 'yoyaku_sw.csv', 'a') as f:
        # print(sw)
        for i in range(4):
            f.write(sw[i])
            f.write(',')
    with open(path + 'yoyaku_no.csv', 'a') as f:
        f.write(str(no))

    # 全削除がある場合
    if del_no == 9: #ファイルを削除、初期化
        # print('全削除')
        yoyaku_file_delete_all()
        yoyaku_file_sakusei()


    # # 設定変更のフラグ'reload'を'iR_command.txt'に書き込む
    with open(path + 'iR_command.txt', mode='w') as f: #上書き
        f.write('reload')

#
# if run this script directly ,do:
if __name__ == '__main__':
    main()