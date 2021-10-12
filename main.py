from recognition import FaceRecognition
from datetime import datetime
from threading import Thread
from drone import Drone
import utils
import cv2
import os

face_recognition = FaceRecognition(detection_model='hog')

# add all faces in the ./faces/ directory. file name in the format "<name>_<permission level>"
for file_name in os.listdir('./faces/'):
    name, permission_level = file_name.split('.')[0].split('_')
    permission_level       = int(permission_level)

    face_recognition.add_face_from_image('./faces/'+file_name, name, permission_level)

tello = Drone()

WIDTH, HEIGHT = 720, 480

video_path = f'./videos/video_{datetime.now().strftime(r"%Y-%m-%d-%H-%M-%S")}.avi'
video      = cv2.VideoWriter(video_path, cv2.VideoWriter_fourcc(*'XVID'), 30, (WIDTH, HEIGHT))

while True:
    frame = tello.get_frame(WIDTH, HEIGHT)

    faces_data = face_recognition.detect_faces(frame)

    utils.drawn_drone_status(frame, tello)

    face_location = utils.get_most_important_face(faces_data)
    tello.track_face(frame, face_location)

    cv2.imshow('Imagem Drone', frame)

    video.write(frame)

    key = cv2.waitKey(1) & 0xff
    if key == 27: # ESC key
        tello.land()
        video.release()
        break

cv2.destroyAllWindows()
