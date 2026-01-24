#!/usr/bin/python3
import asyncio
import json
import subprocess
import logging
import websockets

log = logging.getLogger("provision-webserver-backend")

WS_PORT = 8765

async def handle(ws):
    async for msg in ws:
        log.info("RX: %s", msg)
        data = json.loads(msg)

        if data.get("page") == "setting":
            ssid = data["value"]["ssid"]
            password = data["value"]["password"]

            if ssid is None or ssid == "":
                await ws.send(json.dumps({
                    "status": "error",
                    "msg": "SSID is required"
                }))
                return
            else:
                configure_wifi(ssid, password)

                await ws.send(json.dumps({
                "status": "ok",
                "msg": "WiFi configured, rebooting..."
                }))


def configure_wifi(ssid, password):
    log.info("Configuring WiFi: %s", ssid)

    with open("/etc/wpa_supplicant.conf", "w") as f:
        f.write(f"""
ctrl_interface=/var/run/wpa_supplicant
ctrl_interface_group=0
update_config=1
country=VN
                
network={{
    ssid="{ssid}"
    psk="{password}"
}}
""")

def shutdown_provision():
    subprocess.run(["systemctl", "stop", "provision-web-backend"])


async def main():
    async with websockets.serve(handle, "0.0.0.0", WS_PORT):
        log.info("WiFi provision WS running")
        await asyncio.Future()

asyncio.run(main())