import smbus2 as smbus
import time

# AHT20 Registers
AHT20_ADDRESS = 0x38

AHT20_CMD_SOFTRST = 0xBA

AHT20_CMD_INIT_REG = 0xBE
AHT20_CMD_INIT_DAT = [0x08, 0x00]

AHT20_CMD_STAT_REG = 0x71

AHT20_CMD_MEASURE_REG = 0xAC
AHT20_CMD_MEASURE_DAT = [0x33, 0x00]


def read_AHT20() -> tuple:
    """Reads temperature and humidity from the AHT20 sensor.

    Returns:
        A tuple containing the temperature (in Celsius) and humidity (in percentage).
    """
    try:
        with smbus.SMBus(1) as bus:

            # Soft reset the sensor
            bus.write_byte(AHT20_ADDRESS, AHT20_CMD_SOFTRST)

            time.sleep(0.04)

            # Read sensor status to verify calibreation
            status = bus.read_i2c_block_data(AHT20_ADDRESS, AHT20_CMD_STAT_REG, 1)

            # Send init / calibration command until calibrated
            while status[0] != 0x18:
                bus.write_i2c_block_data(
                    AHT20_ADDRESS, AHT20_CMD_INIT_REG, AHT20_CMD_INIT_DAT
                )
                time.sleep(0.05)
                status = bus.read_i2c_block_data(AHT20_ADDRESS, AHT20_CMD_STAT_REG, 1)

            time.sleep(0.05)

            # Send data read command
            bus.write_i2c_block_data(
                AHT20_ADDRESS, AHT20_CMD_MEASURE_REG, AHT20_CMD_MEASURE_DAT
            )

            time.sleep(0.08)

            # Read received data
            data = bus.read_i2c_block_data(AHT20_ADDRESS, 0x0, 7)

        # Compute temp and humidity values, no CRC check
        temperature_raw = ((data[3] & 0xF) << 16) | (data[4] << 8) | data[5]
        humidity_raw = (data[1] << 12) | (data[2] << 4) | (data[3] >> 4)
        temperature = temperature_raw / (2**20) * 200 - 50
        humidity = humidity_raw / (2**20) * 100

        return temperature, humidity

    except OSError:
        return None, None


if __name__ == "__main__":

    while True:

        temperature_AHT20, humidity_AHT20 = read_AHT20()
        print(
            f"AHT20 Humi : {humidity_AHT20:.2f} %, AHT20 Temp : {temperature_AHT20:.2f} °C"
        )
        time.sleep(1)
