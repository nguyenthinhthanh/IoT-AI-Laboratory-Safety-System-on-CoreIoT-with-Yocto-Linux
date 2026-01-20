#!/usr/bin/python3
import ctypes
import sys
import time
import logging

############################################
# PYTHON LIBRARY FOR LSMY LAB MONITORING   #
# - LSMY Hello World Library Example       #
# - Another Library Example                #
############################################

# ====== HELLO WORLD LIBRARY ======
from lsmy_python_lib.hello import say_hello

# ====== ANOTHER LIBRARY ======

############################################



############################################
# C/C++ LIBRARY FOR LSMY LAB MONITORING    #
# - LSMY Hello World Library Example       #
# - Another Library Example                #
############################################

# ====== HELLO WORLD LIBRARY ======
lib = ctypes.CDLL("/usr/lib/liblsmy_hello.so.1")

# Define the function signature
lib.hello_print.restype = None
lib.hello_print.argtypes = []

# ====== ANOTHER LIBRARY ======

############################################


# -------------------------
# Logging Configuration
# -------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

log = logging.getLogger("run-lsmy")


def main():
    log.info("############################################")
    log.info("#           LSMY SYSTEM STARTUP            #")
    log.info("############################################")


    while True:
        try:
            # Call the function from the shared library
            lib.hello_print()

            # Call the Python function
            say_hello()

            time.sleep(5)

        except Exception as e:
            log.exception("Fatal error in main loop")
            time.sleep(2)

if __name__ == "__main__":
    main()
