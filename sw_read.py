"""
2つのタクトスイッチを読み取り
左のスイッチをA、右のスイッチをBとする
Aを短く押す 1
Bを短く押す 9
Aを1秒以上押す 7
Bを1秒以上押す 8
とする。

2023/10/15  作成開始

"""
# import RPi.GPIO as GPIO
import pigpio 
import time
import getpass

# ユーザー名を取得
user_name = getpass.getuser()
print('user_name', user_name)
path = '/home/' + user_name + '/L_remocon/'  # cronで起動する際には絶対パスが必要
# path = '/home/' + 'tk' + '/L_remocon/' # systemdで起動する際にはrootになり絶対パスが必要

SW_A = 26
SW_B = 6
pi = pigpio.pi()  # Connect to Pi.
pi.set_mode(SW_A, pigpio.INPUT)
pi.set_pull_up_down(SW_A, pigpio.PUD_UP)
pi.set_mode(SW_B, pigpio.INPUT)
pi.set_pull_up_down(SW_B, pigpio.PUD_UP)

# スイッチ確認回数
sw_count = 10  # 0.1秒 * 10回

def main():
    while True:
        # print("sw-A:",pi.read(SW_A))
        # print("sw-B:",pi.read(SW_B))
        time.sleep(0.1)
        input_sw = ""
        #左タクトスイッチ確認
        count_A = 0
        if pi.read(SW_A) == 0:
            while pi.read(SW_A) == 0 :
                count_A = count_A + 1
                time.sleep(0.1)
            if count_A < sw_count:
                print("1")
                input_sw = "1"
            else:
                print("7")
                input_sw = "7"

        #左タクトスイッチ確認
        count_B = 0
        if pi.read(SW_B) == 0:
            while pi.read(SW_B) == 0 :
                count_B = count_B + 1
                time.sleep(0.1)
            if count_B < sw_count:
                print("9")
                input_sw = "9"
            else:
                print("8")
                input_sw = "8"

        if input_sw != "":
            # 入力された値をiR_comman.txtに書き込む
            with open(path + 'iR_command.txt', mode='w') as f:  # 上書き
                f.write(input_sw)


    


# if run this script directly ,do:
if __name__ == '__main__':
    try:
        main()
    #when 'Ctrl+C' is pressed,child program destroy() will be executed.
    except KeyboardInterrupt:
        # print(e)
        pass
    except ValueError as e:
        print(e)
