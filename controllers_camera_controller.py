
from PyQt5 import QtCore
from PyQt5.QtGui import QPixmap

import time
import cv2

from workers_camera_worker import CameraWorker

from config import *


class CameraController:

    def __init__(self, window):
        self.window = window

        self.camera_configs = [
            {
                "id": CAM_ID_1,
                "folder": PHOTO_FOLDER_1,
                "label_id": 1
            },
            {
                "id": CAM_ID_2,
                "folder": PHOTO_FOLDER_2,
                "label_id": 2
            }
        ]


    # CAMERA
    def update_camera(self, image, cam_id):

        pixmap = QPixmap.fromImage(image)

        if cam_id == 1:
            label = self.window.camera_label_1
        else:
            label = self.window.camera_label_2

        label.setPixmap(
            pixmap.scaled(
                label.size(),
                QtCore.Qt.KeepAspectRatio,
                QtCore.Qt.SmoothTransformation
            )
        )

    def closeEvent(self, event):

        self.stop_cameras()

        if hasattr(self, "worker"):
            self.worker.stop()
            self.worker.wait()

        event.accept()

    def start_cameras(self):

        self.camera_workers = []

        for cam in self.camera_configs:

            worker = CameraWorker(cam["id"])

            worker.frame_updated.connect(
                lambda img, label_id=cam["label_id"]:
                self.update_camera(img, label_id)
            )

            worker.start()

            self.camera_workers.append(worker)

    def stop_cameras(self):

        for worker in self.camera_workers:
            worker.stop()

        for worker in self.camera_workers:
            worker.wait()


    def capture_highres_photo(self, camera_id, folder):

        cap = cv2.VideoCapture(camera_id)

        cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAM_CAPTURE_W)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAM_CAPTURE_H)

        # даём камере прогреться
        time.sleep(2.0)

        frame = None

        # считываем несколько кадров
        for _ in range(15):

            ret, frame = cap.read()

            if not ret:
                continue
            time.sleep(0.03)

        if frame is not None:

            filename = (
                f"{folder}/photo_"
                f"{time.strftime('%Y%m%d_%H%M%S')}.jpg"
            )
            cv2.imwrite(filename, frame)
            print(f"Saved: {filename}")

        else:
            print(f"Failed capture from camera {camera_id}")

        cap.release()

    def take_photo(self):

        self.stop_cameras()
        try:
            for cam in self.camera_configs:
                self.capture_highres_photo(
                    cam["id"],
                    cam["folder"]
                )
        finally:
            self.start_cameras()