import cv2
import mediapipe as mp
import pulsar 
from body_landmarks import BODY_LANDMARKS
import json
from landmark import Landmark

# Variables hands target
handsUp = 0
handsDown = 0

# Method pulsar producer
def pulsarProducer():
    client = pulsar.Client('pulsar://localhost:6650')
    producer = client.create_producer('my-topic')
    return producer

# Method pulsar send message
def pulsarSendMessage(producer, handsSendMessage):
    producer.send(('Hands ' + handsSendMessage).encode('utf-8'))
    producer.flush()

def filter(landmarks)->list:
    return [landmarks[landmark_index] for landmark_index in BODY_LANDMARKS.values()]

def instantiate(landmarks)->list[Landmark]:
    return [Landmark(landmark.x, landmark.y, landmark.z) for landmark in landmarks]

def send(landmarks,producer)->None:
    producer.send((landmarks).encode('utf-8'))
    producer.flush()

def landmark_to_json(landmark:Landmark)->str:
    return {
        "x": landmark.x,
        "y": landmark.y,
        "z": landmark.z
    }

def prepare(landmarks):
    landmarks = filter(landmarks)
    landmarks = instantiate(landmarks)
    landmarks = json.dumps(landmarks,default=landmark_to_json)
    return landmarks





# Mediapipe utilities
def recognizeBodyExpressionInRealTime():
    mp_drawing = mp.solutions.drawing_utils # Drawing utilities
    mp_pose = mp.solutions.pose # Pose utilities

    # Initiate the pose model
    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        
        # Open the camera
        cap = cv2.VideoCapture(0)
        
        # Loop through the frames
        while cap.isOpened():
            # Read and resize the frame
            ret, frame = cap.read()
            
            # Is not ret, then break
            if not ret:
                break
            
            frame = cv2.resize(frame, (640, 480)) # Resize the frame
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) # Convert the frame to RGB
            results = pose.process(frame_rgb) # Process the frame

            # Draw the landmarks
            if results.pose_landmarks is not None:
                mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                                        mp_drawing.DrawingSpec(color=(245, 117, 66), thickness=2, circle_radius=2),
                                        mp_drawing.DrawingSpec(color=(245, 66, 230), thickness=2, circle_radius=2)
                                        )
                
                # Get the landmarks for the wrists (left and right)
                left_wrist = results.pose_landmarks.landmark[15]
                right_wrist = results.pose_landmarks.landmark[16]

                # Check if both wrists are above a certain threshold (adjust as needed)
                if left_wrist.y < 0.2 and right_wrist.y < 0.2:
                    landmarks = prepare(results.pose_landmarks.landmark)
                    send(landmarks,pulsarProducer())

                    # Hands are up, so draw a bounding box and message
                    cv2.rectangle(frame, (50, 50), (590, 150), (0, 255, 0), 2)
                    cv2.putText(frame, "Hands Up!", (60, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    # Send message pulsar
                    handsUp = 1
                    if handsUp == 1:
                        pulsarSendMessage(pulsarProducer(), 'Up')
                        #print('SendUp')
                        handsUp = 0

                # Get the landmarks for the hands down (left and right)
                left_hip = results.pose_landmarks.landmark[15]
                right_hip = results.pose_landmarks.landmark[16]

                # Check if both hands are below a certain threshold (adjust as needed)
                if left_hip.y > 0.8 and right_hip.y > 0.8 is not None and results.pose_landmarks.landmark[12].y < 0.5:
                    landmarks = prepare(results.pose_landmarks.landmark)
                    send(landmarks,pulsarProducer())
                    
                    # Hands are up, so draw a bounding box and message
                    cv2.rectangle(frame, (50, 50), (590, 150), (0, 0, 255), 2)
                    cv2.putText(frame, "Hands Down!", (60, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                    # Send message pulsar
                    handsDown = 1
                    if handsDown == 1:
                        pulsarSendMessage(pulsarProducer(), 'Down')
                        #print('SendDown')
                        handsDown = 0
                    
            # Show the frame
            cv2.imshow('Mediapipe Feed', frame)
            # Break if q is pressed
            if cv2.waitKey(10) & 0xFF == ord('q'):
                break

        cap.release()  # Release the camera
        cv2.destroyAllWindows() # Destroy the window

# Main method
if __name__ == "__main__":
    recognizeBodyExpressionInRealTime()