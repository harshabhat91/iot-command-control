import json
import paho.mqtt.client as mqtt
from datetime import datetime

from db import SessionLocal, Base, engine
from models import Device

Base.metadata.create_all(bind=engine)

BROKER = "localhost"

client = mqtt.Client()

def on_connect(client, userdata, flags, rc):
    print("MQTT CONNECTED")
    client.subscribe("devices/+/status")

def on_message(client, userdata, msg):
    print("🔥 RECEIVED:", msg.topic)

    payload = json.loads(msg.payload.decode())

    db = SessionLocal()

    device = db.query(Device).filter(Device.device_id == payload["device_id"]).first()

    if device:
        device.status = payload["status"]
        device.last_seen = datetime.utcnow()
    else:
        device = Device(
            device_id=payload["device_id"],
            status=payload["status"],
            last_seen=datetime.utcnow()
        )
        db.add(device)

    db.commit()
    db.close()

    print("✅ SAVED:", payload["device_id"])


client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER, 1883, 60)

print("STARTING MQTT LOOP")
client.loop_forever()