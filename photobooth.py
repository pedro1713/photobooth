import glob
import time
import datetime
import RPi.GPIO as GPIO
import picamera
import os
import smbus

###Config
GPIO.setmode(GPIO.BCM)
light1_pin = 4
button1_pin = 22
button2_pin = 23
GPIO.setup(light1_pin, GPIO.OUT)
GPIO.setup(button1_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(button2_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.output(light1_pin, False)

###Variables
total_pics = 15
capture_delay = 0.2
prep_delay = 0.2
real_path = os.path.dirname(os.path.realpath(__file__))
bus = smbus.SMBus(1)
FLASH_ADDRESS = 0x70
FLASH_REG0 = 0x00
FLASH_GAIN = 0x09
gain = 0x0f
brightness = 0X32
sunrise = datetime.time(6, 0, 0)
sunset = datetime.time(19,0, 0)

###Functions
# define the shutdown function
def shutdown(channel):
	GPIO.output(light1_pin, True)
	time.sleep(3)
	os.system("sudo reboot")

# define the photo taking function for when the big button is pressed
def start_photobooth():
	################################# Begin Step 1 #################################
	GPIO.output(light1_pin,False)
	time.sleep(prep_delay)

	camera = picamera.PiCamera()
	pixel_width = 640 #use a smaller size to process faster
	pixel_height = 480
	camera.resolution = (pixel_width, pixel_height)
	camera.vflip = False
	camera.hflip = False
	
	now = datetime.datetime.now()
	if now.hour > sunset.hour or now.hour < sunrise.hour:
		camera.brightness = 60
		camera.ISO = 400
		camera.shutter_speed = camera.exposure_speed
	else:
		camera.brightness = 50
		camera.ISO = 100
		camera.shutter_speed = camera.exposure_speed
	
	camera.start_preview()
	time.sleep(1) #warm up camera

	################################# Begin Step 2 #################################
	print "Taking pics"
	now = time.strftime("%Y-%m-%d-%H%M%S") #get the current date and time for the start of the filename
	try: #take the photos
		bus.write_byte_data(FLASH_ADDRESS, FLASH_REG0, 0x5a)
		for i, filename in enumerate(camera.capture_continuous('/home/pi/pics/' + now  +  '-' + '{counter:02d}.jpg')):
                        GPIO.output(light1_pin, True)
			print(filename)
			time.sleep(capture_delay) # pause in-between shots
                        GPIO.output(light1_pin, False)
			if i == total_pics-1:
				break
		bus.write_byte_data(FLASH_ADDRESS, FLASH_REG0, 0x00)
	finally:
		camera.stop_preview()
		camera.close()

def set_flash():
	bus.write_byte_data(FLASH_ADDRESS, FLASH_GAIN, gain)
	bus.write_byte_data(FLASH_ADDRESS, 0x02, brightness)
	bus.write_byte_data(FLASH_ADDRESS, 0x04, brightness)
	bus.write_byte_data(FLASH_ADDRESS, 0x05, brightness)
	bus.write_byte_data(FLASH_ADDRESS, 0x07, brightness)

### Main Program
GPIO.add_event_detect(button2_pin, GPIO.FALLING, callback=shutdown, bouncetime=300)

#delete files in pics folder on startup
files = glob.glob('/home/pi/pics/' + '*')
for f in files:
	os.remove(f)

#set-up flash add-on
set_flash()

while True:
	GPIO.output(light1_pin, True)
        GPIO.wait_for_edge(button1_pin, GPIO.FALLING)
	time.sleep(0.2) #debounce
	start_photobooth()
