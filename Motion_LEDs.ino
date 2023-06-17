/*
 * HC-SR04 example sketch
 *
 * https://create.arduino.cc/projecthub/Isaac100/getting-started-with-the-hc-sr04-ultrasonic-sensor-036380
 *
 * by Isaac100
 */
#include <Adafruit_NeoPixel.h>

#define PIN_NEO_PIXEL  4   // Arduino pin that connects to NeoPixel
#define NUM_PIXELS     144  // The number of LEDs (pixels) on NeoPixel
Adafruit_NeoPixel NeoPixel(NUM_PIXELS, PIN_NEO_PIXEL, NEO_GRB + NEO_KHZ800);

const int trigPin = 7;
const int echoPin = 8;
const int DELAY_INTERVAL = 6
;

float duration, distance;

void setup() {
// Neopixel setup  
  NeoPixel.begin(); // INITIALIZE NeoPixel strip object (REQUIRED)
  NeoPixel.setBrightness(10);
  for (int pixel = 0; pixel < NUM_PIXELS; pixel++) { // for each pixel
    NeoPixel.setPixelColor(pixel, NeoPixel.Color(255, 255, 0)); // it only takes effect if pixels.show() is called
  }
  NeoPixel.show();   // send the updated pixel colors to the NeoPixel hardware.
  delay(500); 
  NeoPixel.clear(); // set all pixel colors to 'off'. It only takes effect if pixels.show() is called
  NeoPixel.show();   // send the updated pixel colors to the NeoPixel hardware.
 

  pinMode(LED_BUILTIN, OUTPUT);

// Ultrasonic setup
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
  Serial.begin(9600);
}

void LightPixels(){
    NeoPixel.clear(); // set all pixel colors to 'off'. It only takes effect if pixels.show() is called
// turn pixels to red  one by one with delay between each pixel
  for (int pixel = 0; pixel < NUM_PIXELS; pixel++) { // for each pixel
    NeoPixel.setPixelColor(pixel, NeoPixel.Color(200, 0, 0));
    NeoPixel.setPixelColor(pixel+1, NeoPixel.Color(200, 0, 0));
    NeoPixel.setPixelColor(pixel+2, NeoPixel.Color(200, 0, 0));
    NeoPixel.setPixelColor(pixel+3, NeoPixel.Color(200, 0, 0));
    NeoPixel.show();   // send the updated pixel colors to the NeoPixel hardware.
    delay(DELAY_INTERVAL); // pause between each pixel
    NeoPixel.setPixelColor(pixel, NeoPixel.Color(25, 75, 200)); // it only takes effect if pixels.show() is called
    NeoPixel.show();   // send the updated pixel colors to the NeoPixel hardware.
    delay(DELAY_INTERVAL); // pause between each pixel
  }
  delay(10000); //15 seconds on

  for (int pixel =  NUM_PIXELS; pixel > 1; --pixel ) { // for each pixel
    NeoPixel.setPixelColor(pixel, NeoPixel.Color(255, 0, 0)); // it only takes effect if pixels.show() is called
    NeoPixel.setPixelColor(pixel-1, NeoPixel.Color(200, 0, 0));
    NeoPixel.setPixelColor(pixel-2, NeoPixel.Color(200, 0, 0));
    NeoPixel.setPixelColor(pixel-3, NeoPixel.Color(200, 0, 0));
    NeoPixel.show();   // send the updated pixel colors to the NeoPixel hardware.
    delay(DELAY_INTERVAL/2); // pause between each pixel
    NeoPixel.setPixelColor(pixel, NeoPixel.Color(0, 0, 0)); // it only takes effect if pixels.show() is called
    NeoPixel.show();   // send the updated pixel colors to the NeoPixel hardware.
    delay(DELAY_INTERVAL/2); // pause between each pixel
  }
      
  // turn off all pixels 
  NeoPixel.clear();
  NeoPixel.show(); // send the updated pixel colors to the NeoPixel hardware.
  delay(2000);     // off time

}

void loop() {
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  duration = pulseIn(echoPin, HIGH);
  distance = (duration*.0343)/2;
  if ((distance > 5) && (distance < 140)) {
    digitalWrite(LED_BUILTIN, HIGH);  // turn the LED on (HIGH is the voltage level)
    Serial.print("Distance: ");
    Serial.println(distance);
  // Go to light display   
    LightPixels();

    digitalWrite(LED_BUILTIN, LOW);   // turn the LED off by making the voltage LOW
    delay(2000);
  }

  delay(500);
}
