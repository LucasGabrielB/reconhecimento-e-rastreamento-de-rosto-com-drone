import cv2
from drone import Drone

def get_most_important_face(faces_data):
    ''' Return the location of the most important face. '''

    if len(faces_data) == 0:
        return None 

    faces_data_ordered = sorted(faces_data, key=lambda x: x['permission_level'])
    
    return faces_data_ordered[0]['location']


def drawn_drone_status(frame, drone: Drone):
    ''' Drawn drone status in the screen. '''

    font = cv2.FONT_HERSHEY_PLAIN

    cv2.putText(frame, f'Bateria: {drone.tello.get_battery()} %',          (10, 10), font, 1, (255, 255, 255))
    cv2.putText(frame, f'Barometro: {drone.tello.get_barometer()} cm',     (10, 25), font, 1, (255, 255, 255))
    cv2.putText(frame, f'Temperatura: {drone.tello.get_temperature()} C',  (10, 40), font, 1, (255, 255, 255))
    cv2.putText(frame, f'Altura: {drone.tello.get_height()} cm',           (10, 55), font, 1, (255, 255, 255))
    cv2.putText(frame, f'Tempo de voo: {drone.tello.get_flight_time()} s', (10, 70), font, 1, (255, 255, 255))
