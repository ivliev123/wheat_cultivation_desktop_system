from pymodbus.client import ModbusSerialClient
import time

PORT = "COM5"
BAUDRATE = 115200
SLAVE_ID = 10

# Регистры каналов
REG_CH1 = 0
REG_CH2 = 1
REG_CH3 = 2
REG_CH4 = 3


client = ModbusSerialClient(
    framer="rtu",
    port=PORT,
    baudrate=BAUDRATE,
    stopbits=1,
    bytesize=8,
    parity="N",
    timeout=0.2
)

print("Connecting...")
if not client.connect():
    print("Connection failed")
    exit()

print("Connected")


# -------------------------------------------------
# ФУНКЦИИ
# -------------------------------------------------

def set_channel(channel, value):
    """Установить яркость одного канала (0-200)"""
    if not 0 <= value <= 200:
        raise ValueError("Value must be 0-200")

    register = channel - 1  # CH1=0, CH2=1 ...
    result = client.write_register(register, value, slave=SLAVE_ID)

    if result.isError():
        print("Write error:", result)
    else:
        print(f"Channel {channel} -> {value}")


def set_all_channels(ch1, ch2, ch3, ch4):
    """Установить сразу 4 канала"""
    values = [ch1, ch2, ch3, ch4]

    for v in values:
        if not 0 <= v <= 200:
            raise ValueError("Value must be 0-200")

    result = client.write_registers(0, values, slave=SLAVE_ID)

    if result.isError():
        print("Write error:", result)
    else:
        print("All channels set:", values)


def read_all():
    """Прочитать 4 канала"""
    result = client.read_holding_registers(0, count=4, slave=SLAVE_ID)

    if result.isError():
        print("Read error:", result)
        return None

    print("Current values:", result.registers)
    return result.registers


# -------------------------------------------------
# ТЕСТОВЫЙ ЦИКЛ
# -------------------------------------------------


# set_all_channels(0, 0, 0, 0)

values = [0, 0, 0, 100]
result = client.write_registers(0, values, slave=SLAVE_ID)
print(result)

result = client.read_holding_registers(0, count=4, slave=SLAVE_ID)
print(result)
print(result.registers)




result = client.read_holding_registers(20, count=3, slave=11)
print(result)
print(result.registers)



