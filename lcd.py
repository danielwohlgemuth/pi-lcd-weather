# Code and ideas from https://github.com/adafruit/AdaFruit-Raspberry-Pi-Python-Code
# and https://github.com/adafruit/Adafruit_Python_CharLCD

import configparser
import datetime
import json
import logging
import pathlib
import time
import urllib.request
from urllib.error import URLError

import Adafruit_CharLCD as LCD
import RPi.GPIO as GPIO

# URL configuration
config = configparser.ConfigParser()
URL = ''

p = pathlib.Path('config.ini')
if p.is_file():
    config.read('config.ini')
    url_config = config['openweathermap.com']
    API_KEY = url_config['api_key']
    CITY_ID = url_config['city_id']
    UNITS = url_config['units']
    if not API_KEY or not CITY_ID or not UNITS:
        if not API_KEY:
            print('Missing api_key value in config.ini file')
        if not CITY_ID:
            print('Missing city_id value in config.ini file')
        if not UNITS:
            print('Missing units value in config.ini file')
        exit()
    URL = 'http://api.openweathermap.org/data/2.5/weather?APPID={}&id={}&units={}'.format(API_KEY, CITY_ID, UNITS)
else:
    print('config.ini file missing, creating one now')
    config['openweathermap.com'] = {'api_key': '', 'city_id': '', 'units': ''}
    with p.open('w') as configfile:
        config.write(configfile)
    exit()

    # with p.open() as api_key_file:
    #     API_KEY = api_key_file.readline().strip()
# else:
#     print('config.ini file missing')
#
#     exit()

# Logging configuration
logging.basicConfig(filename='lcd.log', format='%(asctime)s - %(message)s', level=logging.WARNING)

# Button pin configuration
BTN_PIN = 11

# Initialize button
GPIO.setmode(GPIO.BCM)
GPIO.setup(BTN_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Raspberry Pi pin configuration:
LCD_RS = 27  # Note this might need to be changed to 21 for older revisi$
LCD_EN = 22
LCD_D4 = 25
LCD_D5 = 24
LCD_D6 = 23
LCD_D7 = 18
LCD_BACKLIGHT = 4

# Define LCD column and row size for 16x2 LCD.
LCD_COLUMNS = 16
LCD_ROWS = 2

# Initialize the LCD using the pins above.
lcd = LCD.Adafruit_CharLCD(LCD_RS, LCD_EN, LCD_D4, LCD_D5, LCD_D6, LCD_D7,
                           LCD_COLUMNS, LCD_ROWS, LCD_BACKLIGHT)
lcd.set_backlight(0)
lcd.clear()

data = {}
last_check = datetime.datetime(1, 1, 1)

while True:
    try:
        if not GPIO.input(BTN_PIN):
            lcd.set_backlight(1)

            # Only download new data if last check was 1 hour ago
            if datetime.datetime.now() - last_check > datetime.timedelta(hours=1):
                lcd.message('Downloading')
                lcd.blink(True)

                try:
                    with urllib.request.urlopen(URL) as response:
                        data = json.loads(response.read().decode())
                        last_check = datetime.datetime.now()
                except URLError:
                    lcd.clear()
                    lcd.message('Old data')
                    time.sleep(1.0)

                # data = json.loads('{"coord":{"lon":-57.53,"lat":-25.33},'
                #                   '"weather":[{"id":800,"man":"Clear","description":"clear sky","icon":"01n"}],'
                #                   '"base":"stations",'
                #                   '"main":{"temp":7,"pressure":1015,"humidity":100,"temp_min":7,"temp_max":7},'
                #                   '"visibility":10000,"wind":{"speed":3.06,"deg":78.0048},'
                #                   '"clouds":{"all":0},"dt":1497160800,"sys":{"type":1,"id":4608,"message":0.3824,'
                #                   '"country":"PY","sunrise":1497177146,"sunset":1497215239},"id":3437056,'
                #                   '"name":"San Lorenzo","cod":200}')
                # print(data)

                lcd.clear()
                lcd.blink(False)

            lcd.message('Temp: {0} C\n{1}'.format(data['main']['temp'],
                                                  data['weather'][0]['description'].capitalize()))
            time.sleep(5.0)

            lcd.set_backlight(0)
            lcd.clear()
    except KeyboardInterrupt:
        break
    except BaseException as e:
        logging.warning(repr(e))
    finally:
        lcd.set_backlight(0)
        lcd.clear()
