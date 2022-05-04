import paho.mqtt.client as mqtt
import os
from flask import Flask, redirect, render_template, request, session, url_for
# Will be used to send data to grafana
from influxdb import InfluxDBClient

app = Flask(__name__)


@app.route('/')
def home():
    global TempValue
    return render_template("index.html", Temperature = TempValue)

@app.route('/submit', methods=['POST', 'GET'])
def submit():
    if request.method == "POST":
        if 'manual' in request.form.keys():
            client.publish("RC_AC/manual", "true")
        else:
            client.publish("RC_AC/manual", "false")
        r = request.form["red"]
        b = request.form["blue"]
        g = request.form["green"]
        client.publish("RC_AC/ledR", r)
        client.publish("RC_AC/ledG", g)
        client.publish("RC_AC/ledB", b)
    return redirect(url_for('home'))
    
def custom_callback(client, userdata, message):
    
    # prints the temperature value 
    print("VM: " + str(message.payload, "utf-8"))
    global TempValue
    TempValue = (float(str(message.payload, "utf-8")))
    # publishes mqtt variables using influxdb
    data = [{
        "measurement": "temp",
        "tags":{"host": "rpi"},
        "fields": {
            "value":TempValue
        }
    }]
    # Write data to grafana
    clientdb.write_points(data)

    
    
def on_connect(client, userdata, flags, rc):
    print("Connected to server (i.e., broker) with result code "+str(rc))
    #subscribe to interested topics here
    client.subscribe("RC_AC/TempSensor")
    client.message_callback_add("RC_AC/TempSensor", custom_callback)


if __name__ == "__main__":
    # Starts influx db client
    clientdb = InfluxDBClient('localhost', 8086, 'admin', 'password', 'mydb')
    clientdb.create_database('mydb')
    clientdb.get_list_database()
    clientdb.switch_database('mydb')
    # Starts mqtt client
    client = mqtt.Client()
    client.on_connect = on_connect
    client.connect(host="eclipse.usc.edu", port=11000, keepalive=60)
    # Begin loop
    client.loop_start()
    
    TempValue = 0
    app.secret_key = os.urandom(12)
    app.run()
