# import serial
import time
import sys

""" Get camera informations """


def reqIrisPosition(serial_connection):
    command = bytearray([0x01, 0xc3])
    arg = bytearray([0x02])
    return send_command(serial_connection, command, arg)


def reqNDStatus(serial_connection):
    command = bytearray([0x01, 0xc5])
    arg = bytearray([0x0])
    return send_command(serial_connection, command, arg)


def reqShutterStatus(serial_connection):
    command = bytearray([0x01, 0xc6])
    arg = bytearray([0x1])
    return send_command(serial_connection, command, arg)


def reqIRStatus(serial_connection):
    command = bytearray([0x01, 0xc5])
    arg = bytearray([0xb])
    return send_command(serial_connection, command, arg)


def reqMenuStatus(serial_connection):
    command = bytearray([0x01, 0xc5])
    arg = bytearray([0x9])
    return send_command(serial_connection, command, arg)


def reqGainStatus(serial_connection):
    command = bytearray([0x01, 0xc6])
    arg = bytearray([0x0])
    return send_command(serial_connection, command, arg)


def reqFanStatus(serial_connection):
    command = bytearray([0x01, 0xea])
    arg = bytearray([0xa])
    return send_command(serial_connection, command, arg)


def reqLensStatus(serial_connection):
    command = bytearray([0x01, 0xea])
    arg = bytearray([0xc])
    return send_command(serial_connection, command, arg)


def reqTemperatureStatus(serial_connection):
    command = bytearray([0x01, 0xea])
    arg = bytearray([0xa])
    return send_command(serial_connection, command, arg)


def send_command(serial_connection, command: bytearray, args=None) -> bytearray:
    """ Handle sending commands to camera """

    # assert (command != [], "Command canot be empty")

    cmd = []

    # Lets prepare the constant parts of a message
    prefix = bytearray([0xff, 0x30, 0x30])
    end = bytearray([0xef])

    cmd += prefix
    cmd += command

    if args:
        cmd += args

    cmd += end

    if serial_connection:
        serial_connection.write(cmd)
        response = serial_connection.readline()
        return response

    else:
        print(cmd)


def setMode(serial, value):
    mode = {
        "AUTO": '0',
        "MANUAL": '1',
        "AGC": '2',
        "AV": '3',
        "TV": '4'
    }

    command = bytearray([0x18, 0x4])

    try:
        arg = mode[value]
    except KeyError:
        print(f"Bad iris position value: {value}")
        exit(1)

    print("Result: ", send_command(serial, command, arg))


############ Iris position setting (Mateusz Kojro 2021.05.19) ############################################################


def setAdvancedIrisPosition(serial, value):
    iris = {
        1.0: [ord('F'), ord('F')],
        1.4: [ord('E'), ord('F')],
        2.0: [ord('D'), ord('F')],
        2.8: [ord('C'), ord('F')],
        4.0: [ord('B'), ord('F')],
        5.6: [ord('A'), ord('F')],
        8.0: [ord('9'), ord('F')],
        11.0: [ord('8'), ord('F')],
        16.0: [ord('7'), ord('F')],
        22.0: [ord('6'), ord('F')],
        32.0: [ord('5'), ord('F')],
        45.0: [ord('4'), ord('F')],
        64.0: [ord('3'), ord('F')],
        90.0: [ord('2'), ord('F')],
        128.0: [ord('1'), ord('F')],
        181.0: [ord('0'), ord('F')],
    }
    try:
        cmd = bytearray([
            0xff, 0x30, 0x30, 0x01, 0xa6, iris[value][0], iris[value][1], 0xef
        ])
    except KeyError:
        print(f"Bad iris position value: {value}")
        exit(1)
    if serial:
        serial.write(cmd)
        res = serial.readline()
        print('Set iris position: ', end=' ')
        print(res)
        time.sleep(0.4)
    else:
        print(cmd)


# Turn on and off the settings menu (Mateusz Kojro 2021/06/18)


def setMenu(serial, value):
    menu = {
        "off": [ord('0')],
        "on": [ord('1')],
    }
    try:
        cmd = bytearray([0xff, 0x30, 0x30, 0x01, 0xd0, menu[value][0], 0xef])
    except KeyError:
        print(f"Error: Menu can only be \"on\" or \"off\" got: {value}")
        exit(1)
    if serial:
        serial.write(cmd)
        res = serial.readline()
        print('Set menu: ', end=' ')
        print(res)
        time.sleep(0.4)
    else:
        print(cmd)


# Click a button in the menu (Mateusz Kojro 2021/06/18)


def menuPressButton(serial, value):
    menuClick = {
        "ok": [ord('0')],
        "up": [ord('1')],
        "down": [ord('2')],
        "left": [ord('3')],
        "right": [ord('4')],
        "cancel": [ord('5')],
    }

    try:
        cmd = bytearray(
            [0xff, 0x30, 0x30, 0x01, 0xd1, menuClick[value][0], 0xef])
    except KeyError:
        print(
            f"Error: You can only cllick \"ok\", \"right\", \"left\", \"up\", \"down\", \"cancel\" got: {value}"
        )
        exit(1)
    if serial:
        serial.write(cmd)
        res = serial.readline()
        print('Click in menu: ', end=' ')
        print('response:', res)
        time.sleep(0.4)
    else:
        print(cmd)


