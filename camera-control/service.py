import time
import csv
import serial

import schedule

import CameraControll as cc

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


def decode_response(response):
    pass


def get_serial_connection():
    #_devName = '/dev/tty.usbserial-FTS4PT0F'
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
