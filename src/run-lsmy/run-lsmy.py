#!/usr/bin/python3
import ctypes

# Load shared library
lib = ctypes.CDLL("/usr/lib/liblsmy_hello.so.1")

# Define the function signature
lib.hello_print.restype = None
lib.hello_print.argtypes = []

# Call the function from the shared library
lib.hello_print()
