"""A demonstration of Python's ability to interface with the ezLCD-304"""
import serial

# Thi port may have to be reset between plugins
port = "/dev/tty.usbmodem1412"
baud = 115200

ser = serial.Serial(port, baud, timeout=1)
if ser.isOpen():
    print(ser.name + ' is open...')

while True:
    cmd = input("Enter command or 'exit':")
    if cmd == 'exit':
        ser.close()
        exit()
    else:
        ser.write(cmd.encode('ascii')+'\r\n'.encode('ascii'))
        out = ser.read()
        print('Receiving...'+str(out))

