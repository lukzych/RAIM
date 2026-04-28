
import csv
import random
from datetime import datetime
import time
import json
import threading

from flask import Flask, render_template, Response
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sensors.db'
db = SQLAlchemy(app)

class SensorData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sensor = db.Column(db.String(10), nullable=False)
    value = db.Column(db.Float, nullable=False)
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
'''

with app.app_context():
    db.create_all()
    SensorData.query.delete()
    db.session.commit()

    with open('data/ECG.csv') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            if i >= 70000:
                break
            db.session.add(SensorData(
                sensor='ECG',
                value=float(row['ECG']),
                timestamp=datetime.now(),
                latency_ms=0
            ))
    db.session.commit()

    with open('data/BVP.csv') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            if i>= 6400:
                break
            db.session.add(SensorData(
                sensor='BVP',
                value=float(row['BVP']),
                timestamp=datetime.now(),
                latency_ms=0
            ))
    db.session.commit()

    with open('data/EDA.csv') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            if i>= 400:
                break
            db.session.add(SensorData(
                sensor='EDA',
                value=float(row['EDA']),
                timestamp=datetime.now(),
                latency_ms=0
            ))
        db.session.commit()

def pass_ecg_data():
    with app.app_context():
        rekordy = SensorData.query.filter_by(sensor='ECG').offset(0).limit(70).all()
    print(rekordy[0].value)
    print(rekordy[1].value)
    print(rekordy[2].value)


ecg_thread = threading.Thread(target=pass_ecg_data).start()



@app.route("/")
def index():
    return render_template("index.html")

@app.route("/stream")
def stream():
    def generator():
       pass

    return Response(generator(), mimetype='text/event-stream')

if __name__ == "__main__":
    app.run(debug=True, port=5002)