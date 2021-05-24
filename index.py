import os
import sys
import time
import subprocess
from datetime import datetime, timedelta

from PIL import Image, ImageDraw, ImageFont

from board import SCL, SDA
import busio
import adafruit_ssd1306

import mariadb

if os.getenv('ENVIRONMENT') != 'production':
    from dotenv import load_dotenv
    load_dotenv()

i2c = busio.I2C(SCL, SDA)
disp = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c)
disp.fill(0)
disp.show()

bitcoin_logo = Image.open('bitcoin.png').resize((disp.width, disp.height), Image.ANTIALIAS).convert('1')

image = Image.new('1', (disp.width, disp.height))
draw = ImageDraw.Draw(image)
font = ImageFont.load_default()


def get_price(name, date_start, date_end):
    try: 
        conn = mariadb.connect(
            user=os.getenv('BTCBOT_SQLUSER'),
            password=os.getenv('BTCBOT_SQLPASSWD'),
            host=os.getenv('BTCBOT_SQLHOST'),
            port=int(os.getenv('BTCBOT_SQLPORT')))
    except mariadb.Error as e:
        draw.rectangle((0, 0, disp.width, disp.height), outline=0, fill=0)
        draw.text((0, 0), "!!!SQLERROR CONNECTING!!!", font=font, fill=255)
        draw.text((0, 12), e, font=font, fill=255)
        disp.image(image)
        disp.show()
        print(f"Error connecting to MariaDB Platform: {e}")
        sys.exit(1)
    cur = conn.cursor()
    response = []
    cmd = f"SELECT price FROM {os.getenv('BTCBOT_SQLDATABASE')}.price WHERE name = '{name}' AND datetime >= '{date_start}' AND datetime <= '{date_end}'"
    cur.execute(cmd)
    for elements in cur:
        response.append(elements[0])
    conn.close()
    return response

def show_price():
    names = {
        'binance_brl': 'R$',
        'binance_usd': 'U$',
        'binance_eur': 'EU'
    }
    datetime_now = (datetime.now() + timedelta(minutes=1)).strftime('%Y-%m-%d %H:%M:%S')
    datetime_lasmin = (datetime.now() - timedelta(minutes=1)).strftime('%Y-%m-%d %H:%M:%S')

    draw.rectangle((0, 0, disp.width, disp.height), outline=0, fill=0)
    draw.text((0,0), "    PRICE BITCOIN", font=font, fill=255)
    y=0
    for name in names:
        prices_arr = get_price(name, datetime_lasmin, datetime_now)
        if prices_arr:
            y = y + 16
            draw.text((0, y), f"{prices_arr[-1]} {names[name]}", font=font, fill=255)
    disp.image(image)
    disp.show()
    return
    
def show_stats():
    draw.rectangle((0, 0, disp.width, disp.height), outline=0, fill=0)

    cmd = "hostname -I | cut -d' ' -f1"
    IP = subprocess.check_output(cmd, shell=True).decode("utf-8")
    cmd = 'cut -f 1 -d " " /proc/loadavg'
    CPU = subprocess.check_output(cmd, shell=True).decode("utf-8")
    cmd = 'vcgencmd measure_temp'
    TEMP = subprocess.check_output(cmd, shell=True).decode("utf-8")
    TEMP = TEMP.replace('temp=', '')#.replace("'C\n", '')
    cmd = "free -m | awk 'NR==2{printf \"Mem: %s/%s MB  %.2f%%\", $3,$2,$3*100/$2 }'"
    MemUsage = subprocess.check_output(cmd, shell=True).decode("utf-8")
    MemUsage = MemUsage.replace(' ', '')
    cmd = 'df -h | awk \'$NF=="/"{printf "Disk: %d/%d GB  %s", $3,$2,$5}\''
    Disk = subprocess.check_output(cmd, shell=True).decode("utf-8")

    draw.text((0, 0), "IP: " + IP, font=font, fill=255)
    draw.text((0, 13), "CPU: " + CPU, font=font, fill=255)
    draw.text((0, 26), "TEMP: " + TEMP, font=font, fill=255)
    draw.text((0, 39), MemUsage, font=font, fill=255)
    draw.text((0, 51), Disk, font=font, fill=255)

    disp.image(image)
    disp.show()

    time.sleep(0.1)
    return

while True:
    counter = 0
    while counter < 30:
        show_stats()
        counter += 1
    disp.image(bitcoin_logo)
    disp.show()
    time.sleep(2)
    show_price()
    time.sleep(6)



