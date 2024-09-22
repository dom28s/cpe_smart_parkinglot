import mysql.connector
import numpy as np
import json
park_data =[]
enter_data =[]
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    database="projects"
)

cursor = conn.cursor()
cursor.execute("SELECT * FROM `parkingspace`")
cam2 = cursor.fetchall()



cursor.execute("SELECT * FROM `camera`")
cam = cursor.fetchall()

def load_park_from_sql():
    global park_poly_pos,park_data
    data = []       
    for row in cam2:
        if row[2] != '':
            data.append(row)
        else:
            enter_data.append(json.loads(row[4]))

    for row in data:
        id_value = row[0]
        point_value = eval(row[2]) if row[2] != '' else []
        park_data.append({"id": id_value, "polygon": point_value})

    park_poly_pos = [np.array(shape['polygon'], np.int32) for shape in park_data]
    return park_data,enter_data

w_web = (cam[1][7])
h_web = (cam[1][8])



7
8