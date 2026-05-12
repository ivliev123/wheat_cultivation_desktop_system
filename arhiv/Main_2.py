# import os
# import sys
# from PyQt5.QtCore import QLibraryInfo

# os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = os.path.join(
#     QLibraryInfo.location(QLibraryInfo.PluginsPath),
#     "platforms"
# )

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QGroupBox, QLabel, 
    QGridLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QVBoxLayout, QHBoxLayout, QSpacerItem, 
    QSizePolicy, QHeaderView, QAbstractItemView,
    QLineEdit, QFileDialog, QMessageBox, QComboBox,
    QRadioButton, QButtonGroup
)
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtGui import QPixmap, QColor, QIcon, QFont

import sys
import time
from pymodbus.client import ModbusSerialClient
import serial.tools.list_ports

import cv2


# ================= CONFIG =================
# PORT = "COM3"
BAUDRATE = 115200

SLAVE_BOARD_ID_1 = 10
SLAVE_BOARD_ID_2 = 11

# Регистры управления
REG_Channal_1 = 0
REG_Channal_2 = 1
REG_Channal_3 = 2
REG_Channal_4 = 3

REG_Relay_1 = 10
REG_Relay_2 = 11
REG_Relay_3 = 12
REG_Relay_4 = 13

# Датчики
REG_BME_280_1_Temperature = 10
REG_BME_280_1_Pressure = 11
REG_BME_280_1_Humidity = 12

REG_BME_280_2_Temperature = 20
REG_BME_280_2_Pressure = 21
REG_BME_280_2_Humidity = 22

REG_ADC_1 = 50
REG_FLOW_1 = 60

# ==========================================


# ================= UI CONFIG =================

WINDOW_WIDTH  = 1040
WINDOW_HEIGHT = 900

GROUPBOX_MAX_WIDTH  = 500
GROUPBOX_MAX_HEIGHT = 250

CAMERA_WIDTH  = 640
CAMERA_HEIGHT = 360

SMALL_GROUP_WIDTH  = 400
SMALL_GROUP_HEIGHT = 220

MEDIUM_GROUP_WIDTH  = 600
MEDIUM_GROUP_HEIGHT = 250

LARGE_GROUP_WIDTH  = 800
LARGE_GROUP_HEIGHT = 500
# =============================================


# =============================================
CAM_PREVIEW_W = 640
CAM_PREVIEW_H = 360

CAM_CAPTURE_W = 2560
CAM_CAPTURE_H = 1440


CAM_ID_1 = 1
CAM_ID_2 = 2

PHOTO_FOLDER_1 = "Captures_cam_1"
PHOTO_FOLDER_2 = "Captures_cam_2"


# =============================================




class SerialManager:
    def __init__(self):
        self.port = None
        self.connected = False

    def get_available_ports(self):
        ports = serial.tools.list_ports.comports()
        return [p.device for p in ports]

    def connect(self, port):
        self.port = port
        self.connected = True
        print(f"Connected to {port}")

    def disconnect(self):
        print("Disconnected")
        self.connected = False



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



