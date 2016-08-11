"""A demonstration of Python's ability to interface with the ezLCD-304"""

import serial, time, io

class Display():
    def __init__(self, port = "/dev/tty.usbmodem1412"):
        self.port = port
        self.baud = 115200
        self.ser = serial.Serial(self.port, self.baud, timeout=.005)
        self.sio = io.TextIOWrapper(io.BufferedRWPair(self.ser, self.ser))
        assert self.ser.isOpen(), "%s is not open" % self.port
        self.x = 50
        self.y = 50
        self.xy(self.x, self.y)

    def xy(self, x, y):
        """Moves the cursor to specificed x and y

        x = 50 and y = 100 will place the cursor 50 pixels
        from the right and 100 pixels down
        """

        # Only update if necessary
        # This could glitch if xy is set throgh Display.cmd
        if x !=  self.x and y != self.y:
            self.cmd("xy %s %s" % (x, y))

    def line(self, x1, y1, x2, y2, line_type="solid", line_width="thin"):
        """Draws a line from (x1, y1) to (x2, y2)"""
        self.xy(x1, y1)

        # Set the line type
        line_types = ["solid", "dotted", "dashed"]
        try:
            type_index = line_types.index(line_type)
        except ValueError as e:
            raise ValueError("%s is not a valid line style" % line_type)
        self.cmd("linetype %s" % type_index)

        # Set the line width
        line_widths = ["thin", "thick"]
        try:
            width_index = line_widths.index(line_width)
        except ValueError as e:
            raise ValueError("%s is not a valid line width" % line_width)
        self.cmd("linewidth %s" % width_index)

        self.cmd("line %s %s" % (x2, y2))

    def print(self, string, x=None, y=None, font="sans", size=36, orientation=0):
        # if x and y are not specified, they default to the previous point
        if x and y:
            self.xy(x, y)
        self.cmd("font %s%s" % (font, size))
        t_orientation = orientation
        if t_orientation > 3:
            t_orientation /= 90
        assert -1 < t_orientation < 4, "%s rotation is not valid" % orientation
        self.cmd('print "%s"' % string)

    def cmd(self, string):
        if type(string) == list:
            for mini_command in string:
                self.cmd(mini_command)
        else:
            self.sio.write((string + '\r')) #.encode('ascii'))
            self.sio.flush()
            response = self.sio.read(10)
            # self.ser.write((string + '\r').encode('ascii'))
            # response = str(self.ser.read(100))

            print('Code: ' + str(response.encode('ascii')) + " - " + string)

    def last_touch(self):
        """Returns a tuple that is the coordinate of the last touch"""
        pass

    def live(self):
        while True:
            order = input("> ")
            if order == 'exit':
                self.ser.close()
                break
            elif order == 'help':
                print("Enter command or 'exit'")
            else:
                self.cmd(order)

    def cls(self, color="white"):
        self.cmd("cls white")

    def color_cycle(self):
        for r in reversed(range(0, 256, 10)):
            for g in range(0, 256, 10):
                for b in range(0, 256, 10):
                    command ='colorid 180 %s %s %s' % (r,g,b)
                    self.cmd(command)
                    self.cmd('cls 180')
                    time.sleep(.1)

if __name__ == "__main__":
    a = Display()
