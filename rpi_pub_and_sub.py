import paho.mqtt.client as mqtt
import time
from grovepi import *
from collections import deque

# Connect buzzer to digital port D2; light sensor to port A0; Temperature sensor to A1
buzzer = 2
lightSensor = 0
TempSensor = 1

# set input and outputs
pinMode(soundSensor,"INPUT")
pinMode(buzzer,"OUTPUT")
pinMode(TempSensor,"INPUT")

time.sleep(1)

manual_control_mode = False

def manual_mode_callback(client, userdata, message):
    global manual_control_mode
    m = str(message.payload, "utf-8")
    print("manual_mode_callback: " + message.topic + " " + "\"" + m + "\"")
    if m == "true":
        manual_control_mode = True
        print("Switching to manual control mode")
    else:
        manual_control_mode = False
        print("Switching to auto control mode")

def on_connect(client, userdata, flags, rc):
    print("Connected to server (i.e., broker) with result code "+str(rc))
    #subscribe to topics of interest here
    client.subscribe("RC_AC/buzzer")
    client.message_callback_add("RC_AC/buzzer", buzzer_callback)


if __name__ == '__main__':
    client = mqtt.Client()
    client.on_connect = on_connect
    client.connect(host="eclipse.usc.edu", port=11000, keepalive=60)
    client.loop_start()
    
    # Use a moving average filter of L=5
    # Initializa a deque
    deck = deque([0, 0, 0, 0, 0])  
    while True:
        lightValue = analogRead(lightSensor)
        deck.popleft()
        deck.append(lightValue)
        avg = sum(deck)/5
        print(avg)
        if avg > 5:
            digitalWrite(buzzer,1)
            
        # publish the light sensor reading
        client.publish("RC_AC/lightSensor", avg)
        time.sleep(0.75)