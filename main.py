import cv2
import numpy as np
from PIL import ImageGrab
import time
from Quartz import CGWindowListCopyWindowInfo, kCGWindowListOptionOnScreenOnly, kCGNullWindowID
import os

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
            aspect_ratio = float(w) / h
            if 0.95 <= aspect_ratio <= 1.05 and w >= 26 and h >= 26:  # Filter out squares smaller than 26x26
                shape_counts["square"] += 1
        elif len(approx) > 4:
            # Assume the shape is a circle if it has many vertices
            shape_counts["circle"] += 1

    return shape_counts

def find_minimetro_window():
    # Get a list of all on-screen windows
    window_list = CGWindowListCopyWindowInfo(kCGWindowListOptionOnScreenOnly, kCGNullWindowID)

    for window in window_list:
        # Check if the window belongs to the "MiniMetro" or "Mini Metro" application
        window_name = window.get("kCGWindowName", "")
        if "MiniMetro" in window_name or "Mini Metro" in window_name:
            bounds = window.get("kCGWindowBounds", {})
            if bounds:
                # Return the bounding box of the window
                x = int(bounds.get("X", 0))
                y = int(bounds.get("Y", 0))
                width = int(bounds.get("Width", 0))
                height = int(bounds.get("Height", 0))
                return (x, y, x + width, y + height)

    print("MiniMetro or Mini Metro application not found.")
    return None

def capture_minimetro_window():
    # Find the MiniMetro window
    bbox = find_minimetro_window()
    if bbox is None:
        return None

    # Capture the window area
    screenshot = ImageGrab.grab(bbox=bbox)
    return screenshot

def detect_shapes_and_draw(image):
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

        # Get the bounding rectangle for the contour
        x, y, w, h = cv2.boundingRect(approx)

        # Discard shapes with an aspect ratio greater than 2 in either direction
        if w / h > 2 or h / w > 2:
            continue

        # Determine the shape based on the number of vertices
        if len(approx) == 3:
            shape_counts["triangle"] += 1
            cv2.drawContours(image, [approx], -1, (0, 255, 0), 2)  # Green for triangles
            cv2.putText(image, f"Triangle ({w}x{h})", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        elif len(approx) == 4:
            # Check if the shape is a square (aspect ratio close to 1)
            aspect_ratio = float(w) / h
            if 0.95 <= aspect_ratio <= 1.05 and w >= 26 and h >= 26:  # Filter out squares smaller than 26x26
                shape_counts["square"] += 1
                cv2.drawContours(image, [approx], -1, (255, 0, 0), 2)  # Blue for squares
                cv2.putText(image, f"Square ({w}x{h})", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
        elif len(approx) > 4:
            # Assume the shape is a circle if it has many vertices
            if w >= 26 and h >= 26:  # Filter out circles smaller than 26x26
                shape_counts["circle"] += 1
                cv2.drawContours(image, [approx], -1, (0, 0, 255), 2)  # Red for circles
                cv2.putText(image, f"Circle ({w}x{h})", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

    return shape_counts, image

def capture_and_process_minimetro():
    while True:
        # Capture the MiniMetro window
        screenshot = capture_minimetro_window()
        if screenshot is None:
            time.sleep(5)
            continue

        # Convert the screenshot to a NumPy array (OpenCV format)
        image = np.array(screenshot)

        # Convert RGB to BGR (OpenCV uses BGR format)
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        # Detect shapes and draw on the image
        shape_counts, processed_image = detect_shapes_and_draw(image)

        # Print the shape counts
        print("Shape Counts:")
        for shape, count in shape_counts.items():
            print(f"{shape}: {count}")

        # Save the processed image with shapes highlighted and timestamp in the filename
        destination_folder = "/Users/andrew/Desktop/Projects/neuralmetro/screenshots"
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        screenshot_path = os.path.join(destination_folder, f"processed_screenshot_{timestamp}.png")
        cv2.imwrite(screenshot_path, processed_image)
        print(f"Screenshot copied to '{screenshot_path}'")

        # Wait for 5 seconds
        time.sleep(5)

if __name__ == "__main__":
    capture_and_process_minimetro()
