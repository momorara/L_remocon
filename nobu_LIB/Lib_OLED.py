"""
2025/01/23  luma.xxxを使わずにOLEDを使えるようにしました。
            これにより、pipインストールが不要になります。
            インストールが簡単になります
            bookwormで仮想環境を使わず、OLEDを使えます。
            ただし、billseyeでは、smbus2のインストールが必要になる場合があります。

            OLED 128*32専用です。
    v2.0
2025/10/07  TrixieでL_remocon用に改造した
"""
import smbus2
from PIL import Image, ImageDraw, ImageFont
import time
import unicodedata # 半角、全角の判定

# OLEDディスプレイの設定
OLED_I2C_ADDR = 0x3C
OLED_WIDTH = 128
OLED_HEIGHT = 32

# SSD1306制御用コマンド
SSD1306_COMMAND = 0x00
SSD1306_DATA = 0x40

image = Image.new("1", (OLED_WIDTH, OLED_HEIGHT), "black")
draw = ImageDraw.Draw(image)

# SMBus初期化
bus = smbus2.SMBus(1)

def oled_command(cmd):
    """OLEDにコマンドを送信"""
    bus.write_byte_data(OLED_I2C_ADDR, SSD1306_COMMAND, cmd)

def oled_ini():
    """OLEDを初期化"""
    commands = [
        0xAE,  # Display OFF
        0x20, 0x00,  # Set Memory Addressing Mode to Horizontal
        0xB0,  # Set Page Start Address for Page Addressing Mode
        0xC8,  # Set COM Output Scan Direction
        0x00,  # Set Low Column Address
        0x10,  # Set High Column Address
        0x40,  # Set Display Start Line
        0x81, 0xFF,  # Set Contrast Control
        0xA1,  # Set Segment Re-map
        0xA6,  # Set Normal Display
        0xA8, 0x1F,  # Set Multiplex Ratio (for 128x32)
        0xD3, 0x00,  # Set Display Offset
        0xD5, 0xF0,  # Set Display Clock Divide Ratio
        0xD9, 0x22,  # Set Pre-charge Period
        0xDA, 0x02,  # Set COM Pins Hardware Configuration
        0xDB, 0x20,  # Set VCOMH Deselect Level
        0x8D, 0x14,  # Charge Pump Setting (Enable)
        0xAF  # Display ON
    ]
    for cmd in commands:
        oled_command(cmd)

# def create_canvas():
#     """描画データを格納する領域(キャンバス)を作成"""
#     image = Image.new("1", (OLED_WIDTH, OLED_HEIGHT), "black")
#     draw = ImageDraw.Draw(image)
#     return image, draw

def clear_canvas():
    """キャンバスをクリア"""
    draw.rectangle((0, 0, OLED_WIDTH, OLED_HEIGHT), fill=0)

def clear_oled():
    """OLED画面をクリア"""
    oled_command(0x20)  # Horizontal addressing mode
    for page in range(0, 4):
        oled_command(0xB0 + page)  # Set page start address
        oled_command(0x00)  # Set low column start address
        oled_command(0x10)  # Set high column start address
        for _ in range(OLED_WIDTH):
            if page != 0:
                bus.write_byte_data(OLED_I2C_ADDR, SSD1306_DATA, 0x00)
    oled_command(0xB0 + 0)  # Set page start address
    oled_command(0x00)  # Set low column start address
    oled_command(0x10)  # Set high column start address
    for _ in range(OLED_WIDTH):
        bus.write_byte_data(OLED_I2C_ADDR, SSD1306_DATA, 0x00)

def set_font(font_path="DejaVuSans.ttf", size=12):
    """フォントとフォントサイズを設定"""
    return ImageFont.truetype(font_path, size)

