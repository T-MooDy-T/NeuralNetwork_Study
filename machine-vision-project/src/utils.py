import cv2
import numpy as np

def load_image(image_path):
    return cv2.imread(image_path)

def grayscale(image):
    if len(image.shape) == 3:
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return image

def resize(image, size=(28, 28)):
    return cv2.resize(image, size)

def normalize(image):
    return image / 255.0

def threshold(image, thresh=127):
    _, binary = cv2.threshold(image, thresh, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    return binary

def preprocess_digit(image):
    gray = grayscale(image)
    thresh = threshold(gray)
    resized = resize(thresh)
    normalized = normalize(resized)
    return normalized

def draw_shapes(image, shapes):
    output = image.copy()
    for shape in shapes:
        cv2.drawContours(output, [shape['contour']], -1, (0, 255, 0), 2)
        M = cv2.moments(shape['contour'])
        if M["m00"] != 0:
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            cv2.putText(output, shape['shape'], (cX, cY), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    return output