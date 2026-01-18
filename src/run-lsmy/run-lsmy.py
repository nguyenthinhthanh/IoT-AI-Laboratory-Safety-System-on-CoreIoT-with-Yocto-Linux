import ctypes

# Load shared library
lib = ctypes.CDLL("liblsmy_hello.so")

# Define the function signature
lib.hello_print.restype = None
lib.hello_print.argtypes = []

# Call the function from the shared library
lib.hello_print()
