from PyQt5 import QtCore, QtGui
import cv2
import time


class CameraWorker(QtCore.QThread):

    frame_updated = QtCore.pyqtSignal(QtGui.QImage)

    def __init__(self, camera_index=0):
        super().__init__()

        self.running = True
        self.camera_index = camera_index

        self.last_frame = None

    def run(self):

        self.cap = cv2.VideoCapture(
            self.camera_index,
            cv2.CAP_V4L2
        )

        # FULL HD
        # self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 2560)
        # self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1440)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)        
        # self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        # self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

        # self.cap.set(
        #     cv2.CAP_PROP_FOURCC,
        #     cv2.VideoWriter_fourcc(*'MJPG')
        # )

        # # Ручная экспозиция
        # self.cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1)

        # # подбирай 200-800
        # self.cap.set(cv2.CAP_PROP_EXPOSURE, 200)

        # # отключаем автофокус
        # self.cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)

        # # подбирай
        # self.cap.set(cv2.CAP_PROP_FOCUS, 220)

        last_preview = time.time()

        while self.running:

            ret, frame = self.cap.read()

            if not ret:
                continue

            self.last_frame = frame.copy()

            # preview 1 FPS
            if time.time() - last_preview >= 1:

                preview = cv2.resize(frame, (640, 360))

                preview = cv2.cvtColor(
                    preview,
                    cv2.COLOR_BGR2RGB
                )

                h, w, ch = preview.shape

                qt_image = QtGui.QImage(
                    preview.data,
                    w,
                    h,
                    ch * w,
                    QtGui.QImage.Format_RGB888
                ).copy()

                self.frame_updated.emit(qt_image)

                last_preview = time.time()

        self.cap.release()

    def get_frame(self):

        return self.last_frame

    def stop(self):

        self.running = False