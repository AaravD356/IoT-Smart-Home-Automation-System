#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include "config.h"

#define PIR_PIN D1
  
WiFiClient espClient;
PubSubClient client(espClient);

void setup_wifi() {
  delay(10);
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("WiFi connected");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
}

void setup() {
  pinMode(PIR_PIN, INPUT);
  Serial.begin(115200);
  setup_wifi();
  client.setServer(mqtt_server, 1883);
}

void loop() {
  if (!client.connected()) {
    while (!client.connected()) {
      Serial.print("Attempting MQTT connection...");
      if (client.connect("ESP8266Client")) {
        Serial.println("connected");
      } else {
        Serial.print("failed, rc=");
        Serial.print(client.state());
        delay(5000);
      }
    }
  }
  client.loop();

  int motion = digitalRead(PIR_PIN);
  if (motion == HIGH) {
    client.publish("home/motion", "Motion detected");
    Serial.println("⚠️ Motion Detected!");
  } else {
    client.publish("home/motion", "No motion");
    Serial.println("No motion...");
  }

  delay(1000);
}
