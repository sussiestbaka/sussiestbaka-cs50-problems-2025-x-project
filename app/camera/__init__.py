from flask import Blueprint, render_template, request, redirect, url_for, flash, session, Response
from pywa import WhatsApp
import cv2
import numpy as np
import os
import time

# WhatsApp setup
phone_id = ''
WHATSAPP_API_TOKEN = ""
RECIPIENT_NUMBER = ""  # No '+' to match original usage
SENDER_NUMBER = ""
last_message_time = 0
MESSAGE_DELAY = 10

app = WhatsApp(phone_id=phone_id, token=WHATSAPP_API_TOKEN)

# GPIO setup using command-line tool
GPIO_PIN = 1  # Replace with your actual GPIO pin number
os.system(f"gpio mode {GPIO_PIN} out")
os.system(f"gpio write {GPIO_PIN} 0")

def set_gpio_state(pin, state):
    os.system(f"gpio write {pin} {state}")

camera_preview = Blueprint('camera_preview', __name__)

# Open the camera (index 2 as in original)
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
cap.set(cv2.CAP_PROP_FPS, 25)

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

# Load known faces
KNOWN_FACES_DIR = "known_faces"
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
                startX, startY, w, h = detected_face[0:4].astype(np.int32)
                endX = startX + w
                endY = startY + h

                face_roi = image[startY:endY, startX:endX]
                known_faces.append(np.array([w, h]))
                known_faces_images.append(image)
                known_face_names.append(filename)
        else:
            print(f"No face detected in image: {filename}")

def gen_frames():
    while True:
        success, frame = cap.read()
        if not success:
            break
        else:
            # Face detection and recognition logic inside streaming loop
            height, width, _ = frame.shape
            face_detector.setInputSize((width, height))
            _, faces = face_detector.detect(frame)

            unknown_face_detected = False
            known_face_detected = False
            global last_message_time
            global gpio_on_time

            if faces is not None and len(faces) > 0:
                for detected_face in faces:
                    startX, startY, w, h = detected_face[0:4].astype(np.int32)
                    endX = startX + w
                    endY = startY + h

                    face_roi = frame[startY:endY, startX:endX]

                    match_found = False
                    for i, known_face_image in enumerate(known_faces_images):
                        known_face_box = known_faces[i]
                        score, match_result = recognizer.match(frame, np.array([w, h]), known_face_image, known_face_box)
                        if match_result == 1:
                            print(f"Known face detected: {known_face_names[i]} with score: {score}")
                            match_found = True
                            known_face_detected = True
                            break
                    if not match_found:
                        unknown_face_detected = True

            if unknown_face_detected:
                print("Unknown face detected!")
                image_path = "unknown_face.jpg"
                cv2.imwrite(image_path, frame)

                current_time = time.time()
                if last_message_time == 0 or (current_time - last_message_time >= MESSAGE_DELAY):
                    try:
                        app.send_image(RECIPIENT_NUMBER, image=image_path, caption="Unknown face detected!")
                        print("WhatsApp message sent successfully!")
                        last_message_time = current_time
                    except Exception as e:
                        print(f"Error sending WhatsApp message: {e}")
                else:
                    print("Rate limit exceeded. Skipping message.")

                set_gpio_state(GPIO_PIN, 0)
                gpio_on_time = 0

            elif known_face_detected and not unknown_face_detected:
                if gpio_on_time == 0:
                    print("Known face detected! Activating GPIO pin.")
                    set_gpio_state(GPIO_PIN, 1)
                    gpio_on_time = time.time()
                    

            if gpio_on_time != 0 and time.time() - gpio_on_time >= 30:
                set_gpio_state(GPIO_PIN, 0)
                gpio_on_time = 0

            # Encode frame for streaming
            ret, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@camera_preview.route('/camera_preview')
def index():
    if 'logged_in' not in session:
        return redirect(url_for('auth.login'))
    return render_template('camera_preview.html')

@camera_preview.route('/video_feed')
@login_required
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@camera_preview.route('/whatsapp')
@login_required
def whatsapp():
    # Capture one frame and send via WhatsApp
    success, frame = cap.read()
    if not success:
        flash('Failed to capture image', 'error')
        return redirect(url_for('camera_preview.index'))

    temp_path = "temp_frame.jpg"
    cv2.imwrite(temp_path, frame)

    try:
        app.send_image(RECIPIENT_NUMBER, image=temp_path)
        flash('Image sent successfully!', 'success')
    except Exception as e:
        flash(f'Error sending image: {str(e)}', 'error')

    os.remove(temp_path)
    return render_template('camera_preview.html')


# Initialize global variable for GPIO timing
gpio_on_time = 0
