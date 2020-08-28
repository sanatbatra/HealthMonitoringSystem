import platform
from kafka import KafkaConsumer
import logging
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Conditional Importing
if(platform.system() == 'Darwin'):
    import pync
elif(platform.system() == 'Windows'):
    from win10toast import ToastNotifier
else:
    logger.info('Importing Linux Notification Service')

def notify_user():
    consumer = KafkaConsumer('POSTURE',bootstrap_servers=['localhost:9092'],group_id=None)
    for message in consumer:
        if(platform.system() == 'Darwin'):
            notify_macOS(message.value)
        elif(platform.system() == 'Windows'):
            notify_windows(message.value)
        else:
            notify_linux(message.value)

def notify_macOS(payload):
    pync.notify(payload, title='BlackRock Health')

def notify_windows(payload):
    toaster = ToastNotifier()
    toaster.show_toast("BlackRock Health",
                   payload,
                   icon_path= "resources/BLK.ico",
                   duration=3)

def notify_linux(payload):
    logger.info('To be Implemented')

if __name__ == "__main__":
    notify_user()