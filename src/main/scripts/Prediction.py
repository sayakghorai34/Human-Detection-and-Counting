import cv2
import time
import numpy as np
from PIL import Image, ImageDraw
from tensorflow.lite.python.interpreter import Interpreter


interpreter = Interpreter(model_path="models/yolov10s_simplified_float16.tflite")
interpreter.allocate_tensors()

input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

object_map = {
            0: 'person', 1: 'bicycle', 2: 'car', 3: 'motorcycle', 4: 'airplane',
            5: 'bus', 6: 'train', 7: 'truck', 8: 'boat', 9: 'traffic light',
            10: 'fire hydrant', 11: 'stop sign', 12: 'parking meter', 13: 'bench', 14: 'bird',
            15: 'cat', 16: 'dog', 17: 'horse', 18: 'sheep', 19: 'cow',
            20: 'elephant', 21: 'bear', 22: 'zebra', 23: 'giraffe', 24: 'backpack',
            25: 'umbrella', 26: 'handbag', 27: 'tie', 28: 'suitcase', 29: 'frisbee',
            30: 'skis', 31: 'snowboard', 32: 'sports ball', 33: 'kite', 34: 'baseball bat',
            35: 'baseball glove', 36: 'skateboard', 37: 'surfboard', 38: 'tennis racket', 39: 'bottle',
            40: 'wine glass', 41: 'cup', 42: 'fork', 43: 'knife', 44: 'spoon',
            45: 'bowl', 46: 'banana', 47: 'apple', 48: 'sandwich', 49: 'orange',
            50: 'broccoli', 51: 'carrot', 52: 'hot dog', 53: 'pizza', 54: 'donut',
            55: 'cake', 56: 'chair', 57: 'couch', 58: 'potted plant', 59: 'bed',
            60: 'dining table', 61: 'toilet', 62: 'tv', 63: 'laptop', 64: 'mouse',
            65: 'remote', 66: 'keyboard', 67: 'cell phone', 68: 'microwave', 69: 'oven',
            70: 'toaster', 71: 'sink', 72: 'refrigerator', 73: 'book', 74: 'clock',
            75: 'vase', 76: 'scissors', 77: 'teddy bear', 78: 'hair drier', 79: 'toothbrush'
            }

bbox_colour_map = {
            0: "#FF0000", 1: "#00FF00", 2: "#0000FF", 3: "#FFFF00", 4: "#00FFFF",
            5: "#FF00FF", 6: "#FFA500", 7: "#A52A2A", 8: "#800080", 9: "#008000",
            10: "#000080", 11: "#808000", 12: "#800000", 13: "#008080", 14: "#808080",
            15: "#C0C0C0", 16: "#FF6347", 17: "#FFD700", 18: "#ADFF2F", 19: "#FF69B4",
            20: "#FF4500", 21: "#FF1493", 22: "#6495ED", 23: "#7CFC00", 24: "#DC143C",
            25: "#00CED1", 26: "#20B2AA", 27: "#FF7F50", 28: "#DAA520", 29: "#98FB98",
            30: "#8A2BE2", 31: "#5F9EA0", 32: "#7B68EE", 33: "#6A5ACD", 34: "#00FA9A",
            35: "#4682B4", 36: "#BDB76B", 37: "#FFDAB9", 38: "#DDA0DD", 39: "#E6E6FA",
            40: "#F0E68C", 41: "#EE82EE", 42: "#8B0000", 43: "#B22222", 44: "#556B2F",
            45: "#D2691E", 46: "#9932CC", 47: "#000000", 48: "#F5DEB3", 49: "#2E8B57",
            50: "#8B4513", 51: "#DA70D6", 52: "#32CD32", 53: "#FA8072", 54: "#FFB6C1",
            55: "#B0C4DE", 56: "#9ACD32", 57: "#F4A460", 58: "#1E90FF", 59: "#00BFFF",
            60: "#778899", 61: "#191970", 62: "#483D8B", 63: "#7FFF00", 64: "#66CDAA",
            65: "#9400D3", 66: "#FFD700", 67: "#00FF7F", 68: "#8FBC8F", 69: "#7FFFD4",
            70: "#00FFFF", 71: "#DB7093", 72: "#AFEEEE", 73: "#FF6347", 74: "#CD5C5C",
            75: "#FFA07A", 76: "#FF4500", 77: "#FFDAB9", 78: "#FF69B4", 79: "#FFA07A"
        }

# video_path = "people_vid.mp4"
cap = cv2.VideoCapture(1)
if not cap.isOpened():
    print("Error: Could not open the webcam.")
    exit()

print("Starting live camera feed. Press 'q' to exit.")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("Error: Could not read frame from camera.")
        break

    # Start time for inference
    start_time = time.time()

    # Preprocess the frame
    resized_frame = cv2.resize(frame, (640, 640))
    input_data = np.expand_dims(np.array(resized_frame, dtype=np.float32) / 255.0, axis=0)

    # Run inference
    interpreter.set_tensor(input_details[0]['index'], input_data)
    interpreter.invoke()

    # Get output tensors
    outputs = [interpreter.get_tensor(output['index']) for output in output_details]

    obj_count = 0
    person_count = 0

    # Parse detections
    for detection in outputs[0][0]:
        x_min, y_min, x_max, y_max, confidence, class_id = detection
        if confidence > 0.05:  # Set a confidence threshold
            obj_count += 1
            if int(class_id) == 0:  # 'person' class
                person_count += 1

            # Draw bounding box
            color = tuple(int(bbox_colour_map[int(class_id)].lstrip('#')[i:i + 2], 16) for i in (4, 2, 0))
            cv2.rectangle(resized_frame, (int(x_min), int(y_min)), (int(x_max), int(y_max)), color, 2)

            # Add class label
            cv2.putText(resized_frame, f"{object_map.get(int(class_id), 'Unknown')}",
                        (int(x_min), int(y_min) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)

    # Calculate FPS
    end_time = time.time()
    inference_time = end_time - start_time
    fps = 1 / inference_time if inference_time > 0 else 0

    # Overlay information
    cv2.putText(resized_frame, f"FPS: {fps:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.putText(resized_frame, f"Objects: {obj_count}", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.putText(resized_frame, f"Persons: {person_count}", (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # Display the frame
    cv2.imshow("Live Object Detection", resized_frame)

    # Exit on 'q' key press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()