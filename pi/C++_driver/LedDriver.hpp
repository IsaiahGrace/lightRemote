// Isaiah Grace
// 15 April 2020

#ifndef LEDDRIVER_HPP_
#define LEDDRIVER_HPP_

#include <pthread.h>
#include <signal.h>

#include "ws2811.h"

#define TARGET_FREQ WS2811_TARGET_FREQ
#define GPIO_PIN    18
#define DMA         10
#define STRIP_TYPE  WS2811_STRIP_GBR

// These are the states, or modes of our display driver
typedef enum state_t {
		      IDLE,           // The lights are off
		      HOLD,           // The lights are held in their current configuration
		      REMOTE_COLOR,   // The lights are controlled manually by remote (any remote client)
		      MUSIC_COLOR,    // The lights are controlled by the valence of the currently playing song
		      SHUTDOWN,       // We need to shut down the LedDriver
} state_t;

class LedDriver {
public:
  LedDriver(int ledCount);
  ~LedDriver();
  
  // Public methods
  void printColors(bool newLine);
  void selfTest(); // display some colors to the led strip

  void setRefreshRate(int period_ms); // Sets the frequency at witch the colors mutate (default 20ms)
  
private:
  // Private variables
  ws2811_t ledString;
  ws2811_led_t *ledArray;
  volatile state_t state;
  volatile int refreshPeriod_ms;
  int ledCount;
  volatile int variance;
  volatile uint32_t baseColor; // 0xWWRRGGBB

  // Private methods
  // State control flow:
  void toState(state_t nxt_state);

  // Helpers for baseColor uint32_t:
  char getRed(uint32_t color);
  char getGreen(uint32_t color);
  char getBlue(uint32_t color);
  uint32_t makeColor(char r, char g, char b);

  // Helpers for setting and clearing the strip
  // Note: Don't use this function unless you need to IMMEDIATLY change the colors of the strip
  // just set the variance and baseColor for typical fade effects
  void fillStrip(uint32_t color);
  
  // Read status files:
  void readRemoteFile();
  void readMusicFile();

  // Respond to shutdown requests
  void sigActionHandler(int signum);
  void setupHandlers();
}

#endif
