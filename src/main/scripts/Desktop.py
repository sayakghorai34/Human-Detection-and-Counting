import cv2
from ultralytics import YOLO
import tkinter as tk
from PIL import Image, ImageTk
from threading import Thread


class YOLOApp:
    def __init__(self, root):
        self.root = root
        self.root.title("YOLO Detection GUI")

        # Initialize YOLO model
        self.model = YOLO("src/main/scripts/models/yolo11m.onnx")

        # Set up video capture
        #video Window
        self.cap = cv2.VideoCapture(0)
        self.desired_width = 640
        self.desired_height = 640
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.desired_width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.desired_height)

        # Create GUI elements
        self.video_frame = tk.Label(root)
        self.video_frame.pack()

        self.start_button = tk.Button(root, text="Start", command=self.start_video)
        self.start_button.pack()

        self.stop_button = tk.Button(root, text="Stop", command=self.stop_video)
        self.stop_button.pack()

        self.exit_button = tk.Button(root, text="Exit", command=self.exit_app)
        self.exit_button.pack()

        self.running = False
        self.thread = None

    def start_video(self):
        if not self.running:
            self.running = True
            self.thread = Thread(target=self.video_loop, daemon=True)
            self.thread.start()

    def stop_video(self):
        self.running = False

    def exit_app(self):
        self.stop_video()
        if self.cap.isOpened():
            self.cap.release()
        self.root.destroy()

    def video_loop(self):
        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                print("Error: Unable to fetch frame.")
                break

            # YOLO prediction
            results = self.model.predict(source=frame, conf=0.4, iou=0.55, verbose=False)
            annotated_frame = results[0].plot()

            # Convert frame to ImageTk format
            frame_rgb = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)
            imgtk = ImageTk.PhotoImage(image=img)

            # Update GUI video frame
            self.video_frame.imgtk = imgtk
            self.video_frame.configure(image=imgtk)

        self.video_frame.configure(image=None)  # Clear frame after stopping


if __name__ == "__main__":
    root = tk.Tk()
    app = YOLOApp(root)
    root.mainloop()
