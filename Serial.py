import minimalmodbus
import time
import logging
from datetime import datetime

DETECTION_REGISTER = 0x06
STOP_DETECTION = 0x00
START_DETECTION = 0x01

PORT = "/dev/ttyUSB1"
class SerialComm():
    def __init__(self):
        self.instrument = minimalmodbus.Instrument(PORT, 0xFE, mode=minimalmodbus.MODE_RTU, debug=True)  # Replace with your RS232 port and slave address
        self.input_registers = {
            "0.3Hi": 0x03,
            "0.3Lo": 0x04,
            "0.5Hi": 0x05,
            "0.5Lo": 0x06,
            "0.7Hi": 0x07,
            "0.7Lo": 0x08,
            "1.0Hi": 0x09,
            "1.0Lo": 0x0A,
            "2.5Hi": 0x0B,
            "2.5Lo": 0x0C,
            "5.0Hi": 0x0D,
            "5.0Lo": 0x0E,
            "10Hi": 0x0F,
            "10Lo": 0x10
        }
        self.holding_registers = {
            "Sample_Unit": 0x04, #0x00 TC 0x01 CF 0x02 L
            "Sample Time": 0x05,
            "Start/Stop Detection": 0x06, #stop 0x00 start 0x01
            "Year": 0x64,
            "Month": 0x65,
            "Day": 0x66,
            "Hour": 0x67,
            "Minute": 0x68,
            "Second": 0x69
        }
        self.sensor_values = {
            "0.3Hi": None,
            "0.3Lo": None,
            "0.5Hi": None,
            "0.5Lo": None,
            "0.7Hi": None,
            "0.7Lo": None,
            "1.0Hi": None,
            "1.0Lo": None,
            "2.5Hi": None,
            "2.5Lo": None,
            "5.0Hi": None,
            "5.0Lo": None,
            "10Hi": None,
            "10Lo": None
        }
        self.sensor_values.keys()
        self.instrument.serial.baudrate = 9600
        self.instrument.serial.timeout  = 5
        self.logger = logging.getLogger(__name__)
        start_time = time.strftime("%Y%m%d_%H%M%S")
        logging.basicConfig(filename=f"Logs/sensor_values_{start_time}.log", level=logging.INFO)
        self.logger.info("Start of Log File")

    def readInputReg(self, Register):
        return self.instrument.read_register(Register, functioncode=4) 
    
    def readSensorValue(self, value):
        try:
            out = self.readInputReg(self.input_registers[value])
            self.logger.info(f"Read sensor value: {value}, Received: {out}")
        except Exception as e:
            self.logger.error(e)
        return out
    
    def readHoldingReg(self, Register):
        try:
            out = self.instrument.read_register(Register, functioncode=3)
            self.logger.info(f"Read HoldingRegister: {Register}, Received: {out}")
        except Exception as e:
            self.logger.error(e)
        return out
    
    def startDetection(self):
        self.logger.info("Starting Particle Detection")
        try:
            self.instrument.write_register(DETECTION_REGISTER, START_DETECTION, functioncode = 6)
        except Exception as e:
            self.logger.error(e)

    def stopDetection(self):
        self.logger.info("Ending Particle Detection")
        try:
            self.instrument.write_register(DETECTION_REGISTER, STOP_DETECTION, functioncode = 6)
        except Exception as e:
            self.logger.error(e)

    def readSensorValues(self):
        return self.instrument.read_registers(self.input_registers["0.3Hi"], 14, functioncode=4)
    
    def storeSensorValues(self):
        #Values = self.readSensorValues()
        Values = [i for i in range(14)]
        Keys = list(self.sensor_values.keys())
        for i in range(14):
            self.sensor_values[Keys[i]] = Values[i]
        now = datetime.now()
        self.logger.info(f"Time: {now.time()}, Values: {Values}")



    
if __name__ == "__main__":
    comm = SerialComm();
    comm.startDetection()
    time.sleep(45)
    while True:
        try:
            comm.storeSensorValues()
            time.sleep(30)
        except Exception as e:
            comm.logger.error(e)
            comm.stopDetection()

        