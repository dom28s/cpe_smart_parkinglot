import mysql.connector
import difflib

def similarity_percentage(str1, str2):
    # สร้างออบเจกต์ SequenceMatcher เพื่อเปรียบเทียบ string สองตัว
    matcher = difflib.SequenceMatcher(None, str1, str2)
    
    # คำนวณอัตราความเหมือนเป็นเปอร์เซ็นต์
    similarity = matcher.ratio() * 100
    
    return similarity
# เชื่อมต่อกับฐานข้อมูล MySQL
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    database="projects"
)

cursor = conn.cursor()

# Query เพื่อดึงข้อมูลจากฐานข้อมูล
cursor.execute("SELECT * FROM car")

# ดึงข้อมูลทั้งหมด
rows = cursor.fetchall()




# ตัวอย่างการใช้งาน
while True:
    finalword = input()
    max_per =0
    word = None

    for db in rows:
        matcher = difflib.SequenceMatcher(None, db[3], finalword)
        per = matcher.ratio() * 100

        if per>max_per:
            max_per=per
            word = db[3]
    print(f'{word} {max_per} {finalword}')
    conn.close()
