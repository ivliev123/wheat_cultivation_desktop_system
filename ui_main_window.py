from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QGroupBox, QLabel, 
    QGridLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QVBoxLayout, QHBoxLayout, 
    QSizePolicy, QLineEdit, QComboBox,
    QRadioButton, QButtonGroup
)
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtGui import QPixmap, QColor, QIcon, QFont


from controllers_camera_controller import CameraController
from controllers_modbus_controller import ModbusController
from config import *


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()


        self.init_ui()
        self.camera_controller = CameraController(self)
        self.modbus_controller = ModbusController(self)

        self.camera_controller.start_cameras() 
        self.modbus_controller.update_ports()
        
        self.connect_signals()

    def connect_signals(self):
        # camera_controller
        self.photo_button.clicked.connect(self.camera_controller.take_photo)

        # modbus_controller
        self.pump_1_pushbutton_ON.clicked.connect(lambda: self.modbus_controller.pump_pushbutton_function(1, 1))
        self.pump_1_pushbutton_OFF.clicked.connect(lambda: self.modbus_controller.pump_pushbutton_function(1, 0))
        self.pump_2_pushbutton_ON.clicked.connect(lambda: self.modbus_controller.pump_pushbutton_function(2, 1))
        self.pump_2_pushbutton_OFF.clicked.connect(lambda: self.modbus_controller.pump_pushbutton_function(2, 0))
        self.lamp_pushbutton.clicked.connect(self.modbus_controller.lamp_callback)

        self.update_button.clicked.connect(self.modbus_controller.update_ports)
        self.connect_button.clicked.connect(self.modbus_controller.toggle_connection)

        
    def init_ui(self):

        self.setWindowTitle("Modbus Control Panel")
        self.resize(WINDOW_WIDTH, WINDOW_HEIGHT)
        # self.showMaximized()  # Развернуть на весь экран (с панелью задач)

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QGridLayout(main_widget)


        # ===== Панель подключения =====
        ##############################
        setting_groupbox = QGroupBox("")
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

