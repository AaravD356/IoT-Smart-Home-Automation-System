import paho.mqtt.client as mqtt
import subprocess
import datetime
import os
import requests
import cv2
import numpy as np
import tflite_runtime.interpreter as tflite
from config import BOT_TOKEN, CHAT_ID  # Import Telegram bot token and chat ID from separate config file

# Directory to save captured photos
photo_dir = "/home/pi/motion_captures"
# Create the directory if it does not exist
os.makedirs(photo_dir, exist_ok=True)

# Load TensorFlow Lite model for object detection
interpreter = tflite.Interpreter(model_path="tflite_model/detect.tflite")
interpreter.allocate_tensors()  # Allocate memory for the model
input_details = interpreter.get_input_details()  # Get input details for the model (e.g., input shape)
output_details = interpreter.get_output_details()  # Get output details (e.g., output tensors)

def preprocess_image(img, input_shape):
    """
    Resize and preprocess the input image to match model input requirements:
    - Resize to expected size
    - Convert BGR (OpenCV default) to RGB
    - Change data type to uint8
    - Add batch dimension
    """
    img = cv2.resize(img, (input_shape[2], input_shape[1]))
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = img.astype(np.uint8)
    img = np.expand_dims(img, axis=0)  # Add batch dimension
    return img

def detect_objects(img):
    """
    Run object detection on the given image using the TFLite model.
    Returns:
      - person_detected (bool): True if a person is detected
      - img (numpy.ndarray): Image with bounding boxes drawn if person detected
    """
    input_shape = input_details[0]['shape']  # Model input shape
    input_data = preprocess_image(img, input_shape)  # Preprocess image

    # Set the model input tensor
    interpreter.set_tensor(input_details[0]['index'], input_data)
    interpreter.invoke()  # Run inference

    # Extract detection results from output tensors
    boxes = interpreter.get_tensor(output_details[0]['index'])[0]    # Bounding box coordinates (normalized)
    classes = interpreter.get_tensor(output_details[1]['index'])[0]  # Class IDs for detected objects
    scores = interpreter.get_tensor(output_details[2]['index'])[0]   # Confidence scores for detections
    num = int(interpreter.get_tensor(output_details[3]['index'])[0]) # Number of detections

    threshold = 0.5  # Confidence threshold for detection
    person_detected = False

    height, width, _ = img.shape  # Get image dimensions

    # Loop over all detections
    for i in range(num):
        # Check if detection meets confidence threshold and is a person (class 0)
        if scores[i] > threshold and int(classes[i]) == 0:
            person_detected = True
            # Convert normalized box coordinates to pixel coordinates
            ymin, xmin, ymax, xmax = boxes[i]
            left = int(xmin * width)
            right = int(xmax * width)
            top = int(ymin * height)
            bottom = int(ymax * height)

            # Draw bounding box rectangle around detected person
            cv2.rectangle(img, (left, top), (right, bottom), (0, 255, 0), 2)

            # Add label text with confidence score
            cv2.putText(img, f"Person: {int(scores[i]*100)}%", (right, bottom - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 2)

    return person_detected, img

def send_photo_to_telegram(photo_path):
    """
    Send the specified photo file to the configured Telegram chat using the Telegram Bot API.
    """
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"  # Telegram Bot API endpoint
    with open(photo_path, 'rb') as photo:
        files = {'photo': photo}  # File payload for photo
        data = {'chat_id': CHAT_ID}  # Target chat ID
        response = requests.post(url, files=files, data=data)  # Send POST request
        print("Telegram response:", response.json())  # Print Telegram API response for debugging

def on_connect(client, userdata, flags, rc):
    """
    MQTT callback function called when the client connects to the broker.
    Subscribes to the motion detection topic upon successful connection.
    """
    if rc == 0:
        print("Connected to MQTT broker!")
        client.subscribe("home/motion")  # Subscribe to the topic to receive motion events

def on_message(client, userdata, message):
    """
    MQTT callback function called when a message is received on a subscribed topic.
    Handles motion detection messages by capturing and analyzing images.
    """
    msg = message.payload.decode()  # Decode the message payload from bytes to string

    if "Motion detected" in msg:
        print("Motion detected! Capturing photo...")

        # Create timestamped filenames for raw and annotated images
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        raw_filename = f"{photo_dir}/{timestamp}_raw.jpg"
        annotated_filename = f"{photo_dir}/{timestamp}_annotated.jpg"

        # Capture a photo using fswebcam command-line tool
        subprocess.run(["fswebcam", "-r", "1280x720", "--no-banner", raw_filename])
        print(f"Photo saved: {raw_filename}")

        # Load the captured image into memory using OpenCV
        frame = cv2.imread(raw_filename)
        if frame is None:
            print("Failed to read captured image.")
            return  # Exit if image loading failed

        # Detect if a person is in the image and get annotated image with bounding boxes
        person_found, annotated_frame = detect_objects(frame)
        if person_found:
            # Save the annotated image with bounding box
            cv2.imwrite(annotated_filename, annotated_frame)
            print(f"Person detected! Sending annotated photo: {annotated_filename}")

            # Send the annotated photo via Telegram
            send_photo_to_telegram(annotated_filename)
        else:
            print("No person detected. Not sending photo.")
    else:
        # Ignore other messages not related to motion detection
        print(f"Ignoring message: {msg}")

# Initialize MQTT client and set callback functions
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

# Connect to RaspberryPi MQTT broker and start listening for messages
try:
    print("Connecting to broker...")
    client.connect("localhost", 1883, 60)
except Exception as e:
    print(f"MQTT connection failed: {e}")
    exit(1)

print("Looping for messages...")
client.loop_forever()  # Start infinite loop to process MQTT messages continuously
