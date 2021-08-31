import time
import csv
import serial

import schedule

import CameraControll as cc

from enum import Enum, auto

FILE_NAME = None

SERIAL_DEVICE = 'COM9'


def get_timestamp():
    return time.strftime("%Y-%m-%d_%H_%M_%S", time.localtime())


def get_camera_status(serial_connection):
    status = []

    status.append(get_timestamp())
    status.append(cc.reqGainStatus(serial_connection))
    status.append(cc.reqIrisPosition(serial_connection))
    status.append(cc.reqShutterStatus(serial_connection))
    status.append(cc.reqFanStatus(serial_connection))
    status.append(cc.reqTemperatureStatus(serial_connection))
    return status


def get_ufo_captrue_status():

    raise NotImplementedError

    # coding: utf-8

    # pip install pillow pywinauto
    # see: https://pywinauto.readthedocs.io/en/latest/
    # Caution: Use 32 bit python for UFOCapture. Otherwise, this will kill UFOCapture process.
    # This should be more extensively tested.
    from pywinauto.application import Application
    from pywinauto.findwindows import ElementNotFoundError, ElementAmbiguousError

    try:
        app = Application().connect(title_re='UFOCapture*')
        dlg = app.window(title_re='UFOCapture*')
        print('Detect LevEdit:', dlg['Detect LevEdit'].window_text())
        dlg.maximize()
        dlg.set_focus()
        im = dlg.capture_as_image()
        im.save("screenshot_ufo_capture.png")
        del im
        del dlg
        del app
    except ElementNotFoundError:
        print('UFOCapture window not found')
    except ElementAmbiguousError:
        print('There are several UFOCapture windows')


class Setting(Enum):
    GAIN = auto()
    IRIS_POSITION = auto()
    SHUTTER = auto()
    FAN = auto()
    TEMPERATURE = auto()


def remove(string, substr):
    return string.replace(substr, '')


def other(data):
    return f"ERROR({data})"


def decode_gain(data):
    status_code = [i for i in range(19)]
    status_value = [f"{3 * i}dB" for i in range(19)]

    values = {}
    for key, value in zip(status_code, status_value):
        values[key] = value

    try:
        return values[data]
    except KeyError:
        return other(data)


def decode_iris_position(data):
    values = {
        0xFF: 1.0,
        0x7F: 16,
        0xEF: 1.4,
        0x6F: 22,
        0xDF: 2.0,
        0x5F: 32,
        0xCF: 2.8,
        0x4F: 45,
        0xBF: 4.0,
        0x3F: 64,
        0xAF: 5.6,
        0x2F: 90,
        0x9F: 8.0,
        0x1F: 128,
        0x8F: 11,
        0x0F: 181
    }

    try:
        return values[data]
    except KeyError:
        return other(data)


def decode_shutter_basic(data):
    """
    WARN: This varries for NTSC, PAL, ...
    We are decoding using NTSC(59.94P/i)
    """

    values = {
        0x0: "1/4",
        0x1: "1/20",
        0x2: "1/60",
        0x3: "1/100",
        0x4: "1/1000",
    }

    try:
        return values[data]
    except KeyError:
        return other(data)


def decode_shutter_advanced(data):
    """
    WARN: This varries for NTSC, PAL, ...
    We are decoding using NTSC(59.94P/i)
    """

    values = {
        0x00: "1/4",
        0x01: "1/4",
        0x02: "1/4",
        0x03: "1/5",
        0x04: "1/6",
        0x05: "1/7",
        0x66: "1/8",
        0x07: "1/10",
        0x08: "1/12",
        0x09: "1/15",
        0x0A: "1/17",
        0x0B: "1/20",
        0x0C: "1/24",
        0x0D: "1/30",
        0x0E: "1/34",
        0x0F: "1/40",
        0x10: "1/48",
        0x11: "1/60",
        0x12: "1/75",
        0x13: "1/90",
        0x14: "1/100",
        0x15: "1/120",
        0x16: "1/150",
        0x17: "1/180",
        0x18: "1/210",
        0x19: "1/250",
        0x1A: "1/300",
        0x1B: "1/360",
        0x1C: "1/420",
        0x1D: "1/500",
        0x1E: "1/600",
        0x1F: "1/720",
        0x20: "1/840",
        0x21: "1/1000",
        0x22: "1/1200",
        0x23: "1/1400",
        0x24: "1/1700",
        0x25: "1/2000",
    }

    try:
        return values[data]
    except KeyError:
        return other(data)


def decode_temperature(data):
    if data == 10:
        return f"SENSOR_ERROR({data})"
    return other(data)


def decode_fan(data):
    if data == 10:
        return f"SENSOR_ERROR({data})"
    return other(data)


def decode_response(response, seting: Setting):

    # FIXME: remove preficx and postifx
    print(f"Pre parsed respone: {response}")
    parsed_response = response

    if seting == Setting.GAIN:
        return decode_gain(parsed_response)

    if seting == Setting.IRIS_POSITION:
        return decode_iris_position(parsed_response)

    if seting == Setting.SHUTTER:
        return decode_shutter_advanced(parsed_response)

    if seting == Setting.FAN:
        return decode_fun(parsed_response)

    if seting == Setting.TEMPERATURE:
        return decode_temperature(parsed_response)

    raise Exception("Bad enumeration")


def get_serial_connection():
    try:
        serial_connection = serial.Serial(port=SERIAL_DEVICE,
                                          baudrate=9600,
                                          parity=serial.PARITY_NONE,
                                          bytesize=serial.EIGHTBITS,
                                          stopbits=serial.STOPBITS_ONE,
                                          timeout=1)
    except Exception as e:
        print(f"Connection to serial port {SERIAL_DEVICE} "
              f"failed with:\n{e}\nrunning in debug mode")
        serial_connection = None
    return serial_connection


def save_log():

    serial_connecton = get_serial_connection()
    data_point = get_camera_status(serial_connecton)

    if serial_connecton:
        serial_connecton.close()

    print(f"Saving current status: {data_point}")

    with open(FILE_NAME, 'a') as file:
        writer = csv.writer(file,
                            delimiter=',',
                            quotechar='\'',
                            quoting=csv.QUOTE_MINIMAL)

        writer.writerow(data_point)


if __name__ == '__main__':

    FILE_NAME = get_timestamp() + '.csv'

    with open(FILE_NAME, 'w') as outputfile:

        outputfile.write(
            "Timestamp, Gain, Iris position, Shutter, Fan status, Temperature\n"
        )

    save_log()

    schedule.every(0.5).minutes.do(save_log)

    while True:
        schedule.run_pending()
        time.sleep(1)
