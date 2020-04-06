from machine import RTC, Timer, ADC, Pin, PWM
mode = False
buttonHistory = [False,False,False,False]

def buttonDebounce(arg1):
    global buttonHistory, mode
    buttonHistory[0] = buttonHistory[1]
    buttonHistory[1] = buttonHistory[2]
    buttonHistory[2] = buttonHistory[3]
    buttonHistory[3] = SWITCH1.value()
    if not buttonHistory[0] and not buttonHistory[1] and buttonHistory[2] and buttonHistory[3]:
        #buttonHistory = [False,False,False,False] # built in histeresis
        buttonHistory[0] = True
        buttonHistory[1] = True
        buttonHistory[2] = True
        buttonHistory[3] = True
        mode = not mode
        #print("button Press!")

    
def displayTime(arg1):
    time = rtc.datetime()
    print("Date: " + str(time[1]) + "." + str(time[2]) + "." + str(time[0]))
    print("Time: " + str(time[4]) + ":" + str(time[5]) + ":" + str(time[6]))

def readAnalogInput(arg1):
    voltage = adc.read() #Range 0 - 511
    if mode:
        if voltage == 0:
            voltage = 10
        pwm0.freq(voltage)
        #print("frequency:",voltage)
    else:
        voltage = voltage * 2
        pwm0.duty(voltage)
        pwm1.duty(voltage)
        #print("duty cycle:",voltage)

year = int(input("Year? "))
month = int(input("Month? "))
day = int(input("Day? "))
weekday = int(input("Weekday? "))
hour = int(input("Hour? "))
minute = int(input("Minute? "))
second = int(input("Second? "))
microsecond = int(input("Microsecond? "))

# ------------------- FOR TEST -------------------
#year = 2019
#month = 9
#day = 3
#weekday = 1
#hour = 7
#minute = 30
#second = 00
#microsecond = 000000
# ------------------- FOR TEST -------------------


# Initilize a hardware timer to display the
# current data and time every 30 seconds
rtc = RTC()

rtc.datetime((year, month, day, weekday, hour, minute, second, microsecond))

#print(rtc.datetime())

tim1 = Timer(1)
tim1.init(period=30000,mode=Timer.PERIODIC, callback=displayTime)

# Set up the ADC
adc = ADC(Pin(34))
adc.atten(ADC.ATTN_11DB)
adc.width(ADC.WIDTH_9BIT)

tim2 = Timer(2)
tim2.init(period=100,mode=Timer.PERIODIC, callback=readAnalogInput)

# Start PWM signals on the external LEDs
LED_RED = Pin(27, Pin.OUT)
LED_GREEN = Pin(12, Pin.OUT)

pwm0 = PWM(LED_RED)
pwm1 = PWM(LED_GREEN)
pwm1.freq(10)
pwm1.duty(256)

# Initilize timer for button debounce
SWITCH1 = Pin(26, Pin.IN)
tim3 = Timer(3)
tim3.init(period=50,mode=Timer.PERIODIC, callback=buttonDebounce)

