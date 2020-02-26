from influxdb import InfluxDBClient
import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO
import datetime

broker_ip = "192.168.0.25"

dbclient = InfluxDBClient('0.0.0.0', 8086, 'root', 'root', 'mydb')

def on_message(client, userdata, message):
    data = str(message.payload.decode("utf-8"))
    
    print(message.topic + " " + data)
    if(message.topic == "/Light"):
        receiveTime = datetime.datetime.utcnow()

        json_body = [
            {
                "measurement": '/light',
                "time": receiveTime,
                "fields": {
                    "value": float(data)
                    }
                }
            ]
        dbclient.write_points(json_body)
    if(message.topic == "/piled"):
        if(str(message.payload) == "b'on'"):
            GPIO.output(18, GPIO.HIGH)
        elif(str(message.payload) == "b'off'"):
            GPIO.output(18, GPIO.LOW)



GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.OUT)


client = mqtt.Client()
client.connect(broker_ip)

client.on_message = on_message
client.subscribe("/Light")
client.subscribe("/piled")

client.loop_start()

try:
    while True:
        pass
        
except KeyboardInterrupt:
    pass

client.loop_stop()
