import mysql.connector
import numpy as np
import json

conn = mysql.connector.connect(
    host="100.124.147.43",
    user="admin",
    password = "admin",
    database="projects"
)

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    database="projects2"
)

cursor = conn.cursor()

cursor.execute("SELECT * FROM `parkingspace`")
cam2 = cursor.fetchall()

cursor.execute("SELECT * FROM `camera`")
cam = cursor.fetchall()

cursor.execute("SELECT * FROM `parkinglot`")
parkinglot_status = cursor.fetchall()
all_space = parkinglot_status[0][1] 
green_sql = parkinglot_status[0][2] 
red_sql = parkinglot_status[0][3] 
blue_sql = parkinglot_status[0][4] 
yellow_sql = parkinglot_status[0][5] 
ี
cursor.execute(blue_sql,3)

# บันทึกการเปลี่ยนแปลงในฐานข้อมูล
conn.commit()