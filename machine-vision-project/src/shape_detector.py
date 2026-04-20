import cv2
import numpy as np

class ShapeDetector:
    def __init__(self):
        pass
    
    def detect(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        _, thresh = cv2.threshold(blurred, 60, 255, cv2.THRESH_BINARY)
        
        contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        shapes = []
        for contour in contours:
            perimeter = cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, 0.04 * perimeter, True)
            vertices = len(approx)
            
            shape = self._classify_shape(vertices, contour, perimeter)
            if shape:
                shapes.append({
                    'shape': shape,
                    'contour': contour,
                    'vertices': vertices
                })
        
        return shapes
    
    def _classify_shape(self, vertices, contour, perimeter):
        area = cv2.contourArea(contour)
        
        if vertices == 3:
            return 'triangle'
        elif vertices == 4:
            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = float(w) / h
            if 0.95 <= aspect_ratio <= 1.05:
                return 'square'
            else:
                return 'rectangle'
        elif vertices >= 5:
            circularity = 4 * np.pi * (area / (perimeter ** 2))
            if circularity > 0.7:
                return 'circle'
            else:
                return 'polygon'
        
        return None