############ Gain setting ############################################################


def setGain(serial, value):
    gain = {
        0: ord('0'),
        6: ord('1'),
        12: ord('2'),
        24: ord('3'),
        36: ord('4'),
        75: ord('5')
    }
    try:
        cmd = bytearray([0xff, 0x30, 0x30, 0x01, 0xae, gain[value], 0xef])
    except KeyError:
        print("Error: Value of the gain should be 6, 12, 24, 36, or 75 dB.",
              file=sys.stderr)
        print("       Otherwise, use setAdvancedGain.", file=sys.stderr)
        sys.exit(1)
    if serial:
        serial.write(cmd)
        res = serial.readline()
        print('Set gain: ', end='')
        print(res)
        time.sleep(0.4)
    else:
        print(cmd)


def setAdvancedGain(serial, value):
    gain = {
        0: [ord('0'), ord('0')],
        3: [ord('0'), ord('1')],
        6: [ord('0'), ord('2')],
        9: [ord('0'), ord('3')],
        12: [ord('0'), ord('4')],
        15: [ord('0'), ord('5')],
        18: [ord('0'), ord('6')],
        21: [ord('0'), ord('7')],
        24: [ord('0'), ord('8')],
        27: [ord('0'), ord('9')],
        30: [ord('0'), ord('A')],
        33: [ord('0'), ord('B')],
        36: [ord('0'), ord('C')],
        39: [ord('0'), ord('D')],
        42: [ord('0'), ord('E')],
        45: [ord('0'), ord('F')],
        48: [ord('1'), ord('0')],
        51: [ord('1'), ord('1')],
        54: [ord('1'), ord('2')],
        57: [ord('1'), ord('3')],
        60: [ord('1'), ord('4')],
        63: [ord('1'), ord('5')],
        66: [ord('1'), ord('6')],
        69: [ord('1'), ord('7')],
        72: [ord('1'), ord('8')],
        75: [ord('1'), ord('9')]
    }
    try:
        cmd = bytearray([
            0xff, 0x30, 0x30, 0x01, 0x9e, gain[value][0], gain[value][1], 0xef
        ])
    except KeyError:
        print(
            "Error: Value of the gain should be multiple of 3 from 0 to 75 dB.",
            file=sys.stderr)
        print("       Otherwise, use setAdvancedGain.", file=sys.stderr)
        sys.exit(1)
    if serial:
        serial.write(cmd)
        res = serial.readline()
        print('Set gain: ', end='')
        print(res)
        time.sleep(0.4)
    else:
        print(cmd)


############ Gamma setting ############################################################


def setGamma(serial, value):
    gamma = {
        'Normal_1': ord('0'),
        'Normal_2': ord('1'),
        'Normal_3': ord('2'),
        'Normal_4': ord('3'),
        'EOS_Std': ord('4'),
        'Wide_DR': ord('5'),
        'Canon_Log': ord('6'),
        'Linear': ord('7')
    }
    try:
        cmd = bytearray([0xff, 0x30, 0x30, 0x01, 0xf2, gamma[value], 0xef])
    except KeyError:
        print("Error: Value of the gamma curve should be as following.",
              file=sys.stderr)
        print(
            "       Normal_1, Normal_2, Normal_3, Normal4, EOS_Std, Wide_DR, Canon_Log, Linear.",
            file=sys.stderr)
        sys.exit(1)
    if serial:
        serial.write(cmd)
        res = serial.readline()
        print('Set gamma: ', end='')
        print(res)
        time.sleep(0.4)
    else:
        print(cmd)


############ Shutter speed setting ############################################################


def setShutterSpeed(serial, value):
    shutter = {
        '1/4': ord('0'),
        '1/15': ord('1'),
        '1/30': ord('2'),
        '1/100': ord('3'),
        '1/1000': ord('4')
    }
    try:
        cmd = bytearray([0xff, 0x30, 0x30, 0x01, 0xad, shutter[value], 0xef])
    except KeyError:
        print(
            "Error: Value of the gain should be 1/4, 1/15, 1/30, 1/100, 1000.",
            file=sys.stderr)
        print("       Otherwise, use setAdvancedShutterSpeed.",
              file=sys.stderr)
        sys.exit(1)
    if serial:
        serial.write(cmd)
        res = serial.readline()
        print('Set shutter speed: ', end='')
        print(res)
        time.sleep(0.4)
    else:
        print(cmd)


