from Divu_class import DIVU
import time

divu = DIVU()

try:
	divu.init_device()

	while True:
		divu.write(255) # digiPOT valule (0-255)
		time.sleep(0.1)

except KeyboardInterrupt:
	divu.close()
	print("Have a nice day ;)")
