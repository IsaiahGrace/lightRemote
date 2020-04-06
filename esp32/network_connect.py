# Isaiah Grace
# 5 April 2020

import network
import machine
import ujson
import ntptime
from time import sleep_ms

wlan = None
saved_networks_dict = dict()
network_name = None
network_passwd = None

def load_known_networks():
	global saved_networks_dict
	# Read the list of saved networks, and create a list
	print("Reading known networks file from 'known_networks'")
	try:
		with open('known_networks','r') as f:
			saved_networks_dict = ujson.load(f)
	except OSError:
		# If the known_networks file doesn't exist, that's fine.
		# We'll make an empty dict for later
		print("INFO, no 'known_networks' file found")
		pass
		
def setup_wlan():
	global wlan
	# Turn on the wifi network module
	wlan = network.WLAN(network.STA_IF)
	wlan.active(True)

def scan_networks():
	global wlan
	global network_name
	global network_passwd
	
	print("Scanning for WiFi networks:")
	networks = wlan.scan()
	
	if len(networks) == 0:
		print("ERROR! No WiFi networks found")
		# TODO: Make LEDs flash red and yellow
		return False
		
	# Search for known networks, because we expect to be in range
	for network in networks:
		if network[0].decode() in saved_networks_dict:
			print("Found known network: ",network[0].decode())
			print("Atempting to connect...")
			network_name = network[0].decode()
			network_passwd = saved_networks_dict[network_name]
			return True

	return False

def connect():
	global wlan
	global network_name
	global network_passwd

	if wlan == None:
		print("ERROR, initilize wlan before attempting to connect")
		return False
	
	if network_name == None or network_passwd == None:
		print("ERROR! network_name and network_passwd not set")
		return False

	if wlan.isconnected():
		print("INFO, wlan already connected")
		return True

	wlan.connect(network_name,network_passwd)

	timeout = 0
	while not wlan.isconnected():
		if timeout > 10:
			raise Exception
		print("Waiting for wlan to connect... " ,timeout)
		timeout = timeout + 1
		sleep_ms(3000)

	print("Connceted to WiFi, getting time from ntp")
	ntptime.settime()

def prompt_user_network():
	global network_name
	global network_passwd
	global saved_networks_dict
	# If we haven't found a known network, prompt the user to enter the name and password
	
	print("Could not find a known network")
	print("Please enter a network from the list below:")
	for network in networks:
		print(network[0].decode())

	network_name = input("WiFi name: ")
	network_passwd = input("password: ")

	print("would you like to save these credentials for next time?")
	save = input("[Y/n]")

	if not save == "y" and not save == "Y":
		return

	saved_networks_dict[network_name] = network_passwd

	with open("known_networks","w") as f:
		ujson.dump(saved_networks_dict,f)
		  

def self_test():
	load_known_networks()
	setup_wlan()
	if not scan_networks():
		prompt_user_network()
	connect()