def setAdvancedShutterSpeed(serial, value):
    shutter = {
        '1/4': [ord('0'), ord('0')],
        '1/4': [ord('0'), ord('1')],
        '1/4': [ord('0'), ord('2')],
        '1/5': [ord('0'), ord('3')],
        '1/6': [ord('0'), ord('4')],
        '1/7': [ord('0'), ord('5')],
        '1/8': [ord('0'), ord('6')],
        '1/10': [ord('0'), ord('7')],
        '1/12': [ord('0'), ord('8')],
        '1/15': [ord('0'), ord('9')],
        '1/17': [ord('0'), ord('A')],
        '1/20': [ord('0'), ord('B')],
        '1/24': [ord('0'), ord('C')],
        '1/30': [ord('0'), ord('D')],
        '1/34': [ord('0'), ord('E')],
        '1/40': [ord('0'), ord('F')],
        '1/48': [ord('1'), ord('0')],
        '1/60': [ord('1'), ord('1')],
        '1/75': [ord('1'), ord('2')],
        '1/90': [ord('1'), ord('3')],
        '1/100': [ord('1'), ord('4')],
        '1/120': [ord('1'), ord('5')],
        '1/150': [ord('1'), ord('6')],
        '1/180': [ord('1'), ord('7')],
        '1/210': [ord('1'), ord('8')],
        '1/250': [ord('1'), ord('9')],
        '1/300': [ord('1'), ord('A')],
        '1/360': [ord('1'), ord('B')],
        '1/420': [ord('1'), ord('C')],
        '1/500': [ord('1'), ord('D')],
        '1/600': [ord('1'), ord('E')],
        '1/720': [ord('1'), ord('F')],
        '1/840': [ord('2'), ord('0')],
        '1/1000': [ord('2'), ord('1')],
        '1/1200': [ord('2'), ord('2')],
        '1/1400': [ord('2'), ord('3')],
        '1/1700': [ord('2'), ord('4')],
        '1/2000': [ord('2'), ord('5')]
    }
    try:
        cmd = bytearray([
            0xff, 0x30, 0x30, 0x01, 0x9d, shutter[value][0], shutter[value][1],
            0xef
        ])
    except KeyError:
        print("Error: Value of the gain should be from 1/4 to 1/2000.",
              file=sys.stderr)
        print("       See manual.", file=sys.stderr)
        sys.exit(1)
    if serial:
        serial.write(cmd)
        res = serial.readline()
        print('Set shutter speed: ', end='')
        print(res)
        time.sleep(0.4)
    else:
        print(cmd)


############ IR filter setting ############################################################


def getCameraStatusInfrared(serial):
    cmd = bytearray([0xff, 0x30, 0x30, 0x01, 0xc5, 0x42, 0xef])
    if serial:
        serial.write(cmd)
        print("Camera status of infrared is ", file=sys.stderr)
        res = serial.readline()
        print('Camera Status (Infrared): ', end='')
        print(res)
        time.sleep(0.4)
    else:
        print(cmd)


def setInfraredOff(serial):
    cmd = bytearray([0xff, 0x30, 0x30, 0x01, 0xbb, 0x30, 0xef])
    if serial:
        serial.write(cmd)
        res = serial.readline()
        print('Set Infrared Off: ', end='')
        print(res)
        time.sleep(0.4)
    else:
        print(cmd)


def setInfraredOn(serial):
    cmd = bytearray([0xff, 0x30, 0x30, 0x01, 0xbb, 0x31, 0xef])
    if serial:
        serial.write(cmd)
        res = serial.readline()
        print('Set Infrared On: ', end='')
        print(res)
        time.sleep(0.4)
    else:
        print(cmd)


############ Focussing setting ############################################################


def setFocusManual(serial):
    cmd = bytearray([0xff, 0x30, 0x30, 0x01, 0xa1, 0x31, 0xef])
    if serial:
        serial.write(cmd)
        res = serial.readline()
        print('Set manual focus: ', end='')
        print(res)
        time.sleep(0.4)
    else:
        print(cmd)


def setFocusNear(serial):
    cmd = bytearray([0xff, 0x30, 0x30, 0x01, 0xa1, 0x32, 0xef])
    if serial:
        serial.write(cmd)
        res = serial.readline()
        print('Set focus near: ', end='')
        print(res)
        time.sleep(0.4)
    else:
        print(cmd)


def setFocusFar(serial):
    cmd = bytearray([0xff, 0x30, 0x30, 0x01, 0xa1, 0x33, 0xef])
    if serial:
        serial.write(cmd)
        res = serial.readline()
        print('Set focus far: ', end='')
        print(res)
        time.sleep(0.4)
    else:
        print(cmd)


def setOneFhotAF(serial):
    cmd = bytearray([0xff, 0x30, 0x30, 0x01, 0xa1, 0x41, 0xef])
    if serial:
        serial.write(cmd)
        res = serial.readline()
        print('Set one-shot AF: ', end='')
        print(res)
        time.sleep(0.4)
    else:
        print(cmd)


def setFocusPosition(serial, value):

    cmd = bytearray([0xff, 0x30, 0x30, 0x01, 0xaa, p0, p1, p2, p3, 0xef])
    if serial:
        serial.write(cmd)
        res = serial.readline()
        print('Set one-shot AF: ', end='')
        print(res)
        time.sleep(0.4)
    else:
        print(cmd)


############  ############################################################
############  ############################################################
############  ############################################################
############  ############################################################
############  ############################################################
############  ############################################################
############  ############################################################
############  ############################################################
