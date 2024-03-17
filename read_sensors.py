from read_AHT20 import read_AHT20
from read_BMP280 import read_BMP280
import time

def main() -> None:

    temp_AHT20, humidity = read_AHT20()
    temp_BMP280, pressure = read_BMP280()
    print(f"T_AHT20 : {temp_AHT20:.2f} °C T_BMP280 : {temp_BMP280:.2f} °C P : {pressure/100:.1f} hPa Hmd : {humidity:.2f}%")
    time.sleep(0.5)
    
if __name__ =="__main__":
    while True:
        main()