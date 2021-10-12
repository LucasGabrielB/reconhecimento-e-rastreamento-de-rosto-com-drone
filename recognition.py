import face_recognition
import numpy as np
import cv2


class FaceRecognition:
    def __init__(self, detection_model='hog') -> None:
        self._known_faces_encodings        = []
        self._known_faces_names            = []
        self._known_faces_permission_level = []
        self._detection_model              = detection_model
    
    def add_face(self, face_encoding, face_name: str, permission_level: int) -> None:
        self._known_faces_encodings.append(face_encoding)
        self._known_faces_names.append(face_name)
        self._known_faces_permission_level.append(permission_level)

    def add_face_from_image(self, file_path: str, face_name: str, permission_level: int) -> None:
        image = face_recognition.load_image_file(file_path)
        image_encoding = face_recognition.face_encodings(image)[0]

        self.add_face(image_encoding, face_name, permission_level)

    def detect_faces(self, frame) -> list:
        small_frame      = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25) # resize frame to 1/4 for faster face recognition processing
        rgb_small_frame  = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
        faces_locations  = face_recognition.face_locations(rgb_small_frame, model=self._detection_model)
        faces_encodings  = face_recognition.face_encodings(rgb_small_frame, faces_locations, model='small')

        faces_names = []
        faces_permission_level = []
        for face_encoding in faces_encodings:
            # see if the face is a match for the known face(s)
            matches          = face_recognition.compare_faces(self._known_faces_encodings, face_encoding)
            name             = '<Desconhecido>'
            permission_level = None

            if True in matches:
                first_match_index = matches.index(True)
                name              = self._known_faces_names[first_match_index]
                permission_level  = self._known_faces_permission_level[first_match_index]

            faces_names.append(name)
            faces_permission_level.append(permission_level)

        self.drawn_faces_box(frame, faces_locations, faces_names, faces_permission_level)
        
        # creating a list with the data of all faces finded in the frame 
        faces_data = [
            {
                'name': n, 
                'permission_level': p, 
                'location': [c * 4 for c in l] # scale back up face locations since the frame we detected in was scaled to 1/4 size
            } 
            for n, p, l in zip(faces_names, faces_permission_level, faces_locations)
        ]

        return faces_data

    def drawn_faces_box(self, frame, faces_locations, faces_names, faces_permission_level, box_color=(0, 0, 255), text_color=(255, 255, 255)) -> None:
        ''' Display the results '''
        
        for (top, right, bottom, left), name, permission_level in zip(faces_locations, faces_names, faces_permission_level):
            # scale back up face locations since the frame we detected in was scaled to 1/4 size
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4

            # draw a box around the face
            cv2.rectangle(frame, (left, top), (right, bottom), box_color, 1)

            # calculate the coordinates of the center of the face
            face_center_x = left + (right - left) // 2
            face_center_y = top - (top - bottom) // 2

            # drawn a circle in the center of the face
            cv2.circle(frame, (face_center_x, face_center_y), 3, box_color, -1)

            # draw a label with a name below the face
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), box_color, cv2.FILLED)
            font = cv2.FONT_HERSHEY_PLAIN
            cv2.putText(frame, name, (left, bottom- 25), font, 1, text_color,)

            if permission_level is not None:
                # draw the permission level
                cv2.putText(frame, f'Nivel de permissao: {permission_level}', (left, bottom- 16), font, .5, text_color)


if __name__ == '__main__':
    from pprint import pprint
    import os

    video_capture = cv2.VideoCapture(0)

    face_recognition = FaceRecognition()

    # add all faces in the "./faces/" directory. file name in the format "<name>_<permission level>"
    for file_name in os.listdir('./faces/'):
        name, permission_level = file_name.split('.')[0].split('_')
        permission_level       = int(permission_level)

        face_recognition.add_face_from_image('./faces/'+file_name, name, permission_level)

    while True:
        ret, frame = video_capture.read()

        face_recognition.detect_faces(frame)

        cv2.imshow('Video', frame)

        if cv2.waitKey(1) & 0xFF == 27: # ESC key
            break

    video_capture.release()
    cv2.destroyAllWindows()