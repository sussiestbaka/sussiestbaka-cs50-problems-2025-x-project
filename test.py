import cv2

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Cannot open camera")
else:
    ret, frame = cap.read()
    if ret:
        print("Frame captured successfully")
    else:
        print("Error: Unable to capture frame")
    cap.release()
