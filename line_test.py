from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, TemplateSendMessage, ButtonsTemplate, MessageAction
import mysql.connector

app = Flask(__name__)

# Channel Access Token และ Channel Secret จาก LINE Developers Console
LINE_CHANNEL_ACCESS_TOKEN = 'YOUR_ACCESS_TOKEN'
LINE_CHANNEL_SECRET = 'YOUR_CHANNEL_SECRET'

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# เชื่อมต่อกับฐานข้อมูล
conn = mysql.connector.connect(
    host="100.124.147.43",
    user="admin",
    password="admin",
    database="projects"
)

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    print(body)  # เพิ่มบรรทัดนี้เพื่อตรวจสอบข้อมูลที่รับ
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_message = event.message.text.strip()

    if user_message == "ลานจอดรถทั้งหมด":
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM `parkingspace`")
        park = cursor.fetchall()

        # สร้างข้อความตอบกลับจากข้อมูลในฐานข้อมูล
        reply = "\n".join([f"ลานจอดรถ : {space[7]}" for space in park])

        # สร้างปุ่ม template สำหรับแต่ละลานจอดรถ
        actions = [
            MessageAction(label=f'ดูข้อมูล {space[7]}', text=f'ข้อมูลเพิ่มเติมสำหรับ {space[7]}')
            for space in park
        ]

        # สร้างปุ่มเพิ่มเติม
        actions.append(MessageAction(label='กลับไปที่เมนูหลัก', text='เมนูหลัก'))
        actions.append(MessageAction(label='ขอบคุณ', text='ขอบคุณ'))

        # สร้าง template สำหรับปุ่ม
        buttons_template = TemplateSendMessage(
            alt_text='ตัวเลือก',
            template=ButtonsTemplate(
                title='ข้อมูลลานจอดรถ',
                text='กรุณาเลือกตัวเลือกด้านล่าง',
                actions=actions
            )
        )

        # ส่งข้อความที่มีข้อมูลและปุ่มไปยังผู้ใช้
        line_bot_api.reply_message(
            event.reply_token,
            [TextSendMessage(text=reply), buttons_template]  # ส่งข้อความและปุ่มพร้อมกัน
        )
    else:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=f"คุณพิมพ์: {user_message}")
        )

if __name__ == "__main__":
    app.run(port=5001)
