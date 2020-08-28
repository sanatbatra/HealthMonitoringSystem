from app import app 
from flask import render_template, url_for
import pickle

@app.route('/')
@app.route('/BlackRockHealth')
def index():
    with open('screentime.pickle', 'rb') as handle:
        data = pickle.load(handle)
        startTime = data['startTime']
        endTime = data['endTime']
        activeTime = str(data['activeTime']) + 's'
        totalTime = str(data['totalTime']) + 's'

    keystrokes = [73.7, 73.4, 73.8, 72.8, 68.7, 65.2,
                    61.8, 58.7, 58.2, 58.3, 60.5, 65.7,
                    70.2, 71.4, 71.2, 70.9, 71.3, 71.1]
    blinks = [10, 16, 17, 14, 13, 12, 
                20, 16, 20, 20, 12, 13,
                15, 12, 13, 15, 15, 16]               
    times = ['12:00PM', '12:10PM', '12:20PM', '12:30PM', '12:40PM', '12:50PM',
             '1:00PM', '1:10PM', '1:20PM', '1:30PM', '1:40PM', '1:50PM',
             '2:00PM', '2:10PM', '2:20PM', '2:30PM', '2:40PM', '2:50PM']
    return render_template('index.html', title='BlackRock Health Monitoring System',values=keystrokes, labels=times, blinks=blinks, startTime=startTime, endTime=endTime, activeTime=activeTime, totalTime=totalTime)

@app.route('/settings')
def settings():
    return render_template('settings.html', title='Settings')

@app.route('/about')
def about():
    return render_template('about.html', title='About')

@app.route('/maps')
def maps():
    return render_template('maps.html', title='Maps')