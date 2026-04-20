import cv2
import os
import numpy as np

from src.digit_recognizer import DigitRecognizer
from src.shape_detector import ShapeDetector
from src.utils import load_image, draw_shapes

def generate_test_images():
    os.makedirs('data/samples', exist_ok=True)
    
    canvas = np.ones((200, 200), dtype=np.uint8) * 255
    
    cv2.putText(canvas, '5', (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 5, 0, 10)
    cv2.imwrite('data/samples/digit_5.png', canvas)
    
    canvas2 = np.ones((200, 200, 3), dtype=np.uint8) * 255
    cv2.circle(canvas2, (100, 100), 50, (0, 0, 0), 3)
    cv2.rectangle(canvas2, (30, 30), (170, 170), (0, 0, 0), 3)
    cv2.imwrite('data/samples/shapes.png', canvas2)

def main():
    print("Initializing machine vision project...")
    
    generate_test_images()
    print("Test images generated.")
    
    print("\n--- Testing Digit Recognition ---")
    digit_recognizer = DigitRecognizer()
    
    digit_image = load_image('data/samples/digit_5.png')
    result = digit_recognizer.predict(digit_image)
    print(f"Digit recognition result: {result}")
    
    print("\n--- Testing Shape Detection ---")
    shape_detector = ShapeDetector()
    
    shape_image = load_image('data/samples/shapes.png')
    shapes = shape_detector.detect(shape_image)
    
    print(f"Detected shapes: {[s['shape'] for s in shapes]}")
    
    output_image = draw_shapes(shape_image, shapes)
    cv2.imwrite('data/samples/shapes_detected.png', output_image)
    print("Detection result saved to data/samples/shapes_detected.png")
    
    print("\nMachine vision project test completed successfully!")

if __name__ == '__main__':
    main()