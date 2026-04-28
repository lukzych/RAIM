
import csv
import random
from datetime import datetime
import time
import json

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
EDA 0.5 Hz

do bazy leci np. 5 batchy 
700 * 5
60 * 5
1 * 5

'''
with app.app_context():
    db.create_all()
    SensorData.query.delete()
    db.session.commit()

    with open('data/ECG.csv') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            if i >= 20000:
                break
            db.session.add(SensorData(
                sensor='ECG',
                value=float(row['ECG']),
                timestamp=datetime.now(),
                latency_ms=random.randint(2, 10)
            ))
    db.session.commit()

    with open('data/BVP.csv') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            if i>= 20000:
                break
            db.session.add(SensorData(
                sensor='BVP',
                value=float(row['BVP']),
                timestamp=datetime.now(),
                latency_ms=random.randint(2, 10)
            ))
    db.session.commit()

    with open('data/EDA.csv') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            if i>= 20000:
                break
            db.session.add(SensorData(
                sensor='EDA',
                value=float(row['EDA']),
                timestamp=datetime.now(),
                latency_ms=random.randint(2, 10)
            ))
    db.session.commit()





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