import network

def connect_to_wifi(ssid, password):
    print('Starting to connect to WiFi')

    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    if not wlan.isconnected():
        print('Trying to connect to WiFi')
        wlan.connect(ssid, password)

        while not wlan.isconnected():
            pass
    
    print('Connected to WiFi:', wlan.ifconfig())