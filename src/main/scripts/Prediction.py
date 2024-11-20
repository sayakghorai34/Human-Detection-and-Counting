import cv2
from ultralytics import YOLO

def main():
    model = YOLO("models/yolo11m.onnx")

    video_source = 1
    cap = cv2.VideoCapture(video_source)

    if not cap.isOpened():
        print("Error: Unable to open video source.")
        return

    desired_width = 640
    desired_height = 640
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, desired_width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, desired_height)

    while True:
        ret, frame = cap.read()
        if not ret:
            print("End of video or unable to fetch frame.")
            break

        results = model.predict(source=frame, conf=0.4, iou=0.55, verbose=True)

        annotated_frame = results[0].plot()

        cv2.imshow("YOLO Detection", annotated_frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()