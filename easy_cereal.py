"""A demonstration of Python's ability to interface with the ezLCD-304

Cereal.py - A Python Implementation to control the ezLCD-3xx Product Family
"""

import serial, time, io, os

# Default baud rate for serial communication with ezLCD
BAUD_RATE = 115200

# If developing on a raspberry pi, the default port is likely to be
# the following preset value

RASPBERRY_PI_DEVELOPMENT = False

if (RASPBERRY_PI_DEVELOPMENT):
    # Default port for raspberry pi development
    default_port = "/dev/ttyACM0"
else:
    # Default port for desktop development
    default_port = "/dev/tty.usbmodem1422"

class Display():
    """Controls a ezLCD-403 connected via USB"""

    def __init__(self, port = default_port):
        self.port = port
        self.baud = BAUD_RATE
        try:
            self.ser = serial.Serial(self.port, self.baud, timeout=.05)
        except serial.serialutil.SerialException as e:
            print("No USB device found at port %s" % port)
            print("Available ports:")
            os.system("ls /dev/tty.*")
            raise
        self.sio = io.TextIOWrapper(io.BufferedRWPair(self.ser, self.ser), newline=None)
        assert self.ser.isOpen(), "%s is not open" % self.port

        self.cls()

        # Variables that are stored in the display
        self.font = "sans"
        self.font_size = 14
        self.orientation = 0
        self.x = 0
        self.y = 0
        self.xy(self.x, self.y)

    def cursor_location(self):
        """Returns a tuple containing the (x,y) of the cursor location

        >>> a = Display()
        >>> x = 43
        >>> y = 98
        >>> a.xy(x, y)
        >>> a.cursor_location()
        Code: 43 98 - xy
        (43, 98)
        """
        pos_str = self.cmd("xy")
        coor = pos_str.split()
        result = (int(coor[0]), int(coor[1]))
        assert (self.x, self.y) == result, "Location variables not working"
        return result

    def xy(self, x=None, y=None):
        """Moves the cursor to specificed x and y

        x = 50 and y = 100 will place the cursor 50 pixels
        from the right and 100 pixels down
        """

        if x != None and y == None:
            lat = ["L","C","R","l","c","r"]
            vert =[ "T","C","B","t","c","b"]

            assert x[0] in lat, "Not a valid position"
            assert x[1] in vert, "Not a valid position"

            self.cmd("xy " + x)

        if x != self.x or y != self.y:
            self.x = x
            self.y = y
            self.cmd("xy %s %s" % (x, y))

    def line(self, x1, y1, x2, y2, line_type="solid", line_width="thin"):
        """Draws a line from (x1, y1) to (x2, y2)
        >>> a = Display()
        >>> x1, y1, x2, y2 = 43, 98, 123, 60
        >>> a.line(x1, y1, x2, y2, "dotted", "thick")
        """
        #Set the starting location of the line
        self.xy(x1, y1)

        # Set the line type
        line_types = ["solid", "dotted", "dashed"]
        type_index = line_types.index(line_type)
        self.cmd("linetype %s" % type_index)

        # Set the line width
        line_widths = ["thin", "thick"]
        width_index = line_widths.index(line_width)
        self.cmd("linewidth %s" % width_index)

        self.cmd("line %s %s" % (x2, y2))

    def print(self, string, x=None, y=None, font="sans", size=14, orientation=0):
        """Prints string to the screen
        >>> a = Display()
        >>> a.print("testing", 50, 50)
        """

        # if x and y are not specified, they default to the previous point
        if x != None or y != None:
            self.xy(x, y)

        if font != self.font or size != self.font_size:
            self.font = font
            self.font_size = size
            self.cmd("font %s%s" % (font, size))

        if self.orientation != orientation:
            self.cmd('fonto %s' % self.orientation)

        self.cmd('print "%s"' % string)

    def new_line(self):
        """Moves the cursor down one line"""
        self.xy(self.x, self.y + self.font_size)

    def cmd(self, string):
        """Issues a command to the display

        String must be written in the syntax of the ezLCD
        String could also be a list of string commands
        """

        if type(string) == list:
            for mini_command in string:
                self.cmd(mini_command)
        else:
            self.sio.write((string + '\r')) #.encode('ascii'))
            self.sio.flush()

            response = ""
            while not response:
                response = self.sio.readline().encode('ascii').decode('utf-8')
            response = remove_new_line(response)
            if response:
                print('Code: ' + response + " - " + string)
            return response

    def touch(self):
        """Returns a tuple that is the coordinate of the last touch

        This reading tends to not be very accurate, especially on the
        left side of the screen
        """

        x = int(self.cmd("touchx").strip())
        y = int(self.cmd("touchy").strip())
        return (x,y)

    def is_touching(self):
        """Returns boolean on touch status"""
        return int(self.cmd("touchs").strip()) == 3

    def wait_for_touch(self):
        """Return touch coordinate after waiting"""
        # Wait for touch
        while not self.is_touching():
            pass

        # Wait for release
        while self.is_touching():
            pass

        return self.touch()

    def tap_line(self):
        """Connects a line between two taps"""
        first = self.wait_for_touch()
        second = self.wait_for_touch()
        self.line(first[0],first[1],second[0],second[1])

    def live_tap(self):
        """Prints the coordinate of tap at the location of tap

        Useful for seeing tap interpretation"""

        p = self.wait_for_touch()
        self.print(str(p), p[0], p[1], font=2)

    def live(self):
        """Enter live interface with display using display's language"""
        while True:
            order = input("> ")
            if not order or order == 'exit':
                self.ser.close()
                break
            elif order == 'help':
                print("Enter command or 'exit'")
            else:
                self.cmd(order)

    def cls(self):
        """Clears the screen to white with black text"""
        self.cmd("cls white black")

def remove_new_line(string):
    """Removes a new line at the end of a character if present"""
    length = len(string)
    if not length:
        return string
    if string.endswith("\n"):
        return string[:-1]
    else:
        return string

if __name__ == "__main__":
    a = Display()
