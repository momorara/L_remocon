
"""
2026/10/18
Blynkによるスマホからの制御を受信します。
https://www.blynk.io
2026/10/22  通信障害にとりあえず対応

test_blynk.py にあなたのトークンを入れて、テストして、OKなら
blynk.py にトークンを入れて再起動すれば、動作します。

2026/11/04  エラー処理の強化

pi/L_remocon用
"""

import BlynkLib
import subprocess
import time

BLYNK_AUTH = 'Your_Token'  # Blynkの認証トークン

# Blynkインスタンス
blynk = None

# ---------------------------------
# 赤外線送信処理
# ---------------------------------
def ir_send(command):
    subprocess.run([
        "python3",
        "/home/pi/L_remocon/irrp_long.py",
        "-p", "-g22",
        "-f", "/home/pi/L_remocon/aircon",
        command
    ])

# ---------------------------------
# V0 冷房
# ---------------------------------
def v0_write_handler(value):
    if int(value[0]) == 1:
        print("V0 冷房ボタンが押された", flush=True)
        ir_send("cool_H")

# ---------------------------------
# V1 暖房
# ---------------------------------
def v1_write_handler(value):
    if int(value[0]) == 1:
        print("V1 暖房ボタンが押された", flush=True)
        ir_send("heat")

# ---------------------------------
# V2 電源OFF
# ---------------------------------
def v2_write_handler(value):
    if int(value[0]) == 1:
        print("V2 切りボタンが押された", flush=True)
        ir_send("off")

# ---------------------------------
# Blynk接続・イベント登録
# ---------------------------------
def connect_blynk():
    print("Blynk接続を開始します", flush=True)
    new_blynk = BlynkLib.Blynk(BLYNK_AUTH)
    # イベント登録
    new_blynk.on("V0")(v0_write_handler)
    new_blynk.on("V1")(v1_write_handler)
    new_blynk.on("V2")(v2_write_handler)
    print("Blynkインスタンスを作成しました", flush=True)
    return new_blynk

# ---------------------------------
# メインループ
# ---------------------------------
if BLYNK_AUTH == 'Your_Token':
    print("認証トークンを設定してください")
else:
    while True:
        try:
            # 接続されていなければ新規作成
            if blynk is None:
                blynk = connect_blynk()
            # Blynk通信処理
            blynk.run()
        except Exception as e:
            print("Blynk通信エラー:", e, flush=True)
            # 古いインスタンスを破棄
            blynk = None
            print("5秒後に再接続します", flush=True)
            time.sleep(5)
