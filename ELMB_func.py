import socket
import struct

vref = 0.79932

class DAQ_ELMB:
	def __int__(self):
		pass

	def init(self, port, ELMB_add):

		can_socket= socket.socket(socket.AF_CAN, socket.SOCK_RAW, socket.CAN_RAW)
		can_socket.bind((port,))
		#data = bytes([0x01,(0x00|ELMB_add)])
		#can_dlc = len(data)
		frame_fmt = "IB3x8s"
		#frame = struct.pack(frame_fmt,0x000,can_dlc,data.ljust(8,b'\x00'))
		#can_socket.send(frame)

		return can_socket, frame_fmt

	def write(self, can_id, data , can_socket, frame_fmt):

		can_dlc = len(data)
		frame = struct.pack(frame_fmt,can_id,can_dlc,data.ljust(8,b'\x00'))
		can_socket.send(frame)

	def read(self, can_socket, frame_fmt, ELMB_add):
		channel = 0
		value = 0

		frame = can_socket.recv(16)
		can_id, can_dlc, data = struct.unpack(frame_fmt, frame)
		data_ok = data[:can_dlc]

		if len(data_ok) == 6 and can_id ==(0x380 + ELMB_add):
			channel = data_ok[0]
			b0 = data_ok[2]
			b1 = data_ok[3]
			b2 = data_ok[4]
			b3 = data_ok[5]
			value = (b3<<24)|(b2<<16)|(b1<<8)|(b0)

		return channel, value

	def read_single(self, can_socket, frame_fmt, ELMB_add):
		channel = 0
		value = 0

		frame = can_socket.recv(16)
		can_id, can_dlc, data = struct.unpack(frame_fmt,frame)
		data_ok = data[:can_dlc]

		if len(data_ok) == 8 and can_id == (0x580+ELMB_add):
			channel = data_ok[3]
			b0 = data_ok[5]
			b1 = data_ok[6]
			b2 = data_ok[7]
			value = (b2<<16)|(b1<<8)|(b0)

		return channel, value


	def resistance_to_temperature(self, resistencia):
		if resistencia > 10e3:
			temperatura = ((-24536.24) + (0.02350289 * resistencia * 100) +
					(0.000000001034084 * (resistencia * 100) ** 2)) / 100
		else:
			temperatura = ((-24564.58) + (0.02353718 * resistencia * 100) +
					(0.000000001027502 * (resistencia * 100) ** 2)) / 100
		return temperatura

	def voltage_to_resistance(self, volt):
		R = 1e4*(vref/(volt-vref))
		return R

	def close(self,can_socket):
		can_socket.close()

