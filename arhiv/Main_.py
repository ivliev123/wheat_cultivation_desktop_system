# import os
# import sys
# from PyQt5.QtCore import QLibraryInfo

# os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = os.path.join(
#     QLibraryInfo.location(QLibraryInfo.PluginsPath),
#     "platforms"
# )

import sys
import time
from PyQt5 import QtWidgets, QtCore
from pymodbus.client import ModbusSerialClient

# ================= CONFIG =================
PORT = "COM3"
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

REG_ADC_1 = 50
REG_FLOW_1 = 60

# ==========================================


class ModbusWorker(QtCore.QThread):
    data_updated = QtCore.pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.running = True

        self.client = ModbusSerialClient(
            framer="rtu",
            port=PORT,
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

                # Температура
                r = self.client.read_holding_registers(
                    REG_BME_280_1_Temperature, count=1, slave=SLAVE_BOARD_ID_2
                )
                if not r.isError():
                    data["temp"] = r.registers[0] * 0.01

                # Давление
                r = self.client.read_holding_registers(
                    REG_BME_280_1_Pressure, count=1, slave=SLAVE_BOARD_ID_2
                )
                if not r.isError():
                    data["pressure"] = r.registers[0] * 0.1

                # Влажность
                r = self.client.read_holding_registers(
                    REG_BME_280_1_Humidity, count=1, slave=SLAVE_BOARD_ID_2
                )
                if not r.isError():
                    data["humidity"] = r.registers[0] * 0.1

                # ADC
                r = self.client.read_holding_registers(
                    REG_ADC_1, count=4, slave=SLAVE_BOARD_ID_2
                )
                if not r.isError():
                    data["adc"] = r.registers

                # Flow
                r = self.client.read_holding_registers(
                    REG_FLOW_1, count=4, slave=SLAVE_BOARD_ID_2
                )
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


class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Modbus Control Panel")
        self.resize(400, 400)

        layout = QtWidgets.QVBoxLayout()

        # Датчики
        self.temp_label = QtWidgets.QLabel("Temp: -")
        self.press_label = QtWidgets.QLabel("Pressure: -")
        self.hum_label = QtWidgets.QLabel("Humidity: -")

        layout.addWidget(self.temp_label)
        layout.addWidget(self.press_label)
        layout.addWidget(self.hum_label)

        # ADC
        self.adc_label = QtWidgets.QLabel("ADC: -")
        layout.addWidget(self.adc_label)

        # Flow
        self.flow_label = QtWidgets.QLabel("Flow: -")
        layout.addWidget(self.flow_label)

        # Слайдеры каналов
        self.sliders = []
        for i in range(4):
            slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
            slider.setRange(0, 200)
            slider.valueChanged.connect(self.make_channel_handler(i))
            layout.addWidget(QtWidgets.QLabel(f"Channel {i+1}"))
            layout.addWidget(slider)
            self.sliders.append(slider)

        # Реле
        self.relays = []
        for i in range(4):
            btn = QtWidgets.QPushButton(f"Relay {i+1}")
            btn.setCheckable(True)
            btn.clicked.connect(self.make_relay_handler(i))
            layout.addWidget(btn)
            self.relays.append(btn)

        self.setLayout(layout)

        # Worker
        self.worker = ModbusWorker()
        self.worker.data_updated.connect(self.update_ui)
        self.worker.start()

    def make_channel_handler(self, index):
        def handler(value):
            reg = [REG_Channal_1, REG_Channal_2,
                   REG_Channal_3, REG_Channal_4][index]
            self.worker.set_channel(reg, value)
        return handler

    def make_relay_handler(self, index):
        def handler(checked):
            reg = [REG_Relay_1, REG_Relay_2,
                   REG_Relay_3, REG_Relay_4][index]
            self.worker.set_relay(reg, int(checked))
        return handler

    def update_ui(self, data):
        if "temp" in data:
            self.temp_label.setText(f"Temp: {data['temp']:.2f} °C")

        if "pressure" in data:
            self.press_label.setText(f"Pressure: {data['pressure']:.1f}")

        if "humidity" in data:
            self.hum_label.setText(f"Humidity: {data['humidity']:.1f}%")

        if "adc" in data:
            self.adc_label.setText(f"ADC: {data['adc']}")

        if "flow" in data:
            self.flow_label.setText(f"Flow: {data['flow']}")

    def closeEvent(self, event):
        self.worker.stop()
        self.worker.wait()
        event.accept()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())