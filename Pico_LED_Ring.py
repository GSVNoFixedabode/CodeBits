from machine import Pin
import utime, array, time, rp2, random
# import machine
############################################
#
# Google, pulse, and rotate code based on work 
# by Joshua Hrisko, Maker Portal LLC (c) 2021
# LED updating based on the Example neopixel_ring at:
# https://github.com/raspberrypi/pico-micropython-examples/tree/master/pio/neopixel_ring
############################################
# RP2040 PIO and Pin Configurations
############################################

# Button Code ##############################
# Interrupt Service Routine for Button Pressed Events - with no debounce
button_cycle = 1
def button1_pressed(change):
    global button_cycle
    button_cycle += 1
    button_cycle = button_cycle % 6
    if button_cycle == 0:
        button_cycle = 1
    print(button_cycle)
    alexa_zip()

    
# we define button1 as being connected to GP14 and to use the internal Pico PULL_DOWN resistor
button1 = Pin(14, Pin.IN, Pin.PULL_UP)
# here is how we associate the falling value on the input pin with the callback function
button1.irq(handler=button1_pressed, trigger=Pin.IRQ_FALLING)


############################################
# Start WS2812 definitions
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
# breathe color specifications
colors = [BLUE,YELLOW,CYAN,RED,GREEN,WHITE]


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
 
#
########################################### End WS2812 definitions

###### Breathing loop
#LEDS Display routines
def breathing_led(color):
    global button_cycle
    step = 5
    breath_amps = [ii for ii in range(0,255,step)]
    breath_amps.extend([ii for ii in range(255,-1,-step)])
    for ii in breath_amps:
        if button_cycle != 3:
            break
        for jj in range(len(pixel_array)):
            set_24bit(jj, color) # show all colors
        update_pix(ii/255)
        time.sleep(0.01)

def breathing():
    for color in colors: # emulate breathing LED (similar to Amazon's Alexa)
        breathing_led(color)
        time.sleep(0.1) # wait between colors
####### End Breathing loop
        
def alexa_zip():
# turn off LEDs using the Alexa zipper-type turnoff
    for ii in range(int(len(pixel_array)/2)):
        set_24bit(ii,'#000000') # turn off positive side
        set_24bit(int(len(pixel_array)-ii-1),'#000000') # turn off negative side 
        update_pix() # update
        time.sleep(0.02) # wait

def ring_spin(color,blank):
    global button_cycle
#    blank = "#ffffff"
    cycles = 5 # number of times to cycle 360-degrees
    for ii in range(int(cycles*len(pixel_array))+1):
        for jj in range(len(pixel_array)):
            if jj==int(ii%led_count): # in case we go over number of pixels in array
                set_24bit(jj,color) # color and loop a single pixel
            else:
                set_24bit(jj,blank) # turn others off
        update_pix() # update pixel colors
        time.sleep(0.05) # wait 50ms
        if button_cycle != 5:
           break

####### start RING Spiner
def rgb2hex(r,g,b):
    return "#{:02x}{:02x}{:02x}".format(r,g,b)

def ring_spinner():
    global button_cycle
    spot = '#ff0000' # looping color starts red
    wipe = '#ffffff'
    for rr in range(200):
        if button_cycle != 5:
           break
        ring_spin(spot,wipe)
        wipe = spot # color for other pixels
        c1 = random.randint(1,255)
        c2 = random.randint(1,255)
        c3 = random.randint(1,255)
# next colour
        spot = rgb2hex(c1,c2,c3)
####### End Ring Spinner
        
####### Google loop
def google_loop():
        # Create Google Home four color rotation scheme
    google_colors = ['#4285f4','#ea4335','#fbbc05','#34a853'] # hex colors by Google
    cycles = 2 # number of times to cycle 360-degrees
    for jj in range(int(cycles*len(pixel_array))):
        for ii in range(len(pixel_array)):
            if ii%int(len(pixel_array)/4)==0: # 90-degree leds only
                set_24bit((ii+jj)%led_count,google_colors[int(ii/len(pixel_array)*4)])
            else:
                set_24bit((ii+jj)%led_count,'#000000') # other pixels blank
        update_pix() # update pixel colors
        time.sleep(0.05) # wait between changes
####### End Google Loop
        
####### Google loop       
def amazon_loop():
    # Create Amazon Alexa rotation wheel
    amazon_colors = ['#00dbdc','#0000d4'] # hex colors by Amazon
    light_width = 3 # width of rotating led array
    cycles = 2 # number of times width rotates 360-deg
    for jj in range(int(cycles*len(pixel_array))):
        for ii in range(len(pixel_array)):
            if ii<light_width: 
                set_24bit((ii+jj)%led_count,amazon_colors[0])
            else:
                set_24bit((ii+jj)%led_count,amazon_colors[1]) # other pixels blank
        update_pix() # update pixel colors
        time.sleep(0.03) # wait between changes
    time.sleep(0.1)
####### End Amazon Loop
    
####### Temperature Loop
# Code to simplify...
def paint_leds(colourIn, intTemp):
    global led_count
#    print(colourIn)
    if intTemp == 0:
        intTemp = 10
    print(intTemp)
# clear LEDs
    for index in range(led_count):
        set_24bit(index, '#000000')
# set_24bit(1, '#0000ff')
    for led_num in range(intTemp): #loop for length 
        if led_num < led_count:
            set_24bit(led_num,colourIn)
# done. Now update strip
    update_pix()

def temperature_display():
    reading = sensor_temp.read_u16() * conversion_factor 
    temperature = int(27 - (reading - 0.706)/0.001721)
#    print(temperature)
    if temperature <= 0:
        paint_leds(WHITE, abs(temperature))
    elif temperature <= 10:
        paint_leds(BLUE, temperature)
    elif temperature <= 20:
        paint_leds(GREEN, temperature - 10)
    elif temperature <= 30:
        paint_leds(YELLOW, temperature - 20)
    elif temperature <= 40:
        paint_leds(RED, temperature - 30)
    else:
        paint_leds(PURPLE, temperature % 10)
# then pause 1 second 
    utime.sleep(1)    

####### End Temperature loop

###############################################################
# Create the StateMachine with the ws2812 program, outputting on pre-defined pin
# at the 8MHz frequency
state_mach = rp2.StateMachine(0, ws2812, freq=8_000_000, sideset_base=machine.Pin(PIN_NUM))
# Activate the state machine
state_mach.active(1)
# Range of LEDs stored in an array
pixel_array = array.array("I", [0 for _ in range(led_count)])
    
while True:
    # onboard temperature #####################
    while button_cycle == 1:
        sensor_temp = machine.ADC(4)
        conversion_factor = 3.3 / (65535)
        temperature_display()
    while button_cycle == 2:
        google_loop()
    while button_cycle == 3:
        breathing()
    while button_cycle == 4:
        amazon_loop()
    while button_cycle == 5:
        ring_spinner()
    button_cycle = 1
   
