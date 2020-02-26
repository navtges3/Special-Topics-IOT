#include <ESP8266WiFi.h>
#include <PubSubClient.h>

#define WLAN_SSID     "Little Boy Juice"
#define WLAN_PASS     "ThanksD00d"
//#define WLAN_SSID   "dan_2"
//#define WLAN_PASS   "supersecretpassword"

#define BROKER_IP     "192.168.0.25"

#define LED   4

// vars
int lightstate;
char light[50];
String light_str;

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

  // setup serial connunication speed
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
}

void loop() {
  // put your main code here, to run repeatedly:
  if (!mqttclient.connected()) {
    connect();
  }
  
  //vars to keep track of time
  static const unsigned long REFRESH_INTERVAL = 1000; // ms
  static unsigned long lastRefreshTime = 0;


  //if time between now and last update is more than time interval
  if (millis() - lastRefreshTime >= REFRESH_INTERVAL)
  {
    lastRefreshTime += REFRESH_INTERVAL;
    lightstate = analogRead(A0);
    light_str = String(lightstate);
    light_str.toCharArray(light, light_str.length() + 1);
    Serial.println(light);
    mqttclient.publish("/Light", light, false);
  }

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
