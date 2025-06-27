import serial

# Setting up serial port
ser = serial.Serial()
ser.baudrate = 115200
ser.port = '/dev/tty.usbserial-0001'
ser.timeout = 2
ser.open() # Open serial port

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
        print(byte3)
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

def iterate_scans():
    scan_data = []
    for (new_scan, angle, distance) in iterate_measurements():
        if(new_scan == True):
            print("NEW 360 DEGREES SCAN SWEEP")
            print(scan_data) # or yield scan
            scan_data = []
        print((new_scan, angle, distance))
        scan_data.append((new_scan, angle, distance))

iterate_scans()
