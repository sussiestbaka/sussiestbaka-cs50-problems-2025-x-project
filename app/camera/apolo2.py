import time
import cv2
import numpy as np
import os
import requests
import json
import base64
from pywa import WhatsApp
# WhatsApp setup
phone_id=''
WHATSAPP_API_TOKEN = ""
RECIPIENT_NUMBER = ""
SENDER_NUMBER = ""
last_message_time = 0
MESSAGE_DELAY = 10
app = WhatsApp(phone_id = phone_id, token=WHATSAPP_API_TOKEN)
gpio_on_time = 0

# GPIO setup using command-line tool
GPIO_PIN = 1  # Replace with the actual GPIO pin number you want to use


# Initialize GPIO pin
os.system(f"gpio mode 1 out")
os.system(f"gpio write 1 0")

def set_gpio_state(pin, state):
    """Set GPIO state using command-line."""
    os.system(f"gpio write {pin} {state}")

# OpenCV setup
video_capture = cv2.VideoCapture(0)
video_capture.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'YUYV'))
video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
video_capture.set(cv2.CAP_PROP_FPS, 25)


def send_whatsapp_message(recipient_number, image_path):
    current_time = time.time()
    if last_message_time is None or (current_time - last_message_time >= MESSAGE_DELAY):
        try:
            message = app.send_image(
                recipient_number,
                image=image_path,
                caption="Unknown face detected!"
        )
            print(f"WhatsApp message sent successfully! Message ID: {message.id}")
            return current_time
        except Exception as e:
            print(f"Error sending WhatsApp message: {e}")
    else:
        print("Rate limit exceeded. Skipping message.")
    return last_message_time
# Example usage (assuming image_path is defined and valid):
# image_path = "unknown_face.jpg"
# send_whatsapp_message(RECIPIENT_NUMBER, image_path)

# Load SFace model for face recognition
from sface import SFace
recognizer = SFace(modelPath="face_recognition_sface_2021dec_int8 (1).onnx", disType=0, backendId=cv2.dnn.DNN_BACKEND_TIMVX, targetId=cv2.dnn.DNN_TARGET_NPU)

# Initialize YuNet face detector
from cv2 import FaceDetectorYN
face_detector = FaceDetectorYN.create(
    model='face_detection_yunet_2023mar_int8.onnx',
    config="",
    input_size=(320, 320),
    score_threshold=0.6,
    nms_threshold=0.3,
    top_k=5000,
    backend_id=cv2.dnn.DNN_BACKEND_TIMVX,
    target_id=cv2.dnn.DNN_TARGET_NPU
)

# Constants for face detection and recognition
KNOWN_FACES_DIR = "known_faces"

# Load known faces
known_faces = []
known_faces_images = []
known_face_names = []



for filename in os.listdir(KNOWN_FACES_DIR):
    if filename.endswith(".jpg") or filename.endswith(".png"):
        image = cv2.imread(os.path.join(KNOWN_FACES_DIR, filename))
        if image is None:
            print(f"Error loading image: {filename}")
            continue

        height, width, _ = image.shape
        face_detector.setInputSize((width, height))
        _, faces = face_detector.detect(image)

        if faces is not None and len(faces) > 0:
            for detected_face in faces:
                startX, startY, width, height = detected_face[0:4].astype(np.int32)
                box = np.array([width, height])
                endX = startX + width
                endY = startY + height

                face_roi = image[startY:endY, startX:endX]
                known_faces.append(box)
                known_faces_images.append(image)
                known_face_names.append(filename)
        else:
              print(f"No face detected in image: {filename}")

while True:
    # Capture a frame
    ret, frame = video_capture.read()

    if not ret:
        print("Failed to grab frame")
        break

    # Get frame dimensions and set input size for YuNet
    height, width, _ = frame.shape
    face_detector.setInputSize((width, height))

    # Detect faces in the frame
    _, faces = face_detector.detect(frame)

    unknown_face_detected = False
    known_face_detected = False
    if faces is not None and len(faces) > 0:
        for detected_face in faces:
            startX, startY, width, height = detected_face[0:4].astype(np.int32)
            box = np.array([width, height])
            endX = startX + width
            endY = startY + height

            face_roi = frame[startY:endY, startX:endX]

            # Match with known faces using SFace.match()
            match_found = False
            for i, known_face_image in enumerate(known_faces_images):
                known_face_box = known_faces[i]
                score, match_result = recognizer.match(frame, box, known_face_image, known_face_box)
                if match_result == 1:  # If a match is found based on similarity thresholds
                    print(f"Known face detected: {known_face_names[i]} with score: {score} ")
                    match_found = True
                    known_face_detected = True
                    break
            if not match_found:
                unknown_face_detected = True

    if unknown_face_detected:
        print(f"Unknown face detected!{score}")
        image_path = "unknown_face.jpg"
        cv2.imwrite(image_path, frame)
        send_whatsapp_message(RECIPIENT_NUMBER, image_path)

  # Turn off GPIO pin immediately when an unknown face is detected.
        set_gpio_state(GPIO_PIN, 0)
        gpio_on_time = 0

    elif known_face_detected and not unknown_face_detected:
        print("Known face detected! Activating GPIO pin.")
        set_gpio_state(GPIO_PIN, 1)  # Turn on the pin
        gpio_on_time = time.time()
        time.sleep(10)


    if gpio_on_time != 0 and time.time() - gpio_on_time >= 30:
         set_gpio_state(GPIO_PIN, 0)  # Turn off after delay.
         gpio_on_time = 0
# Release handle to the webcam
video_capture.release()
cv2.destroyAllWindows()
