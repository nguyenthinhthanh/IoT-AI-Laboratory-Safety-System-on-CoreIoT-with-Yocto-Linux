#!/usr/bin/python3
import os
import re
import sys
import asyncio
import json
import subprocess
import logging
import websockets

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
log = logging.getLogger("provision-webserver-backend")

WS_PORT = 8765

async def handle(ws):
    async for msg in ws:
        log.info("RX: %s", msg)
        data = json.loads(msg)

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
                return
            else:
                configure_wifi(clean_ssid, clean_pw)

                await ws.send(json.dumps({
                "status": "ok",
                "msg": "WiFi configured successfully"
                }))
                return


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

def shutdown_provision():
    subprocess.run(["systemctl", "stop", "provision-web-backend"])


async def main():
    async with websockets.serve(handle, "0.0.0.0", WS_PORT):
        log.info("WiFi provision WS running")
        await asyncio.Future()

asyncio.run(main())