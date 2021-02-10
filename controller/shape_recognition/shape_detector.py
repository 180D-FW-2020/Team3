import cv2
import numpy as np

class ShapeDetector:
    def __init__(self):
        pass

    def detect(self, c):
        shape = "unidentified"
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.1 * peri, True)
        coords = np.zeros((3, 2))
        target_info = []
        target_info.append(shape)
        target_info.append(coords)
        if len(approx) == 3:
            coords = np.zeros((3, 2))
            coords[0] = approx[0]
            coords[1] = approx[1]
            coords[2] = approx[2]
            len_1 = np.sqrt(((coords[0, 0]-coords[1, 0])**2)+((coords[0, 1]-coords[1, 1])**2))
            len_2 = np.sqrt(((coords[0, 0]-coords[2, 0])**2)+((coords[0, 1]-coords[2, 1])**2))
            #len_3 = np.sqrt(((coords[1, 0]-coords[2, 0])**2)+((coords[1, 1]-coords[2, 1])**2))
            #error_margin = .1*min(len_1, len_2)
            #if ((np.abs(len_1-len_2) < error_margin)):
            #    shape = "triangle"
            #    target_info[0] = shape
            #    target_info[1] = coords
            shape = "triangle"
            target_info[0] = shape
            target_info[1] = coords
        return target_info       
