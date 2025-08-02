#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include "config.h"  // Wi-Fi and MQTT credentials

#define PIR_PIN D1  // PIR sensor input pin
  
WiFiClient espClient;
PubSubClient client(espClient);

void setup_wifi() {
  delay(10);
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.begin(ssid, password);  // Connect to Wi-Fi
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("WiFi connected");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());  // Print assigned IP address
}

void setup() {
  pinMode(PIR_PIN, INPUT);  // Set PIR pin as input
  Serial.begin(115200);
  setup_wifi();  // Connect to Wi-Fi
  client.setServer(mqtt_server, 1883);  // Set MQTT server and port
}

void loop() {
  // Reconnect to MQTT if connection lost
  if (!client.connected()) {
    while (!client.connected()) {
      Serial.print("Attempting MQTT connection...");
      if (client.connect("ESP8266Client")) {
        Serial.println("connected");
      } else {
        Serial.print("failed, rc=");
        Serial.print(client.state());
        delay(5000);  // Wait before retrying
      }
    }
  }
  client.loop();  // Maintain MQTT connection

  int motion = digitalRead(PIR_PIN);  // Read PIR sensor
  if (motion == HIGH) {
    client.publish("home/motion", "Motion detected");  // Publish motion detected
    Serial.println("⚠️ Motion Detected!");
  } else {
    client.publish("home/motion", "No motion");  // Publish no motion
    Serial.println("No motion...");
  }

  delay(1000);  // Wait 1 second before next read
}
