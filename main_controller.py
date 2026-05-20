

from Controllers.camera_controller import CameraController
from Controllers.modbus_controller import ModbusController
# from Controllers.lamp_controller import LampController
# from Controllers.irrigation_controller import IrrigationController


class MainController():

    def __init__(self, window):

        self.window = window

        self.camera_controller = CameraController(self.window)
        self.modbus_controller = ModbusController(self.window)

        self.camera_controller.start_cameras() 
        self.modbus_controller.update_ports()
        
        self.connect_signals()

    def connect_signals(self):
        # camera_controller
        self.window.photo_button.clicked.connect(self.camera_controller.take_photo)

        # modbus_controller
        self.window.pump_1_pushbutton_ON.clicked.connect(lambda: self.modbus_controller.pump_pushbutton_function(1, 1))
        self.window.pump_1_pushbutton_OFF.clicked.connect(lambda: self.modbus_controller.pump_pushbutton_function(1, 0))
        self.window.pump_2_pushbutton_ON.clicked.connect(lambda: self.modbus_controller.pump_pushbutton_function(2, 1))
        self.window.pump_2_pushbutton_OFF.clicked.connect(lambda: self.modbus_controller.pump_pushbutton_function(2, 0))
        self.window.lamp_pushbutton.clicked.connect(self.modbus_controller.lamp_callback)

        self.window.update_button.clicked.connect(self.modbus_controller.update_ports)
        self.window.connect_button.clicked.connect(self.modbus_controller.toggle_connection)