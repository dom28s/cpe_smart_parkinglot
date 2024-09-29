# from flask import Flask, request, abort
# from linebot import LineBotApi, WebhookHandler
# from linebot.models import MessageEvent, TextMessage, TextSendMessage, TemplateSendMessage, ButtonsTemplate, MessageAction,ConfirmTemplate,CarouselTemplate, CarouselColumn
# import mysql.connector

# app = Flask(__name__)

# # ข้อมูลการเชื่อมต่อ Line Bot
# channel_access_token = 'LrNhBjORvm+h1SsEOcwznThZrIpm0y6ZRe/bogFD+ay2c+EbeVf0qLr1P53sCs+APukq/bdIH04ay/QQTSoO23IS4NM0ubq65sFozCePKGhGiawW9cQ0EoULNXvpflgh0hJphhE1+QK3KowHBONOEgdB04t89/1O/w1cDnyilFU='
# channel_secret = '3e756664e46445ccd4dc313e2b37237f'

# # สร้าง LineBotApi และ WebhookHandler
# line_bot_api = LineBotApi(channel_access_token)
# handler = WebhookHandler(channel_secret)

# # เชื่อมต่อ MySQL Database
# conn = mysql.connector.connect(
#     host="100.124.147.43",
#     user="admin",
#     password="admin",
#     database="projects"
# )

# @app.route("/callback", methods=['POST'])
# def callback():
#     # รับข้อมูลจาก Webhook
#     signature = request.headers['X-Line-Signature']
#     body = request.get_data(as_text=True)
    
#     try:
#         handler.handle(body, signature)
#     except Exception as e:
#         print(f"Error: {e}")
#         abort(400)

#     return 'OK'

# save = ' k'

# # ฟังก์ชันสำหรับจัดการข้อความที่ได้รับ
# @handler.add(MessageEvent, message=TextMessage)
# def handle_message(event):
#     user_message = event.message.text.strip()

#     if user_message == "ลานจอดรถทั้งหมด":
#         cursor = conn.cursor()
#         cursor.execute("SELECT * FROM `parkinglot`")
#         park = cursor.fetchall()
#         print(park)
#         # park =[1,23,4,5,5,3,2,3,4,35,35,23,4,234,234,]
#         carousel_columns = []
#         for space in park:
#             action = MessageAction(label='ดูข้อมูล', text=f'ลานจอดรถ {space[7]} ว่าง : {space[2]} ช่อง')
            
#             carousel_column = CarouselColumn(
#                 thumbnail_image_url='https://i.ytimg.com/vi/mdw6UNfz9Og/maxresdefault.jpg',  # URL ของรูปภาพ
#                 title=f'ลานจอดรถ: {space[7]}',
#                 text='คลิกปุ่มด้านล่างเพื่อดูช่องว่างลานจอดรถ',
#                 actions=[action]  # เพิ่ม action ที่สร้างขึ้น
#             )
            
#             carousel_columns.append(carousel_column)

#         # สร้าง Carousel Template
#         carousel_template = CarouselTemplate(columns=carousel_columns)

#         # ส่งข้อความตอบกลับพร้อม Carousel Template
#         line_bot_api.reply_message(
#             event.reply_token,
#             TemplateSendMessage(
#                 alt_text='ลานจอดรถทั้งหมด',
#                 template=carousel_template
#             )
#     )     
#     else:
#         # กรณีอื่นๆ ส่งข้อความที่ผู้ใช้พิมพ์กลับไป
#         line_bot_api.reply_message(
#             event.reply_token,
#             TextSendMessage(text=f"คุณพิมพ์: **{user_message}**")
#         )


# # สำหรับการรัน Flask
# if __name__ == "__main__":
#     app.run(port=5001)






from flask import Flask, request, abort
from linebot.v3.messaging import MessagingApi
from linebot.v3.webhook import WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage,MessageEvent, TextMessage, TextSendMessage, TemplateSendMessage, ButtonsTemplate, MessageAction,ConfirmTemplate,CarouselTemplate, CarouselColumn

app = Flask(__name__)

# ข้อมูลการเชื่อมต่อ LINE Bot
channel_access_token = 'LrNhBjORvm+h1SsEOcwznThZrIpm0y6ZRe/bogFD+ay2c+EbeVf0qLr1P53sCs+APukq/bdIH04ay/QQTSoO23IS4NM0ubq65sFozCePKGhGiawW9cQ0EoULNXvpflgh0hJphhE1+QK3KowHBONOEgdB04t89/1O/w1cDnyilFU='
channel_secret = '3e756664e46445ccd4dc313e2b37237f'

# สร้าง MessagingApi และ WebhookHandler
line_bot_api = MessagingApi(channel_access_token)  # ใช้ v3
handler = WebhookHandler(channel_secret)  # ใช้ v3

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except Exception as e:
        print(f"Error: {e}")
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_message = event.message.text.strip()
    
    if event.source.type == 'user':  # ถ้าเป็น user
        line_bot_api.push_message(
            'ADMIN_LINE_ID',  # เปลี่ยนเป็น LINE ID ของ admin
            TextSendMessage(text=f'User says: {user_message}')
        )
    elif event.source.type == 'group' or event.source.type == 'room':  # ถ้าเป็น admin
        line_bot_api.push_message(
            'USER_LINE_ID',  # เปลี่ยนเป็น LINE ID ของ user
            TextSendMessage(text=f'Admin says: {user_message}')
        )

# สำหรับการรัน Flask
if __name__ == "__main__":
    app.run(port=5001)
