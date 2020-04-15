#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <time.h>
#include <fcntl.h>
#include <sys/mman.h>
#include <signal.h>
#include <stdarg.h>
#include <getopt.h>

#include "clk.h"
#include "gpio.h"
#include "dma.h"
#include "pwm.h"
#include "ws2811.h"
//#include "musical_lights.h"

#define TARGET_FREQ     WS2811_TARGET_FREQ
#define GPIO_PIN        10
#define DMA             10
#define STRIP_TYPE      WS2811_STRIP_GBR

#define LED_COUNT       150
#define BRIGHTNESS      255

#define RED_MASK        0x00ff0000
#define RED_SHIFT       16
#define GREEN_MASK      0x0000ff00
#define GREEN_SHIFT     12
#define BLUE_MASK       0x000000ff
#define color_tolerance 50

//ws2811_led_t *buffer;
ws2811_led_t base_color;
int mutation_rate;
int mutation_step;
int bound_size;
int running;
char track_file[] = "/home/pi/Documents/lights/current_song";

ws2811_t ledstring = {
  .freq = TARGET_FREQ,
  .dmanum = DMA,
  .channel = {
    [0] = {
      .gpionum = GPIO_PIN,
      .invert = 0,
      .count = LED_COUNT,
      .strip_type = STRIP_TYPE,
      .brightness = BRIGHTNESS,
    },
    [1] = {
      .gpionum = 0,
      .count = 0,
      .invert = 0,
      .brightness = 0,
    },
  },
};

void clear_lights() {
  for (int x = 0; x < LED_COUNT; x++) {
    ledstring.channel[0].leds[x] = 0;
  }
}

ws2811_led_t get_color_from_hue(int hue) {
  // Hue will vary from 0 to 255
  // We need to convert this one number int RGB components
  // We will treat hue as Hue, and set Saturation and intensity to max
  // first off, shift rotate hue by 120 degrees arround the color wheel for asthetics sake
  hue += 170;
  if (hue > 255) hue -= 255;

  unsigned char r,g,b;
    
  unsigned char region = hue / 43;
  unsigned char remainder = (hue - (region * 43)) * 6;

  unsigned char p = (255 * (255 - 255)) >> 8;
  unsigned char q = (255 * (255 - ((255 * remainder) >> 8))) >> 8;
  unsigned char t = (255 * (255 - ((255 * (255 - remainder)) >> 8))) >> 8;


  switch (region) {
  case 0:
    r = 255; g = t; b = p;
    break;
  case 1:
    r = q; g = 255; b = p;
    break;
  case 2:
    r = p; g = 255; b = t;
    break;
  case 3:
    r = p; g = q; b = 255;
    break;
  case 4:
    r = t; g = p; b = 255;
    break;
  default:
    r = 255; g = p; b = q;
    break;
  }   
  return (ws2811_led_t) r << RED_SHIFT | g << GREEN_SHIFT | b;
}

int mutate_color(int value) {
  int random = rand() % 100;

  if (random < mutation_rate * 100) {
    if (random % 2) {
      value += mutation_step;
    } else {
      value -= mutation_step;
    }
    if (value > 255) value = 255;
    if (value < 0) value = 0;
  }
  return value;
}

int apply_bound(int value, int base_value) {
  if (value > base_value + bound_size)
    return --value;
  
  if (value < base_value - bound_size)
    return ++value;
  
  return value;
}

void slow_variations() {
  // Applies slow vatiations to each of the pixels on the strip according to the parameters:
  // mutationRate (0 - 1),
  // mutationStep (0 - 255),
  // baseColor ws2811_led_t packed color,
  // boundSize (0 - 255)

  int base_red   = (RED_MASK   & base_color) >> RED_SHIFT;
  int base_green = (GREEN_MASK & base_color) >> GREEN_SHIFT;
  int base_blue  = (BLUE_MASK  & base_color);

  printf("R: %03d G: %03d B: %03d\n", base_red, base_green, base_blue);
  int red;
  int green;
  int blue;
    
  ws2811_led_t color;
  
  for (int x = 0; x < LED_COUNT; x++) {
    color = ledstring.channel[0].leds[x];

    // Extract RGB values from the color
    red   = (RED_MASK   & color) >> RED_SHIFT;
    green = (GREEN_MASK & color) >> GREEN_SHIFT;
    blue  = (BLUE_MASK  & color);

    // mutate each of the colors
    red   = mutate_color(red);
    green = mutate_color(green);
    blue  = mutate_color(blue);
    
    // Apply the bounds to the new pixel color
    red   = apply_bound(red, base_red);
    green = apply_bound(green, base_green);
    blue  = apply_bound(blue, base_blue);

    // Update the color of this pixel
    ledstring.channel[0].leds[x] = (ws2811_led_t) red << RED_SHIFT | green << GREEN_SHIFT | blue;
  }
  ws2811_render(&ledstring);
  
  printf("R: %03d G: %03d B: %03d\n", red, green, blue);   
}
    
int get_modified_time(char* path) {
  struct stat buff;
  stat(path, &buff);
  return buff.st_mtim.tv_sec;
}

int get_audio_features(char* track_file) {
  // Open up the track_file for reading
  FILE* fptr = fopen(track_file ,"r");
  
  // Find the size of the file and read it all into memory
  fseek(fptr, 0L, SEEK_END);
  int filesize = ftell(fptr);
  char *input_buffer = malloc(sizeof(char) * (filesize + 1));
  rewind(fptr);
  fread(input_buffer, sizeof(char), filesize + 1, fptr);

  // Parse the input_buffer and build up a features_t struct
  int valence =  atoi(input_buffer);
  free(input_buffer);
  return valence;
}

void ms_sleep(int milliseconds) {
  struct timespec ts;
  ts.tv_sec = milliseconds / 1000;
  ts.tv_nsec = (milliseconds % 1000) * 1000000;
  nanosleep(&ts, NULL);
}

int main(int argc, char** argv) {
  // We will always read the curently_playing file when the program starts
  int modified_time = 0;
  int valence;

  // Initilize the ledstring
  ws2811_init(&ledstring);
  
  // Initilize some parameters before starting the loop
  mutation_rate = 0;
  mutation_step = 2;
  bound_size = 0;
  base_color = 0; //0x00ff00ff;
  running = 1;

  while (running) {
    // Check if the track_file has been changed since the last time we looked
    if (get_modified_time(track_file) != modified_time) {
      printf("file was modified!\n");
      // Update the modified_time so that we don't keep reading the track_file
      modified_time = get_modified_time(track_file);

      // Read the audio_features from the track_file
       valence = get_audio_features(track_file);

       if (valence > -1) {
	 printf("Track is playing\n");
	 // The track is currently playing and we should update the lights
	 base_color = get_color_from_hue(valence);

	 // Set bounds and mutation rates
	 bound_size = 50;
	 mutation_rate = 1;
       } else {
	 printf("Track is NOT playing\n");
	 // The track is not currently playing
	 base_color = 0;
	 bound_size = 0;
	 mutation_rate = 0;
       }
    }
    
    if ((valence > -1) || (time(NULL) - modified_time < 60)) {
      // The track is either playing, or has been playing within the last minute
      slow_variations();
    } else {
      printf("Sleep mode\n");
      ms_sleep(1000);
    }
    
    ms_sleep(50);
  }
  
  // Clean up before exiting
  clear_lights();
  //free(buffer);
  ws2811_fini(&ledstring);
  
  return EXIT_SUCCESS;
}
