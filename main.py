import serial
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from math import cos, sin, radians
import numpy as np

# Setting up serial port
ser = serial.Serial()
ser.baudrate = 115200
ser.port = '/dev/tty.usbserial-0001'
ser.timeout = 2
ser.open() # Open serial port
max_distance = 1000

# plot variables and parameters
fig = plt.figure()
ax = plt.gca()
sc = ax.scatter([], [], c=[], s=3)
ax.set_aspect('equal')
ax.set_xlim(-max_distance, max_distance)
ax.set_ylim(-max_distance, max_distance)

plt.title("RPLidar Scan Plot")
plt.xlabel("X (mm)")
plt.ylabel("Y (mm)")
plt.grid(True)


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
        extra_byte = ser.read(1)[0] # Get first element so that variable is of type int and not type bytes
        if not extra_byte:
            print("ERROR READING EXTRA BYTE")
        return find_valid_sample(byte2, byte3, byte4, byte5, extra_byte) # shift the sample frame by one byte

def iterate_scans():
    scan_data = []
    for (new_scan, angle, distance) in iterate_measurements():
        if(new_scan == True):
            print("NEW 360 DEGREES SCAN SWEEP")
            print(scan_data) # or yield scancle
            yield scan_data
            scan_data = []
        scan_data.append((new_scan, angle, distance))

def convert_polar_to_cartesian(frame_data):
    x_vals = []
    y_vals = []
    distance_vals = []

    # convert polar cartesian cordinates to vectors
    for (new_scan, angle, distance) in frame_data:
        angle_rad = radians(angle)
        x = distance * cos(angle_rad)
        y = distance * sin(angle_rad)
        x_vals.append(x)
        y_vals.append(y)
        distance_vals.append(distance)
        
    return x_vals, y_vals, distance_vals

def update_frame(frame_data):
    x_vals, y_vals, dist_vals = convert_polar_to_cartesian(frame_data)
    sc.set_offsets(np.column_stack((x_vals, y_vals)))
    sc.set_array(dist_vals)
    return sc,

def plot_map(): # run animation

    ani = FuncAnimation(fig, update_frame, frames=iterate_scans, interval=50, blit=True)
    plt.show()

plot_map();