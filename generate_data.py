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
            "shape" : "sphere",
            "sensor_id": sensor_id,
            "x" : round(x,3),
            "y" : round(y,3),
            "z" : round(z,3)
        })

    return points


def generate_cube_points():

    points = []

    front = []
    back = []
    left = []
    right = []
    upper = []
    lower = []

    for _ in range(NUM_POINTS//6): # //6 na liczbę ścian inaczej byśmy mieli 1800 punktów

        #I tak moze być za mało zeby ładnie to wizualnie wyglądało
        
        
        #FRONT
        x = random.uniform(-RADIUS, RADIUS)
        y = random.uniform(-RADIUS, RADIUS)
        z = RADIUS

        sensor_id = 1 if x < 0 else 2

        front.append({
            "shape": "cube",
            "sensor_id": sensor_id,
            "x" : round(x,3),
            "y" : round(y,3),
            "z" : round(z,3)
        })

        #BACK
        x = random.uniform(-RADIUS,RADIUS)
        y = random.uniform(-RADIUS,RADIUS)
        z = - RADIUS

        sensor_id = 1 if x < 0 else 2

        back.append({ 
            "shape": "cube",
            "sensor_id": sensor_id,
            "x" : round(x,3),
            "y" : round(y,3),
            "z" : round(z,3)
        })

        #RIGHT
        x = random.uniform(-RADIUS,RADIUS)
        y = RADIUS
        z = random.uniform(-RADIUS,RADIUS)

        sensor_id = 1 if x < 0 else 2

        right.append({
            "shape": "cube",
            "sensor_id": sensor_id,
            "x" : round(x,3),
            "y" : round(y,3),
            "z" : round(z,3)
        })

        #LEFT
        x = random.uniform(-RADIUS,RADIUS)
        y = - RADIUS
        z = random.uniform(-RADIUS,RADIUS)

        sensor_id = 1 if x < 0 else 2

        left.append({
            "shape": "cube",
            "sensor_id": sensor_id,
            "x" : round(x,3),
            "y" : round(y,3),
            "z" : round(z,3)
        })

        #UPPER
        x = RADIUS
        y = random.uniform(-RADIUS,RADIUS)
        z = random.uniform(-RADIUS,RADIUS)

        sensor_id = 1 if x < 0 else 2

        upper.append({
            "shape": "cube",
            "sensor_id": sensor_id,
            "x" : round(x,3),
            "y" : round(y,3),
            "z" : round(z,3)
        })

        #DOWN
        x = - RADIUS
        y = random.uniform(-RADIUS,RADIUS)
        z = random.uniform(-RADIUS,RADIUS)

        sensor_id = 1 if x < 0 else 2

        lower.append({
            "shape": "cube",
            "sensor_id": sensor_id,
            "x" : round(x,3),
            "y" : round(y,3),
            "z" : round(z,3)
        })

        
    return front + back + right + left + upper + lower


#TODO Dodać punkty dla prostopadłościanu

def save_csv(points, filename):
    with open(filename, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["shape","sensor_id", "x", "y", "z"])
        writer.writeheader()
        writer.writerows(points)
 
if __name__ == "__main__":
    points = generate_sphere_points() + generate_cube_points()
    save_csv(points, OUTPUT_FILE)
