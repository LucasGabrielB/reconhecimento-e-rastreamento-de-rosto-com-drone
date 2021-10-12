from djitellopy import Tello
import cv2


class Drone:
    def __init__(self) -> None:
        self._tello = Tello()
        self.tello.connect()

        self.tello.for_back_velocity   = 0
        self.tello.left_right_velocity = 0
        self.tello.up_down_velocity    = 0
        self.tello.yaw_velocity        = 0
        self.tello.speed               = 0

        self.tello.streamoff()
        self.tello.streamon()

        self._frame_read = self.tello.get_frame_read()

        print('Estado atual:', self.get_current_state())

        if self.tello.get_battery() < 20:
            raise Exception(f'Bateria muito fraca. {self.tello.get_battery()}')

        self.tello.takeoff()
        self.tello.send_rc_control(0, 0, 30, 0)

    @property
    def tello(self) -> Tello:
        return self._tello

    def get_frame(self, width=360, height=240):
        frame = self._frame_read.frame
        frame = cv2.resize(frame, (width, height))
        return frame

    def land(self) -> None:
        try:
            self.tello.land()
        except: pass

    def get_current_state(self) -> dict:
        return self.tello.get_current_state()

    def track_face(self, frame, face_location) -> None:
        # calculate the coordinates of the center of the frame
        frame_h, frame_w, _ = frame.shape
        frame_center_x      = frame_w // 2
        frame_center_y      = frame_h // 2

        # drawn a circle in the center of the frame
        cv2.circle(frame, (frame_center_x, frame_center_y), 3, (0, 200, 100), -1)

        if face_location is None: # no face find, return
            self.tello.send_rc_control(0, 0, 0, 0)
            return 
        
        # calculate the coordinates of the center of the face
        top, right, bottom, left = face_location
        face_center_x            = left + (right - left) // 2
        face_center_y            = top - (top - bottom) // 2
        
        # drawn a line between the center of the frame and the center of the face
        cv2.line(frame, (face_center_x, face_center_y), (frame_center_x, frame_center_y), (255, 255, 255), 1)

        if face_center_x > frame_center_x:
            yaw_velocity = 5 # move drone to left
        else:
            yaw_velocity = -5  # move drone to right

        if face_center_y > frame_center_y:
            up_down_velocity = -5 # move drone down
        else:
            up_down_velocity = 5 # move drone up

        self.tello.send_rc_control(0, 0, up_down_velocity, yaw_velocity)
