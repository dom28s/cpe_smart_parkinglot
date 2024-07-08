from ultralytics import YOLO
import cv2 as cv
import pytesseract
import os

# ระบุตำแหน่งของ tesseract executable
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# ตรวจสอบและตั้งค่า TESSDATA_PREFIX
os.environ['TESSDATA_PREFIX'] = r'C:\Program Files\Tesseract-OCR\tessdata'

# Load the YOLO model
# model = YOLO('model/yolov8l.pt')
model = YOLO('model/licenplate.pt')

# Read the image
pic = cv.imread('images/platetest2.png')

# Perform inference with the model
result = model(pic, conf=0.5)

# Process each detected box
for i, x in enumerate(result[0].boxes):
    name = result[0].names[int(x.cls)]
    pix = x.xyxy[0].tolist()
    print(pix)
    
    # Draw the bounding box and label on the original image
    cv.putText(pic, "%s %.2f" % (str(name), (float(x.conf))), (int(pix[0]), int(pix[1])), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    cv.rectangle(pic, (int(pix[0]), int(pix[1])), (int(pix[2]), int(pix[3])), (0, 255, 0), 2)
    
    # Crop the image at the bounding box position
    cropped_pic = pic[int(pix[1]):int(pix[3]), int(pix[0]):int(pix[2])]

    gray = cv.cvtColor(cropped_pic, cv.COLOR_BGR2GRAY)
    gray = cv.threshold(gray, 0, 255, cv.THRESH_BINARY | cv.THRESH_OTSU)[1]

    text = pytesseract.image_to_string(gray, lang='tha')
    
    # Display the cropped image
    window_name = f'Cropped Image {i + 1}'
    cv.imshow(window_name, cropped_pic)
    cv.imshow('gray',gray)

    # แสดงข้อความที่แปลงได้
    print(text)


# Display the annotated original image
cv.imshow('Annotated Image', pic)
cv.waitKey(0)
cv.destroyAllWindows()










