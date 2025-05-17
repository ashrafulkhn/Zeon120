import can


class CanInterface:
	"""Static member where bus_instance would be a single common instance across application"""
	bus_instance = can.interface.Bus(bustype='socketcan', channel='can1', bitrate=125000)
