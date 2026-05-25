# controllers_modbus_controller.py
from PyQt5.QtWidgets import  QMessageBox
from PyQt5 import QtCore
import os


from services_serial_manager import SerialManager
from workers_modbus_worker import ModbusWorker
from config import *

class ModbusController:

    def __init__(self, window, camera_controller):
        self.window = window
        self.serial_manager = SerialManager()
        self.camera_controller = camera_controller

        self.worker = None
        # таймер проверки USB
        self.port_timer = QtCore.QTimer()
        self.port_timer.timeout.connect(
            self.auto_connect
        )
        self.port_timer.start(2000)



    def auto_connect(self):

        # уже подключены
        if self.worker is not None:
            return

        port = "/dev/ttyUSB0"
        # устройство не найдено
        if not os.path.exists(port):
            return

        print(f"Found {port}")

        try:
            self.serial_manager.connect(port)
            self.worker = ModbusWorker(port, self.camera_controller)
            self.worker.data_updated.connect(
                self.update_ui
            )
            self.worker.start()
            self.window.connect_button.setText(
                "Connected"
            )

            print("Modbus connected")

        except Exception as e:

            print("Connect error:", e)



    def update_ports(self):
        self.window.port_combo.clear()
        ports = self.serial_manager.get_available_ports()
        self.window.port_combo.addItems(ports)

    
    def toggle_connection(self):
        if not self.serial_manager.connected:
            port = self.window.port_combo.currentText()
            self.serial_manager.connect(port)

            self.worker = ModbusWorker(port)
            self.worker.data_updated.connect(self.update_ui)
            self.worker.start()

            self.window.connect_button.setText("Disconnect")
        else:
            self.serial_manager.disconnect()

            if hasattr(self, "worker"):
                self.worker.stop()
                self.worker.wait()

            self.window.connect_button.setText("Connect")




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
        self.window.sensor_BME280_1_temperature_lineedit.setText(f"{data['sensor_BME280_1_temperature']:.2f}")
        self.window.sensor_BME280_1_pressure_lineedit.setText(f"{data['sensor_BME280_1_pressure']:.2f}")
        self.window.sensor_BME280_1_humidity_lineedit.setText(f"{data['sensor_BME280_1_humidity']:.2f}")

        self.window.sensor_BME280_2_temperature_lineedit.setText(f"{data['sensor_BME280_2_temperature']:.2f}")
        self.window.sensor_BME280_2_pressure_lineedit.setText(f"{data['sensor_BME280_2_pressure']:.2f}")
        self.window.sensor_BME280_2_humidity_lineedit.setText(f"{data['sensor_BME280_2_humidity']:.2f}")

        # ADC (влажность почвы)
        if "adc" in data:
            for i, value in enumerate(data["adc"]):
                if i < len(self.window.sensor_widgets):
                    self.window.sensor_widgets[i][1].setText(str(value))

        # Flow
        if "flow" in data:
            if len(data["flow"]) > 0:
                self.window.flow_sensor_1_lineedit.setText(str(data["flow"][0]))
            if len(data["flow"]) > 1:
                self.window.flow_sensor_2_lineedit.setText(str(data["flow"][1]))

                

    def lamp_callback(self):
        values = []

        try:
            for i, le in enumerate(self.window.channel_widgets):
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
            QMessageBox.warning(self.window, "Input error", str(e))


