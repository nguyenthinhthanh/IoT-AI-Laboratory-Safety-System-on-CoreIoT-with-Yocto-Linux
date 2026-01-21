# =============================================================================
#  LSMY Application Runtime
# -----------------------------------------------------------------------------
#  Package     : lsmy_app
#  Role        : Main application runtime
#
#  Responsibilities:
#   - Implement main application execution flow
#   - Run the primary control loop
#   - Orchestrate system components (sensors, AI, core services)
#   - Interface with native C libraries
#   - Manage threads, tasks, and internal state
#   - Handle application-level errors and graceful shutdown
#
#  Invocation:
#   - Launched by the run-lsmy system entrypoint
#   - Must not be executed directly as a standalone script
#
#  IMPORTANT:
#   - This is the core runtime of the LSMY system
#   - No system/bootstrap logic here
#   - No process-level initialization here
#   - Keep clear separation between runtime logic and entrypoint
# =============================================================================

import sys
import time
import signal
import ctypes
import logging
from enum import Enum, auto


############################################
# PYTHON LIBRARY FOR LSMY                  #
# - LSMY Hello World Library Example       #
# - Another Library Example                #
############################################

# ====== HELLO WORLD LIBRARY ======
from lsmy_python_lib.hello import say_hello

# ====== WEBSERVER LIBRARY ======
from lsmy_webserver.main import webserver_say_hello

# ====== ANOTHER LIBRARY ======
# Additional Python library imports can go here


############################################
# C/C++ LIBRARY FOR LSMY LAB MONITORING    #
# - LSMY Hello World Library Example       #
# - Another Library Example                #
############################################

# ====== HELLO WORLD LIBRARY ======
lib = ctypes.CDLL("/usr/lib/liblsmy_hello.so.1")
lib.hello_print.restype = None
lib.hello_print.argtypes = []

# ====== ANOTHER LIBRARY ======
# Additional C/C++ library imports can go here


# -------------------------
# Logging Configuration
# -------------------------
log = logging.getLogger("lsmy-app")


# -------------------------
# Application State
# -------------------------
class AppState(Enum):
    """
    Application lifecycle states.
    """
    INIT = auto()       # Application created, not running yet
    RUNNING = auto()    # Main loop active
    ERROR = auto()      # Fatal error occurred
    STOPPED = auto()    # Application fully stopped


class LsmyApplication:
    """
    LSMY Application
    Controls application lifecycle and main execution flow.
    """

    #-------- Constructor --------
    def __init__(self):
        self.state = AppState.INIT
        self.running = False

    # -------- Public lifecycle --------
    def start(self):
        self._setup_signal_handlers()
        self._startup_sequence()
        self._main_loop()

    def stop(self):
        self._shutdown_sequence()

    # -------- Startup / shutdown --------
    def _startup_sequence(self):
        log.info("############################################")
        log.info("#   LSMY SYSTEM - STARTUP                  #")
        log.info("############################################")

        self._load_configuration()
        self._initialize_services()

        self.state = AppState.RUNNING
        self.running = True

        log.info("LSMY system startup completed")

    def _shutdown_sequence(self):
        log.info("############################################")
        log.info("#   LSMY SYSTEM - SHUTDOWN                 #")
        log.info("############################################")

        self.running = False
        self._stop_services()
        self.state = AppState.STOPPED

        log.info("LSMY system shutdown completed")

    # -------- Initialization --------
    def _load_configuration(self):
        log.info("Loading system configuration")
        pass

    def _initialize_services(self):
        log.info("Initializing core services")
        self._init_sensor_subsystem()
        self._init_ai_subsystem()
        self._init_communication_subsystem()

    def _stop_services(self):
        log.info("Stopping core services")
        pass

    # -------- Signals --------
    def _setup_signal_handlers(self):
        signal.signal(signal.SIGTERM, self._handle_termination)
        signal.signal(signal.SIGINT, self._handle_termination)

    def _handle_termination(self, signum, frame):
        log.info(f"Received termination signal ({signum})")
        self.stop()

    # -------- Main loop --------
    def _main_loop(self):
        log.info("Entering main application loop")

        while self.running:
            self._run_cycle()
            time.sleep(5)

    def _run_cycle(self):
        """
        Single application cycle.
        Placeholder for sensor polling, AI inference, and data publishing.
        """
        # Call the function from the shared library
        lib.hello_print()

        # Call the Python function
        say_hello()

        webserver_say_hello()

        pass

    # -------- Subsystems --------
    def _init_sensor_subsystem(self):
        log.info("Initializing sensor subsystem")
        pass

    def _init_ai_subsystem(self):
        log.info("Initializing AI subsystem")
        pass

    def _init_communication_subsystem(self):
        log.info("Initializing communication subsystem")
        pass
