import json
import uuid
import paho.mqtt.client as mqtt
from datetime import datetime

from db import SessionLocal
from models import Device, CommandResponse

BROKER = "localhost"

client = mqtt.Client()

def handle_status(msg):
    try:
        payload = json.loads(msg.payload.decode())
        db = SessionLocal()
        try:
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
            print("✅ DB UPDATED:", payload["device_id"])
        except Exception as e:
            db.rollback()
            print("ERROR:", e)
        finally:
            db.close()
    except Exception as e:
        print("ERROR parsing status:", e)

def handle_response(msg):
    try:
        payload = json.loads(msg.payload.decode())
        db = SessionLocal()
        try:
            response = CommandResponse(
                id=str(uuid.uuid4()),
                device_id=payload["device_id"],
                command=payload["command"],
                result=payload["result"],
                received_at=datetime.utcnow()
            )
            db.add(response)
            db.commit()
            print("✅ RESPONSE SAVED:", payload)
        except Exception as e:
            db.rollback()
            print("ERROR:", e)
        finally:
            db.close()
    except Exception as e:
        print("ERROR parsing response:", e)

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ MQTT CONNECTED")
        client.subscribe("devices/+/status")
        client.subscribe("devices/+/response")
    else:
        print(f"❌ MQTT connection failed with code {rc}")

def on_message(client, userdata, msg):
    print("🔥 MESSAGE HIT:", msg.topic)
    topic_parts = msg.topic.split("/")
    msg_type = topic_parts[2]

    if msg_type == "status":
        handle_status(msg)
    elif msg_type == "response":
        handle_response(msg)
    else:
        print(f"⚠️ Unknown topic type: {msg.topic}")

def on_disconnect(client, userdata, rc):
    print(f"⚠️ MQTT disconnected (rc={rc})")

def get_client():
    return client

def start_mqtt():
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect

    print("CONNECTING MQTT...")
    client.connect(BROKER, 1883, 60)
    client.loop_forever()