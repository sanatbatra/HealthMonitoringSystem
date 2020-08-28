# BlackRock Health Monitor

BlackRock Hack Application to Monitor Health.

# Tested Environments
* python 2.7

# To Do

- [x] Distance Detection
- [x] Monitor Screen Time
- [ ] Keylogging Monitoring
- [x] Blink Rate Detection
- [x] Posture Detection
- [x] Desktop Notifications
- [ ] Incorporate [Firebase](https://pypi.org/project/python-firebase/) library 
- [x] Incorporate [Flask](http://flask.pocoo.org) library
- [ ] Design Frontend With Flask (To Discuss)
- [ ] Incorporate Multithreading (To Discuss - One thread per Service?)

# Setup Pip Dependencies

1. Windows: `pip install -r windows.txt`
2. macOS: `pip install -r macOS.txt`

# How To Run Flask

1. Unix Systems: Export FLASK_APP as `export FLASK_APP=blackrock-health.py`
2. Windows Systems: `set FLASK_APP=blackrock-health.py`
3. Run with: `flask run`
4. Server runs on `http://127.0.0.1:5000/`

# Adding Dependencies to Requirements.txt

1. Unix Systems: `pip freeze > requirements.txt`

# Setting Up Kafka

1. Download [Kafka](https://www.apache.org/dyn/closer.cgi?path=/kafka/2.1.0/kafka_2.11-2.1.0.tgz)
2. `tar -xzf kafka_2.11-2.1.0.tgz`
3. `cd kafka_2.11-2.1.0`
4. Start Zookeeper: `bin/zookeeper-server-start.sh config/zookeeper.properties`
5. Start Kafka:  `bin/kafka-server-start.sh config/server.properties`
6. Create a Topic `bin/kafka-topics.sh --create --zookeeper localhost:2181 --replication-factor 1 --partitions 1 --topic POSTURE`
7. Run your code.