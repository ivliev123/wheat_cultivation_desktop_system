from pymodbus.client import ModbusSerialClient
import serial.tools.list_ports


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
