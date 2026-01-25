#!/usr/bin/python3
import os
import re
import sys
import asyncio
import json
import subprocess
import logging
import websockets
from periphery import GPIO

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
log = logging.getLogger("provision-webserver-backend")

clients = set()
WS_PORT = 8765
SOCK = "/run/lsmy/provision.sock"

# WebSocket handler
async def handle(ws):
    clients.add(ws)
    log.info("Client connected (%d)", len(clients))

    try:
        async for msg in ws:
            log.info("RX: %s", msg)
            data = json.loads(msg)

            # ================= SETTINGS =================
            if data.get("page") == "setting":
                ssid = data["value"]["ssid"]
                password = data["value"]["password"]

                clean_ssid = ssid.strip() if ssid else ""
                clean_pw = password.strip() if password else ""

                if not clean_ssid:
                    await ws.send(json.dumps({
                        "status": "error",
                        "msg": "SSID is required"
                    }))
                else:
                    configure_wifi(clean_ssid, clean_pw)

                    await ws.send(json.dumps({
                    "status": "ok",
                    "msg": "WiFi configured successfully"
                    }))
            # ================= DEVICE / RELAY =================
            elif data.get("page") == "device":
                log.info("Relay command: %s", data["value"])

                value = data.get("value", {})
                # Here is relay control logic
                try:
                    gpio = int(value.get("gpio"))
                    status = value.get("status")
                    name = value.get("name", "Unknown")

                    if status not in ("ON", "OFF"):
                        raise ValueError("Invalid relay status")

                    set_gpio(gpio, status == "ON")

                    await ws.send(json.dumps({
                        "status": "ok",
                        "msg": f"Relay executed {name} turned {status}",
                        "gpio": gpio,
                        "state": status
                    }))

                except Exception as e:
                    log.error("Relay control failed: %s", e)

                    await ws.send(json.dumps({
                        "status": "error",
                        "msg": str(e)
                    }))

    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        clients.remove(ws)
        log.info("Client disconnected (%d)", len(clients))

# Telemetry broadcast task            
async def telemetry_task():
    while True:
        if clients:
            sensor = read_sensors()
            payload = {
                "clients": len(clients),
                **sensor
            }

            msg = json.dumps(payload)

            await asyncio.gather(
                *[ws.send(msg) for ws in clients],
                return_exceptions=True
            )

            log.info("TX telemetry: %s", msg)

        await asyncio.sleep(5)  

# IPC server handler
LAST_TELEMETRY = {
    "temperature": 0.0,
    "humidity": 0.0,
    "no2": 0.0,
    "pm10": 0.0,
    "pm25": 0.0,
}

async def handle_client(reader, writer):
    try:
        data = await reader.readline()
        if not data:
            return

        req = json.loads(data.decode())
        log.info("IPC RX: %s", req)

        if req.get("cmd") == "send_telemetry":
            telemetry = {
                "temperature": float(req.get("temperature", 0)),
                "humidity": float(req.get("humidity", 0)),
                "no2": float(req.get("no2", 0)),
                "pm10": float(req.get("pm10", 0)),
                "pm25": float(req.get("pm25", 0)),
            }

            log.info("Telemetry received: %s", telemetry)

            LAST_TELEMETRY.update(telemetry)

            resp = {"status": "ok"}
        else:
            resp = {"status": "error", "error": "Unknown command"}

        writer.write((json.dumps(resp) + "\n").encode())
        await writer.drain()

    except Exception:
        log.exception("IPC handler error")
    finally:
        writer.close()

# Helper function
def configure_wifi(ssid, password):
    config_path = "/etc/wpa_supplicant.conf"
    log.info("Processing WiFi config for: %s", ssid)

    if password:
        new_network = f'network={{\n    ssid="{ssid}"\n    psk="{password}"\n}}'
    else:
        new_network = f'network={{\n    ssid="{ssid}"\n    key_mgmt=NONE\n}}'

    header_lines = [
        "ctrl_interface=/var/run/wpa_supplicant",
        "ctrl_interface_group=0",
        "update_config=1",
        "country=VN"
    ]
    
    existing_networks = []
    
    if os.path.exists(config_path):
            with open(config_path, "r") as f:
                content = f.read()
                
            networks = re.findall(r'network\s*=\{.*?\n\}', content, re.DOTALL)
            
            for net in networks:
                if not re.search(f'ssid\s*=\s*"{re.escape(ssid)}"', net):
                    existing_networks.append(net.strip())
                else:
                    log.info("Found old config for '%s', replacing it...", ssid)

    existing_networks.append(new_network)

    with open(config_path, "w") as f:
        f.write("\n".join(header_lines) + "\n\n")
        f.write("\n\n".join(existing_networks) + "\n")

    log.info("Saved WiFi '%s' successfully. Total networks remembered: %d", 
             ssid, len(existing_networks))
    
def read_sensors():
    return {
        "temperature": LAST_TELEMETRY["temperature"],
        "humidity":    LAST_TELEMETRY["humidity"],
        "no2":         LAST_TELEMETRY["no2"],
        "pm10":        LAST_TELEMETRY["pm10"],
        "pm25":        LAST_TELEMETRY["pm25"],
    }

def set_gpio(gpio_num: int, on: bool):
    value = True if on else False

    try:
        gpio = GPIO(gpio_num, "out")
        gpio.write(value)
        gpio.close()

        log.info(
            "GPIO %d set to %s",
            gpio_num,
            "ON" if on else "OFF"
        )

    except Exception as e:
        log.error("GPIO %d control failed: %s", gpio_num, e)
        raise

def shutdown_provision():
    subprocess.run(["systemctl", "stop", "provision-web-backend"])


async def main():
    # IPC server setup
    if os.path.exists(SOCK):
        os.unlink(SOCK)

    server = await asyncio.start_unix_server(handle_client, path=SOCK)
    os.chmod(SOCK, 0o660)

    log.info("IPC server listening on %s", SOCK)
    async with server:
        await server.serve_forever()

    # WebSocket server setup
    async with websockets.serve(handle, "0.0.0.0", WS_PORT):
        log.info("WiFi provision WS running on %d", WS_PORT)

        await asyncio.gather(
            telemetry_task(),
            asyncio.Future()
        )

asyncio.run(main())