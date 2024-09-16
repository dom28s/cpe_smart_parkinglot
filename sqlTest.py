import mysql.connector

# เชื่อมต่อกับฐานข้อมูล MySQL
conn = mysql.connector.connect(
    host="100.124.147.43",
    user="root",
    password="",
    database="projects"
)

cursor = conn.cursor()

# Query เพื่อดึงข้อมูลจากฐานข้อมูล
cursor.execute("SELECT * FROM car")

# ดึงข้อมูลทั้งหมด
rows = cursor.fetchall()

# แสดงข้อมูล
for row in rows:
    print(row)

# ปิดการเชื่อมต่อ
conn.close()
