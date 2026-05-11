
import csv
import random
from datetime import datetime
import time
import json
import threading
import queue

from flask import Flask, render_template, Response
from flask_sqlalchemy import SQLAlchemy

from reportlab.pdfgen import canvas

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from report import generate_pdf

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
def pass_sensor_data(sensor_name, batch_size, max_offset, lock_a, lock_b):
    offset = 0
    
    while True:
        if lock_a:
            lock_a.acquire()
        if lock_b:
            lock_b.acquire()
        random_delay = random.uniform(0.1, 0.2)
        random_data_loss = random.uniform(0, 1)
        if random_data_loss > 0.1:
            with app.app_context():
                records = SensorData.query.filter_by(sensor=sensor_name).offset(offset).limit(batch_size).all()
                q.put([{'sensor': r.sensor, 'value': r.value} for r in records])
                db.session.add(StreamLog(sensor=sensor_name, timestamp=datetime.now(), latency_ms=random_delay))
                db.session.commit()
        else:
            with app.app_context():
                db.session.add(StreamLog(sensor=sensor_name, timestamp=datetime.now(), latency_ms=-1))
                db.session.commit()
        offset += batch_size
        if offset >= max_offset:
            offset = 0
        time.sleep(0.1 + random_delay)
        if lock_b:
            lock_b.release()
        if lock_a:
            lock_a.release()


def generate_report():
    time.sleep(10)
    with app.app_context():
        logs_etc = StreamLog.query.filter_by(sensor='ECG').limit(50).all()
        logs_bvp = StreamLog.query.filter_by(sensor='BVP').limit(50).all()
        logs_eda = StreamLog.query.filter_by(sensor='EDA').limit(50).all()

        latency_ecg = [log.latency_ms for log in logs_etc]
        latency_bvp = [log.latency_ms for log in logs_bvp]
        latency_eda = [log.latency_ms for log in logs_eda]

        generate_pdf(latency_ecg, latency_bvp, latency_eda)
    

lock_first = threading.Lock()
lock_second = threading.Lock()

#TODO Dodanie guzika, który wywołuje deadlock np. na 2 sekundy. Fajnie będzie wygenerować taki wykres 
#Pokazanie że wątki na siebie czekały i żaden z nich się nie wykonywał następnie jakoś zwolnienie tego locka
# i pokazanie naprawe wykresów 
#TODO Sprawdzoć czy ma to wpływ na synchronizacje czy wykresy się nie rozjadą (raczej na pewno się rozjadą)
#bo EDA będzie cały czas pakować dane do kolejki a tamte nie
ecg_thread = threading.Thread(target=pass_sensor_data, args=("ECG",70,70000,None, None)).start()
bvp_thread = threading.Thread(target=pass_sensor_data, args=("BVP",6,6400, None, None)).start()
eda_thread = threading.Thread(target=pass_sensor_data, args=("EDA",1,400, None, None)).start()

report_thread = threading.Thread(target=generate_report).start()

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