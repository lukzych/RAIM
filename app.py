from flask import Flask, render_template, jsonify
import csv


app = Flask(__name__)

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