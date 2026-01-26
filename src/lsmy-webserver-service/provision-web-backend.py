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

# ====== IPC LIBRARY ======
from lsmy_python_lib.ipc import ipc_server_task, LAST_TELEMETRY

# ====== WIFI CONFIG LIBRARY ======
from lsmy_python_lib.wifi_config_manager import configure_wifi, update_wifi_connect_signal

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
                action = data.get("action")
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
                    if action == "connectBtn":
                        # Update the wifi config signal
                        update_wifi_connect_signal(True)
                        await ws.send(json.dumps({
                        "status": "ok",
                        "msg": "WiFi connect signal successfully"
                        }))
                    elif action == "saveBtn":
                        # Configure WiFi
                        update_wifi_connect_signal(False)
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

# WebSocket server task
async def ws_server_task():
    async with websockets.serve(handle, "0.0.0.0", WS_PORT):
        log.info("WiFi provision WS running on %d", WS_PORT)
        await asyncio.Future()

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
    await asyncio.gather(
        ipc_server_task(),
        ws_server_task(),
        telemetry_task(),
    )

asyncio.run(main())