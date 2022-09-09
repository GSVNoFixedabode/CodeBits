# Simple test for NeoPixels on Raspberry Pi
import time, sys, os, re
import board
import neopixel
from PIL import Image, ImageDraw, ImageFont, ImageOps
import datetime
import requests

# this version will display current date/time/temperature unless
# it finds a file in the /tmp directory.  If there is a /tmp/display.png
# it will load it, delete the original from the directory, and loop again

# LED strip configuration:
LED_COUNT      = 100     # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (must support PWM!).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 5       # DMA channel to use for generating signal (try 5)
LED_BRIGHTNESS = 0.8     # Set to 0 for darkest and 1 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)

# Speed of movement, in seconds (recommend 0.1-0.3)
SPEED=0.075

# Size of your matrix
MATRIX_WIDTH=10
MATRIX_HEIGHT=10
NumMatrix = MATRIX_WIDTH * MATRIX_HEIGHT
# LED matrix layout
# A list converting LED string number to physical grid layout
# Start with top right and continue right then down
# For example, my string starts bottom right and has horizontal batons
# which loop on alternate rows.
#
# Mine ends at the top right here:     -----------\
# My last LED is number 95                        |
#                                      /----------/
#                                      |
#                                      \----------\
# The first LED is number 0                       |
# Mine starts at the bottom left here: -----------/

myMatrix=[90,91,92,93,94,95,96,97,98,99,
          89,88,87,86,85,84,83,82,81,80,
          70,71,72,73,74,75,76,77,78,79,
          69,68,67,66,65,64,63,62,61,60,
          50,51,52,53,54,55,56,57,58,59,
          49,48,47,46,45,44,43,42,41,40,
          30,31,32,33,34,35,36,37,38,39,
          29,28,27,26,25,24,23,22,21,20,
          10,11,12,13,14,15,16,17,18,19,
           9, 8, 7, 6, 5, 4, 3, 2, 1, 0]


# Check that we have sensible width & height
if NumMatrix != len(myMatrix):
  raise Exception("Matrix width x height does not equal length of myMatrix")

# Choose an open pin connected to the Data In of the NeoPixel strip, i.e. board.D18
# NeoPixels must be connected to D10, D12, D18 or D21 to work.
pixel_pin = board.D18

# The number of NeoPixels
num_pixels = 100

# The order of the pixel colors - RGB or GRB. Some NeoPixels have red and green reversed!
# For RGBW NeoPixels, simply change the ORDER to RGBW or GRBW.
ORDER = neopixel.GRB

# Define the strip object itself
strip = neopixel.NeoPixel(
    pixel_pin, num_pixels, brightness=LED_BRIGHTNESS, auto_write=False, pixel_order=ORDER
)

########### Generate the image from text #######################
def text_on_img(text="Hello", size=10, color=(255,255,0), bg='red'):
	"Draw a text on an Image, saves it, show it"
	fnt = ImageFont.truetype('Times_New_Roman.ttf', size+1)
	# create image with 2 descender lines
	txtlen = int(size/1.6)*len(text)
	image = Image.new(mode = "RGB", size=(txtlen,size+2), color = bg)
	draw = ImageDraw.Draw(image)
	# draw text
	draw.text((0,0), text, font=fnt, fill=color)
	# trim top 2 lines
	shiftIm = Image.new("RGB", (txtlen, size), (0, 0, 0))
	shiftIm.paste(image.crop((0,2,txtlen,size+2)))
	return shiftIm
################################################################

########### Get the text ########################################
def generate_text():
	url = "http://10.1.1.111:81/logline.htm"
	try:
		r = requests.get(url)
		logline_text = r.text
	except:
		tod = datetime.datetime.now()
		logline_text = "{} filler -999c ".format(tod.strftime('%H:%M:%S %Y-%m-%dT'))

# split the line up separated by whitespace, 4th element is temp, split that to remove the c
	x = logline_text.split()
#print(x[3])
	mag = float(x[3].split("c")[0])
	degree = "°"
	weather_text = x[1] + " " + x[0] + " " + str(mag) + degree
# Update coluor to match tempe #
	if mag >= 30:
		magcolour = "red"
	elif mag >= 20:
		magcolour = "yellow"
	elif mag >= 10:
		magcolour = "green"
	elif mag > 0:
		magcolour = "blue"
	else:
		magcolour = "white"
# no weatherstation connect
	if mag == -999:
		magcolour = "cyan"
# call the magic
	Img_txt = text_on_img(text=weather_text, color=magcolour, bg='black')
#	Img_txt.save("check.png")
	return Img_txt
#################################################################

