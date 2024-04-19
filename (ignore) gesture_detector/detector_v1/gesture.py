import numpy as np
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 

import cv2
import mediapipe as mp
from tensorflow.keras.models import load_model
import tensorflow as tf

print("Num GPUs Available: ", len(tf.config.list_physical_devices('GPU')))

# Initialize MediaPipe Hands module
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()

# Initialize MediaPipe Drawing module for drawing landmarks
mp_drawing = mp.solutions.drawing_utils

# Open a video capture object (0 for the default camera)
cap = cv2.VideoCapture(0)
address = 'https://192.168.1.21:8080/video'
cap.open(address)

classNames = ['okay', 'peace', 'thumbs up', 'thumbs down', 'call me', 'stop', 'rock', 'live long', 'fist', 'smile']
model = tf.saved_model.load('mp_hand_gesture')

while cap.isOpened():
    ret, frame = cap.read()
    x, y, c = frame.shape

    if not ret:
        continue
    
    # Convert the frame to RGB format
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Process the frame to detect hands
    results = hands.process(frame_rgb)
    
    # Check if hands are detected
    if results.multi_hand_landmarks:
        landmarks = []
        for hand_landmarks in results.multi_hand_landmarks:
            for lm in hand_landmarks.landmark:
                lmx = int(lm.x * x)
                lmy = int(lm.y * y)
                landmarks.append([lmx, lmy])

            # Draw landmarks on the frame
        mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
        try:
            prediction = model([landmarks])
            classID = np.argmax(prediction)
            className = classNames[classID]
            cv2.putText(frame, className, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2, cv2.LINE_AA)
        except Exception as e:
            print(e)

    # Display the frame with hand landmarks
    cv2.imshow('Hand Recognition', frame)
    
    # Exit when 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video capture object and close the OpenCV windows
cap.release()
cv2.destroyAllWindows()