#!/usr/bin/python3
import ctypes

from lsmy_python_lib.hello import say_hello

# Load shared library
lib = ctypes.CDLL("/usr/lib/liblsmy_hello.so.1")

# Define the function signature
lib.hello_print.restype = None
lib.hello_print.argtypes = []

# Call the function from the shared library
lib.hello_print()

# Call the Python function
say_hello()
