import spidev
import time
import RPi.GPIO as GPIO

# GPIO setup
RESET_PIN = 24
GPIO.setmode(GPIO.BCM)
GPIO.setup(RESET_PIN, GPIO.OUT)

# SPI setup
spi = spidev.SpiDev()
spi.open(0,0)
spi.max_speed_hz = 500
spi.mode = 0
spi.no_cs = False
spi.cshigh = False

class DIVU:
	def __init__(self):
		pass

	def reset_device(self):
		GPIO.output(RESET_PIN, 0)
		time.sleep(0.01)
		GPIO.output(RESET_PIN, 1)

	def write(self, value):
		if value > 255:
			raise ValueError("Register value out of range")
		self.reset_device()

		for reg in range(4):
			b1 = ((value >> 6)|(reg << 2)) & 0b11111111
			b2 = ((value << 2)|(reg)) & 0b11111111
			b3 = value & 0b11111111
			b4 = ((value >> 2)|(reg << 6)) & 0b11111111
			b5 = ((value << 6)|(reg << 4)|(value >> 4)) & 0b11111111
			b6 = ((value << 4)|(reg << 2)|(value >> 6)) & 0b11111111
			b7 = ((value << 2)|(reg)) & 0b11111111
			b8 = value & 0b11111111
			data = ([b1,b2,b3,b4,b5,b6,b7,b8])
			spi.xfer2(data)

		print(f"DIVU resistors set in value: {value}")

	def close(self):
		print("Closing SPI and GPIO")
		spi.close()
		GPIO.cleanup()
