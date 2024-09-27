from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import mysql.connector

app = Flask(__name__)

# Channel Access Token และ Channel Secret จาก LINE Developers Console
LINE_CHANNEL_ACCESS_TOKEN = 'LrNhBjORvm+h1SsEOcwznThZrIpm0y6ZRe/bogFD+ay2c+EbeVf0qLr1P53sCs+APukq/bdIH04ay/QQTSoO23IS4NM0ubq65sFozCePKGhGiawW9cQ0EoULNXvpflgh0hJphhE1+QK3KowHBONOEgdB04t89/1O/w1cDnyilFU='
LINE_CHANNEL_SECRET = '3e756664e46445ccd4dc313e2b37237f'

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

conn = mysql.connector.connect(
    host="100.124.147.43",
    user="admin",
    password="admin",
    database="projects"
)

cursor = conn.cursor()
cursor.execute("SELECT * FROM `parkingspace`")
cam2 = cursor.fetchall()

cursor = conn.cursor()
cursor.execute("SELECT * FROM car")
car_row = cursor.fetchall()

cursor.execute("SELECT * FROM `camera`")
cam = cursor.fetchall()

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

# ฟังก์ชันตอบกลับข้อความเมื่อผู้ใช้ส่งข้อความมา
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    # สร้างข้อความจากข้อมูลใน cam2
    cam2_text = "\n".join([f"ID: {space[0]}, ข้อมูล: {space[1]}" for space in cam2])  # เปลี่ยนให้เข้ากับข้อมูลที่คุณต้องการ
    reply_text = f"ข้อมูลที่ดึงจากฐานข้อมูล:\n{cam2_text}"
    
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_text)
    )

if __name__ == "__main__":
    app.run(port=5000)
