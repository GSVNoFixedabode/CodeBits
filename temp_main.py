import machine
import utime
import array, time
import rp2

#
# LED updating based on the Example neopixel_ring at:
# https://github.com/raspberrypi/pico-micropython-examples/tree/master/pio/neopixel_ring
############################################
# RP2040 PIO and Pin Configurations
############################################
########################################## Start WS2812 definitions
# WS2812 LED strip Configuration
led_count = 10 # number of LEDs in LED Ring
brightness = 0.2 # 0.1 = darker, 1.0 = brightest
PIN_NUM = 22 # pin connected to lightstrip
BLACK = '#000000'
RED = '#ff0000'
YELLOW = '#ff9600'
GREEN = '#00ff00'
CYAN = '#00ffff'
BLUE = '#0000ff'
PURPLE = '#b400ff'
WHITE = '#ffffff'
COLORS = (BLACK, RED, YELLOW, GREEN, CYAN, BLUE, PURPLE, WHITE)

@rp2.asm_pio(sideset_init=rp2.PIO.OUT_LOW, out_shiftdir=rp2.PIO.SHIFT_LEFT,
             autopull=True, pull_thresh=24) # PIO configuration


# define WS2812 parameters
def ws2812():
	T1 = 2
	T2 = 5
	T3 = 3
	wrap_target()
	label("bitloop")
	out(x, 1)               .side(0)    [T3 - 1]
	jmp(not_x, "do_zero")   .side(1)    [T1 - 1]
	jmp("bitloop")          .side(1)    [T2 - 1]
	label("do_zero")
	nop()                   .side(0)    [T2 - 1]
	wrap()

#
############################################
# Functions for RGB Coloring
############################################
#
def update_pix(brightness_input=brightness): # dimming colors and updating state machine (state_mach)
	dimmer_array = array.array("I", [0 for _ in range(led_count)])
	for ii,cc in enumerate(pixel_array):
		r = int(((cc >> 8) & 0xFF) * brightness_input) # 8-bit red dimmed to brightness
		g = int(((cc >> 16) & 0xFF) * brightness_input) # 8-bit green dimmed to brightness
		b = int((cc & 0xFF) * brightness_input) # 8-bit blue dimmed to brightness
		dimmer_array[ii] = (g<<16) + (r<<8) + b # 24-bit color dimmed to brightness
	state_mach.put(dimmer_array, 8) # update the state machine with new colors
	time.sleep_ms(10)

def set_24bit(ii, color): # set colors to 24-bit format inside pixel_array
	color = hex_to_rgb(color)
	pixel_array[ii] = (color[1]<<16) + (color[0]<<8) + color[2] # set 24-bit color
    
def hex_to_rgb(hex_val):
	return tuple(int(hex_val.lstrip('#')[ii:ii+2],16) for ii in (0,2,4))

#Pin definitions
# blinky LED for testing
led = machine.Pin(15, machine.Pin.OUT)
# PIR
# sensor_pir = machine.Pin(16, machine.Pin.IN, machine.Pin.PULL_DOWN)

#
########################################### End WS2812 definitions

#LEDS Display routines
# Code to simplify...
def paint_leds(colourIn, intTemp):
	global led_count
	print(colourIn)
	if intTemp == 0:
		intTemp = 10
	print(intTemp)
# clear LEDs
	for index in range(led_count):
		set_24bit(index, '#000000')
#	set_24bit(1, '#0000ff')

	for led_num in range(intTemp): #loop for length 
		if led_num < led_count:
			set_24bit(led_num,colourIn)
# done. Now update strip
	update_pix()

# onboard temperature #####################
sensor_temp = machine.ADC(4)
conversion_factor = 3.3 / (65535)

###############################################################
# Create the StateMachine with the ws2812 program, outputting on pre-defined pin
# at the 8MHz frequency
state_mach = rp2.StateMachine(0, ws2812, freq=8_000_000, sideset_base=machine.Pin(PIN_NUM))
# Activate the state machine
state_mach.active(1)
# Range of LEDs stored in an array
pixel_array = array.array("I", [0 for _ in range(led_count)])

while True:
    reading = sensor_temp.read_u16() * conversion_factor 
    temperature = int(27 - (reading - 0.706)/0.001721)
    print(temperature)
    if temperature <= 0:
        paint_leds(WHITE, abs(temperature))
    elif temperature <= 10:
        paint_leds(BLUE, temperature)
    elif temperature <= 20:
        paint_leds(GREEN, temperature % 10)
    elif temperature <= 30:
        paint_leds(YELLOW, temperature % 10)
    elif temperature <= 40:
        paint_leds(RED, temperature % 10)
    else:
        paint_leds(PURPLE, temperature % 10)
# then pause 1 second 
    utime.sleep(1)

