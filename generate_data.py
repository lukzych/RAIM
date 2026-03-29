import csv
import math
import random


RADIUS = 50
NUM_POINTS = 300
OUTPUT_FILE = "sensor_data.csv"


def generate_sphere_points():
    points = []

    for _ in range(NUM_POINTS):
        theta = random.uniform(0, math.pi)
        phi = random.uniform(0, 2 * math.pi)

        x = RADIUS * math.sin(theta) * math.cos(phi)
        y = RADIUS * math.sin(theta) * math.sin(phi)
        z = RADIUS * math.cos(theta)

        sensor_id = 1 if x < 0 else 2

        points.append({
            "sensor_id": sensor_id,
            "x" : round(x,3),
            "y" : round(y,3),
            "z" : round(z,3)
        })

    return points


#TODO Dodać punkty dla sześcianu i prostopadłościanu 

def save_csv(points, filename):
    with open(filename, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["sensor_id", "x", "y", "z"])
        writer.writeheader()
        writer.writerows(points)
 
if __name__ == "__main__":
    points = generate_sphere_points()
    save_csv(points, OUTPUT_FILE)
