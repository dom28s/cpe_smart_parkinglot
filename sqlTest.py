import mysql.connector
from PIL import ImageFont, ImageDraw, Image
import numpy as np
import json

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    database="projects"
)

cursor = conn.cursor()
cursor.execute("SELECT * FROM car")

car_row = cursor.fetchall()


cursor.execute("SELECT * FROM `camera`")
camara_row = cursor.fetchall()

print(camara_row[0][3][0])
print(camara_row[0][3][1])
print(camara_row[0][3][2])
print(camara_row[0][3][3])
print(type(camara_row[0][3]))
print(type(camara_row[0]))
print(camara_row[0][3])
print(type(camara_row[0][3]))
line1_load = json.loads(camara_row[0][3])
print(line1_load)
print(type(line1_load))
