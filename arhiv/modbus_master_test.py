# pymodbus 3.11.3
# from pymodbus.constants import Endian
# from pymodbus.payload import BinaryPayloadDecoder
# from pymodbus.payload import BinaryPayloadBuilder
# from pymodbus.client.sync import ModbusSerialClient

# pymodbus            3.8.6
from pymodbus.client import ModbusSerialClient
import time
import struct

# client = ModbusSerialClient(framer="rtu", port="COM6", stopbits=1, bytesize=8, parity="N", baudrate=115200, timeout=0.2)
client = ModbusSerialClient(framer="rtu", port="COM6", stopbits=1, bytesize=8, parity="N", baudrate=115200, timeout=0.2)

print(client)

connection = client.connect()
connect_status = client.connect()
print("Connect_status", connect_status)

SLAVE_BOARD_ID_1 = 10   #Управление лампами и реле (насосы)
# SLAVE_BOARD_ID_2 = 11   #Сбор данных с датчиков


# # SLAVE_BOARD_ID_1 REG_CONFIG
# REG_Channal_1 = 0       #Red    [0 200]
# REG_Channal_2 = 1       #Blue   [0 200]
# REG_Channal_3 = 2       #Red2   [0 200]
# REG_Channal_4 = 3       #White  [0 200]

# REG_Relay_1 = 10        #Relay_1    [0 1]
# REG_Relay_2 = 11        #Relay_2    [0 1]
# REG_Relay_3 = 12        #Relay_3    [0 1]   Насос 1
# REG_Relay_4 = 13        #Relay_4    [0 1]   насос 2


# # SLAVE_BOARD_ID_2 REG_CONFIG
# REG_BME_280_1_Temperature = 10    # * 100 Значение необходимо делить на указанный множитель 
# REG_BME_280_1_Pressure    = 11    # * 10
# REG_BME_280_1_Humidity    = 12    # * 10

# REG_BME_280_2_Temperature = 20    # * 100 Значение необходимо делить на указанный множитель 
# REG_BME_280_2_Pressure    = 21    # * 10
# REG_BME_280_2_Humidity    = 22    # * 10

# REG_ADC_1  = 50     # Регистры аналоговых входов (Датчики влажности почвы)
# REG_ADC_2  = 51
# REG_ADC_3  = 52
# REG_ADC_4  = 53
# REG_ADC_5  = 54
# REG_ADC_6  = 55
# REG_ADC_7  = 56
# REG_ADC_8  = 57
# REG_ADC_9  = 58
# REG_ADC_10 = 59

# REG_FLOW_1 = 60
# REG_FLOW_2 = 61
# REG_FLOW_3 = 62
# REG_FLOW_4 = 63


# # SLAVE_BOARD_ID_2
# write_result = client.write_registers(REG_Channal_1, [0],  slave=SLAVE_BOARD_ID_1)
# write_result = client.write_registers(REG_Channal_2, [0],  slave=SLAVE_BOARD_ID_1)
# write_result = client.write_registers(REG_Channal_3, [100],  slave=SLAVE_BOARD_ID_1)
# write_result = client.write_registers(REG_Channal_4, [10],  slave=SLAVE_BOARD_ID_1)


# write_result = client.write_registers(REG_Relay_1, [0],  slave=SLAVE_BOARD_ID_1)
# write_result = client.write_registers(REG_Relay_2, [0],  slave=SLAVE_BOARD_ID_1)
# write_result = client.write_registers(REG_Relay_3, [0],  slave=SLAVE_BOARD_ID_1)
# write_result = client.write_registers(REG_Relay_4, [0],  slave=SLAVE_BOARD_ID_1)

# print(write_result)


# # result = client.read_holding_registers(0, count=1,  slave=10)
# # print(result)
# # regs_l = result.registers
# # print(regs_l)


# # SLAVE_BOARD_ID_2
# # BME_280_1
# result = client.read_holding_registers(REG_BME_280_1_Temperature, count=1,  slave=SLAVE_BOARD_ID_2)
# regs_l = result.registers
# print(regs_l[0] * 0.01)
# result = client.read_holding_registers(REG_BME_280_1_Pressure, count=1,  slave=SLAVE_BOARD_ID_2)
# regs_l = result.registers
# print(regs_l[0] * 0.1)
# result = client.read_holding_registers(REG_BME_280_1_Humidity, count=1,  slave=SLAVE_BOARD_ID_2)
# regs_l = result.registers
# print(regs_l[0] * 0.1)

# print()

# # BME_280_2
# result = client.read_holding_registers(REG_BME_280_2_Temperature, count=1,  slave=SLAVE_BOARD_ID_2)
# regs_l = result.registers
# print(regs_l)
# result = client.read_holding_registers(REG_BME_280_2_Pressure, count=1,  slave=SLAVE_BOARD_ID_2)
# regs_l = result.registers
# print(regs_l)
# result = client.read_holding_registers(REG_BME_280_2_Humidity, count=1,  slave=SLAVE_BOARD_ID_2)
# regs_l = result.registers
# print(regs_l)

# # ADC data from sensors
# result = client.read_holding_registers(REG_ADC_1, count=10,  slave=SLAVE_BOARD_ID_2)
# regs_l = result.registers
# print(regs_l)


while(1):
    print()

    result = client.read_holding_registers(1, count=4,  slave=SLAVE_BOARD_ID_1)
    print(result)
    regs_l = result.registers
    print(regs_l)

    time.sleep(0.2)
