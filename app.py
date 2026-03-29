from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
import csv


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sensor.db'
db = SQLAlchemy(app)


#TODO dodać kolumne shape i zapisywać to jako jedna tabela dla innych kształtów
class Measurement(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    shape = db.Column(db.String)
    sensor_id = db.Column(db.Integer)
    x = db.Column(db.Float)
    y = db.Column(db.Float)
    z = db.Column(db.Float)

def load_csv_to_db():
    db.session.query(Measurement).delete()
    db.session.commit()
    with open('sensor_data.csv', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            m = Measurement(
                shape=row['shape'],
                sensor_id=int(row['sensor_id']),
                x=float(row['x']),
                y=float(row['y']),
                z=float(row['z'])
            )
            db.session.add(m)
        db.session.commit()


@app.route("/")
def index():
    points = Measurement.query.all()
    return render_template("index.html", points = points)


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        load_csv_to_db()
    app.run(debug=True)