
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
        random_data_loss = random.uniform(0,1)
        if random_data_loss > 0.1:
            with app.app_context():
                records = SensorData.query.filter_by(sensor='ECG').offset(offset_ecg).limit(70).all()
                q.put([{'sensor': r.sensor, 'value': r.value} for r in records])
                db.session.add(StreamLog(
                    sensor='ECG',
                    timestamp=datetime.now(),
                    latency_ms= random_delay
                ))
                db.session.commit()

        else:
            with app.app_context():
                db.session.add(StreamLog(
                        sensor='ECG',
                        timestamp=datetime.now(),
                        latency_ms= -1
                    ))
                db.session.commit()

        offset_ecg += 70
        if offset_ecg >= 70000:
            offset_ecg = 0

        time.sleep(0.1 + random_delay)


def pass_bvp_data():
    offset_bvp = 0

    while True:
        random_delay = random.uniform(0.1, 0.2)
        random_data_loss = random.uniform(0,1)
        
        if random_data_loss > 0.1:
            with app.app_context():
                records = SensorData.query.filter_by(sensor='BVP').offset(offset_bvp).limit(6).all()
                q.put([{'sensor': r.sensor, 'value': r.value} for r in records])
                db.session.add(StreamLog(
                    sensor='BVP',
                    timestamp=datetime.now(),
                    latency_ms= random_delay
                ))
                db.session.commit()

        else:
            with app.app_context():
                db.session.add(StreamLog(
                        sensor='BVP',
                        timestamp=datetime.now(),
                        latency_ms= -1
                    ))
                db.session.commit()
        offset_bvp += 6

        if offset_bvp >= 6400:
            offset_bvp = 0
        time.sleep(0.1)

def pass_eda_data():
    offset_eda = 0

    while True:
        random_delay = random.uniform(0.1, 0.2)
        random_data_loss = random.uniform(0,1)

        if random_data_loss > 0.1:
            with app.app_context():
                records = SensorData.query.filter_by(sensor='EDA').offset(offset_eda).limit(1).all()
                q.put([{'sensor': r.sensor, 'value': r.value} for r in records])
                db.session.add(StreamLog(
                    sensor='EDA',
                    timestamp=datetime.now(),
                    latency_ms= random_delay
                ))
                db.session.commit()

        else:
            with app.app_context():
                db.session.add(StreamLog(
                        sensor='EDA',
                        timestamp=datetime.now(),
                        latency_ms= -1
                    ))
                db.session.commit()
        offset_eda += 1

        if offset_eda >= 400:
            offset_eda = 0
        time.sleep(0.1 + random_delay)

def generate_report():
    time.sleep(10)
    with app.app_context():
        logs_etc = StreamLog.query.filter_by(sensor='ECG').limit(50).all()
        logs_bvp = StreamLog.query.filter_by(sensor='BVP').limit(50).all()
        logs_eda = StreamLog.query.filter_by(sensor='EDA').limit(50).all()

        latency_ecg = [log.latency_ms for log in logs_etc]
        latency_bvp = [log.latency_ms for log in logs_bvp]
        latency_eda = [log.latency_ms for log in logs_eda]

    plt.figure(figsize=(10, 4))
    plt.plot(latency_ecg, label='ECG', color='blue')
    plt.plot(latency_bvp, label='BVP', color='green')
    plt.plot(latency_eda, label='EDA', color='red')
    
    plt.xlabel('Iteracja')
    plt.ylabel('Latencja [s]')
    plt.title('Latencja sensorów w czasie')
    plt.legend()
    plt.savefig('latency_chart.png')
    plt.close()
    

    c = canvas.Canvas("report.pdf")
    c.drawString(250,800, "Raport")
    c.drawString(400,800, "Lukasz Zych")
    c.drawString(400,780, "Rafal Kruszewski")
    c.drawString(100,700, "Pomiary latencji")
    c.drawImage('latency_chart.png', 50, 350, width=500, height=300)
    c.drawString(50, 330, "Latencja w systemie agregacji danych z wielu sensorów " \
    "to czas miedzy momentem gdy sensor ")
    c.drawString(50, 315,"wygenerowal probke a momentem gdy dane zostaly wyslane " \
    "do odbiorcy")

    c.drawString(50,300, "W tym projekcie latencja jest symulowana przez losowe " \
    "opoznienie random_delay dodawane do ")
    c.drawString(50,285, "bazowego interwalu 100ms kazdego watku, reprezentuje niestabilnosc " \
    "lacza miedzy")
    c.drawString(50,270, "sensorem a serwerem, w rzeczywistych systemach " \
    "latencja zalezy od np. jakosci polaczenia")
    c.drawString(50, 225, "Packet loss - utrata pakietow, wystepuje gdy dane nie zostaly " \
    "wyslane do odbiorcy")
    c.drawString(50,210, "W systemach czasu rzeczywistego utrata pakietow powoduje przerwy" \
    " w sygnale ")
    c.drawString(50,195, "Offset przesuwa sie dalej wiec po kilku iteracjach znowu pokaze" \
    " dane z")
    c.drawString(50,180,"podobnego momentu czasowego")
    c.save()
    


ecg_thread = threading.Thread(target=pass_ecg_data).start()
bvp_thread = threading.Thread(target=pass_bvp_data).start()
eda_thread = threading.Thread(target=pass_eda_data).start()

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