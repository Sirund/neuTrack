from gpiozero import DistanceSensor, Buzzer
ultrasonic = DistanceSensor(echo=17, trigger=4, threshold_distance=0.5)
buzzer = Buzzer(23)

print("setup complete")

def in_range():
	buzzer.on()
	print("in range")

def out_range():
	buzzer.off()
	print("out of range")

print("function created") 

while True:
	print(ultrasonic.distance)
	if ultrasonic.distance < 0.5:
		buzzer.on()
		print("in range")
	else:
		buzzer.off()
		print("out of range")

