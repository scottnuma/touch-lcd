from time import strftime 
import cereal

date_string = strftime("%A, %b %d %I:%M %p")
print(date_string)
a = cereal.Display()
a.cls()
a.print(date_string, 400, 0, size=24, orientation=270)
