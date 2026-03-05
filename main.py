import cv2
import numpy as np
from PIL import ImageGrab
import time

def detect_shapes(image):
    # Convert the image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply Gaussian blur to reduce noise
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Detect edges using Canny edge detection
    edges = cv2.Canny(blurred, 50, 150)

    # Find contours in the edge-detected image
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Initialize shape counts
    shape_counts = {"circle": 0, "triangle": 0, "square": 0}

    for contour in contours:
        # Approximate the contour to a polygon
        epsilon = 0.04 * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)

        # Determine the shape based on the number of vertices
        if len(approx) == 3:
            shape_counts["triangle"] += 1
        elif len(approx) == 4:
            # Check if the shape is a square (aspect ratio close to 1)
            x, y, w, h = cv2.boundingRect(approx)
            aspect_ratio = float(w) / h
            if 0.95 <= aspect_ratio <= 1.05:
                shape_counts["square"] += 1
        elif len(approx) > 4:
            # Assume the shape is a circle if it has many vertices
            shape_counts["circle"] += 1

    return shape_counts

def capture_screen_and_detect_shapes():
    while True:
        # Capture the screen
        screenshot = ImageGrab.grab()

        # Convert the screenshot to a NumPy array (OpenCV format)
        image = np.array(screenshot)

        # Convert RGB to BGR (OpenCV uses BGR format)
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        # Detect shapes in the image
        shape_counts = detect_shapes(image)

        # Print the shape counts
        print("Shape Counts:")
        for shape, count in shape_counts.items():
            print(f"{shape}: {count}")

        # Wait for 5 seconds
        time.sleep(5)

if __name__ == "__main__":
    capture_screen_and_detect_shapes()
