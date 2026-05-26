# iot-command-control
A lightweight IoT command &amp; control system using MQTT, FastAPI, and SQLite — remotely execute shell commands on Linux devices from a Windows host.
## Features

- 🖥️ Execute any shell command on a remote Linux device
- 📡 MQTT pub/sub messaging for real-time communication
- 💾 Stores command responses in SQLite for retrieval
- 🔁 Device heartbeat every 30 seconds
- 🌐 REST API with auto-generated Swagger UI
- 🪶 Lightweight — no cloud dependency, fully self-hosted

## Tech Stack

| Component | Technology |
|---|---|
| Transport protocol | MQTT (Mosquitto) |
| API server | FastAPI + Uvicorn |
| Database | SQLite via SQLAlchemy |
| Device agent | Python (paho-mqtt) |
| Command execution | subprocess |

## Project Structure
├── db.py               # Database engine and session setup
├── models.py           # SQLAlchemy models (Device, CommandResponse)
├── mqtt_handler.py     # MQTT client — handles status and responses
├── server.py           # FastAPI app — REST endpoints
├── agent.py            # Ubuntu device agent — executes commands
└── requirements.txt    # Python dependencies

## Getting Started

### Prerequisites

- Python 3.8+
- [Mosquitto MQTT broker](https://mosquitto.org/download/) installed on Windows
- Both machines on the same local network

### Windows (Hub)

1. Install and start Mosquitto:
   - Add to `mosquitto.conf`:
  
   - listener 1883
 allow_anonymous true

- Start the service:
```powershell
     net start mosquitto
```

2. Install dependencies:
```powershell
   pip install -r requirements.txt
```

3. Start the server:
```powershell
   uvicorn server:app --reload
```

4. Visit `http://127.0.0.1:8000/docs` to access the API.

### Ubuntu (Agent)

1. Edit `agent.py` and set your Windows machine's local IP:
```python
   BROKER = "192.168.x.x"  # your Windows IP (run ipconfig to find it)
```

2. Install dependencies:
```bash
   pip install -r requirements.txt
```

3. Run the agent:
```bash
   python3 agent.py
```

## Usage

### Send a command to the Linux device

```bash
curl -X POST "http://127.0.0.1:8000/devices/linux001/command" \
  -H "Content-Type: application/json" \
  -d '{"cmd": "whoami"}'
```

### Read the response

```bash
curl http://127.0.0.1:8000/devices/linux001/responses
```

### Available endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/devices` | List all connected devices |
| POST | `/devices/{id}/command` | Send a shell command |
| GET | `/devices/{id}/responses` | Get last 20 command responses |

### Supported commands (examples)

Any valid Linux shell command works:

```json
{ "cmd": "whoami" }
{ "cmd": "uptime" }
{ "cmd": "df -h" }
{ "cmd": "ls -la /home" }
{ "cmd": "cat /etc/os-release" }
{ "cmd": "touch myfile.txt" }
```

## MQTT Topics

| Topic | Direction | Purpose |
|---|---|---|
| `devices/{id}/commands` | Windows → Ubuntu | Send shell command |
| `devices/{id}/response` | Ubuntu → Windows | Command output |
| `devices/{id}/status` | Ubuntu → Windows | Heartbeat / online status |

## Security Notice

This project is intended for **local network use only**. It allows arbitrary 
shell command execution on the target device. Do not expose the FastAPI server 
or MQTT broker to the public internet without adding:

- Authentication on the API (e.g. API keys or OAuth)
- TLS encryption on the MQTT broker
- A command allowlist on the agent

## License

MIT
