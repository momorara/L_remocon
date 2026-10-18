"""
2026/10/18
Blynkによるスマホからの制御を受信します。
https://www.blynk.io

test_blynk.py にあなたのトークンを入れて、テストして、OKなら
blynk.py にトークンを入れて再起動すれば、動作します。

"""

import BlynkLib


BLYNK_AUTH = 'Your_Token' # Blynkの認証トークンに置き換えてください


# Blynkインスタンスを初期化
blynk = BlynkLib.Blynk(BLYNK_AUTH)

# 仮想ピンV0に対するコールバック関数を定義（暖房モードで運転）
@blynk.on("V0")
def v0_write_handler(value):
    # ボタンが押されたら冷房モード運転のスクリプトを実行
    if int(value[0]) == 1:
        print("v0 冷房ボタンが押された")

# 仮想ピンV1に対するコールバック関数を定義（冷房モードで運転）
@blynk.on("V1")
def v1_write_handler(value):
    # ボタンが押されたら暖房モードのスクリプトを実行
    if int(value[0]) == 1:
        print("v1 暖房ボタンが押された")

# 仮想ピンV2に対するコールバック関数を定義（冷房モードで運転）
@blynk.on("V2")
def v2_write_handler(value):
    # ボタンが押されたら切りモードのスクリプトを実行
    if int(value[0]) == 1:
        print("v2 切りボタンが押された")

# メインループ
while True:
    blynk.run()