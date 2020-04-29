import logging
import os

from flask import Flask
from flask_ask import Ask, request, session, question, statement

from influxdb import InfluxDBClient
import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO
import datetime
import smtplib

#Alexa
app = Flask(__name__)
ask = Ask(app, "/")
logging.getLogger('flask_ask').setLevel(logging.DEBUG)

# Email Stuff
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
GMAIL_USERNAME = 'navtgespi@gmail.com'
GMAIL_PASSWORD = 'Spbdgh28!'

@ask.launch
def launch():
    speech_text = 'Welcome to Raspberry Pi Automation'
    return question(speech_text).reprompt(speech_text).simple_card(speech_text)

@ask.intent('GpioIntent', mapping = {'status':'status'})
def Gpio_Intent(status, room):
    query = 'select mean("value") from "/temp" where "time" > now()-10s'

    result = dbclient.query(query)
    
    temp_list = list(result.get_points(measurement='/temp'))
    if(temp_list != []):
        temp_avg = temp_list[0]['mean']
        temp_avg = round(temp_avg, 2)
        speech_text = ""
        print('Temp_avg', temp_avg)
        if temp_avg < 50.0:
            speech_text = "YOUR BEER IS COLD! The current temperature is " + str(temp_avg) + " degrees. Enjoy!"
        elif temp_avg > 55.0:
            speech_text = "You will be notified when your beer is cold. The current temperature is " + str(temp_avg) + " degrees."
        else:
            speech_text = "Your beer is " + str(temp_avg) + " degrees currently."
        return statement(speech_text)
    return statement("I am not sure")
@ask.intent('AMAZON.FallbackIntent')
def fallbackintent():
    speech_text = 'Hello'
    return question(speech_text).reprompt(speech_text).simple_card('HelloWorld', speech_text)

@ask.intent('AMAZON.CancelIntent')
def cancel():
    speech_text = 'nah'
    return question(speech_text).reprompt(speech_text).simple_card('HelloWorld', speech_text)

@ask.intent('AMAZON.StopIntent')
def stop():
    speech_text = 'nah'
    return question(speech_text).reprompt(speech_text).simple_card('HelloWorld', speech_text)

@ask.intent('AMAZON.NavigateHomeIntent')
def home():
    speech_text = 'nah'
    return question(speech_text).reprompt(speech_text).simple_card('HelloWorld', speech_text)

@ask.intent('AMAZON.HelpIntent')
def help():
    speech_text = 'You can say hello to me!'
    return question(speech_text).reprompt(speech_text).simple_card('HelloWorld', speech_text)

@ask.session_ended
def session_ended():
    return "{}", 200

class Emailer:
    def sendmail(self, recipient, subject, content):
        #Create Headers
        headers = ["From: " + GMAIL_USERNAME, "Subject: " + subject, "To: " + recipient, "MIME-version: 1.0", "Content-Type: text/html"]
        headers = "\r\n".join(headers)

        #Connect to Gmail Server
        session = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        session.ehlo()
        session.starttls()
        session.ehlo()

        #Login to Gmail
        session.login(GMAIL_USERNAME, GMAIL_PASSWORD)

        #Send Email & Exit
        session.sendmail(GMAIL_USERNAME, recipient, headers + "\r\n\r\n" + content)
        session.quit

sender = Emailer()
sendTo = 'navtges3@gmail.com'
emailSubject = "Beer Thermometer Report"

broker_address = "10.0.0.30"

dbclient = InfluxDBClient('0.0.0.0', 8086, 'root', 'root', 'mydb')

def on_message(client, userdata, message):
    data = str(message.payload.decode("utf-8"))
    #print(message.topic + " " + str(message.payload))

    if(message.topic == "/Temp"):
        receiveTime = datetime.datetime.utcnow()

        json_body = [
            {
                "measurement": '/temp',
                "time": receiveTime,
                "fields": {
                    "value": float(data)
                    }
                }
            ]
        dbclient.write_points(json_body)


client = mqtt.Client()
client.connect(broker_address)

client.on_message = on_message
client.subscribe("/Temp")

client.loop_start()

cold = False

try:
    if __name__ == '__main__':
        if 'ASK_VERIFY_REQUESTS' in os.environ:
            verify = str(os.environ.get('ASK_VERIFY_REQUESTS', '')).lower()
            if verify == 'false':
                app.config['ASK_VERIFY_REQUESTS'] = False
        app.run(debug=True)
    
    while True:
        query = 'select mean("value") from "/temp" where "time" > now()-10s'

        result = dbclient.query(query)

        temp_list = list(result.get_points(measurement='/temp'))
        if(temp_list != []):
            temp_avg = temp_list[0]['mean']
            print('Temp_avg', temp_avg)
            if not cold and temp_avg < 50.0:
                cold = True
                emailContent = "YOUR BEER IS COLD!\nThe current temperature is " + str(temp_avg) + " degrees F.\nEnjoy!"
                sender.sendmail(sendTo, emailSubject, emailContent)
            if cold and temp_avg > 55.0:
                cold = False
                emailContent = "You will be notified when your beer is cold.\nThe current temperature is " + str(temp_avg) + " degrees F."
                sender.sendmail(sendTo, emailSubject, emailContent)
            

except KeyboardInterrupt:
    pass

client.loop_stop()
