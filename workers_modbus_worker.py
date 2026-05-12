from PyQt5 import QtCore
from pymodbus.client import ModbusSerialClient
import time

from config import *

# Сценарий скорей всего прийдется писать здесь


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
