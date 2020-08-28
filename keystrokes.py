import pyHook, pythoncom, sys, logging
from datetime import datetime
from kafka import KafkaProducer

counter=0;
TOPIC= 'POSTURE'
startTime= None
producer = KafkaProducer(bootstrap_servers='localhost:9092')


def OnKeyboardEvent(event):
    global counter, startTime
    if(counter==0):
        startTime=datetime.now()
    counter+=1
    if((datetime.now()-startTime).total_seconds()>60.0):
        producer.send(TOPIC,counter)
        counter=0
    return True
hooks_manager = pyHook.HookManager()
hooks_manager.KeyDown = OnKeyboardEvent
hooks_manager.HookKeyboard()
pythoncom.PumpMessages()