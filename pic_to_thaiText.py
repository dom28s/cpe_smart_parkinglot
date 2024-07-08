
import cv2
import pytesseract
import os

# ระบุตำแหน่งของ tesseract executable
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# ตรวจสอบและตั้งค่า TESSDATA_PREFIX
os.environ['TESSDATA_PREFIX'] = r'C:\Program Files\Tesseract-OCR\tessdata'

# อ่านภาพด้วย OpenCV
image_path = 'images/thai_text.png'
image = cv2.imread(image_path)

# แปลงภาพเป็นขาวดำเพื่อเพิ่มความแม่นยำในการตรวจจับ
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

# ใช้ Tesseract OCR เพื่อแปลงภาพเป็นข้อความภาษาไทย
text = pytesseract.image_to_string(gray, lang='tha')

# แสดงข้อความที่แปลงได้
print(text)
