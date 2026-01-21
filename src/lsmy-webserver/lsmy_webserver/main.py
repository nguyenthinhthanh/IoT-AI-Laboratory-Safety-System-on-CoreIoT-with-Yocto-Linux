import logging

# -------------------------
# Logging Configuration
# -------------------------
log = logging.getLogger("lsmy-app")

def webserver_say_hello():
    log.info("Hello world from Webserver!")

if __name__ == "__main__":
    webserver_say_hello()