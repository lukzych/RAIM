
import csv
import random
from datetime import datetime
import time
import json
import threading
import queue

from flask import Flask, render_template, Response
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sensors.db'
db = SQLAlchemy(app)

class SensorData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sensor = db.Column(db.String(10), nullable=False)
    value = db.Column(db.Float, nullable=False)
    

class StreamLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sensor = db.Column(db.String(10), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    latency_ms = db.Column(db.Float, nullable=False)

'''
Matematyka
ECG - 700Hz
BVP - 64Hz
EDA - 4Hz

do bazy leci
70 000 ECG
6400 BVP
400 EDA

== 76 800
'''

with app.app_context():
    db.create_all()
    SensorData.query.delete()
    StreamLog.query.delete()
    db.session.commit()

    with open('data/ECG.csv') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            if i >= 70000:
                break
            db.session.add(SensorData(
                sensor='ECG',
                value=float(row['ECG'])
            ))
    db.session.commit()

    with open('data/BVP.csv') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            if i>= 6400:
                break
            db.session.add(SensorData(
                sensor='BVP',
                value=float(row['BVP'])
            ))
    db.session.commit()

    with open('data/EDA.csv') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            if i>= 400:
                break
            db.session.add(SensorData(
                sensor='EDA',
                value=float(row['EDA'])
            ))
        db.session.commit()

#Kolejka 
q = queue.Queue()



def pass_ecg_data():
    offset_ecg = 0
    while True:
        random_delay = random.uniform(0.1, 0.2)
        with app.app_context():
            records = SensorData.query.filter_by(sensor='ECG').offset(offset_ecg).limit(70).all()
            q.put([{'sensor': r.sensor, 'value': r.value} for r in records])
            db.session.add(StreamLog(
                sensor='ECG',
                timestamp=datetime.now(),
                latency_ms= random_delay
            ))
            db.session.commit()
            offset_ecg += 70
            if offset_ecg >= 70000:
                offset_ecg = 0

        time.sleep(0.1 + random_delay)


def pass_bvp_data():
    offset_bvp = 0

    while True:
        random_delay = random.uniform(0.1,0.2)
        with app.app_context():
            records = SensorData.query.filter_by(sensor='BVP').offset(offset_bvp).limit(70).all()
            q.put([{'sensor': r.sensor, 'value': r.value} for r in records])
            db.session.add(StreamLog(
                sensor='BVP',
                timestamp=datetime.now(),
                latency_ms= random_delay
            ))
            db.session.commit()
            offset_bvp += 6

            if offset_bvp >= 6400:
                offset_bvp = 0
        time.sleep(0.1 + random_delay)

def pass_eda_data():
    offset_eda = 0

    while True:
        random_delay = random.uniform(0.1, 0.2)
        with app.app_context():
            records = SensorData.query.filter_by(sensor='EDA').offset(offset_eda).limit(70).all()
            q.put([{'sensor': r.sensor, 'value': r.value} for r in records])
            db.session.add(StreamLog(
                sensor='EDA',
                timestamp=datetime.now(),
                latency_ms= random_delay
            ))
            db.session.commit()
            offset_eda += 1

            if offset_eda >= 400:
                offset_eda = 0
        time.sleep(0.1 + random_delay)



ecg_thread = threading.Thread(target=pass_ecg_data).start()
bvp_thread = threading.Thread(target=pass_bvp_data).start()
eda_thread = threading.Thread(target=pass_eda_data).start()


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/stream")
def stream():
    def generator():
        while True:

            data = q.get()
            if not data: continue
            sensor = data[0]['sensor']
            values = [r['value'] for r in data]

            yield f"data: {json.dumps({'sensor': sensor, 'values': values})}\n\n"


    return Response(generator(), mimetype='text/event-stream')

if __name__ == "__main__":
    app.run(debug=True, use_reloader = False, port=5002)