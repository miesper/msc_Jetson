import os

temp = os.popen('cat /sys/devices/virtual/thermal/thermal_zone*/temp').read()
print ( temp )