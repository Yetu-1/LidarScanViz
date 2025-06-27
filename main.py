import serial
import matplotlib.pyplot as plt
from math import cos, sin, radians

# Setting up serial port
ser = serial.Serial()
ser.baudrate = 115200
ser.port = '/dev/tty.usbserial-0001'
ser.timeout = 2
ser.open() # Open serial port
show_flag = True

def send_scan_request():
    print("Sending Scan Request...")
    ser.write(bytes([0xA5, 0x20]))
    descriptor = ser.read(7) 

def iterate_measurements():
    send_scan_request()

    while True:
        # Read sample
        byte1, byte2, byte3, byte4, byte5 = find_valid_sample(*ser.read(5));
        # Process sample
        new_scan = byte1 & 0x01

        angle = ((byte3 << 7) | (byte2 >> 1)) / 64.0

        distance = ((byte5 << 8) | byte4) / 4.0

        yield(new_scan, angle, distance)

def find_valid_sample(byte1, byte2, byte3, byte4, byte5):
    # Extract check bits
    check_bit = (byte2 & 0x01)
    bit0 = byte1 & 0x01
    bit1 = (byte1 >> 1) & 0x01

    # Check validity of the sample
    if(check_bit == 1) and (bit1 ^ bit0 == 1): # Confirm that the check bit is 1 and bit1 is the inverse of bit0
        return byte1, byte2, byte3, byte4, byte5
    else:
        # check if they are the same value
        extra_byte = ser.read(1)
        if not extra_byte:
            print("ERROR READING EXTRA BYTE")
        return find_valid_sample(byte2, byte3, byte4, byte5, extra_byte) # shift the sample frame by one byte

def iterate_scans(show_flag):
    scan_data = []
    for (new_scan, angle, distance) in iterate_measurements():
        if(new_scan == True):
            print("NEW 360 DEGREES SCAN SWEEP")
            print(scan_data) # or yield scancle
            if show_flag == True:
                plot_map(scan_data)
                show_flag = False
            scan_data = []
        scan_data.append((new_scan, angle, distance))

def convert_polar_to_cartesian(frame_data):
    x_vals = []
    y_vals = []

    # convert polar cartesian cordinates to vectors
    for (new_scan, angle, distance) in frame_data:
        angle_rad = radians(angle)
        x = distance * cos(angle_rad)
        y = distance * sin(angle_rad)
        x_vals.append(x)
        y_vals.append(y)
        
    return x_vals, y_vals

def plot_map(scan_data):
    x_vals = []
    y_vals = []

    x_vals, y_vals = convert_polar_to_cartesian(scan_data)

    plt.figure()
    plt.scatter(x_vals, y_vals, s=1)
    plt.gca().set_aspect('equal', adjustable='box')
    plt.title("RPLidar Scan Plot")
    plt.xlabel("X (mm)")
    plt.ylabel("Y (mm)")
    plt.grid(True)
    plt.show()

iterate_scans(True)