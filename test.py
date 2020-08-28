from scipy.spatial import distance as dist
from imutils.video import VideoStream
from imutils import face_utils
import dlib
import cv2
from datetime import datetime
import pickle
from kafka import KafkaProducer
import math

def eye_aspect_ratio(eye):
    # compute the euclidean distances between the two sets of
    # vertical eye landmarks (x, y)-coordinates
    A = dist.euclidean(eye[1], eye[5])
    B = dist.euclidean(eye[2], eye[4])

    # compute the euclidean distance between the horizontal
    # eye landmark (x, y)-coordinates
    C = dist.euclidean(eye[0], eye[3])

    # compute the eye aspect ratio
    ear = (A + B) / (2.0 * C)

    # return the eye aspect ratio
    return ear


# construct the argument parse and parse the arguments

# define two constants, one for the eye aspect ratio to indicate
# blink and then a second constant for the number of consecutive
# frames the eye must be below the threshold
EYE_AR_THRESH = 0.30
EYE_AR_CONSEC_FRAMES = 2

# initialize the frame counters and the total number of blinks
COUNTER = 0
TOTAL = 0

# initialize dlib's face detector (HOG-based) and then create
# the facial landmark predictor
print("[INFO] loading facial landmark predictor...")
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor('shape_predictor_68_face_landmarks.dat')

# grab the indexes of the facial landmarks for the left and
# right eye, respectively
(lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
(rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]

vs = VideoStream(src=0).start()
current_frame_has_face = False
current_frame_displaying_warning = False
prev_frame_displaying_warning = False
font = cv2.FONT_HERSHEY_SIMPLEX
bottomLeftCornerOfText = (10, 400)
fontScale = 1
fontColor = (0, 10, 255)
lineType = 2
signIn = None
delta = None
signOut = None
flag = True
displaying_notification = False
producer = KafkaProducer(bootstrap_servers='localhost:9092')
TOPIC = 'POSTURE'
# loop over frames from the video stream
while True:
    # if this is a file video stream, then we need to check if
    # there any more frames left in the buffer to process

    # grab the frame from the threaded video file stream, resize
    # it, and convert it to grayscale
    # channels)
    frame = vs.read()
    # frame = imutils.resize(frame, width=450)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # detect faces in the grayscale frame
    rects = detector(gray, 0)

    # loop over the face detections
    for rect in rects:
        # determine the facial landmarks for the face region, then
        # convert the facial landmark (x, y)-coordinates to a NumPy
        # array
        current_frame_has_face = True
        if ((rect.left()-rect.right())*(rect.top()-rect.bottom())) > 32000:
            current_frame_displaying_warning = True
            cv2.putText(frame, 'TOO CLOSE!',
                        bottomLeftCornerOfText,
                        font,
                        fontScale,
                        fontColor,
                        lineType)

            if displaying_notification and (datetime.now()- time_display).total_seconds() > 3.0:
                displaying_notification = False
            if not displaying_notification:
                producer.send(TOPIC, "YOU'RE TOO CLOSE TO THE CAMERA")
                time_display = datetime.now()
                displaying_notification = True


        shape = predictor(gray, rect)
        shape = face_utils.shape_to_np(shape)

        # extract the left and right eye coordinates, then use the
        # coordinates to compute the eye aspect ratio for both eyes
        leftEye = shape[lStart:lEnd]
        rightEye = shape[rStart:rEnd]
        leftEAR = eye_aspect_ratio(leftEye)
        rightEAR = eye_aspect_ratio(rightEye)

        # average the eye aspect ratio together for both eyes
        ear = (leftEAR + rightEAR) / 2.0

        # compute the convex hull for the left and right eye, then
        # visualize each of the eyes
        leftEyeHull = cv2.convexHull(leftEye)
        rightEyeHull = cv2.convexHull(rightEye)
        cv2.drawContours(frame, [leftEyeHull], -1, (0, 255, 0), 1)
        cv2.drawContours(frame, [rightEyeHull], -1, (0, 255, 0), 1)

        # check to see if the eye aspect ratio is below the blink
        # threshold, and if so, increment the blink frame counter
        if ear < EYE_AR_THRESH:
            COUNTER += 1

        # otherwise, the eye aspect ratio is not below the blink
        # threshold
        else:
            # if the eyes were closed for a sufficient number of
            # then increment the total number of blinks
            if COUNTER >= EYE_AR_CONSEC_FRAMES:
                TOTAL += 1

            # reset the eye frame counter
            COUNTER = 0

        # draw the total number of blinks on the frame along with
        # the computed eye aspect ratio for the frame
        cv2.putText(frame, "Blinks: {}".format(TOTAL), (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        cv2.putText(frame, "EAR: {:.2f}".format(ear), (300, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

    if not current_frame_has_face and prev_frame_displaying_warning and not current_frame_displaying_warning:
        cv2.putText(frame, 'WAY TOO CLOSE!',
                    bottomLeftCornerOfText,
                    font,
                    fontScale,
                    fontColor,
                    lineType)
        if displaying_notification and (datetime.now() - time_display).total_seconds() > 3.2:
            displaying_notification = False
        if not displaying_notification:
            producer.send(TOPIC, "YOU'RE WAY TOO CLOSE TO THE CAMERA")
            time_display = datetime.now()
            displaying_notification = True
        current_frame_has_face = True
        current_frame_displaying_warning = True

    if len(rects) > 0:
        delta = None
        signOut = None
        if signIn is None:
            signIn = datetime.now()
            payload = "Sign in time " + str(signIn.time())
            producer.send(TOPIC,payload)
        if (datetime.now() - signIn).total_seconds() > 20 and flag is True:
            payload = "You have been sitting for way too long, go take a walk."
            producer.send(TOPIC,payload)
            flag = False

    else:
        if signOut is None:
            signOut = datetime.now()
        delta = datetime.now()
        elapsedTime = delta - signOut
        elapsedTime = elapsedTime.total_seconds()
        if elapsedTime > 4 and signIn is not None:
            endTime = delta
            activeTime = signOut - signIn
            activeTime = activeTime.total_seconds()
            payload = "User was active for " + str(int(float(activeTime))) + "seconds"
            producer.send(TOPIC , payload)
            break

    current_frame_has_face = False
    prev_frame_displaying_warning = current_frame_displaying_warning
    current_frame_displaying_warning = False
    current_frame_has_upperbody = False
    # show the frame
    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF
totalTime = (endTime - signIn).total_seconds()
store = {'startTime': signIn.strftime("%I:%M:%S"), 'endTime': endTime.strftime("%I:%M:%S"),
         'activeTime': int(float(activeTime)), 'totalTime': int(float(totalTime))}
with open('screentime.pickle', 'wb') as handle:
    pickle.dump(store, handle, protocol=pickle.HIGHEST_PROTOCOL)