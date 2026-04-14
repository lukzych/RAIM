from flask import Flask, render_template, jsonify
import csv

from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sensors.db'


db = SQLAlchemy(app)

class SensorData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sensor = db.Column(db.String(10), nullable=False)
    value = db.Column(db.Float, nullable=False)

with app.app_context():
    db.create_all()



@app.route("/")
def index():
    return render_template("index.html")



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


if __name__ == "__main__":
    app.run(debug=True)