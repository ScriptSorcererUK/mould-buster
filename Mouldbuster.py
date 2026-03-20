home_dir = '/root/home/pi' # home folder


import time, gpiozero, serial, board, os, neopixel
from gpiozero import Button
from time import sleep
from picamzero import Camera


# talk to the Wemos D1 mini (it sends the gas numbers)
ser = serial.Serial("/dev/ttyS0", 9600, timeout=1)


button = Button(16) # the button is on pin 16  # Button help from https://techexplorations.com/guides/rpi/begin/read-a-button-with-gpiozero/

pixels = neopixel.NeoPixel(board.D18, 32) # LED strip on pin 18 (needs root)  # LED strip help from https://magazine.raspberrypi.com/articles/neopixels-python


# LED colours (R, G, B)
col0 = (0,0,0) # off
col1 = (0,100,100) # ready colour
col2 = (100,100,0) # reading colour
col3 = (255,255,255) # camera light

pixels.fill(col0) # turn all LEDs off


def lightscan(pixels):
    # this makes the LEDs do a little show
    n = pixels.n # how many LEDs

    # one white dot goes around
    for i in range(4 * n):
        for j in range(n):
            pixels[j] = (0, 0, 0)
        pixels[i % n] = (255, 255, 255)
        pixels.write()
        sleep(0.025)

    # a dark dot goes left and right on blue
    for i in range(4 * n):
        for j in range(n):
            pixels[j] = (0, 0, 128)
        if (i // n) % 2 == 0:
            pixels[i % n] = (0, 0, 0)
        else:
            pixels[n - 1 - (i % n)] = (0, 0, 0)
        pixels.write()
        sleep(0.025)

    # red goes brighter then darker
    for i in range(0, 4 * 256, 8):
        for j in range(n):
            if (i // 256) % 2 == 0:
                val = i & 0xff
            else:
                val = 255 - (i & 0xff)
            pixels[j] = (val, 0, 0)
        pixels.write()

    # turn them all off
    for i in range(n):
        pixels[i] = (0, 0, 0)
    pixels.write()


# relay pin for the fans
RELAY_PIN = 20
relay = gpiozero.OutputDevice(RELAY_PIN, active_high=True, initial_value=False)  # Relay help from https://docs.sunfounder.com/projects/umsk/en/latest/05_raspberry_pi/pi_lesson30_relay_module.html

relay.off() # fans off


def sensing_cycle():
    # this does one full run (gas -> camera preview -> fans)

    pixels.fill(col1)
    print("")
    print("Sensing system ready")
    print("Press the button to begin")
    print("created by Churchers College")
    print("")

    # press 1: get ready
    button.wait_for_press()

    print("Get the gas sample ready")
    print("Press again when it looks stable")
    print("")

    # LED show while you wait
    lightscan(pixels)

    # press 2: start reading
    button.wait_for_press()
    print("Reading gas now (press to stop)")
    print("")

    time.sleep(2.0)

    # keep reading until button is pressed
    pixels.fill(col2)
    reading = True

    while reading:
        data = ser.read(16) # read some text from the Wemos
        print("Current Gas Level %ammonia per m3:- ", end="")
        print(data.decode('utf-8', 'ignore'))

        # press to stop reading
        if button.is_pressed:
            time.sleep(1.0)
            reading = False

    print("")
    print("Reading stopped")
    print("Camera preview...")
    print("")

    # camera preview (photo line stays off)
    cam = Camera()  # Camera help from https://raspberrytips.com/picamzero-guide-raspberry-pi/
    # more camera help from https://www.raspberrypi.org/blog/picamzero-raspberry-pi-camera-projects-for-beginners/

    pixels.fill(col3) # make it bright for the camera
    cam.start_preview()
    sleep(3)
    #cam.take_photo(f"{home_dir}/Downloads/foodimage.jpg") # saves a photo (OFF for now)
    cam.stop_preview()

    pixels.fill(col0) # LEDs off

    print("")
    print("Fan time!")
    print("")

    # little LED countdown (only LEDs 0 and 1)
    pixels.fill(col1)

    pixels[0] = (128, 0, 0)
    sleep(1)
    pixels[0] = (255, 0, 0)
    sleep(1)

    pixels[1] = (128, 0, 0)
    sleep(1)
    pixels[1] = (255, 0, 0)
    sleep(1)

    # fans on for 10 seconds
    relay.on()
    print(relay.value) # 1 means on
    sleep(10)

    relay.off()
    print(relay.value) # 0 means off

    # flash red to show finished
    pixels[0] = (255, 0, 0)
    pixels[1] = (255, 255, 0)  # (kept as your original pattern)
    sleep(1)

    pixels[0] = (0, 0, 0)
    pixels[1] = (0, 0, 0)

    pixels.fill(col0)
    print("")
    print("Done. Ready for the next one.")


# run forever
while True:
    sensing_cycle()
    sleep(1) # tiny break so it doesn't spam too fast
