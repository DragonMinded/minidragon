import sys

from hardware.serial import (
    serial_clear,
    serial_send,
    serial_recv,
    serial_move,
)


def main() -> void:
    # Clear the screen from the boot ROM's display.
    serial_clear()

    # Write out version information that we were built off of.
    serial_send(f"MiniDragon v{sys.version}\n")

    # Display hello world.
    serial_send("Hello, world!\n")
    serial_move(24, 1)
    serial_send("Press [ENTER] to return to boot ROM")
    serial_move(24, 80)

    # Wait until enter pressed.
    serial_recv(echo_input=False, allow_empty=True)
