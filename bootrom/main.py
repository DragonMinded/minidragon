from serial import (
    serial_init,
    serial_clear,
    serial_send,
    serial_input,
    serial_normal,
    serial_bold,
    serial_reverse,
    serial_underline,
)


def main() -> void:
    # Initialize hardware.
    serial_init()
    serial_clear()

    # Write out a hello world string.
    serial_send("System ready.\n")

    # Core loop.
    while True:
        pass
