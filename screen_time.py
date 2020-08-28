import numpy as np
import cv2
from datetime import datetime
from notifications import notify_user
from kafka import KafkaProducer
face_cascade = cv2.CascadeClassifier('resources/haarcascade_frontalface_default.xml')

cap = cv2.VideoCapture(0)
signIn = None
delta = None
signOut = None
store = []
flag= True
producer = KafkaProducer(bootstrap_servers='localhost:9092')
TOPIC = 'POSTURE'
while True:
	# Capture frame-by-frame
	ret, img = cap.read()

	img = cv2.medianBlur(img, 3)

	gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
	faces = face_cascade.detectMultiScale(gray, 1.3, 5)

	if len(faces) > 0:
		delta = None
		signOut = None
		if signIn is None:
			signIn = datetime.now()
			payload= "Sign in time "+str(signIn.time())
			producer.send(TOPIC,payload)
			print(payload)
		if (datetime.now()-signIn).total_seconds()>20 and flag is True:
			payload="You have been sitting for way too long, go take a walk."
			producer.send(TOPIC,payload)
			flag= False

	else:
		if signOut is None:
			signOut = datetime.now()
		delta = datetime.now()
		elapsedTime = delta - signOut
		elapsedTime = elapsedTime.total_seconds()
		if elapsedTime > 10 and signIn != None:
			activeTime = signOut-signIn
			activeTime = activeTime.total_seconds()
			payload = "User was active for " + str(activeTime) + "seconds"
			producer.send(TOPIC,payload)
			store.append(activeTime)
			signIn = None
			delta = None
			signOut = None
			flag= True