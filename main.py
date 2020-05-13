#!/usr/bin/env python3
"""
Module Docstring
"""

import serial
import time
import logging

__author__ = "Timur Yigit"
__version__ = "0.1.0"
__license__ = "MIT"

""" Data Frame """
""" BYTE 0  - BYTE 1        - BYTE 2 - BYTE 3 """
""" Command - Board address - Data   - Check sum XOR BYTE 1 BYTE 2 BYTE 3 """

logging.basicConfig(level=logging.DEBUG)

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

logging.info("Opening Serial Port")
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
    logging.debug("Calculated CRC: %d", crc)
    return crc

def get_data_frame(command, address, data):
    return 0

""" Checks if the return code and CRC are OK"""
def check_response(command, response):
    
    resp = response[0:3]
    rx_crc = response[CRC]
    crc = get_crc(resp)

    if rx_crc == crc:
      logging.debug("Received CRC OK")
    else:
      raise RuntimeError("Received CRC wrong, received: %d, expected: %d", rx_crc, crc)

    if response[CMD] == command["resp"]:
        logging.debug("Response code OK")
    else:
        print("response: ", response)
        raise RuntimeError("Response code wrong, received: %d, expected: %d", response[CMD], command["resp"])

def send_command(command, address, data):
    
    logging.info("Sending: %s", command["name"])
    cmd = [command["cmd"], address, data]
    crc = get_crc(cmd)
    cmd.append(crc)
    start_time = time.time()
    ser.write(cmd)     # write a string
    end_time = time.time()
    logging.debug("Execution time send: %f", end_time-start_time)
    start_time = time.time()
    response = ser.read(FRAME_SIZE)
    end_time = time.time()
    logging.debug("Execution time read: %f", end_time-start_time)
    logging.debug("Received response: %s", response)
    #This will cause an exeption if received package is wrong
    check_response(command, response)

def get_data(command, address, data):
    logging.info("Getting data for: %s", command["name"])
    cmd = [command["cmd"], address, data]
    crc = get_crc(cmd)
    cmd.append(crc)
    start_time = time.time()
    ser.write(cmd)     # write a string
    end_time = time.time()
    logging.debug("Execution time send: %f", end_time-start_time)
    start_time = time.time()
    # Before the Address is not set response is 8 bytes
    response = ser.read(FRAME_SIZE*2)
    check_response(command, response)
    end_time = time.time()
    logging.debug("Execution time read: %f", end_time-start_time)
    return response[DATA]

def main():
    """ Main entry point of the app """
    fw_version = get_data(SETUP, BOARD_ADDRESS, BOARD_ADDRESS)
    logging.info("FW_Version: %d", fw_version)
    send_command(SET_OPTION, BOARD_ADDRESS, 2)
    send_command(NOP, BOARD_ADDRESS, 0)
    ser.close()             # close port

if __name__ == "__main__":
    """ This is executed when run from the command line """
    main()