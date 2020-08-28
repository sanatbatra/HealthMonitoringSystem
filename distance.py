import cv2#, sys, numpy, os , msvcrt
from kafka import KafkaProducer

TOPIC = 'POSTURE'
payload ='Too close to the screen'
def run():
    producer = KafkaProducer(bootstrap_servers='localhost:9092')
    haar_face_file = 'resources/haarcascade_frontalface_default.xml'
    eye_face_file = 'resources/'
    haar_upperbody_file = 'resources/HS.xml'
    cooldown = True
    face_cascade = cv2.CascadeClassifier(haar_face_file)
    upperbody_cascade = cv2.CascadeClassifier(haar_upperbody_file)
    webcam = cv2.VideoCapture(0)
    if webcam is None:
        webcam = cv2.VideoCapture(1)

    count = 1
    has_upperbody_log = [False, False, False, False, False]
    current_frame_has_face = False
    current_frame_displaying_warning = False
    prev_frame_displaying_warning = False
    current_frame_has_upperbody = False
    font = cv2.FONT_HERSHEY_SIMPLEX
    bottomLeftCornerOfText = (10, 400)
    fontScale = 1
    fontColor = (0, 10, 255)
    lineType = 2
    while True:
        (_, im) = webcam.read()
        gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 4)
        # upperbodies = upperbody_cascade.detectMultiScale(gray, 1.3, 4)

        for (x, y, w, h) in faces:
            current_frame_has_face = True
            #cv2.rectangle(im, (x, y), (x + w, y + h), (255, 0, 0), 2)


            if w > 300 and h > 300 and cooldown:
                current_frame_displaying_warning = True
                producer.send(TOPIC, payload)
                cv2.putText(im, 'TOO CLOSE!',
                            bottomLeftCornerOfText,
                            font,
                            fontScale,
                            fontColor,
                            lineType)
                #cooldown = True
        
        count += 1

        #current_frame_has_face = False
        #prev_frame_displaying_warning = current_frame_displaying_warning
        #current_frame_displaying_warning = False
        #current_frame_has_upperbody = False

        cv2.imshow('Proximity Detector', im)
        # if msvcrt.kbhit() and msvcrt.getch() == chr(27).encode():
        #     aborted = True
        #     break
        key = cv2.waitKey(1)


def set_recent_as(log, value):
    log[0] = log[1]
    log[1] = log[2]
    log[2] = log[3]
    log[3] = log[4]
    log[4] = value
    return log


def check_for_true(log):
    for element in log:
        if element:
            return True
    return False


if __name__ == '__main__':
    run()