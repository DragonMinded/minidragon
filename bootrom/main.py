from serial import serial_init, serial_send

def main() -> void:
    # Initialize hardware.
    serial_init()

    # Write out a hello world string.
    serial_send("Hello, world!\n")

    # Core loop.
    while True:
        pass
