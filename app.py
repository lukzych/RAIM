from flask import Flask, render_template, jsonify
import csv

from flask_sqlalchemy import SQLAlchemy

import threading

import random

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sensors.db'


db = SQLAlchemy(app)

class SensorData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sensor = db.Column(db.String(10), nullable=False)
    value = db.Column(db.Float, nullable=False)
    timespamp = db.Column(db.Float, nullable = False)
    latency_ms = db.Column(db.Float, nullable = False)

with app.app_context():
    db.create_all()



@app.route("/")
def index():
    return render_template("index.html")




@app.route("/api/stream")
def stream():

    
    def generator():
        index_ecg = 0
        index_bvp = 0

        all_ecg = []
        with open('data/ECG.csv') as f:
            reader = csv.DictReader(f)
            for row in reader:
                all_ecg.append(float(row['ECG']))


        data_ecg = []
        while True:
            data_ecg = all_ecg[index_ecg: index_ecg + 70]
            index_ecg += 70


            if index_ecg >= len(all_ecg):
                index_ecg = 0

        latency_ecg = random.randint(2,10)
        latency_bvp = random.randint(2,10)
        
        db.session.add(SensorData(sensor="ECG"), value = data_ecg[1])


'''
@app.route("/api/ecg")
def get_ecg():
    data = []
    with open('data/ECG.csv') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            if i >= 700: 
                break
            data.append(float(row['ECG']))

    return jsonify(data)

@app.route("/api/bvp")
def get_bvp():
    data = []
    with open('data/BVP.csv') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            if i >= 64: 
                break
            data.append(float(row['BVP']))

    return jsonify(data)
'''


if __name__ == "__main__":
    app.run(debug=True)