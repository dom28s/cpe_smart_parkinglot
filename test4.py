import cv2
import numpy as np

# โหลดภาพระดับสีเทา
image = cv2.imread('images/licen_p1.png', cv2.IMREAD_GRAYSCALE)

# ใช้ Otsu's thresholding
_, binary_image = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

# แสดงผลลัพธ์
cv2.imshow('Original Image', image)
cv2.imshow('Otsu Thresholding', binary_image)
cv2.waitKey(0)
cv2.destroyAllWindows()
