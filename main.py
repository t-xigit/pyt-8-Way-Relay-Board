#!/usr/bin/env python3
"""
Module Docstring
"""

import serial
import time

__author__ = "Your Name"
__version__ = "0.1.0"
__license__ = "MIT"

""" Data Frame """
""" BYTE 0  - BYTE 1        - BYTE 2 - BYTE 3 """
""" Command - Board address - Data   - Check sum XOR BYTE 1 BYTE 2 BYTE 3 """

BOARD_ADDRESS = 1
FRAME_SIZE = 4
CMD = 0
ADDR = 1
DATA = 2
CRC = 3

NOP = {
  "name": "NOP",
  "cmd": 0,
  "resp": 255
}

SETUP = {
  "name": "SETUP",
  "cmd": 1,
  "resp": 254
}

GET_PORT = {
  "name": "GET_PORT",
  "cmd": 2,
  "resp": 253
}

SET_PORT = {
  "name": "GET_PORT",
  "cmd": 3,
  "resp": 252
}

GET_OPTION = {
  "name": "GET_PORT",
  "cmd": 4,
  "resp": 251
}

SET_OPTION = {
  "name": "SET_OPTION",
  "cmd": 5,
  "resp": 250
}

SET_SINGLE = {
  "name": "SET_SINGLE",
  "cmd": 6,
  "resp": 249
}

DEL_SINGLE = {
  "name": "DEL_SINGLE",
  "cmd": 7,
  "resp": 248
}

TOGGLE = {
  "name": "TOGGLE",
  "cmd": 8,
  "resp": 247
}

print("Opening Serial Port")
ser = serial.Serial('/dev/ttyUSB0')  # open serial port
ser.baudrate = 19200
ser.timeout = 5
ser.bytesize = 8
ser.stopbits = 1
ser.parity = 'N'
print(ser)         # check which port was really used

def get_crc(data):
    
    crc = 0
    for i in data:
        crc = crc ^ i
    print("CRC: ", crc)
    return crc

def get_data_frame(command, address, data):
    return 0

def send_command(command, address, data):
    
    print(command, address, data)
    cmd = [command["cmd"], address, data]
    crc = get_crc(cmd)
    cmd.append(crc)
    print("cmd: ", cmd)
    start_time = time.time()
    ser.write(cmd)     # write a string
    end_time = time.time()
    print("Execution time send:", end_time-start_time)
    start_time = time.time()
    response = ser.read(FRAME_SIZE)
    print("response: ", response)
    if response[CMD] == command["resp"]:
        print("cmd ok")
    else:
        print("response: ", response)
        raise RuntimeError("Command Response wrong")
    end_time = time.time()
    print("Execution time read:", end_time-start_time)

def get_data(command, address, data):
    cmd = [command["cmd"], address, data]
    crc = get_crc(cmd)
    cmd.append(crc)
    print("cmd: ", cmd)
    start_time = time.time()
    ser.write(cmd)     # write a string
    end_time = time.time()
    print("Execution time send:", end_time-start_time)
    start_time = time.time()
    response = ser.read(FRAME_SIZE*2)
    print("response: ", response)
    if response[CMD] == command["resp"]:
        print("cmd ok")
    else:
        print("response: ", response)
        raise RuntimeError("Command Response wrong")
    end_time = time.time()
    print("Execution time read:", end_time-start_time)
    return response[DATA]

def main():
    """ Main entry point of the app """
    fw_version = get_data(SETUP, BOARD_ADDRESS, BOARD_ADDRESS)
    print("FW_Version: ", fw_version)
    send_command(SET_OPTION, BOARD_ADDRESS, 2)
    send_command(NOP, BOARD_ADDRESS, 0)
    send_command(TOGGLE, BOARD_ADDRESS, 1)
    ser.close()             # close port

if __name__ == "__main__":
    """ This is executed when run from the command line """
    main()