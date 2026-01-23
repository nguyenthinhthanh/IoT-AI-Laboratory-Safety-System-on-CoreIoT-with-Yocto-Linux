import time
import subprocess
import logging
from enum import Enum

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

    def _run(self, cmd: list[str], check: bool = True):
        log.debug("Running command: %s", " ".join(cmd))
        result = subprocess.run(cmd, check=check)
        return result.returncode == 0

    def _run_with_retry(
        self,
        cmd: list[str],
        retries: int = 3,
        delay: float = 2.0,
    ):
        for attempt in range(1, retries + 1):
            log.info(
                "Exec (attempt %d/%d): %s",
                attempt,
                retries,
                " ".join(cmd),
            )

            if self._run(cmd, False):
                return True

            if attempt < retries:
                log.warning("Retrying in %.1fs...", delay)
                time.sleep(delay)

        raise RuntimeError(f"Command failed after {retries} attempts: {' '.join(cmd)}")

    def _link_network(self, target: str):
        self._run([
            "ln", "-sf", target, SYSTEMD_NETWORK_FILE
        ])

    def _restart_networkd(self):
        self._run(["systemctl", "restart", "systemd-networkd"])

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

        self._run(["systemctl", "stop", "wpa_supplicant"])
        self._wait_for_interface("wlan0", timeout=10)
        self._run_with_retry(["systemctl", "start", "hostapd"], retries=5, delay=2)
        self._run_with_retry(["systemctl", "start", "dnsmasq"], retries=5, delay=2)

        log.info("AP mode enabled")

    def switch_to_sta(self):
        log.info("========== SWITCH TO STA MODE ==========")
        self.mode = WiFiMode.STA

        self._link_network(STA_NETWORK_FILE)
        self._restart_networkd()

        self._run(["systemctl", "stop", "hostapd"])
        self._run(["systemctl", "stop", "dnsmasq"])
        self._run(["systemctl", "start", "wpa_supplicant"])

        log.info("STA mode enabled")

    # Cleanup function to reset WiFi state
    def cleanup_wifi(self):
        log.info("========== CLEANUP WIFI STATE ==========")

        # Stop AP-related services
        self._run(["systemctl", "stop", "hostapd"], check=False)
        self._run(["systemctl", "stop", "dnsmasq"], check=False)

        # Stop STA service
        self._run(["systemctl", "stop", "wpa_supplicant"], check=False)

        # Restore default network config (STA)
        self._link_network(STA_NETWORK_FILE)

        # Restart network stack
        self._restart_networkd()

        self.mode = WiFiMode.STA
        log.info("WiFi state cleaned, system returned to STA baseline")