def disp_oled():
    """キャンバスの内容をOLEDに表示"""
    oled_command(0x20)  # Horizontal addressing mode
    for page in range(0, 4):  # 4ページ (32ピクセル / 8)
        oled_command(0xB0 + page)  # Set page start address
        oled_command(0x00)  # Set low column start address
        oled_command(0x10)  # Set high column start address
        for x in range(OLED_WIDTH):
            byte = 0
            if page != 0:
                for bit in range(8):  # 各ページ内で8ピクセルを処理
                    y = page * 8 + bit
                    if y < OLED_HEIGHT and image.getpixel((x, y)):
                        byte |= (1 << bit)
            if page != 0:
                bus.write_byte_data(OLED_I2C_ADDR, SSD1306_DATA, byte)
    
    # ページゼロが転送されないので、再度送る
    page =0
    oled_command(0xB0 + page)  # Set page start address
    # oled_command(0x00)  # Set low column start address
    # oled_command(0x10)  # Set high column start address
    for x in range(OLED_WIDTH):
        byte = 0
        for bit in range(8):  # 各ページ内で8ピクセルを処理
            y = page * 8 + bit
            if y < OLED_HEIGHT and image.getpixel((x, y)):
                byte |= (1 << bit)
        bus.write_byte_data(OLED_I2C_ADDR, SSD1306_DATA, byte)

def text( x, y, text, font):
    """指定された位置にテキストを描画"""
    draw.text((x, y), text, font=font, fill=255)

def point( x, y):
    """指定された位置にドットを描画"""
    draw.point((x, y), fill=255)

def line( x1, y1, x2, y2):
    """指定された位置に線を描画"""
    draw.line((x1, y1, x2, y2), fill=255)

def square( x1, y1, x2, y2,set):
    """指定された位置に四角を描画"""
    if set == 0:
        draw.rectangle((x1, y1, x2, y2), outline=255, fill=0)
    else:
        draw.rectangle((x1, y1, x2, y2), outline=255, fill=1)

def bitmap_to_image(bitmap_path):
    """BMPファイルを画像オブジェクトに変換"""
    img = Image.open(bitmap_path).convert('1')  # 1ビットカラー（白黒画像）
    img = img.resize((OLED_WIDTH, OLED_HEIGHT))  # サイズをOLEDに合わせる
    return img

def draw_bitmap( x, y, bitmap_image):
    """指定された位置にBMP画像を描画"""
    bitmap_image = bitmap_image.convert('1')  # 白黒に変換
    for i in range(bitmap_image.width):
        for j in range(bitmap_image.height):
            if bitmap_image.getpixel((i, j)) == 255:  # 白い部分を描画
                draw.point((x + i, y + j), fill=255)

oled_ini()
clear_oled()
clear_canvas()

def SSD1306(disp_str,disp_size=32,font_size=0):

    clear_canvas()
    
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

    font = set_font("fonts-japanese-gothic.ttf", font_size)
    text( 0,16-int(font_size/2) ,disp_str, font)
    disp_oled()

def main():

    test_s = "エアコントローラー"
    SSD1306(test_s)
    time.sleep(2)
    SSD1306('テスト')
    time.sleep(2)
    SSD1306('テストテスト')
    time.sleep(2)



    # # OLED初期化
    # oled_ini()

    # # 描画領域(キャンバス)を作る
    # # image, draw = create_canvas()

    # # oledをクリア
    # clear_oled()
    # # 描画領域をクリア
    # clear_canvas()



    # # 四角を描画領域に書く　最後の0で白抜き、1:塗りつぶし
    # square( 0, 0, 127, 31,0)
    # # 描画領域のデータをOLEDに転送
    # disp_oled()

    # # 点を書く
    # point(120, 16)
    # # 描画領域のデータをOLEDに転送
    # disp_oled()

    # # フォント設定
    # font = set_font("fonts-japanese-gothic.ttf", 32)

    # # 20,10に16ポイントの文字を書く
    # text( 0, 0, "テスト", font)
    # disp_oled()
    # time.sleep(1)
    # clear_oled()
    # clear_canvas()

    # # 30,10,50,30に線を描く
    # line( 30, 10, 50, 30)
    # disp_oled()
    # time.sleep(1)

    # # 60,15,80,25に四角を描く
    # square( 0, 14, 127, 31,0)
    # disp_oled()
    # time.sleep(1)

    # font = set_font("fonts-japanese-gothic.ttf", 32)
    # text( 0, 0, "Hello", font)
    # disp_oled()

    # # BMP画像を読み込み
    # bitmap_image = bitmap_to_image('kingyo.png')
    # # BMP画像を描画
    # draw_bitmap( 0, 0, bitmap_image)
    # # キャンバスをOLEDに表示
    # disp_oled()
    
    # time.sleep(2)
    # clear_oled()
    # clear_canvas()
    # text( 0, 0, "Hello", font)
    # disp_oled()
    # time.sleep(2)
    # clear_oled()

if __name__ == "__main__":
    main()
