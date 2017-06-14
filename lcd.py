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

# Button pin configuration
BTN_PIN = 11
# LCD pin configuration:
LCD_RS = 27  # Note this might need to be changed to 21 for older revision
LCD_EN = 22
LCD_D4 = 25
LCD_D5 = 24
LCD_D6 = 23
LCD_D7 = 18
LCD_BACKLIGHT = 4
# Define LCD column and row size for 16x2 LCD.
LCD_COLUMNS = 16
LCD_ROWS = 2

# Initialize button
GPIO.setmode(GPIO.BCM)
GPIO.setup(BTN_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)


def setup_url():
    """
    Compose the url by reading in the parameters from a config file
    Exits if the file or some parameter is missing
    :return: API call url
    """
    config = configparser.ConfigParser()

    p = pathlib.Path('config.ini')
    if p.is_file():
        config.read('config.ini')
        url_config = config['openweathermap.com']
        api_key = url_config['api_key']
        city_id = url_config['city_id']
        units = url_config['units']
        if not api_key or not city_id or not units:
            if not api_key:
                print('Missing api_key value in config.ini file')
            if not city_id:
                print('Missing city_id value in config.ini file')
            if not units:
                print('Missing units value in config.ini file')
            exit()
        return 'http://api.openweathermap.org/data/2.5/weather?APPID={}&id={}&units={}'.format(api_key, city_id, units)
    else:
        print('config.ini file missing, creating one now')
        config['openweathermap.com'] = {'api_key': '', 'city_id': '', 'units': ''}
        with p.open('w') as configfile:
            config.write(configfile)
        exit()


URL = setup_url()

# Logging configuration
logging.basicConfig(filename='lcd.log', format='%(asctime)s - %(message)s', level=logging.WARNING)
logging.basicConfig(filename='weather.log', format='%(asctime)s - %(message)s', level=logging.DEBUG)


def setup_lcd():
    global LCD_D4, LCD_D5, LCD_D6, LCD_D7, LCD_BACKLIGHT, LCD_COLUMNS, LCD_ROWS

    # Initialize the LCD
    lcd = LCD.Adafruit_CharLCD(LCD_RS, LCD_EN, LCD_D4, LCD_D5, LCD_D6, LCD_D7,
                               LCD_COLUMNS, LCD_ROWS, LCD_BACKLIGHT)
    lcd.set_backlight(0)
    lcd.clear()

    return lcd


data = {}
last_lcd_setup = datetime.datetime(1, 1, 1)
last_check = datetime.datetime(1, 1, 1)

while True:
    try:
        if not GPIO.input(BTN_PIN):
            datetime_now = datetime.datetime.now()

            # Display glitches after some time of inactivity
            if datetime_now - last_lcd_setup > datetime.timedelta(hours=6):
                lcd = setup_lcd()
                last_lcd_setup = datetime_now

            lcd.set_backlight(1)

            # Only download new data if last check was 30 minutes ago
            if datetime_now - last_check > datetime.timedelta(minutes=30):
                lcd.message('Downloading')
                lcd.blink(True)

                try:
                    with urllib.request.urlopen(URL) as response:
                        data = json.loads(response.read().decode())
                        last_check = datetime_now
                except URLError:
                    data = {}

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

            if data:
                lcd.message('Temp: {0}\n{1}'.format(data['main']['temp'],
                                                    data['weather'][0]['description'].capitalize()))
                logging.debug(data)
            else:
                lcd.message('No data')
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
