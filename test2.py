import cv2 as cv
from ultralytics import YOLO
from PIL import ImageFont, ImageDraw, Image
import numpy as np
import json

# Load character mapping dictionary
with open('class_new.json', 'r', encoding='utf-8') as file:
    letter_dic = json.load(file)

# Load YOLO models
char_model = YOLO('model/char11x.pt')  # Character detection model
licen_model = YOLO('model/plate11m.pt')  # License plate detection model

# Read the input image
image_path = 'images/platetest2.png'
pic = cv.imread(image_path)

# Function to add Thai text to the image
def put_thai_text(image, text, position, font_path, font_size, color):
    image_pil = Image.fromarray(cv.cvtColor(image, cv.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(image_pil)
    font = ImageFont.truetype(font_path, font_size)
    draw.text(position, text, font=font, fill=color)
    image = cv.cvtColor(np.array(image_pil), cv.COLOR_RGB2BGR)
    return image

# Detect objects (characters) in the image
result_licen = licen_model(pic, conf=0.5)

for e in result_licen[0].boxes:
    name = result_licen[0].names[int(e.cls)]
    cls_id = int(e.cls)  # Get the class ID of the detected character
    pix = e.xyxy.tolist()[0]  # Get bounding box coordinates
    # Crop the image based on bounding box
    cropped_image = pic[int(pix[1]):int(pix[3]), int(pix[0]):int(pix[2])]
    
    # Perform license plate detection within the cropped character area
    result_char = char_model(cropped_image, conf=0.5)
    
    for licen_box in result_char[0].boxes:
        licen_cls_id = int(licen_box.cls)  # Get class ID for license plate detec   tion
        licen_pix = licen_box.xyxy.tolist()[0]  # Get bounding box for license plate
        
        pic = put_thai_text(pic, letter_dic[str(name)], (int(pix[0]), int(pix[1])), 'THSarabunNew.ttf', 32, (0, 255, 0))
        cv.rectangle(pic, (int(licen_pix[0]), int(licen_pix[1])), (int(licen_pix[2]), int(licen_pix[3])), (0, 0, 255), 2)
        
        print(f'{letter_dic[str(licen_cls_id)]} {licen_box.conf}')

# Show the result
cv.imshow("Detected Objects", pic)
cv.waitKey(0)
cv.destroyAllWindows()
