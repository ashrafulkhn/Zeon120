
try:
	import can
except ImportError:
	print("Error: The 'can' module is not installed. Please install it using 'pip install python-can'.")
	# Handle the case where the 'can' module is not available
	# You can raise an exception or exit the program


class CanInterface:
	"""Static member where bus_instance would be a single common instance across application"""
	bus_instance = can.interface.Bus(bustype='socketcan', channel='can1', bitrate=125000)
