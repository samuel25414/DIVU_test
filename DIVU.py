from Divu_class import DIVU
import time

divu = DIVU()

try:
	while True:
	#	for value in range(255):
		#	divu.write(value)
		#	time.sleep(1)
		divu.write(255)
		time.sleep(1)

except KeyboardInterrupt:
	divu.close()
	print("Have a nice day ;)")
