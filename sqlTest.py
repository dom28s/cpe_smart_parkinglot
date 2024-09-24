import mysql.connector
import numpy as np
import json
park_data =[]
enter_data =[]
conn = mysql.connector.connect(
    host="100.124.147.43",
    user="admin",
    password = "admin",
    database="projects"
)

cursor = conn.cursor()
cursor.execute("SELECT * FROM `parkingspace`")
cam2 = cursor.fetchall()



cursor.execute("SELECT * FROM `camera`")
cam = cursor.fetchall()

print(cam)

