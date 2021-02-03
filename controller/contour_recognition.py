import cv2
import numpy as np
from shaperecognition.shapedetector import ShapeDetector
from shaperecognition.colorlabeler import ColorLabeler
import imutils

vc = cv2.VideoCapture(0)

if vc.isOpened():
    rval, frame = vc.read()
else:
    rval = False

show_frame = 1

def target_recognition(image):
    targets = list()
    kernel = np.ones((5,5),np.uint8)

    #resized = imutils.resize(image, width=300)
    resized = image
    gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
    lab = cv2.cvtColor(resized, cv2.COLOR_BGR2LAB)
    blurred = cv2.GaussianBlur(gray, (7, 7), 0)
    #blurred = gray
    edges = cv2.Canny(blurred,50,200)
    dilated = cv2.dilate(edges, kernel, iterations = 1)
    cv2.imshow("edges", edges)
    cv2.imshow("dilated", dilated)
    # gray = resized

    ratio = image.shape[0] / float(edges.shape[0])
    cnts = cv2.findContours(dilated.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)

    sd = ShapeDetector()
    cl = ColorLabeler()
    if len(cnts) > 0:
        #print(str(cnts) + " circles/n")
        for c in cnts:
            M = cv2.moments(c)
            if M["m00"] != 0:
                cX = int((M["m10"] / M["m00"]) * ratio)
                cY = int((M["m01"] / M["m00"]) * ratio)
                c_target = sd.detect(c)
                shape = c_target[0]
                coordinates = c_target[1]
                c = c.astype("float")
                c *= ratio
                c = c.astype("int")
                if shape == "triangle":
                    if cv2.contourArea(c) > 600:
                        color = cl.label(lab, c)
                        targets.append(c_target)
                        text = "{} {}".format(color, shape)
                        coords = np.array([np.array(coordinates[0]), np.array(coordinates[1]), np.array(coordinates[2])])
                        cv2.drawContours(image, [coords.astype(int)], -1, (0, 255, 0), 2)
                        cv2.putText(image, text, (cX, cY), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
    
    cv2.imshow("labels", image)
    return targets

while rval:
    rval, image = vc.read()
    target_recognition(image)

    key = cv2.waitKey(20)
    if key == 27:
        break
