import cv2
from kafka import KafkaProducer
import time
import datetime

NOTIFICATIONS_TOPIC = 'POSTURE'
UI_TOPIC = 'FLASK'

def run():
    notifications_producer = KafkaProducer(bootstrap_servers='localhost:9092')
    ui_producer = KafkaProducer(bootstrap_servers='localhost:9092')
    too_close_count = 0
    posture_count = 0
    haar_face_file = 'resources/haarcascade_frontalface_default.xml'
    haar_upperbody_file = 'resources/HS.xml'

    # datasets = 'datasets'

    # sub_data = 'sanat'
    #
    # path = os.path.join(datasets, sub_data)
    # if not os.path.isdir(path):
    #     os.mkdir(path)

    # defining the size of images

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
    while True:
        (_, im) = webcam.read()
        gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 4)
        upperbodies = upperbody_cascade.detectMultiScale(gray, 1.3, 4)
        font = cv2.FONT_HERSHEY_SIMPLEX
        bottomLeftCornerOfText = (10, 400)
        fontScale = 1
        fontColor = (0, 10, 255)
        lineType = 2
        for (x, y, w, h) in faces:
            current_frame_has_face = True
            #cv2.rectangle(im, (x, y), (x + w, y + h), (255, 0, 0), 2)

            if w > 300 and h > 300:
                current_frame_displaying_warning = True
                cv2.putText(im, 'TOO CLOSE!',
                            bottomLeftCornerOfText,
                            font,
                            fontScale,
                            fontColor,
                            lineType)
                notifications_producer.send(NOTIFICATIONS_TOPIC, 'YOU ARE TOO CLOSE')
                too_close_count += 1
                ui_producer.send(UI_TOPIC, str(too_close_count))
        if prev_frame_displaying_warning and not current_frame_displaying_warning and not current_frame_has_face:
            cv2.putText(im, 'WAY TOO CLOSE!',
                        bottomLeftCornerOfText,
                        font,
                        fontScale,
                        fontColor,
                        lineType)
            too_close_count += 1
            ui_producer.send(UI_TOPIC, str(too_close_count))
            notifications_producer.send(NOTIFICATIONS_TOPIC, "YOU'RE WAY TOO CLOSE TO THE CAMERA")
            current_frame_has_face = True
            current_frame_displaying_warning = True

        count += 1

        for (x, y, w, h) in upperbodies:
            current_frame_has_upperbody = True

            #cv2.rectangle(im, (x, y), (x + w, y + h), (0, 0, 255), 2)

        if current_frame_has_upperbody:
            has_upperbody_log = set_recent_as(has_upperbody_log, True)
        else:
            has_upperbody_log = set_recent_as(has_upperbody_log, False)
        if not check_for_true(has_upperbody_log) and current_frame_has_face:
            cv2.putText(im, 'SIT UPRIGHT!',
                        (150, 50),
                        font,
                        fontScale,
                        fontColor,
                        lineType)
            posture_count += 1
            ui_producer.send(UI_TOPIC, str(posture_count))
            notifications_producer.send(NOTIFICATIONS_TOPIC, "SIT UPRIGHT")
        current_frame_has_face = False
        prev_frame_displaying_warning = current_frame_displaying_warning
        current_frame_displaying_warning = False
        current_frame_has_upperbody = False

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
