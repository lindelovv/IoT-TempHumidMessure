from machine import Pin, reset, unique_id
import time, dht, network, socket, binascii, private
from lib.umqtt import MQTTClient

led = Pin("LED", Pin.OUT)
dht11 = dht.DHT11(Pin(15, Pin.IN, Pin.PULL_UP))

def get_readings():
    dht11.measure()
    return (dht11.temperature(), dht11.humidity())

def flash_led(led):
    led.on()
    time.sleep(1)
    led.off()

def connect_wifi():
    wifi = network.WLAN(network.STA_IF)
    wifi.active(True)
    wifi.connect(private.NEWWORK_SSID, private.NETWORK_PASSWORD)
    while not wifi.isconnected():
        print('Waiting for connection...')
        time.sleep(1)
    print("Connected to WIFI: " + private.NEWWORK_SSID + " (" + str(wifi.ifconfig()[0]) + ")")
    return wifi.ifconfig()[0]

def open_socket(ip):
    adress = (ip, 80)
    connection = socket.socket()
    connection.setsockopt(socket.AF_INET, socket.SO_REUSEADDR, 1)
    connection.bind(adress)
    connection.listen(1)
    return connection

def callback(topic, msg):
    print("Topic: {}\nMessage: {}".format(topic, msg))

def connect_mqtt():
    print("Attempting to connect to MQTT Broker")
    client = MQTTClient(
        client_id   = binascii.hexlify(unique_id()),
        server      = "io.adafruit.com",
        port        = 1883,
        user        = private.ADAFRUIT_USERNAME,
        password    = private.ADAFRUIT_PASSWORD,
        keepalive   = 60
        )
    try:
        client.connect()
        print("MQTT connected successfully.")
        return client
    except Exception as e:
        print("Error: Could not connect to MQTT Broker; {}{}".format(type(e).__name__, e))
        reset()

def main():
    try:
        ip = connect_wifi()
        connection = open_socket(ip)
        mqtt_client = connect_mqtt()

        while True:
            temperature, humidity = get_readings()

            if temperature is None:
                print("Error: No temperature output to measure.")
            else:
                print("\tTemperature:\t" + str(temperature) + " C\n\tHumidity:\t" + str(humidity) + " %")

            mqtt_client.publish(    private.TEMPERATURE_FEED,    str(temperature).encode()    )
            mqtt_client.publish(    private.HUMIDITY_FEED,       str(humidity).encode()       )
            try:
                mqtt_client.check_msg()
            except:
                print("Error: mqtt_client.check_msg() exception.")
                mqtt_client.disconnect()
                reset()

            flash_led(led)
            time.sleep(60)
    except KeyboardInterrupt:
        reset()

if __name__ == '__main__':
    try:
        main()
    except OSError as e:
        print("Error: " + str(e))
        reset()