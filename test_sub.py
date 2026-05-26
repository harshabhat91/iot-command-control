import paho.mqtt.client as mqtt

def on_connect(client, userdata, flags, rc):
    print("CONNECTED TO BROKER")
    client.subscribe("#")
    print("SUBSCRIBED TO ALL")

def on_message(client, userdata, msg):
    print("MESSAGE RECEIVED")
    print("TOPIC:", msg.topic)
    print("PAYLOAD:", msg.payload.decode())

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
client.on_connect = on_connect
client.on_message = on_message

client.connect("localhost", 1883, 60)
client.loop_forever()