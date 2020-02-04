import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

GPIO.setup(21, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(18, GPIO.OUT)

clickedflag = False

while True:
  
    buttonstate = GPIO.input(21)

    if(buttonstate and not clickedflag):
        clickedflag = True

    if(not buttonstate and clickedflag):
        clickedflag = False
        print('clicked')
        GPIO.output(18, GPIO.HIGH)
        time.sleep(1)
        GPIO.output(18, GPIO.LOW)
