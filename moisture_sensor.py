#!/usr/bin/env python

import json
import urllib2
import time
import RPi.GPIO as GPIO
import sys
import os
from neopixel import *


# Define functions which animate LEDs in various ways.
def wheel(pos):
  """Generate rainbow colors across 0-255 positions."""
  if pos < 85:
    return Color(pos * 3, 255 - pos * 3, 0)
  elif pos < 170:
    pos -= 85
    return Color(255 - pos * 3, 0, pos * 3)
  else:
    pos -= 170
    return Color(0, pos * 3, 255 - pos * 3)

def rainbow(strip, wait_ms=20, iterations=1):
  """Draw rainbow that uniformly distributes itself across all pixels."""
  for j in range(256*iterations):
    for i in range(strip.numPixels()):
      strip.setPixelColor(i, wheel((i+j) & 255))
    strip.show()
    time.sleep(wait_ms/1000.0)
    
def theaterChase(strip, color, wait_ms=50, iterations=10):
  """Movie theater light style chaser animation."""
  for j in range(iterations):
    for q in range(3):
      for i in range(0, strip.numPixels(), 3):
        strip.setPixelColor(i+q, color)
      strip.show()
      time.sleep(wait_ms/1000.0)
      for i in range(0, strip.numPixels(), 3):
        strip.setPixelColor(i+q, 0)

def colorWipe(strip, color, wait_ms=50):
  """Wipe color across display a pixel at a time."""
  for i in range(strip.numPixels()):
    strip.setPixelColor(i, color)
    strip.show()
    time.sleep(wait_ms/1000.0)
    
def setLedGreen(strip):
  rainbow(strip)
  theaterChase(strip, Color(255, 255, 255), 50, 5)
  colorWipe(strip, Color(0, 255, 0), 20)
    
def setLedRed(strip):
  rainbow(strip)
  theaterChase(strip, Color(255, 255, 255), 50, 5)
  colorWipe(strip, Color(255, 0, 0), 20)
    
# Send moisture state to server
def sendDataToServer(moisture_state):
  try:
    data = {'field1': moisture_state, 'api_key': '{YOUR API KEY}'}
    request = urllib2.Request('https://api.thingspeak.com/update.json')
    request.add_header("Content-Type", "application/json")
    request.add_data(json.dumps(data))
    urllib2.urlopen(request)
    print "sent data to server"
  except:
    print "error connecting to cloud server"

# Main function
def main():

  # Tell the GPIO module that we want to use
  GPIO.setmode(GPIO.BCM)

  # Pins setup
  led_pin = 18
  moisture_sensor_pin = 23
  moisture_sensor_enable = 24

  GPIO.setup(moisture_sensor_pin, GPIO.IN)
  GPIO.setup(moisture_sensor_enable, GPIO.OUT)
  
  # Turn off moisture sensing
  GPIO.output(moisture_sensor_enable, GPIO.LOW)

  # LED configuration:
  LED_COUNT   = 1        # Number of LED pixels.
  LED_PIN     = led_pin  # GPIO pin connected to the pixels (must support PWM!).
  LED_FREQ_HZ = 800000   # LED signal frequency in hertz (usually 800khz)
  LED_DMA     = 5        # DMA channel to use for generating signal (try 5)
  LED_INVERT  = False    # True to invert the signal (when using NPN transistor level shift)

  # Create NeoPixel object with appropriate configuration.
  strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT)
  
  # Intialize the library (must be called once before other functions).
  strip.begin()
  
  # Set to undefined state
  try:
    last_moisture_state = int(os.environ["last_moisture_state"])
  except:
    last_moisture_state = -1

  # Sample the moisture sensor every minute and set led color according to the moisture state
  GPIO.output(moisture_sensor_enable, GPIO.HIGH)
  time.sleep(0.1)
  moisture_state = GPIO.input(moisture_sensor_pin)
  GPIO.output(moisture_sensor_enable, GPIO.LOW)

  if (moisture_state != last_moisture_state):
    if (moisture_state == 1):
      setLedGreen(strip)
    else:
      setLedRed(strip)

  sendDataToServer(moisture_state)
  os.environ["last_moisture_state"] = str(moisture_state)

  # Always clean up the GPIOs
  GPIO.cleanup()

if __name__=="__main__":
  try:
    main()
  except KeyboardInterrupt:
    GPIO.cleanup()
    sys.exit
