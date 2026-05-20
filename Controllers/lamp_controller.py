
from workers_modbus_worker import ModbusWorker
from config import *

class LampController:

    def __init__(self, modbus_controller):
        self.modbus = modbus_controller

        self.current_channels = {
            "white": 0,
            "red": 0,
            "blue": 0,
            "farred": 0
        }



    def set_channels(self, white, red, blue, farred):

        values = [
            white,
            red,
            blue,
            farred
        ]

        self.modbus.worker.client.write_registers(
            REG_Channal_1,
            values,
            slave=SLAVE_BOARD_ID_1
        )

        self.current_channels = {
            "white": white,
            "red": red,
            "blue": blue,
            "farred": farred
        }

    def restore(self):
        self.set_channels(**self.current_channels)