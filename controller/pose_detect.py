import cv2
import numpy as np

class DetectStatus:
    def __init__(self, keys):
        self.detected_colors = {kDictKeys[0]: 0, kDictKeys[1] : 0}

# Define constants
kDictKeys = ["left", "right"]
kAreaThreshold = 6000

color_ranges = {}
kLowerGreen = np.array([50, 100, 100])
kUpperGreen = np.array([70, 255, 255])
color_ranges[kDictKeys[0]] = [kLowerGreen, kUpperGreen]

kLowerBlue = np.array([110, 100, 100])
kUpperBlue = np.array([130, 255, 255])
color_ranges[kDictKeys[1]] = [kLowerBlue, kUpperBlue]

def unlock_pose(image):
    status_tracker = DetectStatus(kDictKeys)

    image_halves = {}
    kHalfImageWidth = image.shape[1]//2
    image_halves[kDictKeys[0]] = image[:, :kHalfImageWidth]
    image_halves[kDictKeys[1]] = image[:, kHalfImageWidth:]
    
    # Process each half separately
    x_offset = 0
    for side in kDictKeys:
        # Color thresholding
        hsv_img = cv2.cvtColor(image_halves[side], cv2.COLOR_BGR2HSV)
        color_mask = cv2.inRange(hsv_img, color_ranges[side][0],  color_ranges[side][1])
        post_mask = cv2.bitwise_and(image_halves[side], image_halves[side], mask=color_mask)

        # Convert image to grayscale, apply blur and thresholding
        grey_img = cv2.cvtColor(post_mask.astype('float32'), cv2.COLOR_BGR2GRAY)
        blurred_img = cv2.GaussianBlur(grey_img, (5, 5), 0)
        ret, thresh = cv2.threshold(blurred_img.astype('uint8'), 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # Contour detection
        contours, hierarchy = cv2.findContours(thresh, 1, 2)
        max_contour_area = 0
        if len(contours) > 0:
            biggest_contour = max(contours, key = cv2.contourArea)
            if cv2.contourArea(biggest_contour) > kAreaThreshold:
                status_tracker.detected_colors[side] = 1
                x, y, w, h = cv2.boundingRect(biggest_contour)
                image = cv2.rectangle(image, (x+x_offset, y), (x+x_offset+w, y+h), (0, 0, 255), 2)
                thresh = cv2.rectangle(thresh, (x, y), (x+w, y+h), (0, 0, 255), 2)
        x_offset += kHalfImageWidth

    # Check if both objects detected
    successful_unlock = True
    for side in kDictKeys:
        if status_tracker.detected_colors[side] == 0:
            successful_unlock = False

    return image, successful_unlock

    


