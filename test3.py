# from ultralytics import YOLO
# import cv2 as cv
# import numpy as np
# import json

# model = YOLO('model/yolov8l.pt')

# # vdo = cv.VideoCapture('rtsp://admin:Admin123456@192.168.1.100:554/cam/realmonitor?channel=1&subtype=0&unicast=true&proto=Onvif')
# vdo = cv.VideoCapture('vdo_from_park/topCam.mp4') # Uncomment this line if using a video file

# frame_counter = 0
# skip_frames = 15

# cv.namedWindow('Full Scene', cv.WND_PROP_FULLSCREEN)
# cv.setWindowProperty('Full Scene', cv.WND_PROP_FULLSCREEN, cv.WINDOW_FULLSCREEN)

# # color definitions
# green = (0, 255, 0)  # empty
# red = (0, 0, 255)    # not empty
# blue = (255, 0, 0)   # unknown
# yellow = (0, 255, 255)  # undefined occupancy

# # Variables for drawing
# points = []
# park = []
# max_points = 4
# start_point = None
# check = True
# x_threshold =400



# def draw_shape(event, x, y, flags, param):
#     global points, park
#     if event == cv.EVENT_LBUTTONDOWN:
#         points.append((x, y))
#         print(points)
#         if len(points) == max_points:
#             points.append(points[0])  # Close the polygon
#             park.append(points.copy())
#             points.clear()

# # Function to save park data to JSON file
# def save_park_to_json(filename):
#     park_data = []
#     for shape in park:
#         park_data.append([[int(p[0]), int(p[1])] for p in shape])
#     with open(filename, 'w') as f:
#         json.dump(park_data, f)

# # Read the first frame to set up the drawing
# ret, pic = vdo.read()
# pic = cv.rotate(pic, cv.ROTATE_90_COUNTERCLOCKWISE)

# while check:
#     cv.imshow("Full Scene", pic)
#     cv.setMouseCallback('Full Scene', draw_shape)

#     if len(park) > 0:  # Draw polygons on the image
#         overlay = pic.copy()
#         for shape in park:
#             points_array = np.array(shape, np.int32)  # Convert list of points to NumPy array
#             points_array = points_array.reshape((-1, 1, 2))  # Reshape for fillPoly
#             cv.fillPoly(overlay, [points_array], yellow)
#         alpha = 0.5  # Transparency level
#         pic2 = cv.addWeighted(pic, 1 - alpha, overlay, alpha, 0)
#         cv.imshow("Full Scene", pic2)

#     if cv.waitKey(1) & 0xFF == ord('p'):
#         break

# save_park_to_json('park.json')  # Save the polygons to a JSON file

# while True:
#     ret, pic = vdo.read()
#     if not ret:
#         break

#     pic = cv.rotate(pic, cv.ROTATE_90_COUNTERCLOCKWISE)
#     pic_de = pic.copy()

#     cv.rectangle(pic_de, (0, 0), (x_threshold, pic.shape[0]), (0, 0, 0), thickness=cv.FILLED)

#     frame_counter += 1
#     if frame_counter % (skip_frames + 1) != 0:
#         continue

#     result = model.track(pic_de, conf=0.5, persist=1)

#     for x in result[0].boxes:
#         name = result[0].names[int(x.cls)]
#         pix = x.xyxy.tolist()[0]
#         id = int(x.id)

#         cv.putText(pic, "%s  %.0f" % (str(name), float(x.id)), (int(pix[0]), int(pix[1])), cv.FONT_HERSHEY_SIMPLEX, 1, red, 2)
#         cv.rectangle(pic, (int(pix[0]), int(pix[1])), (int(pix[2]), int(pix[3])), green, 2)


#     cv.imshow('Full Scene', pic)
#     if cv.waitKey(1) & 0xFF == ord('p'):
#         break

# vdo.release()
# cv.destroyAllWindows()
