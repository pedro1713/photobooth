import time
import RPi.GPIO as GPIO
import picamera
#import socket
import os

###Config
GPIO.setmode(GPIO.BCM)
light1_pin = 4
light2_pin = 17
light3_pin = 18
button1_pin = 22
button2_pin = 23
button3_pin = 24
GPIO.setup(light1_pin, GPIO.OUT)
GPIO.setup(light2_pin, GPIO.OUT)
GPIO.setup(light3_pin, GPIO.OUT)
GPIO.setup(button1_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(button2_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(button3_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.output(light1_pin, False)
GPIO.output(light2_pin, False)
GPIO.output(light3_pin, False)

###Variables
total_pics = 4
capture_delay = 2
prep_delay = 3
real_path = os.path.dirname(os.path.realpath(__file__))

###Functions
# define the photo taking function for when the big button is pressed 
def start_photobooth(): 
	################################# Begin Step 1 ################################# 
	print "Get Ready"
	GPIO.output(light1_pin,True);
	time.sleep(prep_delay) 
	GPIO.output(light1_pin,False)
	
	camera = picamera.PiCamera()
	pixel_width = 640 #use a smaller size to process faster
	pixel_height = 480 
	camera.resolution = (pixel_width, pixel_height) 
	camera.vflip = True
	camera.hflip = False
	#camera.saturation = -100 # comment out this line if you want color images
	camera.start_preview()
	
	time.sleep(2) #warm up camera

	################################# Begin Step 2 #################################
	print "Taking pics" 
	now = time.strftime("%Y-%m-%d-%H:%M:%S") #get the current date and time for the start of the filename
	try: #take the photos
		for i, filename in enumerate(camera.capture_continuous('/home/pi/pics/' + now + '-' + '{counter:02d}.jpg')):
			#GPIO.output(led2_pin,True) #turn on the LED
			print(filename)
			#time.sleep(0.25) #pause the LED on for just a bit
			#GPIO.output(led2_pin,False) #turn off the LED
			time.sleep(capture_delay) # pause in-between shots
			if i == total_pics-1:
				break
	finally:
		camera.stop_preview()
		camera.close()


###Main Program
while True:
        GPIO.wait_for_edge(button1_pin, GPIO.FALLING)
	time.sleep(0.2) #debounce
	start_photobooth()


