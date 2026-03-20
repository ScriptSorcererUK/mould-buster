from machine import Pin, ADC, UART
from time import sleep


# ADC help (reading a voltage):
# https://docs.micropython.org/en/latest/esp8266/tutorial/adc.html  (ESP8266 ADC basics)
# https://randomnerdtutorials.com/esp32-esp8266-analog-readings-micropython/ (guide)


# UART help (serial send/receive):
# https://www.engineersgarage.com/micropython-esp8266-esp32-uart/


# LED on pin 18
led = Pin(18, Pin.OUT)

# gas sensor on ADC pin 2
gas = ADC(2)

# serial to Raspberry Pi
uart = UART(4, baudrate=9600)


print('Bens ADC sampler\n')
uart.write('BXG STARTING TO TEST\n')

# blink once at the start
led.value(1)
sleep(1)
led.value(0)


# startup wait (blinking)
l = 10
for i in range(l):
    led.value(0)
    sleep(0.4)

    c = (l - i) / l
    print("loop:", c)

    led.value(1)
    sleep(c)


# not used now
gasLevel = 0.0


# main loop
while True:
    gasreading = gas.read_u16()  # read the gas sensor

    print("ADC reading:", gasreading)  # show on screen
    uart.write(str(gasreading) + "\n")  # send to Pi

    # blink so we know it’s working
    led.value(1)
    sleep(0.1)
    led.value(0)

    sleep(0.7)