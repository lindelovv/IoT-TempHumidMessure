from machine import Pin
from time import sleep
from dht import DHT11

led = Pin("LED", Pin.OUT)
dht11 = DHT11(Pin(15, Pin.IN, Pin.PULL_UP))

while True:
    led.on()

    dht11.measure()
    temperature = dht11.temperature()
    humidity = dht11.humidity()

    if temperature is None:
        print(chr(27) + "[2J" + "Error: No temperature output to measure.")
    else:
        print(chr(27) + "[2J" + "Temperature:\t" + str(temperature) + " C\nHumidity:\t" + str(humidity) + " %")

    led.off()
    sleep(1200)
