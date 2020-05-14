#!/usr/bin/env python3
"""
Module Docstring
"""

import serial
import time
import logging
import click

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
K1 = 1
K2 = 2
K3 = 4
K4 = 8
K5 = 16
K6 = 32
K7 = 64
K8 = 128

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
    ser.write(cmd)     # write a string
    end_time = time.time()
    logging.debug("Execution time send: %f", end_time - start_time)
    start_time = time.time()
    response = ser.read(FRAME_SIZE)
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
    ser.write(cmd)     # write a string
    end_time = time.time()
    logging.debug("Execution time send: %f", end_time - start_time)
    start_time = time.time()
    # Before the Address is not set response is 8 bytes
    response = ser.read(FRAME_SIZE * 2)
    check_response(command, response)
    end_time = time.time()
    logging.debug("Execution time read: %f", end_time - start_time)
    return response[DATA]


@click.group()
def cli():
    """Tool for controlling a serial relay box"""
    click.echo("Hello World")


@cli.command("set-relay", help="Set the status of a single relay")
@click.option('--relay', '-r', type=int, help='Set number relay from 0 to 7')
@click.option('--state', '-s', type=int, help='0 for Off and 1 for On')
def set_relay(relay, state):
    if relay > 8:
        raise ValueError('Only relay 1 to 8 available')
    bit = 1 << relay
    if state == 1:
        send_command(SET_SINGLE, BOARD_ADDRESS, bit)
    if state == 0:
        send_command(DEL_SINGLE, BOARD_ADDRESS, bit)


@cli.command("set-all-off", help="Sets all relays to off")
def set_all_off():
    send_command(SET_PORT, BOARD_ADDRESS, 0)


@cli.command("test-all", help="Tests all relays by tuning them on and off")
def test_all():
    send_command(SET_PORT, BOARD_ADDRESS, 0)
    time.sleep(0.5)
    for i in range(8):
        send_command(SET_SINGLE, BOARD_ADDRESS, (1 << i))
        time.sleep(0.3)
        send_command(DEL_SINGLE, BOARD_ADDRESS, (1 << i))


def main():
    """ Main entry point of the app """
    fw_version = get_data(SETUP, BOARD_ADDRESS, BOARD_ADDRESS)
    logging.info("FW_Version: %d", fw_version)
    send_command(SET_OPTION, BOARD_ADDRESS, 2)
    send_command(NOP, BOARD_ADDRESS, 0)
    send_command(SET_SINGLE, BOARD_ADDRESS, 8)
    status = get_data(GET_PORT, BOARD_ADDRESS, 0)
    print(status)
    set_relay(1, 1)
    time.sleep(5)
    set_relay(1, 0)
    ser.close()             # close port


if __name__ == "__main__":
    """ This is executed when run from the command line """
    cli()
    # main()
