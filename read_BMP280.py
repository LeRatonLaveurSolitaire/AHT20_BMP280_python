import smbus2 as smbus
import time

# BMP280 Registers
BMP280_ADDRESS = 0x77

BMP280_REG_TEMP_XLSB = 0xFC
BMP280_REG_TEMP_LSB = 0xFB
BMP280_REG_TEMP_MSB = 0xFA

BMP280_REG_PRES_XLSB = 0xF9
BMP280_REG_PRES_LSB = 0xF8
BMP280_REG_PRES_MSB = 0xF7

BMP280_REG_CONFIG = 0xF5
BMP280_REG_CTRL = 0xF4
BMP280_REG_STAT = 0xF3
BMP280_REG_RESET = 0xE0

BMP280_REG_ID = 0xD0


def read_BMP280() -> tuple:
    """Read the temperature and pressure froma BMP280 sensor.

    Returns:
        tuple: (float) temperature in °C, (float) pressure in Pa
    """

    try:
        with smbus.SMBus(1) as bus:
            bus.write_byte_data(BMP280_ADDRESS, BMP280_REG_CTRL, 0xB6)

            time.sleep(0.05)

            # Read calibration data
            bmp280_calib = {}

            bmp280_calib["dig_T1"] = bus.read_word_data(BMP280_ADDRESS, 0x88)
            bmp280_calib["dig_T2"] = bus.read_word_data(BMP280_ADDRESS, 0x8A)
            bmp280_calib["dig_T3"] = bus.read_word_data(BMP280_ADDRESS, 0x8C)
            bmp280_calib["dig_P1"] = bus.read_word_data(BMP280_ADDRESS, 0x8E)
            bmp280_calib["dig_P2"] = bus.read_word_data(BMP280_ADDRESS, 0x90)
            bmp280_calib["dig_P3"] = bus.read_word_data(BMP280_ADDRESS, 0x92)
            bmp280_calib["dig_P4"] = bus.read_word_data(BMP280_ADDRESS, 0x94)
            bmp280_calib["dig_P5"] = bus.read_word_data(BMP280_ADDRESS, 0x96)
            bmp280_calib["dig_P6"] = bus.read_word_data(BMP280_ADDRESS, 0x98)
            bmp280_calib["dig_P7"] = bus.read_word_data(BMP280_ADDRESS, 0x9A)
            bmp280_calib["dig_P8"] = bus.read_word_data(BMP280_ADDRESS, 0x9C)
            bmp280_calib["dig_P9"] = bus.read_word_data(BMP280_ADDRESS, 0x9E)

            for name, value in bmp280_calib.items():
                if (type(value) == int) and (name not in ["dig_P1", "dig_T1"]):
                    if value > 32767:
                        value -= 65536
                bmp280_calib[name] = value

            # Read raw temperature data
            rawData = bus.read_i2c_block_data(BMP280_ADDRESS, BMP280_REG_TEMP_MSB, 3)
            adc_T = (rawData[0] << 16 | rawData[1] << 8 | rawData[2]) >> 4

            # Convert raw temperature data to Celsius
            var1 = (
                (((adc_T >> 3) - (bmp280_calib["dig_T1"] << 1)))
                * bmp280_calib["dig_T2"]
            ) >> 11
            var2 = (
                (
                    (
                        ((adc_T >> 4) - bmp280_calib["dig_T1"])
                        * ((adc_T >> 4) - bmp280_calib["dig_T1"])
                    )
                    >> 12
                )
                * bmp280_calib["dig_T3"]
            ) >> 14
            t_fine = var1 + var2
            temperature = float((t_fine * 5 + 128) >> 8) / 100

            # Read raw pressure data
            rawData = bus.read_i2c_block_data(BMP280_ADDRESS, BMP280_REG_PRES_MSB, 3)
            adc_P = (rawData[0] << 16 | rawData[1] << 8 | rawData[2]) >> 4

            # Convert raw pressure data to Pascals
            var1 = t_fine - 128000
            var2 = var1 * var1 * bmp280_calib["dig_P6"]
            var2 = var2 + ((var1 * bmp280_calib["dig_P5"]) << 17)
            var2 = var2 + (bmp280_calib["dig_P4"] << 35)
            var1 = ((var1 * var1 * bmp280_calib["dig_P3"]) >> 8) + (
                (var1 * bmp280_calib["dig_P2"]) << 12
            )
            var1 = (((1 << 47) + var1) * bmp280_calib["dig_P1"]) >> 33
            if var1 == 0:
                return 0
            p = 1048576 - adc_P
            p = (((p << 31) - var2) * 3125) // var1
            var1 = (bmp280_calib["dig_P9"] * (p >> 13) * (p >> 13)) >> 25
            var2 = (bmp280_calib["dig_P8"] * p) >> 19
            pressure = ((p + var1 + var2) >> 8) + (bmp280_calib["dig_P7"] << 4)

        return temperature, pressure / 256

    except OSError:
        return None, None


if __name__ == "__main__":

    while True:

        temp, pressure = read_BMP280()
        print(
            "Temperature: {:.2f} C, Pressure: {:.2f} hPa".format(temp, pressure / 100)
        )
        time.sleep(1)
