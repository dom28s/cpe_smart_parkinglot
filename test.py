import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    database="projects2"
    )
cursor = conn.cursor()
cursor.execute("SELECT * FROM car")
car_row = cursor.fetchall()

print(car_row)