#include <ESP8266WiFi.h>
#include <PubSubClient.h>

#define WLAN_SSID     "Little Boy Juice"
#define WLAN_PASS     "ThanksD00d"
#define BROKER_IP     "192.168.0.25"

// Pins
#define LED    5
#define BUTTON 4

int buttonLastState = LOW;
int LED_State = LOW;

WiFiClient client;
PubSubClient mqttclient(client);

void callback (char* topic, byte* payload, unsigned int length) {
    Serial.println(topic);
    Serial.write(payload, length);
    Serial.println("");

    payload[length] = '\0';

    if (strcmp(topic, "/led") == 0) {
      if (strcmp((char*)payload, "on") == 0) {
        digitalWrite(LED, HIGH);
      }
      else if(strcmp((char*)payload, "off") == 0) {
        digitalWrite(LED, LOW);
      }
    }
}

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);

  // connect to wifi
  WiFi.mode(WIFI_STA);
  WiFi.begin(WLAN_SSID, WLAN_PASS);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(F("."));
  }

  Serial.println(F("WiFi connected"));
  Serial.println(F("IP address: "));
  Serial.println(WiFi.localIP());

  // connect to mqtt server
  mqttclient.setServer(BROKER_IP, 1883);
  mqttclient.setCallback(callback);
  connect();

  // setup pins
  pinMode(LED, OUTPUT);
}

void loop() {
  // put your main code here, to run repeatedly:
  if (!mqttclient.connected()) {
    connect();
  }

  int val = digitalRead(BUTTON);

  if(val == LOW && buttonLastState == HIGH) {
    if(LED_State == LOW){
      LED_State = HIGH;
      mqttclient.publish("/piLED", "on", false);
    }
    else {
      LED_State = LOW;
      mqttclient.publish("/piLED", "off", false);
    }
  }
  buttonLastState = val;
  
  mqttclient.loop();
}

void connect() {
  while (WiFi.status() != WL_CONNECTED) {
    Serial.println(F("WiFi issue"));
    delay(3000);
  }

  Serial.print(F("Connecting to MQTT server... "));
  while(!mqttclient.connected()) {
    if (mqttclient.connect(WiFi.macAddress().c_str())) {
      Serial.println(F("MQTT server Connected!"));

      mqttclient.subscribe("/led");
    }
    else {
      Serial.print(F("MQTT server connection failed! rc="));
      Serial.print(mqttclient.state());
      Serial.println("try again in 10 seconds");
    }
  }
}
