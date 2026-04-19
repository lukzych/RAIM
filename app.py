
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

with app.app_context():
    db.create_all()

all_ecg = []
with open('data/ECG.csv') as f:
    reader = csv.DictReader(f)
    for row in reader:
        all_ecg.append(float(row['ECG']))

all_bvp = []
with open('data/BVP.csv') as f:
    reader = csv.DictReader(f)
    for row in reader:
        all_bvp.append(float(row['BVP']))

all_eda = []
with open('data/EDA.csv') as f:
    reader = csv.DictReader(f)
    for row in reader:
        all_eda.append(float(row['EDA']))
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/stream")
def stream():
    def generator():
        index_ecg = 0
        index_bvp = 0
        index_eda = 0
        counter = 0
        
        while True:
            data_ecg = all_ecg[index_ecg: index_ecg + 70]
            index_ecg += 70
            if index_ecg >= len(all_ecg):
                index_ecg = 0


            data_bvp = all_bvp[index_bvp: index_bvp + 6]
            index_bvp += 6
            if index_bvp >= len(all_bvp):
                index_bvp = 0


            data_eda = all_eda[index_eda: index_eda + 1]
            index_eda += 1
            if index_eda >= len(all_eda):
                index_eda = 0


            latency_ecg = random.randint(2, 10)
            latency_bvp = random.randint(2,10)
            latency_eda = random.randint(2, 10)

            with app.app_context():
                db.session.add(SensorData(
                    sensor="ECG",
                    value=data_ecg[0],
                    timestamp=datetime.now(),
                    latency_ms=latency_ecg
                ))
                db.session.add(SensorData(
                    sensor="BVP",
                    value=data_bvp[0],
                    timestamp=datetime.now(),
                    latency_ms=latency_bvp
                ))
                db.session.add(SensorData(
                    sensor="EDA",
                    value=data_eda[0],
                    timestamp=datetime.now(),
                    latency_ms=latency_eda
                ))
                counter += 1
                if counter % 50 == 0:
                    db.session.commit()

            yield f"data: {json.dumps({'sensor': 'ECG', 'values': data_ecg})}\n\n"
            yield f"data: {json.dumps({'sensor': 'BVP', 'values': data_bvp})}\n\n"
            yield f"data: {json.dumps({'sensor': 'EDA', 'values': data_eda})}\n\n"
            time.sleep(0.1)

    return Response(generator(), mimetype='text/event-stream')

if __name__ == "__main__":
    app.run(debug=True, port=5000)