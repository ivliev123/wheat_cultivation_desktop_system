# ================= CONFIG =================
# PORT = "COM3"
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

REG_BME_280_2_Temperature = 20
REG_BME_280_2_Pressure = 21
REG_BME_280_2_Humidity = 22

REG_ADC_1 = 50
REG_FLOW_1 = 60

# ==========================================


# ================= UI CONFIG =================

WINDOW_WIDTH  = 1040
WINDOW_HEIGHT = 900

GROUPBOX_MAX_WIDTH  = 500
GROUPBOX_MAX_HEIGHT = 250

CAMERA_WIDTH  = 640
CAMERA_HEIGHT = 360

SMALL_GROUP_WIDTH  = 400
SMALL_GROUP_HEIGHT = 220

MEDIUM_GROUP_WIDTH  = 600
MEDIUM_GROUP_HEIGHT = 250

LARGE_GROUP_WIDTH  = 800
LARGE_GROUP_HEIGHT = 500
# =============================================


# =============================================
CAM_PREVIEW_W = 640
CAM_PREVIEW_H = 360

CAM_CAPTURE_W = 2560
CAM_CAPTURE_H = 1440


CAM_ID_1 = 0
CAM_ID_2 = 2

PHOTO_FOLDER_1 = "Captures_cam_1"
PHOTO_FOLDER_2 = "Captures_cam_2"

CAMERA_CAPTURE_INTERVAL = 60 * 2

# =============================================


# Полив

# IRRIGATION_INTERVAL = 60 * 2       # раз в 2 минуты
IRRIGATION_INTERVAL = 60 * 60 * 24 * 2       # раз в 2 дня
IRRIGATION_DURATION = 41.4          # поливать 41.4 секунд

IRRIGATION_RELAY_1 = REG_Relay_3
IRRIGATION_RELAY_2 = REG_Relay_4

IRRIGATION_STATE_FILE = "irrigation_state.json"

# площадь контейнера 25 см. * 35 см.
# S = 875 * 10^-4 м2
# Оросительная норма на контейнер 
#  3000 м3/га  -->  26,25 л/контейнер за весь сезон

# Сезон полива 90 дней
# 26.25 / 90 = 0.2916666666666667 л/контейнер в день
# расходная характеристика насоса 1л за 71с
# в день насос должен работать 0.2916666666666667 * 71 = 20.708333333333336 секунд
# в 2 дня насос должен работать 41.41666666666667 секунд

