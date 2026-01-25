#!/usr/bin/python3
import os
import re
import sys
import asyncio
import json
import subprocess
import logging
import websockets
import gpiod

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
    import random
    return {
        "temperature": round(random.uniform(25, 35), 1),
        "humidity": round(random.uniform(40, 70), 1),
        "no2": round(random.uniform(0.01, 0.08), 3),
        "pm10": round(random.uniform(10, 60), 1),
        "pm25": round(random.uniform(5, 40), 1),
    }

GPIO_CHIP = "gpiochip0"

def set_gpio(gpio_num: int, on: bool):
    line_value = 1 if on else 0

    chip = gpiod.Chip(GPIO_CHIP)
    line = chip.get_line(gpio_num)

    line.request(
        consumer="lsmy-relay",
        type=gpiod.LINE_REQ_DIR_OUT,
        default_val=0
    )

    line.set_value(line_value)
    line.release()

    log.info("GPIO %d set to %s", gpio_num, "ON" if on else "OFF")

def shutdown_provision():
    subprocess.run(["systemctl", "stop", "provision-web-backend"])


async def main():
    async with websockets.serve(handle, "0.0.0.0", WS_PORT):
        log.info("WiFi provision WS running on %d", WS_PORT)

        await asyncio.gather(
            telemetry_task(),
            asyncio.Future()
        )

asyncio.run(main())