import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO

broker_address = "192.168.0.25"
    
def on_message(client, userdata, message):
    print(message.topic + " " +str(message.payload))
    if(message.topic == "/piLED"):
        if(str(message.payload) == "b'on'"):
            GPIO.output(18, GPIO.HIGH)
        elif(str(message.payload) == "b'off'"):
            GPIO.output(18, GPIO.LOW)
                

GPIO.setmode(GPIO.BCM)
GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(18, GPIO.OUT)

clickedflag = False
led = True

client = mqtt.Client()
client.connect(broker_address)

client.on_message = on_message
client.subscribe("/piLED")

client.loop_start()

try:
    while True:
        buttonstate = GPIO.input(23)

        if(buttonstate and not clickedflag):
            clickedflag = True

        if(not buttonstate and clickedflag):
            clickedflag = False

            if(led):
                print("Setting LED to ON")
                client.publish("/led", "on")
                led = False
            elif(not led):
                print("Setting LED to OFF")
                client.publish("/led", "off")
                led = True
        

except KeyboardInterrupt:
    pass

client.loop_stop()
