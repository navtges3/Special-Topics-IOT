/*
 * Author: Nick Avtges
 * 
 * This program runs the arduino side of an IOT device that takes the temperautre
 * of cans of beer inside a refregerator. The temperature is sent to a raspberry
 * Pi over mqtt.
 */

#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <Wire.h>
#include <Adafruit_MLX90614.h>

#define WLAN_SSID   "connect if you like dick"
#define WLAN_PASS   "aabhjm2019"
#define BROKER_IP   "10.0.0.30"

WiFiClient client;
PubSubClient mqttclient(client);

Adafruit_MLX90614 mlx = Adafruit_MLX90614();

// vars
float temp = 0.0;

// mqtt callback function not used in my project here just in case
void callback (char* topic, byte* payload, unsigned int length) {
  Serial.println(topic);
  Serial.write(payload, length);
  Serial.println("");

  payload[length] = '\0';
}

void setup() {
  Serial.begin(9600);

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

  // set up mqttclient
  mqttclient.setServer(BROKER_IP, 1883);
  mqttclient.setCallback(callback);
  connect();
  
  mlx.begin();  
}

void loop() {
  if (!mqttclient.connected()) {
    connect();
  }

  //vars to keep track of time
  static const unsigned long REFRESH_INTERVAL = 1000; // ms
  static unsigned long lastRefreshTime = 0;

  // Read the temperature only one the refresh interval above
  if (millis() - lastRefreshTime >= REFRESH_INTERVAL) {
    lastRefreshTime += REFRESH_INTERVAL;
    temp = mlx.readObjectTempF();

    // Publish and print
    mqttclient.publish("/Temp", String(temp).c_str(), false);
    Serial.print("Object = "); Serial.print(String(temp).c_str()); Serial.println("*F");
  }

  mqttclient.loop();
}

// Connect to mqtt client
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
