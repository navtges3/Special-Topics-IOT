import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

GPIO.setup(21, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(18, GPIO.OUT)

clickedflag = False

ledState = GPIO.LOW

while True:
  
    buttonstate = GPIO.input(21)

    if(buttonstate and not clickedflag):
        clickedflag = True

    if(not buttonstate and clickedflag):
        clickedflag = False
        if(ledState == GPIO.LOW):
            ledState = GPIO.HIGH
            GPIO.output(18, GPIO.HIGH)
        else:
            ledState = GPIO.LOW
            GPIO.output(18, GPIO.LOW)
