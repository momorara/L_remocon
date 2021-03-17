# -*- coding: utf-8 -*-

"""

i2c_disp02.py

#Filename      :Lib_OLED.py
#Author        :kawabata

OLEDディスプレイへの表示

2020/08/09  ネットで調べる
            SSD1306_128_64
            SSD1306_128_32 に対応
            TrueTypeフォントで字を拡大に成功
2020/08/10  ライブラリ化
            from nobu_LIB import Lib_OLED
2020/09/05  文字数に合わせてフォントサイズを調整します。
            font_sizeをnullで関数を読む




http://ytkyk.info/blog/2016/06/19/raspberry-pi%E3%81%A7128x64%E3%81%AEoled%E3%81%AB%E6%97%A5%E6%9C%AC%E8%AA%9E%E3%82%92%E8%A1%A8%E7%A4%BA%E7%BE%8E%E5%92%B2%E3%83%95%E3%82%A9%E3%83%B3%E3%83%88/

**** 使用にあたっての設定ステップ ***

1. i2cの設定
2. i2cの確認
3. SSD1306 のライブラリインストール

git clone https://github.com/adafruit/Adafruit_Python_SSD1306.git 
cd Adafruit_Python_SSD1306 
sudo python3 setup.py install

フォントのインストール

pip3 install Adafruit_GPIO 
sudo apt-get install libopenjp2-7 
sudo apt-get install libtiff5-dev 
pip3 install pillow

scp -r i2c_disp pi@192.168.68.127:/home/pi
"""

import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306
from PIL import Image, ImageDraw, ImageFont
import unicodedata # 半角、全角の判定
import time

def SSD1306(disp_str,disp_size=32,font_size=0):

    # Raspberry Pi pin configuration
    RST = 40
    if disp_size == 64:
        disp = Adafruit_SSD1306.SSD1306_128_64(rst=RST) # 大きい方
    else:
        disp = Adafruit_SSD1306.SSD1306_128_32(rst=RST) # 小さい方


    # 文字数に合わせてフォントサイズを調整する 半角、全角を認識します。
    if font_size == 0:
        moji_n = 0
        for i in disp_str:
            hantei = unicodedata.east_asian_width(i)
            if hantei == 'Na' or hantei == 'H' or hantei == 'N' :
                moji_n += 1
            else:
                moji_n += 2
            # print(i,moji_n)
        # print(disp_str,moji_n)
        font_size = (int(128/moji_n) + 1) * 2
        if font_size > 32 : font_size = 32
        if moji_n > 8: font_size = int(font_size * 0.9)

    """
    F, W, Aは全角（= 2文字分）
    H, Na, Nは半角（= 1文字分）
    https://note.nkmk.me/python-unicodedata-east-asian-width-count/
    """

    # Initialize library.
    disp.begin()
    # Clear display.
    disp.clear()
    disp.display()
    # Create blank image for drawing.
    # Make sure to create image with mode '1' for 1-bit color.
    width = disp.width
    height = disp.height
    image = Image.new('1', (width, height))
    # Get drawing object to draw on image.
    draw = ImageDraw.Draw(image)
    # Draw a black filled box to clear the image.
    draw.rectangle((0,0,width-1,height-1), outline=0, fill=0)

    # 日本語フォント導入方法
    # Misaki Font, awesome 8x8 pixel Japanese font, can be downloaded from the following URL.
    # $ wget http://www.geocities.jp/littlimi/arc/misaki/misaki_ttf_2015-04-10.zip
    # font = ImageFont.truetype('/home/pi/font/misakifont/misaki_gothic.ttf', 8, encoding='unic')

    # font = ImageFont.load_default()
    #  ↑ デフォルトフォントでは小さすぎるので、
    # TrueTypeフォントを導入して、サイズを変更する。
    # http://kinokorori.hatenablog.com/entry/2017/10/02/000000
    # $ sudo apt-get install fonts-ipafont
    # で、インストールして、下の様にTrueTypeを指定する。
    # IPAフォントは日本語フォントなので、そのまま日本語が表示できます。
    # pythonスクリプトの文字コードをutf-8にして、ファイル先頭にcoding:utf-8を入れます。
    # u"テスト" って感じ
    font = ImageFont.truetype("fonts-japanese-gothic.ttf", 16)
    font = ImageFont.truetype("fonts-japanese-gothic.ttf", 32)
    font = ImageFont.truetype("fonts-japanese-gothic.ttf", 40) # Max Size

    font = ImageFont.truetype("fonts-japanese-gothic.ttf", font_size)
    # font = ImageFont.truetype("fonts-japanese-gothic.ttf", 36) 
    # Write two lines of text.
    x=0
    y=0
    text = "Hello!"
    text = disp_str

    # 画面左からに表示 デフォルトフォントなら4行書けるけど、小さすぎ
    # draw.text((x,y), text,font=font,fill=255, )

    # 画面中央に表示
    (font_width, font_height) = font.getsize(text)
    draw.text(
        (width // 2 - font_width // 2, height // 2 - font_height // 2),
        text,
        font=font,
        fill=255, )

    # 実際に表示
    disp.image(image)
    disp.display()
    

def main():
    disp_size = 'SSD1306_128_64' 
    disp_size = 'SSD1306_128_32'
    font_size = 32 # TrueType フォントサイズ
    disp_str = ''

    SSD1306(disp_str,disp_size,font_size)

    test_s = "エアコントローラー"
    SSD1306(test_s,disp_size)
    time.sleep(2)
    SSD1306('い',disp_size)
    time.sleep(2)
    SSD1306('にい',disp_size)
    time.sleep(2)
    SSD1306('さんさ',disp_size)
    time.sleep(2)
    SSD1306('ヨンよん',disp_size)
    time.sleep(2)
    SSD1306('ご後ご後ご',disp_size)
    time.sleep(2)
    SSD1306('六なり六六ろ',disp_size)
    time.sleep(2)
    SSD1306('ナナナ七七七な',disp_size)
    time.sleep(2)
    SSD1306('はちはちはちはち',disp_size)
    time.sleep(2)
    SSD1306('はちはちはちはち九',disp_size)
    time.sleep(2)
    SSD1306('はちはちはちはち九十',disp_size)
    time.sleep(2)

if __name__ == '__main__':
    try:
        main()
    #when 'Ctrl+C' is pressed,child program destroy() will be executed.
    except KeyboardInterrupt:
        pass
    except ValueError as e:
        print(e)

