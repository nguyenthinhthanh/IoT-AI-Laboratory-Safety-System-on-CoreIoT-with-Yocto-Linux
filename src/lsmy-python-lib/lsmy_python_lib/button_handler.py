from periphery import GPIO
import time
import logging

# ====== WIFI MODE LIBRARY ======
from lsmy_python_lib.wifi_mode_manager import WiFiModeManager

# ====== WIFI CONFIG LIBRARY ======
from lsmy_python_lib.wifi_config_manager import reset_wifi_config

log = logging.getLogger("button-handler")

BUTTON_PIN = 17

def execute_full_reset(wifi_manager: WiFiModeManager):
    log.warning("!!! STARTING FACTORY RESET !!!")

    # Clear WiFi configurations
    reset_wifi_config()
    # Disconnect WiFi
    wifi_manager.cleanup_wifi()

    log.info("Reset complete. WiFi disconnected and Config cleared.")

def monitor_button_reset(wifi_manager: WiFiModeManager):
    try:
        button = GPIO(BUTTON_PIN, "in")
        button.edge = "both"
        
        press_start = 0
        log.info(f"Button monitor active on GPIO {BUTTON_PIN}")

        while True:
            if button.poll(timeout=None):
                state = button.read()
                
                if state == False:
                    press_start = time.time()
                else:
                    if press_start > 0:
                        duration = time.time() - press_start
                        if duration >= 3.0:
                            execute_full_reset(wifi_manager)
                        press_start = 0
    except Exception as e:
        log.error(f"GPIO Error: {e}")