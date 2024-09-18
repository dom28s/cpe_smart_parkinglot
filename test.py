import cv2
import numpy as np
from PIL import ImageFont, ImageDraw, Image

# สร้างภาพสีดำ
image = np.zeros((500, 500, 3), dtype=np.uint8)

# แปลงภาพจาก OpenCV เป็น PIL
pil_img = Image.fromarray(image)

# เลือกฟอนต์และขนาดฟอนต์ (คุณสามารถใช้ฟอนต์ที่รองรับ UTF-8)
font = ImageFont.truetype("THSarabunNew.ttf", 32)

# วาดข้อความ UTF-8 โดยใช้ Pillow
draw = ImageDraw.Draw(pil_img)
text = "สวัสดี, OpenCV กับ UTF-8"
draw.text((50, 100), text, font=font, fill=(255, 255, 255, 0))

# แปลงภาพกลับไปเป็น OpenCV format
image = np.array(pil_img)

# แสดงภาพที่มีข้อความ
cv2.imshow("Image", image)
cv2.waitKey(0)
cv2.destroyAllWindows()
