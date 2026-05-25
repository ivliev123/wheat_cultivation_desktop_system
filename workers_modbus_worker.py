from PyQt5 import QtCore
from pymodbus.client import ModbusSerialClient
import time

from Controllers.camera_controller import CameraController
from config import *

# Сценарий скорей всего прийдется писать здесь


class ModbusWorker(QtCore.QThread):
    data_updated = QtCore.pyqtSignal(dict)

    def __init__(self, port, camera_controller):
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

        # camera_controller
        self.camera_controller = camera_controller

        self.last_camera_capture = time.time()

        # irrigaetion_controller_calback
        # irrigation
        self.irrigation_running = False
        self.irrigation_start_time = 0

        # self.last_irrigation_time = self.load_last_irrigation_time()


        # lamp_controller
        self.flag_lamp_controller_callback = 1
        self.flag_camera_controller_callback = 0
        # sensor_controller


        # test
        self.test_time = time.time()

    def run(self):
        self.client.connect()

        while self.running:
            
            self.sensor_controller_callback()
            # self.lamp_controller_callback()
            # self.irrigation_controller_callback()
            # self.camera_controller_callback()

            time.sleep(0.5)




    # sensor_controller
    def sensor_controller_callback(self):

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

    def stop(self):
        self.running = False
        self.client.close()

    # Управление каналами
    def set_channel(self, reg, value):
        self.client.write_registers(reg, [value], slave=SLAVE_BOARD_ID_1)

    def set_relay(self, reg, value):
        self.client.write_registers(reg, [value], slave=SLAVE_BOARD_ID_1)




    ###############################################################################
    def lamp_controller_callback(self):
        if self.flag_lamp_controller_callback:
            d_time = time.time() - self.test_time

            red = 0
            blue = int(d_time*10 % 200)
            farred = 0
            white = int(d_time*10 % 200)

            self.set_channels(red, blue, farred, white)


    def set_channels(self, red, blue, farred, white):
        values = [red, blue, farred, white]

        self.client.write_registers(REG_Channal_1, values, slave=SLAVE_BOARD_ID_1)

        print(values)

        # бужу использовать позже для обновления состояния в line edit
        # self.current_channels = {
        #     "white": white,
        #     "red": red,
        #     "blue": blue,
        #     "farred": farred
        # }
    



    ###############################################################################
    def irrigation_controller_callback(self):

        current_time = time.time()

        # =========================
        # Запуск полива
        # =========================

        if not self.irrigation_running:

            if current_time - self.last_irrigation_time >= IRRIGATION_INTERVAL:

                print("START IRRIGATION")

                self.irrigation_running = True
                self.irrigation_start_time = current_time

                # включаем реле
                self.set_relay(IRRIGATION_RELAY, 1)

        # =========================
        # Остановка полива
        # =========================

        else:

            if current_time - self.irrigation_start_time >= IRRIGATION_DURATION:

                print("STOP IRRIGATION")

                self.set_relay(IRRIGATION_RELAY, 0)

                self.irrigation_running = False

                self.last_irrigation_time = current_time

                self.save_last_irrigation_time(current_time)







    ############################################################################################
    # camera_controller_callback тут будем вызывать из нег офункции чтоб сделать фото
    def camera_controller_callback(self):

        current_time = time.time()

        if (current_time - self.last_camera_capture >= CAMERA_CAPTURE_INTERVAL):
            self.last_camera_capture = current_time
            self.flag_lamp_controller_callback = 0
            time.sleep(0.5)     # нужно для того чтоб лампа перешла в режим ожидания команды
            self.set_channels(0, 0, 0, 50)
            # r = self.client.read_holding_registers(REG_Channal_1, count=4, slave=SLAVE_BOARD_ID_1)
            # print(r)
            # print(r.registers)
            self.flag_camera_controller_callback = 1


        if self.flag_camera_controller_callback == 1:
            time.sleep(10)
            self.camera_controller.take_photo()
            time.sleep(1)
            self.flag_lamp_controller_callback = 1