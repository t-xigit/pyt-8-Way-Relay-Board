#!/usr/bin/env python3
"""
Module Docstring
"""

import serial
import time
import sys
import logging
import click

__author__ = "Timur Yigit"
__version__ = "0.1.0"
__license__ = "MIT"


logging.basicConfig(level=logging.DEBUG)

# Parameters for the serial inteface
BAUDRATE = 19200
TIMEOUT = 5
BYTESIZE = 8
STOPBITS = 1
PARITY = 'N'

serial_port = None

""" Data Frame """
""" BYTE 0  - BYTE 1        - BYTE 2 - BYTE 3 """
""" Command - Board address - Data   - Check sum XOR BYTE 1 BYTE 2 BYTE 3 """
# Protokol parameters for the relay box
FRAME_SIZE = 4
CMD = 0
ADDR = 1
DATA = 2
CRC = 3
K1 = 1
K2 = 2
K3 = 4
K4 = 8
K5 = 16
K6 = 32
K7 = 64
K8 = 128


board_address = 0

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
    "name": "SET_PORT",
    "cmd": 3,
    "resp": 252
}

GET_OPTION = {
    "name": "GET_OPTION",
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


def get_crc(data):
    crc = 0
    for i in data:
        crc = crc ^ i
    logging.debug("Calculated CRC: %d", crc)
    return crc


def check_response(command, response):
    resp = response[0:3]
    rx_crc = response[CRC]
    crc = get_crc(resp)

    if rx_crc == crc:
        logging.debug("Received CRC OK")
    else:
        raise RuntimeError('Received CRC wrong, received: ', rx_crc, ', expected: ', crc)

    if response[CMD] == command["resp"]:
        logging.debug("Response code OK")
    else:
        raise RuntimeError('Response code wrong, received: ', response[CMD], ', expected: ', command["resp"])


def send_command(command, address, data):
    logging.info("Sending: %s", command["name"])
    cmd = [command["cmd"], address, data]
    crc = get_crc(cmd)
    cmd.append(crc)
    start_time = time.time()
    serial_port.write(cmd)     # write a string
    end_time = time.time()
    logging.debug("Execution time send: %f", end_time - start_time)
    start_time = time.time()
    response = serial_port.read(FRAME_SIZE)
    logging.debug("Received Response: %s", response)
    end_time = time.time()
    logging.debug("Execution time read: %f", end_time - start_time)
    logging.debug("Received response: %s", response)
    # This will cause an exeption if received package is wrong
    check_response(command, response)


def get_data(command, address, data):
    logging.info("Getting data for: %s", command["name"])
    cmd = [command["cmd"], address, data]
    crc = get_crc(cmd)
    cmd.append(crc)
    start_time = time.time()
    logging.debug("Sending Comand: %s", cmd)
    serial_port.write(cmd)
    end_time = time.time()
    logging.debug("Execution time send: %f", end_time - start_time)
    start_time = time.time()
    # Before the Address is not set response is 8 bytes
    response = serial_port.read(FRAME_SIZE * 2)
    logging.debug("Received Response: %s", response)
    check_response(command, response)
    end_time = time.time()
    logging.debug("Execution time read: %f", end_time - start_time)
    return response[DATA]


@click.group()
def cli():
    """Tool for controlling a serial relay box"""
    pass


@cli.command("set-relay", help="Set the status of a single relay")
@click.option('--relay', '-r', type=int, help='Set number relay from 0 to 7')
@click.option('--state', '-s', type=int, help='0 for Off and 1 for On')
def set_relay(relay, state):
    if relay > 8:
        raise ValueError('Only relay 1 to 8 available')
    bit = 1 << relay
    if state == 1:
        send_command(SET_SINGLE, board_address, bit)
    if state == 0:
        send_command(DEL_SINGLE, board_address, bit)


@cli.command("set-all-off", help="Sets all relays to off")
def set_all_off():
    send_command(SET_PORT, board_address, 0)


@cli.command("test-all", help="Tests all relays by tuning them on and off")
def test_all():
    logging.info("Testing all relays")
    send_command(SET_PORT, board_address, 0)
    time.sleep(0.5)
    for i in range(8):
        send_command(SET_SINGLE, board_address, (1 << i))
        time.sleep(0.3)
        send_command(DEL_SINGLE, board_address, (1 << i))


def main():
    """ Main entry point of the app """
    fw_version = get_data(SETUP, board_address, board_address)
    logging.info("FW_Version: %d", fw_version)
    send_command(SET_OPTION, board_address, 2)
    send_command(NOP, board_address, 0)
    send_command(SET_SINGLE, board_address, 8)
    status = get_data(GET_PORT, board_address, 0)
    print(status)
    set_relay(1, 1)
    time.sleep(5)
    set_relay(1, 0)
    ser.close()             # close port


def set_brodcast_opt():

    logging.debug("Setting Broadcast Option to: %d", brdcast_opt)
    send_command(SET_OPTION, board_address, brdcast_opt)


def close_port(port):
    logging.debug("Closing serial port")
    port.close()
    

def open_port(port):
    logging.debug("Opening Serial Port")
    port = serial.Serial('/dev/ttyUSB0')  # open serial port
    port.baudrate = BAUDRATE
    port.timeout = TIMEOUT
    port.bytesize = BYTESIZE
    port.stopbits = STOPBITS
    port.parity = PARITY
    logging.debug(port)
    return port


def init_relay_box():

    global board_address

    SET_BRD_ADDR = 1
    logging.info("Initializing relay box with Address: %d", SET_BRD_ADDR)
    # Setup command initalizes the board the address, and returns FW Version
    fw_version = get_data(SETUP, SET_BRD_ADDR, SET_BRD_ADDR)
    #logging.info("FW_Version: %d", fw_version)
    brdcast_opt = get_data(GET_OPTION, SET_BRD_ADDR , SET_BRD_ADDR)
    logging.info("Broadcast Option: %d", brdcast_opt)
    brdcast_opt = 2
    logging.debug("Setting Broadcast Option to: %d", brdcast_opt)
    #send_command(SET_OPTION, SET_BRD_ADDR, brdcast_opt)
    board_address = SET_BRD_ADDR


serial_port = open_port(serial_port)
init_relay_box()
if __name__ == "__main__":
    """ This is executed when run from the command line """
    cli()
    serial_port.close()             # close port
    sys.exit(0)
