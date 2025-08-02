# IoT Smart Home Automation System

This project implements a smart home security solution using an ESP8266 microcontroller, a PIR motion sensor, MQTT messaging, and AI-powered image analysis.

## Overview

The system continuously monitors motion via a PIR sensor connected to the ESP8266. When motion is detected, the ESP8266 publishes a message over MQTT to a Raspberry Pi acting as the central hub. Upon receiving the alert, the Raspberry Pi triggers a connected USB camera to capture an image of the scene.

The captured image is then processed locally on the Raspberry Pi using TensorFlow and OpenCV. The AI model analyzes the image to detect whether a person is present. This ensures that alerts are meaningful and reduces false positives caused by pets or other moving objects.

If a person is detected, the system automatically sends the photo to the user’s phone via the Telegram bot API, providing real-time notification of potential intruders or visitors.

## Key Features

- **Real-time motion detection** using a PIR sensor and ESP8266 microcontroller.
- **Robust communication** via MQTT protocol between ESP8266 and Raspberry Pi.
- **AI-powered image recognition** using TensorFlow Lite and OpenCV to verify human presence.
- **Instant notifications** sent directly to user’s phone through Telegram bot API.

## Technology Stack

- ESP8266 with Arduino IDE for sensor monitoring and MQTT publishing
- MQTT protocol for lightweight, reliable messaging
- Raspberry Pi for camera control and AI processing
- TensorFlow Lite and OpenCV for efficient image analysis
- Telegram Bot API for user notifications

## Files
- motion_camera_objectdetection.py is the python script run through the RaspberryPi terminal to start system. 


