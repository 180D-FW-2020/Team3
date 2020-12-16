<<<<<<< HEAD
import numpy as np
import cv2
=======
>>>>>>> 4fa30ab0b193b9bb7281683acd4e116a34ec0e33
def unlock_pose(image):
    # Define range of green color in HSV
    lower_green = np.array([50, 100, 100])
    upper_green = np.array([70, 255, 255])
    # Define range of blue color in HSV
    lower_blue = np.array([110, 100, 100])
    upper_blue = np.array([130, 255, 255])
    # variables to keep track of states
    object_detected=0
    green_detected=0
    blue_detected=0

    upper_half_image=image[0:180][:]
    lower_half_image=image[180:360][:]            
    #convert BGR to HSV
    hsv = cv2.cvtColor(upper_half_image, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower_green,  upper_green)
    res = cv2.bitwise_and(upper_half_image, upper_half_image, mask=mask)
    # convert the image to grayscale, blur it slightly,
    # and threshold
    gray = cv2.cvtColor(res.astype('float32'), cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    ret, thresh = cv2.threshold(blurred.astype('uint8'), 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    cv2.imshow("thresh_green", thresh)
    # find contours in the thresholded image and initialize the max color area
    contours, hierarchy = cv2.findContours(thresh, 1, 2)
    max_contour_area = 0
    if (len(contours) > 0):
        cnt = contours[0]
        object_detected=1
        for contour_i in contours:
            if cv2.contourArea(contour_i) > max_contour_area:
                cnt = contour_i
                max_contour_area=cv2.contourArea(contour_i)
    if (object_detected and (max_contour_area>6000)):
        green_detected = 1
    object_detected = 0
    
    lower_blue = np.array([110, 100, 100])
    upper_blue = np.array([130, 255, 255])
    #convert BGR to HSV
    hsv = cv2.cvtColor(lower_half_image, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower_blue,  upper_blue)
    res = cv2.bitwise_and(lower_half_image, lower_half_image, mask=mask)
    # convert the image to grayscale, blur it slightly,
    # and threshold
    gray = cv2.cvtColor(res.astype('float32'), cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    ret, thresh = cv2.threshold(blurred.astype('uint8'), 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    cv2.imshow("thresh_blue", thresh)
    # find contours in the thresholded image and initialize the max color area
    contours, hierarchy = cv2.findContours(thresh, 1, 2)
    max_contour_area = 0
    if (len(contours) > 0):
        cnt = contours[0]
        object_detected=1
        for contour_i in contours:
            if cv2.contourArea(contour_i) > max_contour_area:
                cnt = contour_i
                max_contour_area=cv2.contourArea(contour_i)
    if (object_detected and (max_contour_area>6000)):
        blue_detected = 1
    if (blue_detected and green_detected):
        print("It works")
        return True
    else:
        return False