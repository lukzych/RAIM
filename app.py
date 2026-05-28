
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

        acquired_a = False
        acquired_b = False

        if deadlock_active and lock_a:
            acquired_a = lock_a.acquire(timeout=3)
            if not acquired_a:
                continue

        if deadlock_active and lock_b:
            acquired_b = lock_b.acquire(timeout=3)
            if not acquired_b:
                if acquired_a and lock_a:
                    lock_a.release()
                continue

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


        if acquired_b and lock_b:
            lock_b.release()
        if acquired_a and lock_a:
            lock_a.release()

        acquired_a = False
        acquired_b = False


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


deadlock_active = False
ecg_thread = threading.Thread(target=pass_sensor_data, args=("ECG",70,70000,lock_first, lock_second)).start()
bvp_thread = threading.Thread(target=pass_sensor_data, args=("BVP",6,6400, lock_second, lock_first)).start()
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

@app.route('/trigger_deadlock')
def trigger_deadlock():
    def reset():
        global deadlock_active
        deadlock_active = True
        time.sleep(2)
        deadlock_active = False
    threading.Thread(target=reset).start()
    return {'status': 'ok'}

if __name__ == "__main__":
    app.run(debug=True, use_reloader = False, port=5002)