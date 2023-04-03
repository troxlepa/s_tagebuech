import cv2
import numpy as np
import matplotlib.pyplot as plt

img = cv2.imread('img2.jpg',0)
#img = cv2.rotate(img,rotateCode=cv2.ROTATE_90_COUNTERCLOCKWISE)
img = cv2.medianBlur(img,5)
img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 17, 21)

#edges = cv2.Canny(img, 10, 100,apertureSize=3)
cv2.imshow("img",img)
cv2.waitKey(0)