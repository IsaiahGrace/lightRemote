import network
import machine
import neopixel
import ujson
#import time
#import sys
#import micropython
#import ntptime
#import esp32
#import socket
#import struct
#import utime

# Read the list of saved networks, and create a list
print("Reading known networks file from 'known_networks'")
try:
	saved_networks_file = open('known_networks','r')
	saved_networks_dict = ujson.loads(saved_networks_file.read())
	saved_networks_file.close()
except IOError:
	# If the known_networks file doesn't exist, that's fine.
	# We'll make an empty dict for later
	saved_networks_dict = dict()

# Turn on the wifi network module
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
print("Scanning for WiFi networks:")
networks = wlan.scan()

if networks.len() == 0:
	print("ERROR! No WiFi networks found")
	# TODO: Make LEDs flash red and yellow
	
# print a list of available WiFi networks for the user
for network in networks:
	print(network[0].decode())


# Search for known networks, because we expect to be in range
network_name = None
network_passwd = None
for network in networks:
	if network[0].decode() in saved_networks_dict:
		print("Found known network: " + network[0].decode())
		print("Atempting to connect...")
		network_name = network[0].decode()
		network_passwd = saved_networks_dict[saved_network_name]
		break

# If we haven't found a known network, prompt the user to enter the name and password
if network_name == None or network_passwd == None:
	print("Could not find a known 


for network in wlan.scan():
	print(network[0])
	if network[0] == b'Graceland 2.4 GHz':
		print("Connecting to Graceland 2.4 GHz")
		found_saved_network = True
		wlan.connect("Graceland 2.4 GHz","KisumuKE@311")
		break
	
while not wlan.isconnected():
    print('Connecting to Wifi ...')
    print('   ')
    time.sleep_ms(3000)

recieved = False

while not recieved:
    try:
        ntptime.settime()
        recieved = True
    except:
        print("Retrieving date and time from pool.ntp.org ...")
        print("  ")
        sleep_ms(3000)

print('Oh Yes! Get connected')
print('Connected to ' + wlan.config('essid'))
mac = ":".join("{:02x}".format(c) for c in wlan.config('mac'))
print('MAC Address: ' + mac.upper())
print('IP Address: ' + wlan.ifconfig()[0] )

time = RTC().datetime()

RTC().init((time[0], time[1], time[2], time[3], time[4] - 4, time[5], time[6], '<EST>'))

micropython.alloc_emergency_exception_buf(100)

start = utime.ticks_us()

x = 0
for i in range(0, 1000000):
    x = x + 1

stop = utime.ticks_us()

diff = utime.ticks_diff(stop,start)

print("Total microseconds to get out of while loop = " + str(diff))


