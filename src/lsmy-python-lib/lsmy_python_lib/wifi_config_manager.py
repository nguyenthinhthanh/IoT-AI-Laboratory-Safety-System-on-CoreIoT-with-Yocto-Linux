import os
import re
import logging
import subprocess
import time
from typing import List, Dict

log = logging.getLogger("wifi-config")

WPA_CONF = "/etc/wpa_supplicant.conf"

HEADER_LINES = [
    "ctrl_interface=/var/run/wpa_supplicant",
    "ctrl_interface_group=0",
    "update_config=1",
    "country=VN",
]

IS_HAVE_WIFI_CONFIG_SIGNAL = False

class WiFiConfigManager:
    def __init__(self):
        log.info("WiFiConfigManager initialized")

    # Get is_have_wifi_config signal
    def get_wifi_config_signal(self) -> bool:
        return IS_HAVE_WIFI_CONFIG_SIGNAL

    # Load WiFi configurations function
    def load_wifi_configs(self, config_path: str = WPA_CONF) -> List[Dict]:
        """
        Load all WiFi network blocks from wpa_supplicant.conf
        """
        if not os.path.exists(config_path):
            return []

        with open(config_path, "r") as f:
            content = f.read()

        networks = re.findall(r'network\s*=\{.*?\n\}', content, re.DOTALL)
        results = []

        for net in networks:
            ssid_match = re.search(r'ssid\s*=\s*"(.+?)"', net)
            psk_match = re.search(r'psk\s*=\s*"(.+?)"', net)

            if not ssid_match:
                continue

            results.append({
                "ssid": ssid_match.group(1),
                "password": psk_match.group(1) if psk_match else None,
                "raw": net.strip(),
            })

        return results

    # Check if WiFi config exists function
    def has_any_wifi_config(self, config_path: str = WPA_CONF) -> bool:
        configs = self.load_wifi_configs(config_path)
        return len(configs) > 0

    # Wait for WiFi connection
    def is_wait_for_wifi(self, interface="wlan0", timeout=10) -> bool:
        start_time = time.time()

        while time.time() - start_time < timeout:
            result = subprocess.run(["wpa_cli", "-i", interface, "status"], 
                                    capture_output=True, text=True)
            status_output = result.stdout
            
            if "wpa_state=COMPLETED" in status_output:
                log.info("WiFi is connected successfully!")
                return True
            
            if "wpa_state=DISCONNECTED" in status_output:
                log.info("WiFi disconnected, retrying...")
                pass
                
            time.sleep(1)

        log.error("WiFi connection timeout!")
        return False
    
    def request_ip(self, interface="wlan0"):
        log.info("Requesting IP address for %s...", interface)
        subprocess.run(["udhcpc", "-i", interface, "-n", "-q"], check=False)

# Update is_have_wifi_config signal
def update_wifi_config_signal(value: bool):
    global IS_HAVE_WIFI_CONFIG_SIGNAL
    IS_HAVE_WIFI_CONFIG_SIGNAL = value
    # log.info("WiFi config signal updated: %s", IS_HAVE_WIFI_CONFIG_SIGNAL)
    
# Configure WiFi function
def configure_wifi(ssid, password):
    """
    Save or update WiFi configuration in wpa_supplicant.conf
    Automatically handles multiple networks.
    """
    log.info("Processing WiFi config for: %s", ssid)

    if password:
        new_network = f'network={{\n    ssid="{ssid}"\n    psk="{password}"\n}}'
    else:
        new_network = f'network={{\n    ssid="{ssid}"\n    key_mgmt=NONE\n}}'
    
    existing_networks = []
    
    if os.path.exists(WPA_CONF):
            with open(WPA_CONF, "r") as f:
                content = f.read()
                
            networks = re.findall(r'network\s*=\{.*?\n\}', content, re.DOTALL)
            
            for net in networks:
                if not re.search(f'ssid\s*=\s*"{re.escape(ssid)}"', net):
                    existing_networks.append(net.strip())
                else:
                    log.info("Found old config for '%s', replacing it...", ssid)

    existing_networks.append(new_network)

    with open(WPA_CONF, "w") as f:
        f.write("\n".join(HEADER_LINES) + "\n\n")
        f.write("\n\n".join(existing_networks) + "\n")

    log.info("Saved WiFi '%s' successfully. Total networks remembered: %d", 
            ssid, len(existing_networks))
    
    # Update the wifi config signal
    update_wifi_config_signal(True)