import time
import subprocess

from PIL import Image, ImageDraw, ImageFont

from board import SCL, SDA
import busio
import adafruit_ssd1306

i2c = busio.I2C(SCL, SDA)
disp = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c)
disp.fill(0)
disp.show()

bitcoin_logo = Image.open('bitcoin.png').resize((disp.width, disp.height), Image.ANTIALIAS).convert('1')

image = Image.new('1', (disp.width, disp.height))
draw = ImageDraw.Draw(image)
font = ImageFont.load_default()

def stats():
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
    MemUsage = MemUsage.replace('  ', ' ')
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
    return True

while True:
    stats()
