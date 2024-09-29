import mysql.connector
import numpy as np
import json

conn = mysql.connector.connect(
    host="100.124.147.43",
    user="admin",
    password = "admin",
    database="projects"
)

# conn = mysql.connector.connect(
#     host="localhost",
#     user="root",
#     database="projects2"
# )

cursor = conn.cursor()

cursor.execute("SELECT * FROM `parkingspace`")
cam2 = cursor.fetchall()

cursor.execute("SELECT * FROM `parkinglot` WHERE `ParkingLot_ID` = 1;")
cam = cursor.fetchall()
print(cam)
