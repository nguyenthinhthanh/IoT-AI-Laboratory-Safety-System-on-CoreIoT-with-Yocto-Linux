import time
import subprocess
import logging
from enum import Enum

# ====== COMMAND RUNNER LIBRARY ======
from lsmy_python_lib.command_runner import run_cmd, run_cmd_with_retry

log = logging.getLogger("wifi-mode")

SYSTEMD_NETWORK_FILE = "/etc/systemd/network/10-wlan0.network"
AP_NETWORK_FILE = "/etc/systemd/network/wlan0-ap.network"
STA_NETWORK_FILE = "/etc/systemd/network/wlan0-sta.network"


class WiFiMode(Enum):
    AP = "ap"
    STA = "sta"


class WiFiModeManager:
    def __init__(self):
        self.mode = WiFiMode.STA
        log.info("WiFiModeManager initialized with mode=%s", self.mode.value)

    def _link_network(self, target: str):
        run_cmd([
            "ln", "-sf", target, SYSTEMD_NETWORK_FILE
        ])

    def _restart_networkd(self):
        run_cmd(["systemctl", "restart", "systemd-networkd"])

    def _wait_for_interface(self, iface: str, timeout: int = 10):
        log.info("Waiting for interface %s...", iface)

        for _ in range(timeout):
            result = subprocess.run(
                ["ip", "link", "show", iface],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            if result.returncode == 0:
                log.info("%s is present", iface)
                return True

            time.sleep(1)

        raise TimeoutError(f"Interface {iface} not available")


    def switch_to_ap(self):
        log.info("========== SWITCH TO AP MODE ==========")
        self.mode = WiFiMode.AP

        self._link_network(AP_NETWORK_FILE)
        self._restart_networkd()

        run_cmd(["systemctl", "stop", "wpa_supplicant"])
        self._wait_for_interface("wlan0", timeout=10)
        run_cmd_with_retry(["systemctl", "start", "hostapd"], retries=5, delay=2)
        run_cmd_with_retry(["systemctl", "start", "dnsmasq"], retries=5, delay=2)

        log.info("AP mode enabled")

    def switch_to_sta(self):
        log.info("========== SWITCH TO STA MODE ==========")
        self.mode = WiFiMode.STA

        self._link_network(STA_NETWORK_FILE)
        self._restart_networkd()

        run_cmd(["systemctl", "stop", "hostapd"])
        run_cmd(["systemctl", "stop", "dnsmasq"])
        run_cmd(["systemctl", "start", "wpa_supplicant"])

        log.info("STA mode enabled")

    # Cleanup function to reset WiFi state
    def cleanup_wifi(self):
        log.info("========== CLEANUP WIFI STATE ==========")

        # Stop AP-related services
        run_cmd(["systemctl", "stop", "hostapd"], check=False)
        run_cmd(["systemctl", "stop", "dnsmasq"], check=False)

        # Stop STA service
        run_cmd(["systemctl", "stop", "wpa_supplicant"], check=False)
        # Restore default network config (STA)
        self._link_network(STA_NETWORK_FILE)

        # Restart network stack
        self._restart_networkd()

        self.mode = WiFiMode.STA
        log.info("WiFi state cleaned, system returned to STA baseline")