class ModbusWorker(QtCore.QThread):
    data_updated = QtCore.pyqtSignal(dict)

    def __init__(self, port):
        super().__init__()
        self.running = True

        self.client = ModbusSerialClient(
            framer="rtu",
            port=port,
            baudrate=BAUDRATE,
            stopbits=1,
            bytesize=8,
            parity="N",
            timeout=0.2
        )

    def run(self):
        self.client.connect()

        while self.running:
            try:
                data = {}

                # BME280_1
                r = self.client.read_holding_registers(REG_BME_280_1_Temperature, count=1, slave=SLAVE_BOARD_ID_2)
                if not r.isError():
                    data["sensor_BME280_1_temperature"] = r.registers[0] * 0.01
                r = self.client.read_holding_registers(REG_BME_280_1_Pressure, count=1, slave=SLAVE_BOARD_ID_2)
                if not r.isError():
                    data["sensor_BME280_1_pressure"] = r.registers[0] * 0.1
                r = self.client.read_holding_registers(REG_BME_280_1_Humidity, count=1, slave=SLAVE_BOARD_ID_2)
                if not r.isError():
                    data["sensor_BME280_1_humidity"] = r.registers[0] * 0.1

                # BME280_2
                r = self.client.read_holding_registers(REG_BME_280_2_Temperature, count=1, slave=SLAVE_BOARD_ID_2)
                if not r.isError():
                    data["sensor_BME280_2_temperature"] = r.registers[0] * 0.01
                r = self.client.read_holding_registers(REG_BME_280_2_Pressure, count=1, slave=SLAVE_BOARD_ID_2)
                if not r.isError():
                    data["sensor_BME280_2_pressure"] = r.registers[0] * 0.1
                r = self.client.read_holding_registers(REG_BME_280_2_Humidity, count=1, slave=SLAVE_BOARD_ID_2)
                if not r.isError():
                    data["sensor_BME280_2_humidity"] = r.registers[0] * 0.1

                # ADC
                r = self.client.read_holding_registers(REG_ADC_1, count=8, slave=SLAVE_BOARD_ID_2)
                if not r.isError():
                    data["adc"] = r.registers

                # Flow
                r = self.client.read_holding_registers(REG_FLOW_1, count=4, slave=SLAVE_BOARD_ID_2)
                if not r.isError():
                    data["flow"] = r.registers

                self.data_updated.emit(data)

            except Exception as e:
                print("Error:", e)

            time.sleep(0.5)

    def stop(self):
        self.running = False
        self.client.close()

    # Управление каналами
    def set_channel(self, reg, value):
        self.client.write_registers(reg, [value], slave=SLAVE_BOARD_ID_1)

    def set_relay(self, reg, value):
        self.client.write_registers(reg, [value], slave=SLAVE_BOARD_ID_1)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

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




        self.init_ui()

        self.camera_worker_1 = CameraWorker(CAM_ID_1)
        self.camera_worker_2 = CameraWorker(CAM_ID_2)

        self.camera_worker_1.frame_updated.connect(
            lambda img: self.update_camera(img, 1)
        )
        self.camera_worker_2.frame_updated.connect(
            lambda img: self.update_camera(img, 2)
        )

        self.camera_worker_1.start()
        self.camera_worker_2.start()

        self.photo_button.clicked.connect(self.take_photo)


        self.pump_1_pushbutton_ON.clicked.connect(lambda: self.pump_pushbutton_function(1, 1))
        self.pump_1_pushbutton_OFF.clicked.connect(lambda: self.pump_pushbutton_function(1, 0))
        self.pump_2_pushbutton_ON.clicked.connect(lambda: self.pump_pushbutton_function(2, 1))
        self.pump_2_pushbutton_OFF.clicked.connect(lambda: self.pump_pushbutton_function(2, 0))

        self.lamp_pushbutton.clicked.connect(self.lamp_callback)

        self.update_button.clicked.connect(self.update_ports)
        self.connect_button.clicked.connect(self.toggle_connection)

        self.update_ports()


    def update_ports(self):
        self.port_combo.clear()
        ports = self.serial_manager.get_available_ports()
        self.port_combo.addItems(ports)

    
    def toggle_connection(self):
        if not self.serial_manager.connected:
            port = self.port_combo.currentText()
            self.serial_manager.connect(port)

            # 👇 передаём порт сюда
            self.worker = ModbusWorker(port)
            self.worker.data_updated.connect(self.update_ui)
            self.worker.start()

            self.connect_button.setText("Disconnect")
        else:
            self.serial_manager.disconnect()

            if hasattr(self, "worker"):
                self.worker.stop()
                self.worker.wait()

            self.connect_button.setText("Connect")


    # CAMERA
    def update_camera(self, image, cam_id):

        pixmap = QPixmap.fromImage(image)

        if cam_id == 1:
            label = self.camera_label_1
        else:
            label = self.camera_label_2

        label.setPixmap(
            pixmap.scaled(
                label.size(),
                QtCore.Qt.KeepAspectRatio,
                QtCore.Qt.SmoothTransformation
            )
        )

    def closeEvent(self, event):

        if hasattr(self, "camera_worker_1"):
            self.camera_worker_1.stop()
            self.camera_worker_1.wait()

        if hasattr(self, "camera_worker_2"):
            self.camera_worker_2.stop()
            self.camera_worker_2.wait()

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

        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 2560)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1440)

        time.sleep(0.3)

        ret, frame = cap.read()

        if ret:

            filename = (
                f"{folder}/photo_"
                f"{time.strftime('%Y%m%d_%H%M%S')}.jpg"
            )

            cv2.imwrite(filename, frame)

            print(f"Saved: {filename}")

        else:
            print(f"Failed capture from camera {camera_id}")

        cap.release()


    # def take_photo(self):
    #     # Временно останавливаем оба потока камеры
    #     self.camera_worker_1.stop()
    #     self.camera_worker_2.stop()
    #     self.camera_worker_1.wait()
    #     self.camera_worker_2.wait()
        
    #     # Создаём временное подключение для фото
    #     temp_cap = cv2.VideoCapture(CAM_ID_1)  # Камера 1
        
    #     # Устанавливаем высокое разрешение
    #     temp_cap.set(cv2.CAP_PROP_FRAME_WIDTH, 2560)
    #     temp_cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1440)
        
    #     # Даём камере время на переключение разрешения
    #     time.sleep(0.5)
        
    #     ret, frame = temp_cap.read()
        
    #     if ret:
    #         filename = f"{PHOTO_FOLDER_1}/photo_{int(time.time())}.jpg"
    #         cv2.imwrite(filename, frame)
    #         print(f"Saved: {filename}")
    #     else:
    #         print("Failed to capture image from cam 1")
        
    #     temp_cap.release()
        
    #     # Перезапускаем потоки камеры
    #     self.camera_worker_1 = CameraWorker(CAM_ID_1)
    #     self.camera_worker_2 = CameraWorker(CAM_ID_2)
    #     self.camera_worker_1.frame_updated.connect(
    #         lambda img: self.update_camera(img, 1)
    #     )
    #     self.camera_worker_2.frame_updated.connect(
    #         lambda img: self.update_camera(img, 2)
    #     )
    #     self.camera_worker_1.start()
    #     self.camera_worker_2.start()

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


    # CAMERA


    def pump_pushbutton_function(self, pump_number, pump_status):
        # отправка через ModbusWorker
        if hasattr(self, "worker"):
            if pump_number == 1:
                REG = REG_Relay_3
            if pump_number == 2:
                REG = REG_Relay_4
            self.worker.client.write_registers(REG, [pump_status], slave=SLAVE_BOARD_ID_1)


        else:
            print("Worker not initialized")


        print(f"Pump №{pump_number}: {pump_status}")


    def update_ui(self, data):
        # Температура
        self.sensor_BME280_1_temperature_lineedit.setText(f"{data['sensor_BME280_1_temperature']:.2f}")
        self.sensor_BME280_1_pressure_lineedit.setText(f"{data['sensor_BME280_1_pressure']:.2f}")
        self.sensor_BME280_1_humidity_lineedit.setText(f"{data['sensor_BME280_1_humidity']:.2f}")

        self.sensor_BME280_2_temperature_lineedit.setText(f"{data['sensor_BME280_2_temperature']:.2f}")
        self.sensor_BME280_2_pressure_lineedit.setText(f"{data['sensor_BME280_2_pressure']:.2f}")
        self.sensor_BME280_2_humidity_lineedit.setText(f"{data['sensor_BME280_2_humidity']:.2f}")

        # ADC (влажность почвы)
        if "adc" in data:
            for i, value in enumerate(data["adc"]):
                if i < len(self.sensor_widgets):
                    self.sensor_widgets[i][1].setText(str(value))

        # Flow
        if "flow" in data:
            if len(data["flow"]) > 0:
                self.flow_sensor_1_lineedit.setText(str(data["flow"][0]))
            if len(data["flow"]) > 1:
                self.flow_sensor_2_lineedit.setText(str(data["flow"][1]))

                

    def lamp_callback(self):
        values = []

        try:
            for i, le in enumerate(self.channel_widgets):
                text = le.text().strip()

                if text == "":
                    raise ValueError(f"Channel {i+1} is empty")

                value = int(text)

                if not 0 <= value <= 200:
                    raise ValueError(f"Channel {i+1} out of range (0-200)")

                values.append(value)

            # отправка через ModbusWorker
            if hasattr(self, "worker"):
                self.worker.client.write_registers(
                    REG_Channal_1,  # стартовый регистр (0)
                    values,
                    slave=SLAVE_BOARD_ID_1
                )
            else:
                print("Worker not initialized")

            print("Lamp channels set:", values)

        except Exception as e:
            QMessageBox.warning(self, "Input error", str(e))


    def init_ui(self):

        self.setWindowTitle("Modbus Control Panel")
        self.resize(WINDOW_WIDTH, WINDOW_HEIGHT)
        # self.showMaximized()  # Развернуть на весь экран (с панелью задач)

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QGridLayout(main_widget)

        # SERIAL
        ############################################################################################### 
        # (тут должны быть 3 подблока: выбор компорта, устройства с указанием удресов устройств, режим авто или ручной )
        self.serial_manager = SerialManager()
        # ===== Панель подключения =====
        ##############################
        setting_groupbox = QGroupBox("")
        # setting_groupbox.setMaximumSize(1200, 300)
        setting_gridlayout = QGridLayout(setting_groupbox)

        serial_groupbox = QGroupBox("Serial")
        serial_groupbox.setMaximumSize(SMALL_GROUP_WIDTH, SMALL_GROUP_HEIGHT)
        serial_gridlayout = QGridLayout(serial_groupbox)

        self.port_combo = QComboBox()
        self.update_button = QPushButton("Update")
        self.update_button.setIcon(QIcon("icons/reload.png"))
        self.connect_button = QPushButton("Connect")
        self.connect_button.setIcon(QIcon("icons/usb.png"))

        serial_gridlayout.addWidget(QLabel("COM port:"), 0, 0)
        serial_gridlayout.addWidget(self.port_combo, 0, 1)
        serial_gridlayout.addWidget(self.update_button, 0, 2)
        serial_gridlayout.addWidget(self.connect_button, 1, 1, 1, 2)
        ##############################

        ##############################
        device_groupbox = QGroupBox("Device")
        device_groupbox.setMaximumSize(SMALL_GROUP_WIDTH, SMALL_GROUP_HEIGHT)
        device_gridlayout = QGridLayout(device_groupbox)

        self.slave1_edit = QLineEdit("10")
        self.slave1_edit.setReadOnly(True)
        self.slave2_edit = QLineEdit("11")
        self.slave2_edit.setReadOnly(True)

        device_gridlayout.addWidget(QLabel("Device 1 ID:"), 0, 0)
        device_gridlayout.addWidget(self.slave1_edit, 0, 1)

        device_gridlayout.addWidget(QLabel("Device 2 ID:"), 1, 0)
        device_gridlayout.addWidget(self.slave2_edit, 1, 1)
        ##############################

        ##############################
        mode_groupbox = QGroupBox("Mode")
        mode_groupbox.setMaximumSize(SMALL_GROUP_WIDTH, SMALL_GROUP_HEIGHT)
        mode_layout = QGridLayout(mode_groupbox)

        self.manual_radio = QRadioButton("Manual")
        self.auto_radio = QRadioButton("Auto")

        # по умолчанию пусть будет Manual
        self.manual_radio.setChecked(True)

        # группировка (важно!)
        self.mode_group = QButtonGroup()
        self.mode_group.addButton(self.manual_radio)
        self.mode_group.addButton(self.auto_radio)

        mode_layout.addWidget(self.manual_radio, 0, 0)
        mode_layout.addWidget(self.auto_radio, 1, 0)
        ##############################

        setting_gridlayout.addWidget(serial_groupbox, 0, 0)
        setting_gridlayout.addWidget(device_groupbox, 0, 1)
        setting_gridlayout.addWidget(mode_groupbox, 0, 2)
        
        ###############################################################################################
        
        # Блоки управления и сбора данных 
        ###############################################################################################
        # блок датчиков температуры, влажности, давления 
        self.dev2_sensor_BME280_group = QGroupBox("Device 2 | BME280 (Temperature humidity pressure) Sensors")
        self.dev2_sensor_BME280_group.setMaximumSize(MEDIUM_GROUP_WIDTH, MEDIUM_GROUP_HEIGHT)
        self.dev2_sensor_BME280_gridlayout = QGridLayout(self.dev2_sensor_BME280_group)

        self.sensor_BME280_1_group = QGroupBox("Sensor №1")
        self.sensor_BME280_1_group.setMaximumSize(SMALL_GROUP_WIDTH, SMALL_GROUP_HEIGHT)
        self.sensor_BME280_1_gridlayout = QGridLayout(self.sensor_BME280_1_group)
        
        sensor_BME280_1_temperature_label = QLabel(f'Temperature [°C]')
        sensor_BME280_1_humidity_label    = QLabel(f'Humidity [%]')
        sensor_BME280_1_pressure_label    = QLabel(f'Pressure [hPA]')
        self.sensor_BME280_1_temperature_lineedit   = QLineEdit()
        self.sensor_BME280_1_humidity_lineedit      = QLineEdit()
        self.sensor_BME280_1_pressure_lineedit      = QLineEdit()
        self.sensor_BME280_1_temperature_lineedit.setReadOnly(True)
        self.sensor_BME280_1_humidity_lineedit.setReadOnly(True)
        self.sensor_BME280_1_pressure_lineedit.setReadOnly(True)

        self.sensor_BME280_1_gridlayout.addWidget(sensor_BME280_1_temperature_label, 0, 0)
        self.sensor_BME280_1_gridlayout.addWidget(sensor_BME280_1_humidity_label, 1, 0)
        self.sensor_BME280_1_gridlayout.addWidget(sensor_BME280_1_pressure_label, 2, 0)
        self.sensor_BME280_1_gridlayout.addWidget(self.sensor_BME280_1_temperature_lineedit, 0, 1)
        self.sensor_BME280_1_gridlayout.addWidget(self.sensor_BME280_1_humidity_lineedit, 1, 1)
        self.sensor_BME280_1_gridlayout.addWidget(self.sensor_BME280_1_pressure_lineedit, 2, 1)

        self.sensor_BME280_2_group = QGroupBox("Sensor №2")
        self.sensor_BME280_2_group.setMaximumSize(SMALL_GROUP_WIDTH, SMALL_GROUP_HEIGHT)
        self.sensor_BME280_2_gridlayout = QGridLayout(self.sensor_BME280_2_group)

        sensor_BME280_2_temperature_label = QLabel(f'Temperature [°C]')
        sensor_BME280_2_humidity_label    = QLabel(f'Humidity [%]')
        sensor_BME280_2_pressure_label    = QLabel(f'Pressure [hPa]')
        self.sensor_BME280_2_temperature_lineedit   = QLineEdit()
        self.sensor_BME280_2_humidity_lineedit      = QLineEdit()
        self.sensor_BME280_2_pressure_lineedit      = QLineEdit()
        self.sensor_BME280_2_temperature_lineedit.setReadOnly(True)
        self.sensor_BME280_2_humidity_lineedit.setReadOnly(True)
        self.sensor_BME280_2_pressure_lineedit.setReadOnly(True)
        
        self.sensor_BME280_2_gridlayout.addWidget(sensor_BME280_2_temperature_label, 0, 0)
        self.sensor_BME280_2_gridlayout.addWidget(sensor_BME280_2_humidity_label, 1, 0)
        self.sensor_BME280_2_gridlayout.addWidget(sensor_BME280_2_pressure_label, 2, 0)
        self.sensor_BME280_2_gridlayout.addWidget(self.sensor_BME280_2_temperature_lineedit, 0, 1)
        self.sensor_BME280_2_gridlayout.addWidget(self.sensor_BME280_2_humidity_lineedit, 1, 1)
        self.sensor_BME280_2_gridlayout.addWidget(self.sensor_BME280_2_pressure_lineedit, 2, 1)

        self.dev2_sensor_BME280_gridlayout.addWidget(self.sensor_BME280_1_group, 0, 0)
        self.dev2_sensor_BME280_gridlayout.addWidget(self.sensor_BME280_2_group, 0, 1)
        ###############################################################################################


        ###############################################################################################
        self.dev1_pump_dev2_sensor_flow_group = QGroupBox("Device 1 | Pumps; Device 2 | Flow Sensors")
        self.dev1_pump_dev2_sensor_flow_group = QGroupBox("")
        self.dev1_pump_dev2_sensor_flow_group.setMaximumSize(MEDIUM_GROUP_WIDTH, MEDIUM_GROUP_HEIGHT)
        self.dev1_pump_dev2_sensor_flow_gridlayout = QGridLayout(self.dev1_pump_dev2_sensor_flow_group)

        ##############################
        self.dev1_pump_group = QGroupBox("Device 1 | Pumps")
        self.dev1_pump_group.setMaximumSize(SMALL_GROUP_WIDTH, SMALL_GROUP_HEIGHT)
        self.dev1_pump_gridlayout = QGridLayout(self.dev1_pump_group)

        self.pump_1_label = QLabel(f'Pump №1')
        self.pump_1_pushbutton_ON = QPushButton(f"ON")
        self.pump_1_pushbutton_OFF = QPushButton(f"OFF")

        self.pump_2_label = QLabel(f'Pump №2')
        self.pump_2_pushbutton_ON = QPushButton(f"ON")
        self.pump_2_pushbutton_OFF = QPushButton(f"OFF")

        self.dev1_pump_gridlayout.addWidget(self.pump_1_label, 0, 0)
        self.dev1_pump_gridlayout.addWidget(self.pump_1_pushbutton_ON, 0, 1)
        self.dev1_pump_gridlayout.addWidget(self.pump_1_pushbutton_OFF, 0, 2)
        self.dev1_pump_gridlayout.addWidget(self.pump_2_label, 1, 0)
        self.dev1_pump_gridlayout.addWidget(self.pump_2_pushbutton_ON, 1, 1)
        self.dev1_pump_gridlayout.addWidget(self.pump_2_pushbutton_OFF, 1, 2)
        ##############################

        ##############################
        self.dev2_flow_sensor_group = QGroupBox("Device 2 | Flow Sensors")
        self.dev2_flow_sensor_group.setMaximumSize(SMALL_GROUP_WIDTH, SMALL_GROUP_HEIGHT)
        self.dev2_flow_sensor_gridlayout = QGridLayout(self.dev2_flow_sensor_group)

        flow_sensor_1_label = QLabel(f'Flow Sensor №1')
        self.flow_sensor_1_lineedit   = QLineEdit()
        self.flow_sensor_1_lineedit.setReadOnly(True)
        flow_sensor_2_label = QLabel(f'Flow Sensor №2')
        self.flow_sensor_2_lineedit   = QLineEdit()
        self.flow_sensor_2_lineedit.setReadOnly(True)

        self.dev2_flow_sensor_gridlayout.addWidget(flow_sensor_1_label, 0, 0)
        self.dev2_flow_sensor_gridlayout.addWidget(self.flow_sensor_1_lineedit, 0, 1)
        self.dev2_flow_sensor_gridlayout.addWidget(flow_sensor_2_label, 1, 0)
        self.dev2_flow_sensor_gridlayout.addWidget(self.flow_sensor_2_lineedit , 1, 1)
        ##############################
        
        self.dev1_pump_dev2_sensor_flow_gridlayout.addWidget(self.dev1_pump_group, 0, 0)
        self.dev1_pump_dev2_sensor_flow_gridlayout.addWidget(self.dev2_flow_sensor_group, 0, 1)
        ###############################################################################################


        ###############################################################################################
        # блок датчиков влажности грунта
        self.dev2_sensor_humidity_gnd_group = QGroupBox("Device 2 | Soil Moisture Sensor")
        self.dev2_sensor_humidity_gnd_group.setMaximumSize(MEDIUM_GROUP_WIDTH, MEDIUM_GROUP_HEIGHT)
        self.dev2_sensor_humidity_gnd_gridlayout = QGridLayout(self.dev2_sensor_humidity_gnd_group)

        self.sensor_widgets = []  # если нужно потом к ним обращаться
        for i in range(8):
            label = QLabel(f'Sensor №{i + 1}')
            lineedit = QLineEdit()
            lineedit.setReadOnly(True)

            # вычисляем позицию
            row = i % 4          # 0–3
            col = (i // 4) * 2   # 0 или 2 (каждый блок = 2 колонки)

            self.dev2_sensor_humidity_gnd_gridlayout.addWidget(label, row, col)
            self.dev2_sensor_humidity_gnd_gridlayout.addWidget(lineedit, row, col + 1)

            self.sensor_widgets.append((label, lineedit))
        ###############################################################################################


        ###############################################################################################
        # LAMP
        self.dev1_lamp_group = QGroupBox("Device 1 | Lamp")
        self.dev1_lamp_group.setMaximumSize(MEDIUM_GROUP_WIDTH, MEDIUM_GROUP_HEIGHT)
        self.dev1_lamp_gridlayout = QGridLayout(self.dev1_lamp_group)

        self.channel_widgets = [] 
        self.color_buttons = [] 
        channel_name_array = ['Red', 'Blue', 'Far Red', 'White']
        color_array = ['#D32F2F', '#3B71CA', '#D50000', '#FBFBFB']

        for i in range(4):
            channel_label = QLabel(channel_name_array[i])
            channel_lineedit = QLineEdit()
            channel_lineedit.setPlaceholderText("0-200")
            channel_lineedit.setText("0")

            # (только числа 0–200)
            validator = QtGui.QIntValidator(0, 200)
            channel_lineedit.setValidator(validator)

            self.channel_widgets.append(channel_lineedit)

            color_button = QPushButton()
            color_button.setFixedSize(20, 20) 
            color_button.setEnabled(False)

            color_button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color_array[i]};
                    border-radius: 10px;
                }}
            """)
            
            self.color_buttons.append(color_button)
            
            self.dev1_lamp_gridlayout.addWidget(color_button, i, 0)
            self.dev1_lamp_gridlayout.addWidget(channel_label, i, 1)
            self.dev1_lamp_gridlayout.addWidget(channel_lineedit, i, 2)


        self.lamp_pushbutton = QPushButton(f"Setup")
        self.dev1_lamp_gridlayout.addWidget(self.lamp_pushbutton, 5, 0, 1, 3)


        ###############################################################################################
        # CAMERA
        self.camera_group = QGroupBox("Camera")
        self.camera_layout = QVBoxLayout(self.camera_group)

        self.camera_label_1 = QLabel()
        self.camera_label_1.setFixedSize(CAMERA_WIDTH, CAMERA_HEIGHT)
        self.camera_label_1.setStyleSheet("background-color: black;")

        self.camera_label_2 = QLabel()
        self.camera_label_2.setFixedSize(CAMERA_WIDTH, CAMERA_HEIGHT)
        self.camera_label_2.setStyleSheet("background-color: black;")

        self.photo_button = QPushButton("Take Photo")
        self.camera_layout.addWidget(self.photo_button)

        self.camera_layout.addWidget(self.camera_label_1)
        self.camera_layout.addWidget(self.camera_label_2)




        ###############################################################################################

        main_layout.addWidget(setting_groupbox, 0, 0, 1, 2)
        main_layout.addWidget(self.dev1_lamp_group, 1, 0, 1, 1) 
        main_layout.addWidget(self.dev2_sensor_BME280_group, 2, 0, 1, 1) 
        main_layout.addWidget(self.dev1_pump_dev2_sensor_flow_group, 3, 0, 1, 1)  
        main_layout.addWidget(self.dev2_sensor_humidity_gnd_group, 4, 0, 1, 1)  

        

        main_layout.addWidget(self.camera_group, 1, 1, 4, 1)
        # main_layout.addWidget(self.test_wire_group, 1, 1, 1, 1)  
        # main_layout.addWidget(self.edit_wire_group, 1, 2, 1, 1)  






if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())