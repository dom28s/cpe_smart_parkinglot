from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage, TemplateSendMessage, ButtonsTemplate, MessageAction,ConfirmTemplate,CarouselTemplate, CarouselColumn,FlexSendMessage
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

save = None

# ฟังก์ชันสำหรับจัดการข้อความที่ได้รับ
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    global save  # ประกาศตัวแปร save ให้เป็น global
    user_message = event.message.text.strip()
    # if event.source.type == 'user':  # ถ้าเป็น user
    #     line_bot_api.push_message(
    #         '@335kkxwf',  # เปลี่ยนเป็น LINE ID ของ user
    #         TextSendMessage(text=f'User says: {user_message}')
    #     )
    # elif event.source.type == 'group' or event.source.type == 'room':  # ถ้าเป็น admin
    #     line_bot_api.push_message(
    #         '@873ppksc',  # เปลี่ยนเป็น LINE ID ของ admin
    #         TextSendMessage(text=f'Admin says: {user_message}')
    #     )

    if user_message == "ลานจอดรถทั้งหมด":
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM `parkinglot`")
        park = cursor.fetchall()
        # cursor.close()  # ปิด cursor เก่า
        print(park)
        carousel_columns = []
        
        for space in park:
            # สร้าง action สำหรับดูข้อมูลที่ผู้ใช้จะกด
            action = MessageAction(label='ดูข้อมูล', text=f'ลานจอดรถ {space[7]}')  # เมื่อผู้ใช้กดปุ่ม จะส่งข้อความนี้กลับมา
            save = space[7]
            carousel_column = CarouselColumn(
                thumbnail_image_url='https://i.ytimg.com/vi/mdw6UNfz9Og/maxresdefault.jpg',  # URL ของรูปภาพ
                title=f'ลานจอดรถ: {space[7]}',
                text='📍 คลิกปุ่มด้านล่างเพื่อดูข้อมูลช่องว่างลานจอดรถ',
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
        cursor.close()  # ปิด cursor เก่า

    else:
        if "ลานจอดรถ" in user_message:
            print(save)
            save = user_message.replace("ลานจอดรถ ", "")
            cursor = conn.cursor()
            query = "SELECT * FROM `parkinglot` WHERE `ParkingLot_Name` = %s;"
            cursor.execute(query, (save,))
            park_status = cursor.fetchall()
            flex_message = FlexSendMessage(
                alt_text=f'🚗 ลานจอดรถ: {save}\n📊 ว่าง: {park_status[0][2]} ช่องจอด',
                contents={
                    "type": "bubble",
                    "body": {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "text",
                                "text": f"🚗 ลานจอดรถ: {save}",
                                "weight": "bold",
                                "size": "xxl",
                                "align": "center",
                                "color": "#FF0000",  # สีแดงเข้มเพื่อความชัดเจน
                                "margin": "md"
                            },
                            {
                                "type": "separator",
                                "margin": "lg",
                                "color": "#CCCCCC"
                            },
                            {
                                "type": "box",
                                "layout": "horizontal",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": "🔓 ว่าง: ",
                                        "size": "lg",
                                        "align": "center",
                                        "color": "#000000",
                                        "flex": 1
                                    },
                                    {
                                        "type": "text",
                                        "text": f"{park_status[0][2]} ช่องจอด",
                                        "size": "lg",
                                        "align": "center",
                                        "weight": "bold",
                                        "color": "#32CD32",  # สีเขียวสดใสแสดงจำนวนที่ว่าง
                                        "flex": 1
                                    }
                                ],
                                "margin": "lg"
                            }
                        ]
                    },
                }
            )

            line_bot_api.reply_message(
                event.reply_token,
                flex_message
            )
        if user_message == 'ว่าง':
            print(f'in elif {save}')
            if save == None:
                flex_message = FlexSendMessage(
                    alt_text=f'กรุณาเลือกลานจอดรถก่อน',
                    contents={
                        "type": "bubble",
                        "body": {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": f"กรุณาเลือกลานจอดรถก่อน",
                                    "weight": "bold",
                                    "size": "xl",
                                    "align": "center",
                                    "color": "#FF0000"
                                }
                            ]
                        }
                    }
                )
            else:
                print(f'in esle {save}')
                cursor = conn.cursor()
                query = "SELECT * FROM `parkinglot` WHERE `ParkingLot_Name` = %s;"
                cursor.execute(query, (save,))
                park_status = cursor.fetchall()
                print(park_status)
                flex_message = FlexSendMessage(
                alt_text=f'🚗 ลานจอดรถ: {save}\n📊 ว่าง: {park_status[0][2]} ช่องจอด',
                contents={
                    "type": "bubble",
                    "body": {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "text",
                                "text": f"🚗 ลานจอดรถ: {save}",
                                "weight": "bold",
                                "size": "xxl",
                                "align": "center",
                                "color": "#FF0000",  # สีแดงเข้มเพื่อความชัดเจน
                                "margin": "md"
                            },
                            {
                                "type": "separator",
                                "margin": "lg",
                                "color": "#CCCCCC"
                            },
                            {
                                "type": "box",
                                "layout": "horizontal",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": "🔓 ว่าง: ",
                                        "size": "lg",
                                        "align": "center",
                                        "color": "#000000",
                                        "flex": 1
                                    },
                                    {
                                        "type": "text",
                                        "text": f"{park_status[0][2]} ช่องจอด",
                                        "size": "lg",
                                        "align": "center",
                                        "weight": "bold",
                                        "color": "#32CD32",  # สีเขียวสดใสแสดงจำนวนที่ว่าง
                                        "flex": 1
                                    }
                                ],
                                "margin": "lg"
                            }
                        ]
                    },
                }
            )
            
            line_bot_api.reply_message(
                event.reply_token,
                flex_message
            )
        else:
            print(save)
            flex_message = FlexSendMessage(
                    alt_text=f'กรุณาเลือกลานจอดรถก่อน',
                    contents={
                        "type": "bubble",
                        "body": {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": 'กรุณาเลือกลานจอดรถก่อน',
                                    "weight": "bold",
                                    "size": "xl",
                                    "align": "center",
                                    "color": "#FF0000"
                                }
                            ]
                        }
                    }
                )
            line_bot_api.reply_message(
                event.reply_token,
                flex_message
            )
    cursor.close()  # ปิด cursor เก่า
        


# สำหรับการรัน Flask
if __name__ == "__main__":
    app.run(port=5000)




