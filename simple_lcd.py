import Adafruit_CharLCD as LCD
import RPi.GPIO as GPIO

# LCD pin configuration:
LCD_RS = 22
LCD_EN = 17
LCD_D4 = 25
LCD_D5 = 24
LCD_D6 = 23
LCD_D7 = 18
LCD_BACKLIGHT = 4
# Define LCD column and row size for 16x2 LCD.
LCD_COLUMNS = 16
LCD_ROWS = 2

try:
    GPIO.setmode(GPIO.BCM)
    lcd = LCD.Adafruit_CharLCD(LCD_RS, LCD_EN, LCD_D4, LCD_D5, LCD_D6, LCD_D7,
                               LCD_COLUMNS, LCD_ROWS, LCD_BACKLIGHT)

    lcd.message('Hello\nWorld!')

    input('Press Enter to continue')

finally:
    lcd.set_backlight(0)
    lcd.clear()
    GPIO.cleanup()
