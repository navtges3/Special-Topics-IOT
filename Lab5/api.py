import paho.mqtt.client as mqtt
from influxdb import InfluxDBClient
from flask import Flask, request, json
from flask_restful import Resource, Api
import datetime

broker_address = "192.168.0.25"

client = mqtt.Client()
client.connect(broker_address)

dbclient = InfluxDBClient('0.0.0.0', 8086, 'root', 'root', 'mydb')

app = Flask(__name__)
api = Api(app)

class Test(Resource):
    def get(self):
        light_avg = 0.0
        query = 'select mean("value") from "/light" where "time" > now()-10s'
        result = dbclient.query(query)
        light_list = list(result.get_points(measurement='/light'))
        if(light_list != []):
            light_avg = light_list[0]['mean']
        return('Light_avg': str(light_avg))
            
    def post(self):
        value = request.get_data()
        value = json.loads(value)
        if(value['device'] == 'pi'):
            if(value['state'] == 'on'):
                client.publish('/piled', 'on')
            if(value['state'] == 'off'):
                client.publish('/piled', 'off')
        if(value['device'] == 'arduino'):
            if(value['state'] == 'on'):
                client.publish('/led', 'on')
            if(value['state'] == 'off'):
                client.publish('/led', 'off')

api.add_resource(Test, '/test')

app.run(host='0.0.0.0', debug=True)
