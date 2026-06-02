# controllers_modbus_controller.py
from PyQt5.QtWidgets import  QMessageBox
from PyQt5 import QtCore
import os


from services_serial_manager import SerialManager
from workers_modbus_worker import ModbusWorker
from config import *

class ModbusController:

    def __init__(self, window, camera_controller, is_auto=False):
        self.window = window
        self.serial_manager = SerialManager()
        self.camera_controller = camera_controller

        self.worker = None
        
        # таймер проверки USB
        self.port_timer = QtCore.QTimer()
        self.port_timer.timeout.connect(self.auto_connect)
        self.port_timer.start(2000)

        # Подключаем сигналы смены режима
        self.window.manual_radio.toggled.connect(self.mode_changed)
        self.window.auto_radio.toggled.connect(self.mode_changed)
        
        # Флаг авто режима
        self.is_auto = is_auto

    def mode_changed(self, checked):
        # Вызывается при смене Manual ↔ Auto
        if self.worker is None:
            return
        
        if not checked:
            return
        
        if self.window.auto_radio.isChecked():
            self.worker.set_mode(True)
        else:
            self.worker.set_mode(False)
        
        
        
    
    def auto_connect(self):

        # уже подключены
        if self.worker is not None:
            return

        port = "/dev/ttyUSB0"
        # устройство не найдено
        if not os.path.exists(port):
            return

        print(f"Найден порт: {port}")

        try:
            self.serial_manager.connect(port)
            self.worker = ModbusWorker(port, self.camera_controller)
            self.worker.data_updated.connect(self.update_ui)
            self.worker.set_mode(self.is_auto)
            self.worker.start()
            self.window.connect_button.setText("Connected")
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
            
            if not port:
                return
            
            self.serial_manager.connect(port)

            self.worker = ModbusWorker(port, self.camera_controller)
            self.worker.data_updated.connect(self.update_ui)
            self.worker.set_mode(self.is_auto)
            self.worker.start()

            self.window.connect_button.setText("Disconnect")
        else:
            self.toggle_disconnect()

    def toggle_disconnect(self):
        self.serial_manager.disconnect()
        self.stop_worker()
        self.window.connect_button.setText("Connect")

    def stop_worker(self):
        if self.worker is not None and self.worker.isRunning():
            self.worker.stop()
            self.worker.quit()
            self.worker.wait()
            self.worker = None
            print("ModBus остановлен")

    def pump_pushbutton_function(self, pump_id, pump_status):
        # отправка через ModbusWorker
        if self.worker is not None and self.worker.isRunning():
            if pump_id == 1:
                REG = REG_Relay_3
            if pump_id == 2:
                REG = REG_Relay_4
            else:
                return
            
            self.worker.send_command(
                self.worker.client.write_register,
                REG,
                pump_status,
                slave=SLAVE_BOARD_ID_1
            )

        else:
            print("Worker not initialized or not running")


        print(f"Pump №{pump_id}: {pump_status}")


    def update_ui(self, data):
        # BME280 #1
        if 'sensor_BME280_1_temperature' in data:
            self.window.sensor_BME280_1_temperature_lineedit.setText(f"{data['sensor_BME280_1_temperature']:.2f}")
        if 'sensor_BME280_1_pressure' in data:
            self.window.sensor_BME280_1_pressure_lineedit.setText(f"{data['sensor_BME280_1_pressure']:.2f}")
        if 'sensor_BME280_1_humidity' in data:
            self.window.sensor_BME280_1_humidity_lineedit.setText(f"{data['sensor_BME280_1_humidity']:.2f}")

        # BME280 #2
        if 'sensor_BME280_2_temperature' in data:
            self.window.sensor_BME280_2_temperature_lineedit.setText(f"{data['sensor_BME280_2_temperature']:.2f}")
        if 'sensor_BME280_2_pressure' in data:
            self.window.sensor_BME280_2_pressure_lineedit.setText(f"{data['sensor_BME280_2_pressure']:.2f}")
        if 'sensor_BME280_2_humidity' in data:
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
            if self.worker is not None and self.worker.isRunning():
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


