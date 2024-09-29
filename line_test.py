from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage, TemplateSendMessage, ButtonsTemplate, MessageAction,ConfirmTemplate,CarouselTemplate, CarouselColumn
import mysql.connector

app = Flask(__name__)

# ข้อมูลการเชื่อมต่อ Line Bot
channel_access_token = 'LrNhBjORvm+h1SsEOcwznThZrIpm0y6ZRe/bogFD+ay2c+EbeVf0qLr1P53sCs+APukq/bdIH04ay/QQTSoO23IS4NM0ubq65sFozCePKGhGiawW9cQ0EoULNXvpflgh0hJphhE1+QK3KowHBONOEgdB04t89/1O/w1cDnyilFU='
channel_secret = '3e756664e46445ccd4dc313e2b37237f'

# สร้าง LineBotApi และ WebhookHandler
line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)

# เชื่อมต่อ MySQL Database
conn = mysql.connector.connect(
    host="100.124.147.43",
    user="admin",
    password="admin",
    database="projects"
)

@app.route("/callback", methods=['POST'])
def callback():
    # รับข้อมูลจาก Webhook
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    
    try:
        handler.handle(body, signature)
    except Exception as e:
        print(f"Error: {e}")
        abort(400)

    return 'OK'

save = ' '

# ฟังก์ชันสำหรับจัดการข้อความที่ได้รับ
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    global save  # ประกาศตัวแปร save ให้เป็น global
    user_message = event.message.text.strip()

    if user_message == "ลานจอดรถทั้งหมด":
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM `parkinglot`")
        park = cursor.fetchall()
        print(park)
        carousel_columns = []
        
        for space in park:
            # สร้าง action สำหรับดูข้อมูลที่ผู้ใช้จะกด
            action = MessageAction(label='ดูข้อมูล', text=f'ลานจอดรถ {space[7]}')  # เมื่อผู้ใช้กดปุ่ม จะส่งข้อความนี้กลับมา
            save = space[7]
            print(f'{save} save in ')
            carousel_column = CarouselColumn(
                thumbnail_image_url='https://i.ytimg.com/vi/mdw6UNfz9Og/maxresdefault.jpg',  # URL ของรูปภาพ
                title=f'ลานจอดรถ: {space[7]}',
                text='คลิกปุ่มด้านล่างเพื่อดูช่องว่างลานจอดรถ',
                actions=[action]  
            )
            carousel_columns.append(carousel_column)

        carousel_template = CarouselTemplate(columns=carousel_columns)

        line_bot_api.reply_message(
            event.reply_token,
            TemplateSendMessage(
                alt_text='ลานจอดรถทั้งหมด',
                template=carousel_template
            )
        )
    else:
        if "ลานจอดรถ" in user_message:
            save = user_message.replace("ลานจอดรถ ", "")
            print(save)
            reply = f'คุณเลือก {save}'
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=reply)
            )
        elif user_message == 'ว่าง':
            print(save)
            reply = f'คุณเลือก {save}'
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=reply)
            )


# สำหรับการรัน Flask
if __name__ == "__main__":
    app.run(port=5000)





