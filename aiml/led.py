import sys
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(12, GPIO.OUT)

def on():
    GPIO.output(12, GPIO.HIGH)

def off():
    GPIO.output(12, GPIO.LOW)

if len(sys.argv) >= 2:
    print sys.argv[1]
    if sys.argv[1] == '1':
        on()
    elif sys.argv[1] == '0':
        off()
    elif sys.argv[1] == 'd':
        GPIO.cleanup()
