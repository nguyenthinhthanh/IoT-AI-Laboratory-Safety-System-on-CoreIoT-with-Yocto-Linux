#!/usr/bin/python3
import ctypes
import time

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


while True:
    # Call the function from the shared library
    lib.hello_print()

    # Call the Python function
    say_hello()

    time.sleep(5)