def allonecolour(strip,colour,numPixels):
  # Paint the entire matrix one colour
  for i in range(numPixels):
    strip[i] = colour
  strip.show()

# Changed color() call to just ()
def colour(r,g,b):
  # Fix for Neopixel RGB->GRB, also British spelling. 
  return (g,r,b)

# Changed color() call to just ()
def colourTuple(rgbTuple): 
  return (rgbTuple[1],rgbTuple[0],rgbTuple[2])

def wheel(pos):
    # Input a value 0 to 255 to get a color value.
    # The colours are a transition r - g - b - back to r.
    if pos < 0 or pos > 255:
        r = g = b = 0
    elif pos < 85:
        r = int(pos * 3)
        g = int(255 - pos * 3)
        b = 0
    elif pos < 170:
        pos -= 85
        r = int(255 - pos * 3)
        g = 0
        b = int(pos * 3)
    else:
        pos -= 170
        r = 0
        g = int(pos * 3)
        b = int(255 - pos * 3)
    return (r, g, b) if ORDER in (neopixel.RGB, neopixel.GRB) else (r, g, b, 0)


def rainbow_cycle(wait):
    for i in range(num_pixels):
        pixel_index = (i * 256 // num_pixels)
        strip[i] = wheel(pixel_index & 255)
        strip.show()
        time.sleep(wait)

def clear_cycle(wait):
    for i in range(num_pixels):
        pixel_index = (i * 256 // num_pixels)
        strip[i] = (0,0,0)
        strip.show()
        time.sleep(wait)

# concatenate horizontal images  
def get_concat_h(im1, im2):
	dst = Image.new('RGB', (im1.width + im2.width, im1.height))
	dst.paste(im1, (0, 0))
	dst.paste(im2, (im1.width, 0))
	return dst

stopflag = "stop.flag"

if os.path.exists(stopflag):
   os.remove(stopflag)

displayfile = "/tmp/display.png"

try:
   while(True):
      rainbow_cycle(0.001)
      clear_cycle(0)
      if os.path.exists(stopflag):
        strip.deinit()
        break

# check for a displayfile in the tmp directory and load  if found
# else call logline to get temp
      try:
        if os.path.exists(displayfile):
           loadIm = Image.open(displayfile)
           os.remove(displayfile)
        else:
           loadIm = generate_text() 
      except:
        raise Exception("Image file %s could not be loaded" % 'Generated_weather.png')
#with os.scandir(path) as it:
#    for entry in it:
#        if not entry.name.startswith('.') and entry.is_file():
#            print(entry.name)

# If the image height doesn't match the matrix, resize it
      if loadIm.size[1] != MATRIX_HEIGHT:
        origIm=loadIm.resize((int(loadIm.size[0]*(MATRIX_HEIGHT/loadIm.size[1])),MATRIX_HEIGHT),Image.BICUBIC)
      else:
        origIm=loadIm.copy()
# If the input is a very small portrait image, then no amount of resizing will save us
      if origIm.size[0] < MATRIX_WIDTH:
        raise Exception("Picture is too narrow. Must be at least %s pixels wide" % MATRIX_WIDTH)
      im=Image.new('RGB',(origIm.size[0]+MATRIX_WIDTH,MATRIX_HEIGHT))
      im.paste(origIm,(0,0,origIm.size[0],MATRIX_HEIGHT))
#      im.paste(origIm.crop((0,0,MATRIX_WIDTH,MATRIX_HEIGHT)),(origIm.size[0],0,origIm.size[0]+MATRIX_WIDTH,MATRIX_HEIGHT))

# COVID ########################################################
      CovidAlert = text_on_img(text="/// COVID-19 ALERT LEVEL 2 ///", color="yellow", bg="black")
      im = get_concat_h(CovidAlert,im)
################################################################

# And here we go.
      x=0
      tx=0

      while x<im.size[0]-MATRIX_WIDTH:
      # Set the sleep period for this frame
      # This might get changed by a textfile command
         thissleep=SPEED
      # Set the increment for this frame
      # Typically advance 1 pixel at a time but
      # the FLIP command can change this
         thisincrement=1
         rg=im.crop((x,0,x+MATRIX_WIDTH,MATRIX_HEIGHT))
         dots=list(rg.getdata())
         for i in range(len(dots)):
#       strip(myMatrix[i],colourTuple(dots[i]))
           strip[myMatrix[i]]=colourTuple(dots[i])
		   
         strip.show()
         x=x+thisincrement
         time.sleep(thissleep)

except (KeyboardInterrupt, SystemExit):
  print("Stopped")
  allonecolour(strip,colour(0,0,0),NumMatrix)
  strip.deinit()
