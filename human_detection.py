import cv2
import time
import os
import requests

# Set your Line Notify access token here
LINE_NOTIFY_ACCESS_TOKEN = "C4G5Rma1l78k8qyknDUBDewYldtacj7dGK0u7mw0bT8"

# Function to send Line Notify message with image
def send_line_notify(message, image_path):
    url = "https://notify-api.line.me/api/notify"
    headers = {"Authorization": "Bearer " + LINE_NOTIFY_ACCESS_TOKEN}
    payload = {"message": message}
    files = {"imageFile": open(image_path, "rb")}
    response = requests.post(url, headers=headers, data=payload, files=files)
    return response

cap = cv2.VideoCapture('in.avi')

human_cascade = cv2.CascadeClassifier('haarcascade_fullbody.xml')

while True:
    # Capture frame-by-frame
    ret, frame = cap.read()

    if not ret:
        break

    # Our operations on the frame come here
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    humans = human_cascade.detectMultiScale(gray, 1.9, 1)

    # Display the resulting frame
    for (x, y, w, h) in humans:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
        print("Detected!")

    cv2.imshow('frame', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    # Sleep for 10 seconds after detecting humans
    if len(humans) > 0:
        print("Detected!")
        cv2.imwrite("detected_image.jpg", frame)

        with open('status.txt', 'w') as status_file:
            status_file.write("1")

        # Send notification to Line Notify using the function
        message = "ตรวจพบผู้บุกรุก !"
        response = send_line_notify(message, "detected_image.jpg")
        os.system("start detected_image.jpg")  # Open the saved image using the default image viewer in Windows
        
        # Delay for 10 seconds
        # time.sleep(10)
        time.sleep(60)
    else:
        with open('status.txt', 'w') as status_file:
            status_file.write("0")

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
