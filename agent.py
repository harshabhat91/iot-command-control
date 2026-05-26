import paho.mqtt.client as mqtt
import json
import socket
import subprocess
import time

DEVICE_ID = "linux001"
BROKER = "192.168.0.133"

def send_status(client, status="online"):
    payload = {
        "device_id": DEVICE_ID,
        "status": status
    }
    client.publish(
        f"devices/{DEVICE_ID}/status",
        json.dumps(payload)
    )

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ Connected to broker")
        client.subscribe(f"devices/{DEVICE_ID}/commands")
        send_status(client)
    else:
        print(f"❌ Connection failed with code {rc}")

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        cmd = payload.get("cmd", "").strip()

        print(f"📥 Command received: {cmd}")

        if not cmd:
            result = "error: empty command"
        else:
            result = subprocess.getoutput(cmd)

        response = {
            "device_id": DEVICE_ID,
            "command": cmd,
            "result": result
        }

        client.publish(
            f"devices/{DEVICE_ID}/response",
            json.dumps(response)
        )
        print(f"📤 Response sent: {result}")

    except Exception as e:
        print(f"❌ Error handling message: {e}")

def on_disconnect(client, userdata, rc):
    print(f"⚠️ Disconnected (rc={rc}), reconnecting...")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.on_disconnect = on_disconnect

client.connect(BROKER, 1883, 60)
client.loop_start()

last_status_time = time.time()

try:
    while True:
        if time.time() - last_status_time >= 30:
            send_status(client)
            last_status_time = time.time()
        time.sleep(1)
except KeyboardInterrupt:
    print("🛑 Shutting down agent...")
    send_status(client, status="offline")
    time.sleep(1)
    client.loop_stop()
    client.disconnect()
