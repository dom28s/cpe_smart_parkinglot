import cv2 as cv
import numpy as np
import json
import os
from shapely.geometry import Polygon
from ultralytics import YOLO

# Load YOLO model
model = YOLO('model/yolov8s.pt')

# Open camera stream
vdo = cv.VideoCapture('rtsp://admin:Admin123456@192.168.1.107:554/cam/realmonitor?channel=1&subtype=0&unicast=true&proto=Onvif')

frame_counter = 0
skip_frames = 7
check = True

# Set up window for display
cv.namedWindow('Full Scene', cv.WND_PROP_FULLSCREEN)
cv.setWindowProperty('Full Scene', cv.WND_PROP_FULLSCREEN, cv.WINDOW_FULLSCREEN)

# Define colors for display
green = (0, 255, 0)  # vacant
red = (0, 0, 255)    # occupied
yellow = (0, 255, 255)  # uncertain occupancy

points = []  # Store points for drawing polygons
park_poly_pos = []  # Store polygons for parking spaces
park_data = []
park_id = 0  # ID for new polygons

def load_park_from_json(filename):
    global park_poly_pos, park_data, park_id
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            park_data = json.load(f)
            park_poly_pos = [np.array(shape['polygon'], np.int32) for shape in park_data]
            if park_data:
                park_id = max([shape['id'] for shape in park_data]) + 1  # Set next park_id


def save_park_to_json(filename):
    global park_data 
    with open(filename, 'w') as f:
        json.dump(park_data, f)


def draw_shape(event, x, y, flags, param):
    global points, park_poly_pos, park_id, park_data
    if event == cv.EVENT_LBUTTONDOWN:
        points.append((x, y))
        if len(points) == 4:
            points.append(points[0])  # Close the polygon
            park_poly_pos.append(np.array(points, np.int32))  # Convert to NumPy array
            # Add polygon data with ID
            park_data.append({
                'id': park_id,
                'polygon': [list(p) for p in points]
            })
            park_id += 1  # Increment park_id for the next polygon
            points.clear()
            save_park_to_json('park.json')  # Save polygons after adding a new one


def polygon_area(polygon):
    """ Calculate the area of a polygon """
    return Polygon(polygon).area

def polygon_intersection_area(polygon1, polygon2):
    """ Calculate the intersection area of two polygons """
    poly1 = Polygon(polygon1)
    poly2 = Polygon(polygon2)
    intersection = poly1.intersection(poly2)
    return intersection.area


load_park_from_json('park.json')


ret, pic = vdo.read()

while check:
    cv.imshow("Full Scene", pic)
    cv.setMouseCallback('Full Scene', draw_shape)
    if len(park_poly_pos) > 0:  # Draw polygons on the image
        overlay = pic.copy()
        for shape in park_poly_pos:
            points_array = shape.reshape((-1, 1, 2))  # Ensure correct shape for fillPoly
            cv.fillPoly(overlay, [points_array], yellow)
        alpha = 0.5  # Transparency level
        pic2 = cv.addWeighted(pic, 1 - alpha, overlay, alpha, 0)
        cv.imshow("Full Scene", pic2)

    if cv.waitKey(1) & 0xFF == ord('p'):
        break

while True:
    try:
        ret, pic = vdo.read()
        if not ret:
            break

        pic_de = pic.copy()
        
        frame_counter += 1
        if frame_counter % (skip_frames + 1) != 0:
            continue

        result = model.track(pic_de, conf=0.5, persist=1, classes=2)
        overlay = pic.copy()
        copy_park_data = park_data.copy()
        id_inPark = []  # To track which objects are processed in parking spaces

        for x in result[0].boxes:
            name = result[0].names[int(x.cls)]
            pix = x.xyxy.tolist()[0]
            id = int(x.id)

            # Display detected object name and ID
            cv.putText(pic, "%s  %.0f" % (str(name), float(x.id)), (int(pix[0]), int(pix[1])), cv.FONT_HERSHEY_SIMPLEX, 1, red, 2)
            cv.rectangle(pic, (int(pix[0]), int(pix[1])), (int(pix[2]), int(pix[3])), green, 2)

            # Convert the bounding box to a polygon for overlap calculation
            pix_polygon = [[pix[0], pix[1]], [pix[2], pix[1]], [pix[2], pix[3]], [pix[0], pix[3]]]

            highest_overlap = 0
            highest_overlap_polygon = None

            for shape_data in park_data:
                park_polygon = shape_data['polygon']
                park_id = shape_data['id']

                inter_area = polygon_intersection_area(park_polygon, pix_polygon)
                pix_area = polygon_area(park_polygon)
                if pix_area > 0:
                    overlap_percentage = (inter_area / pix_area) * 100

                    # Check if this is the highest overlap for this object
                    if overlap_percentage >= 30 and overlap_percentage > highest_overlap:
                        highest_overlap = overlap_percentage
                        highest_overlap_polygon = shape_data

            # If highest overlap found, mark the parking space as occupied
            if highest_overlap_polygon is not None:
                cv.fillPoly(overlay, [np.array(highest_overlap_polygon['polygon'], np.int32).reshape((-1, 1, 2))], red)
                copy_park_data = [p for p in copy_park_data if p['id'] != highest_overlap_polygon['id']]  # Remove reserved

        # Fill remaining unoccupied polygons in green
        for shape_data in copy_park_data:
            park_polygon = shape_data['polygon']
            cv.fillPoly(overlay, [np.array(park_polygon, np.int32).reshape((-1, 1, 2))], green)

        # Draw polygon IDs and percentages
        for shape_data in park_data:
            park_polygon = shape_data['polygon']
            park_id = shape_data['id']
            poly = Polygon(park_polygon)
            centroid = poly.centroid.coords[0]
            cv.putText(pic, f"ID {park_id}", (int(centroid[0]), int(centroid[1])), cv.FONT_HERSHEY_SIMPLEX, 1, green, 2)

        alpha = 0.5
        cv.addWeighted(overlay, alpha, pic, 1 - alpha, 0, pic)
        cv.imshow('Full Scene', pic)
        if cv.waitKey(1) & 0xFF == ord('p'):
            break
    except Exception as e:
        print(f'Error: {e}')
        
vdo.release()
cv.destroyAllWindows()
