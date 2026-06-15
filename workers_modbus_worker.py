from PyQt5 import QtCore
from pymodbus.client import ModbusSerialClient
import time
from datetime import datetime
import json
import os
import csv



# from Controllers.camera_controller import CameraController
from config import *
import queue


# Сценарий скорей всего прийдется писать здесь


class ModbusWorker(QtCore.QThread):
    data_updated = QtCore.pyqtSignal(dict)

    def __init__(self, port, camera_controller, window):
        super().__init__()
        self.running = True
        self.command_queue = queue.Queue()

        self.client = ModbusSerialClient(
            framer="rtu",
            port=port,
            baudrate=BAUDRATE,
            stopbits=1,
            bytesize=8,
            parity="N",
            timeout=0.2
        )

        self.window = window
        
        # camera_controller
        self.camera_controller = camera_controller
        self.last_camera_capture = time.time()

        # irrigation
        self.irrigation_running = False
        self.irrigation_start_time = 0
        self.last_irrigation_time = self.load_last_irrigation_time()

        # lamp_controller
        self.flag_lamp_controller_callback = 1
        self.flag_irrigation_controller_callback = 1
        self.is_auto = 1

        # sensor_controller
        

        self.last_processed_hour = None


    def run(self):
        self.client.connect()

        while self.running:
            while not self.command_queue.empty():
                try:
                    func, args, kwargs = self.command_queue.get_nowait()
                    self.sensor_controller_callback()
                    
                    time.sleep(0.1)
                except Exception as e:
                    print(f"Ошибка обработки UI: {e}")
            
            self.sensor_controller_callback()

            # тут нужно будет ввести машину состояния, так как должно выполниться полностью одно перед тем кк начнется другой,
            # критично для полива, полив может не завершиться и начнет работать камера, и лить будет долго
            if self.is_auto:
                self.lamp_controller_callback()
                self.irrigation_controller_callback()
                
                if self.flag_irrigation_controller_callback == 1:
                    self.camera_controller_callback() # тут реализовано на задержках поэтому делаем через состояние полива

            time.sleep(0.1)

        self.client.close()

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

    def set_mode(self, is_auto):
        self.is_auto = is_auto
        # print("Режим поменялся")
        print(f"Режим изменён → {'Авто' if self.is_auto else 'Ручной'}")
        # Создаём счётчик последнего часа
        if self.is_auto:
            self.set_spectrum_for_lamp()
        
        time.sleep(0.1)
    
    def lamp_controller_callback(self):
        if not self.is_auto:
            return
        
        local_time = datetime.now()
        
        print(local_time.hour, self.last_processed_hour)
        
        if (local_time.hour != self.last_processed_hour or self.last_processed_hour == -1) and self.flag_lamp_controller_callback == 1:
            self.last_processed_hour = local_time.hour
            self.set_spectrum_for_lamp()
            
            
    def set_spectrum_for_lamp(self):
        print(0)
        local_time = datetime.now()
        rounded_time = local_time.replace(minute=0, second=0, microsecond=0)
        standart_time = rounded_time.strftime("%Y-%m-%d %H:%M:%S+03:00")
        
        with open("/home/lab1/imitation_of_natural_light/optimum_spectrum_results.json", "r", encoding="utf-8") as f:
            data = json.load(f)[standart_time]
            
            red     = int(max(0, min(200, data[0])))
            blue    = int(max(0, min(200, data[1])))
            farred  = int(max(0, min(200, data[2])))
            white   = int(max(0, min(200, data[3])))
            
            self.set_channels(red, blue, farred, white)
            print(f"[{local_time.strftime('%H:%M')}] Автообновление спектра: R{red} B{blue} FR{farred} W{white}")

    # запись данных в БД...

    def set_channels(self, red, blue, farred, white):
        values = [red, blue, farred, white]

        self.client.write_registers(REG_Channal_1, values, slave=SLAVE_BOARD_ID_1)

        print(values)
        # обновление состояния в line edit
        for i, value in enumerate(values):
            self.window.channel_widgets[i].setText(str(value))



    ###############################################################################
    def irrigation_controller_callback(self):

        current_time = time.time()

        # =========================
        # Запуск полива
        # =========================
        if not self.irrigation_running:

            if current_time - self.last_irrigation_time >= IRRIGATION_INTERVAL:
                self.flag_irrigation_controller_callback = 0
                print("START IRRIGATION")

                self.irrigation_running = True
                self.irrigation_start_time = current_time

                # включаем реле
                self.set_relay(IRRIGATION_RELAY_1, 1)
                self.set_relay(IRRIGATION_RELAY_2, 1)

        # =========================
        # Остановка полива
        # =========================
        else:

            if current_time - self.irrigation_start_time >= IRRIGATION_DURATION:

                print("STOP IRRIGATION")

                self.set_relay(IRRIGATION_RELAY_1, 0)
                self.set_relay(IRRIGATION_RELAY_2, 0)
                self.irrigation_running = False

                self.last_irrigation_time = current_time

                self.save_last_irrigation_time(current_time)

                self.flag_irrigation_controller_callback = 1



    def save_last_irrigation_time(self, timestamp):

        data = {
            "last_irrigation_time": timestamp
        }

        with open(IRRIGATION_STATE_FILE, "w") as f:
            json.dump(data, f)

            

    def load_last_irrigation_time(self):

        if not os.path.exists(IRRIGATION_STATE_FILE):
            return 0

        try:
            with open(IRRIGATION_STATE_FILE, "r") as f:
                data = json.load(f)

            return data.get("last_irrigation_time", 0)

        except:
            return 0
            


    ############################################################################################
    # camera_controller_callback тут будем вызывать из него офункции чтоб сделать фото
    def camera_controller_callback(self):

        current_time = time.time()

        if (current_time - self.last_camera_capture >= CAMERA_CAPTURE_INTERVAL):
            self.last_camera_capture = current_time
            self.flag_lamp_controller_callback = 0
            time.sleep(0.5)     # нужно для того чтоб лампа перешла в режим ожидания команды
            self.set_channels(0, 0, 0, 50)

            time.sleep(5)
            self.camera_controller.take_photo()
            time.sleep(1)
            self.flag_lamp_controller_callback = 1

            # вернуть рабочий спектр
            if self.is_auto:
                self.set_spectrum_for_lamp()