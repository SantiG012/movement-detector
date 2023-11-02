import cv2
import mediapipe as mp
import pulsar 
from bodyLandmarks import BODY_LANDMARKS
import json
from landMark import LandMark

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

def instantiate(landmarks)->list[LandMark]:
    return [LandMark(landmark.x, landmark.y, landmark.z) for landmark in landmarks]

def send(landmarks,producer)->None:
    producer.send((landmarks).encode('utf-8'))
    producer.flush()

def landmarkToJson(landmark:LandMark)->str:
    return {
        "x": landmark.x,
        "y": landmark.y,
        "z": landmark.z
    }

def prepare(landmarks):
    landmarks = filter(landmarks)
    landmarks = instantiate(landmarks)
    landmarks = json.dumps(landmarks,default=landmarkToJson)
    return landmarks


# Mediapipe utilities
def recognizeBodyExpressionInRealTime():
    mpDrawing = mp.solutions.drawing_utils # Drawing utilities
    mpPose = mp.solutions.pose # Pose utilities

    # Initiate the pose model
    with mpPose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        
        # Open the camera
        cap = cv2.VideoCapture(0)
        
        # Loop through the frames
        while cap.isOpened():
            # Read and resize the frame
            ret, frame = cap.read()
            
            # Is not ret, then break
            if not ret:
                break
            
            frame = cv2.resize(frame, (1600, 900)) # Resize the frame
            frameRgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) # Convert the frame to RGB
            results = pose.process(frameRgb) # Process the frame

            # Draw the landmarks
            if results.pose_landmarks is not None:
                mpDrawing.draw_landmarks(frame, results.pose_landmarks, mpPose.POSE_CONNECTIONS,
                                        mpDrawing.DrawingSpec(color=(245, 117, 66), thickness=2, circle_radius=2),
                                        mpDrawing.DrawingSpec(color=(245, 66, 230), thickness=2, circle_radius=2)
                                        )
                
                # Get the landmarks for the wrists (left and right)
                leftWrist = results.pose_landmarks.landmark[15]
                rightWrist = results.pose_landmarks.landmark[16]

                # Check if both wrists are above a certain threshold (adjust as needed)
                if leftWrist.y < 0.2 and rightWrist.y < 0.2:
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