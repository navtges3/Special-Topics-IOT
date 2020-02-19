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



GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.OUT)


client = mqtt.Client()
client.connect(broker_ip)

client.on_message = on_message
client.subscribe("/Light")

client.loop_start()

light_avg = 0.0

try:
    while True:
        query = 'select mean("value") from "/light" where "time" > now()-10s'

        result = dbclient.query(query)

        #print(result)
        
        light_list = list(result.get_points(measurement='/light'))
        if(light_list != []):
            light_avg = light_list[0]['mean']
            if(light_avg > 200.0):
                GPIO.output(18, GPIO.HIGH)
            else:
                GPIO.output(18, GPIO.LOW)
        
except KeyboardInterrupt:
    pass

client.loop_stop()
