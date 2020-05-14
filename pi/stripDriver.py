# Isaiah Grace
# May 13 2020

import colorsys
import random
import rpi_ws281x


class StripDriver():
    def __init__(self, config):
        self.strip = rpi_ws281x.PixelStrip(
            config['COUNT'],
            config['PIN'],
            config['FREQ_HZ'],
            config['DMA'],
            config['INVERT'],
            config['BRIGHTNESS'],
            config['CHANNEL']
        )
        self.strip.begin()

        # This is the color that pixels will gravitate towards
        self.base_red = 0 # range 0 - 255
        self.base_blue = 0 # range 0 - 255
        self.base_green = 0 # range 0 - 255

        # Pixels can mutate to any color with +- the tolerance from the base
        # A tolerance of 0 means all pixels will be the base_color
        # A tolerance of 255 means pixels color will randomly span the entire color space
        self.tolerance = 0         # range 0 - 255

        # This is the % chance that a color value of a pixel has to mutate
        self.mutation_rate = 0     # range 0 - 100

        # A mutated color will change by this value, either + or -
        # increasing this will increase the speed that the colors change
        self.mutation_step = 2     # range 0 - 255

        # This offset is applied to the hue color wheel and will create a phase change from the valence mapping to the RGB mapping.
        # This website has a good demonstration of HSV color: http://aleto.ch/color-mixer/
        # A offset value of 0.66 would be equivelent of a Hue value of 240 on the above site.
        # Our mapping of the range 0 - 1 to the RGB color space is then represented by the circumpfrence of the HSV color wheel.
        # Note that this only allows mixing of two of the three colors, one will always be zero.
        # Thankfully our mutations will take care of this and we can rely on them to produce more colors.
        self.hue_offset = 0.66     # range 0 - 1

        # These HSV values allow a direct mapping from the 0 - 1 range to the RGB space
        # See: https://en.wikipedia.org/wiki/HSL_and_HSV
        # maximum values for S and V create more vivid and intense colors, and are a good choice with these cheep LEDs
        self.hsv_S = 1
        self.hsv_V = 1
        
    def refresh(self):
        # This transmits data to the LED strip to set the color of each LED according to the strip array
        self.strip.show()
        
        
    def clear(self):
        # DOES NOT TRANSMIT NEW COLORS TO STRIP
        # refresh is needed after this to actually turn off the lights
        for i in range(strip.numPixels()):
            self.strip.setPixelColorRGB(i,0,0,0)

                
    def set_base_color_from_valence(self, valence):
        # Takes a valence value (0 - 1) describing the song and returns a color mapping of that value, with the hue_offset applied
        # The offset shifts 
        hue = valence + self.hue_offset
        if hue > 1:
            hue = hue - 1
            
        # colorsys.hsv_to_rgb returns values from 0 - 1, we need to scale these to integers in the range 0 - 255
        (self.base_red, self.base_green, self.base_blue) = tuple(int(i * 255) for i in colorsys.hsv_to_rgb(hue, self.hsv_S, self.hsv_V))


    def set_base_color_from_RGB(self, red, green, blue):
        self.base_red = red
        self.base_green = green
        self.base_blue = blue
    
    def music_effect(self):
        for i in range(self.strip.numPixels()):
            pixel_color = self.strip.getPixelColor(i)
            
            # Extract the R G B values for this pixel from the packed 24 bit color
            pixel_color = ((0xFF0000 & pixel_color) >> 16,
                           (0x00FF00 & pixel_color) >> 8,
                           (0x0000FF & pixel_color))
            
            # Mutate each of the colors to find a new color value for the pixel
            pixel_color = self.mutate_color(pixel_color, self.mutation_rate, self.mutation_step)
            
            # Apply the limiting bound on the new pixel color
            red   = self.apply_bound(pixel_color[0], self.base_red,   self.tolerance)
            green = self.apply_bound(pixel_color[1], self.base_green, self.tolerance)
            blue  = self.apply_bound(pixel_color[2], self.base_blue,  self.tolerance)
            
            # Update the color of this pixel
            self.strip.setPixelColorRGB(i, red, green, blue)
            
            
    def mutate_color(self, color, mutation_rate, mutationStep):
        # Applies a random mutation to each pixel, allowing a natural variation between pixel colors
        mutated_color = [0,0,0]
        
        # This arithmetic means we only need one call to random in order to generate all three random numbers
        rand = random.randint(0,10000000)
        mutation = [rand % 100,
                    (rand // 100) % 100,
                    (rand // 100000) % 100
        ]

        for i in (0,1,2):
            if mutation[i] < mutation_rate:
                # Apply the color mutation, either increase or decrease the color
                if mutation[i] % 2 == 0:
                    mutated_color[i] = color[i] + mutationStep
                else:
                    mutated_color[i] = color[i] - mutationStep

                # Make sure the mutated color is within 0 - 255
                if mutated_color[i] > 255:
                    mutated_color[i] = 255
                if mutated_color[i] < 0:
                    mutated_color[i] = 0
                    
        return mutated_color

    
    def apply_bound(self, color, base_color, bound_size):
        # Applies the bound on a particular color value (0 - 255).
        # If the color is outside the allowed bound, gently push it towards the bound.
        # This allows the lights to turn on/off change colors from song to song gradually
        if color > base_color + bound_size:
            return color - 1
        if color < base_color - bound_size:
            return color + 1
        return color
