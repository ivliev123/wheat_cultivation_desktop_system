from PyQt5 import QtCore, QtGui
import cv2


class CameraWorker(QtCore.QThread):
    frame_updated = QtCore.pyqtSignal(QtGui.QImage)

    def __init__(self, camera_index=0):
        super().__init__()
        self.running = True
        self.camera_index = camera_index

    def run(self):
        self.cap = cv2.VideoCapture(self.camera_index)

        # Linux/Ubuntu compatibility
        # self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 2560)
        # self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1440)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 360)

        while self.running:
            ret, frame = self.cap.read()

            if ret:
                # BGR -> RGB
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                h, w, ch = frame.shape
                bytes_per_line = ch * w

                qt_image = QtGui.QImage(
                    frame.data,
                    w,
                    h,
                    bytes_per_line,
                    QtGui.QImage.Format_RGB888
                ).copy()

                self.frame_updated.emit(qt_image)

            self.msleep(30)

        self.cap.release()

    def stop(self):
        self.running = False
