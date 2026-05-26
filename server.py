from fastapi import FastAPI
from contextlib import asynccontextmanager
import threading
import json

from db import Base, engine, SessionLocal
from models import Device, CommandResponse
from mqtt_handler import start_mqtt, get_client

Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    threading.Thread(target=start_mqtt, daemon=True).start()
    yield

app = FastAPI(lifespan=lifespan)

@app.get("/devices")
def get_devices():
    db = SessionLocal()
    try:
        devices = db.query(Device).all()
        return [
            {
                "device_id": d.device_id,
                "status": d.status,
                "last_seen": d.last_seen
            }
            for d in devices
        ]
    finally:
        db.close()

@app.post("/devices/{device_id}/command")
def send_command(device_id: str, body: dict):
    cmd = body.get("cmd")
    if not cmd:
        return {"error": "cmd is required"}

    get_client().publish(
        f"devices/{device_id}/commands",
        json.dumps({"cmd": cmd})
    )
    return {"status": "command sent", "cmd": cmd}

@app.get("/devices/{device_id}/responses")
def get_responses(device_id: str):
    db = SessionLocal()
    try:
        responses = db.query(CommandResponse)\
            .filter(CommandResponse.device_id == device_id)\
            .order_by(CommandResponse.received_at.desc())\
            .limit(20)\
            .all()
        return [
            {
                "command": r.command,
                "result": r.result,
                "received_at": r.received_at
            }
            for r in responses
        ]
    finally:
        db.close()