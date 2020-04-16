// Isaiah Grace
// 15 April 2020

// This class is the main driver for the LED light string
// This will read text files and set the colors of the LED lights accordingly

// #include <pthread.h> // Hopefully this is not needed because it was included in LedDriver.hpp ??

#include <iostream>

#include "LedDriver.hpp"

LedDriver::LedDriver(int ledCount) {
  // Initilize some state variables
  refreshPeriod_ms = 20;
  this.ledCount = ledCount;
  ledArray = malloc(sizeof(ws2811_led_t) * ledCount);
  variance = 0;
  baseColor = 0;
    
  // Initilize the ws2811_t ledString varibale 
  ledString = {
	       .freq = TARGET_FREQ,
	       .dmanum = DMA,
	       .channel =
	       {
		[0] =
		{
		 .gpionum = GPIO_PIN
		 .count = led_count,
		 .invert = 0,
		 .brightness = 255,
		 .strip_type = STRIP_TYPE
		},
		[1] =
		{
		 .gpionum = 0,
		 .count = 0,
		 .invert = 0,
		 .brightness = 0,
		}
	       }
  };

  // Setup handlers so that we can exit gracefully
  setupHandlers();
}


LedDisplay::~LedDriver() {
  free(ledArray);
}


void LedDisplay::printColors(bool newLine) {
  // The newLine bool controlls weather or not we should print a new line after the colors:
  // Set newLine to False if you want to call this function many times in a row and have the outputs overwrite eachother
  
  // TODO: Add logic here to traverse the ledArray and print out block characters to stdout that show the color of each pixel
}


void LedDisplay::selfTest() {
  // This function just turns on some leds so we know we are sane
  //            0xWWRRGGBB
  ledArray[0] = 0x00200000;  // red
  ledArray[1] = 0x00201000;  // orange
  ledArray[2] = 0x00202000;  // yellow
  ledArray[3] = 0x00002000;  // green
  ledArray[4] = 0x00002020;  // lightblue
  ledArray[5] = 0x00000020;  // blue
  ledArray[6] = 0x00100010;  // purple
  ledArray[7] = 0x00200010;  // pink
}


void LedDisplay::SetRefreshRate(int period_ms) {
  // The thread that mutates the LEDs will look to this variable to tell it how frequently to update the colors
  refreshPeriod_ms = period_ms;
}


void LedDisplay::toState(state_t nxt_state) {
  switch(nxt_state) {
    
  case IDLE:
    variance = 0;
    baseColor = 0;
    break;
    
  case HOLD:
    break;
    
  case REMOTE_COLOR:
    readRemoteFile(); // Should we do this now? When do we do the things that need to happen? Tomorrow?
    break;
    
  case MUSIC_COLOR:
    readMusicFile();
    break;
    
  case SHUTDOWN:
    fillStrip(0x00000000);
    // TODO: Do something here that makes sure the SPI fires once, and make sure we quit
    break;
  }
  state = nxt_state;
}

// Get rekt with these awesome little functions!
// Compiler, inline these bad boys!
char LedDriver::getRed(uint32_t color) {
  return (char)((0x00ff0000 & color) >> 16);
}
char LedDriver::getBlue(uint32_t color) {
  return (char)((0x0000ff00 & color) >> 8);
}
char LedDriver::getGreen(uint32_t color) {
  return (char)(0x000000ff & color);
}
uint32_t LedDriver::makeColor(char r, char g, char b) {
  return ((uint32_t)(r) << 16) | ((uint32_t)(g) << 8) | (uint32_t)(b);
}

void LedDisplay::fillStrip(uint32_t color); {
  for (int i = 0; i < ledCount; i++) {
    ledArray[i] = (ws2811_led_t)(color);
  }
}


void LedDisplay::setupHandlers() {
  struct sigaction sa =
    {
     .sa_handler = sigActionHandler()
    };
  
  sigaction(SIGINT, &sa, NULL);
  sigaction(SIGTERM, &sa, NULL);
}


void LedDisplay::sigActionHandler(int signum) {
  // We have been asked by the OS or User to exit, ensure that the lights get turned off, and then quit
  toStateSHUTDOWN();
}
