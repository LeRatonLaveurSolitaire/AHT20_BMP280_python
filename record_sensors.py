from influxdb import InfluxDBClient
from datetime import datetime

from read_AHT20 import read_AHT20
from read_BMP280 import read_BMP280


INFLUXDB_HOST = "localhost"
INFLUXDB_PORT = 8086
INFLUXDB_DB = "sensor_data"


def main() -> None:

    client = InfluxDBClient(host=INFLUXDB_HOST, port=INFLUXDB_PORT)
    client.create_database(INFLUXDB_DB)
    client.switch_database(INFLUXDB_DB)

    temp_AHT20, humidity_AHT20 = read_AHT20()
    temp_BMP280, pressure_BMP280 = read_BMP280()

    if None not in [temp_AHT20, humidity_AHT20, temp_BMP280, pressure_BMP280]:

        json_body = [
            {
                "measurement": "room_environment",
                "time": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
                "fields": {
                    "temperature_AHT20": temp_AHT20,
                    "temperature_BMP280": temp_BMP280,
                    "pressure": pressure_BMP280,
                    "humidity": humidity_AHT20,
                },
            }
        ]

        client.write_points(json_body)


if __name__ == "__main__":
    main()
