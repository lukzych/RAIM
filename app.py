
import csv
import random
from datetime import datetime
import time
import json

from flask import Flask, render_template, Response
from flask_sqlalchemy import SQLAlchemy

from itertools import islice

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


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/stream")
def stream():

    def generator():
        
        counter = 0

        batch_ecg = batch_reader('data/ECG.csv','ECG',70)
        batch_bvp = batch_reader('data/BVP.csv', 'BVP', 6)
        batch_eda = batch_reader('data/EDA.csv','EDA', 1)
    
        while True:

            data_ecg = next(batch_ecg)
            data_bvp = next(batch_bvp)
            data_eda = next(batch_eda)

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


def batch_reader(filepath, column_name, n):
    while True:
        with open(filepath) as f:
            reader = csv.DictReader(f)
            while True:
                batch = list(islice(reader, n))
                if not batch:
                    break
                yield [float(row[column_name]) for row in batch]

if __name__ == "__main__":
    app.run(debug=True, port=5000)