import cv2
import numpy as np
from shape_recognition.shape_detector import ShapeDetector
from shape_recognition.color_labeler import ColorLabeler
import imutils


def target_recognition(image):
    targets = list()
    kernel = np.ones((5,5),np.uint8)

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    blurred = cv2.GaussianBlur(gray, (7, 7), 0)
    edges = cv2.Canny(blurred,50,200)
    dilated = cv2.dilate(edges, kernel, iterations = 1)

    ratio = image.shape[0] / float(edges.shape[0])
    cnts = cv2.findContours(dilated.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)

    shape_detector = ShapeDetector()
    color_labeler = ColorLabeler()
    if len(cnts) > 0:
        for c in cnts:
            M = cv2.moments(c)
            if M["m00"] != 0:
                cX = int((M["m10"] / M["m00"]) * ratio)
                cY = int((M["m01"] / M["m00"]) * ratio)
                c_target = shape_detector.detect(c)
                shape = c_target[0]
                coordinates = c_target[1]
                c = c.astype("float")
                c *= ratio
                c = c.astype("int")
                if shape == "triangle":
                    if cv2.contourArea(c) > 600:
                        color = color_labeler.label(lab, c)
                        c_target[0] = color
                        targets.append(c_target)
                        #text = "{} {}".format(color, shape)
                        coords = np.array([np.array(coordinates[0]), np.array(coordinates[1]), np.array(coordinates[2])])
                        #cv2.drawContours(image, [coords.astype(int)], -1, (0, 255, 0), 2)
                        #cv2.putText(image, text, (cX, cY), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
    return targets
