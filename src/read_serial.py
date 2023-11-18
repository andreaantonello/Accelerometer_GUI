# Dr. Andrea Antonello, Dec 2020. For any question, write to andrea@automata.tech
import time
import serial
import serial.tools.list_ports

# List of VID/PID combinations: https://github.com/arduino/Arduino/blob/1.8.0/hardware/arduino/avr/boards.txt#L51-L58
ARDUINO_UNO_VID = [0x2341, 0x2341, 0x2A03, 0x2341]  # Arduino UNO vendor ID
ARDUINO_UNO_PID = [0x0043, 0x0001, 0x0043, 0x0243]  # Arduino UNO product ID
BAUD_RATE = 19200
STRING_LENGTH = 9  # Number of string items: Ax, Ay, Az, Gx, Gy, Gz, Mx, My, Mz
STRING_DELIMITER = ","


class ArduinoInterface:
    def __init__(self, port=None, baud=BAUD_RATE, timeout=1):
        self.arduino_vid = ARDUINO_UNO_VID
        self.arduino_pid = ARDUINO_UNO_PID
        if port is None:
            port = self.get_arduino_uno_port()
        self.serial = serial.Serial(port, baud, timeout=timeout)
        time.sleep(1)  # wait for serial to setup
        self.serial.reset_input_buffer()

    def verify_decoded_string(self, decoded_string):
        if decoded_string:
            split_string = decoded_string.split(STRING_DELIMITER)
            if len(split_string) == STRING_LENGTH:
                split_string = [float(item) for item in split_string]
                return split_string

    def decode_serial(self):
        raw_string = self.serial.readline()
        if raw_string:
            decoded_string = raw_string.strip().decode('utf-8')
            split_string = self.verify_decoded_string(decoded_string)
            return split_string

    def get_arduino_uno_port(self):
        ports = serial.tools.list_ports.comports()
        for p in ports:
            if p.vid in self.arduino_vid:
                if p.pid in self.arduino_pid:
                    print('found!')
                    return p.device
        raise RuntimeError('Could not find Arduino UNO. Check connection and try again.')
