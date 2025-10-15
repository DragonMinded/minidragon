from serial import serial_init, serial_clear, serial_send, serial_input


def main() -> void:
    # Initialize hardware.
    serial_init()
    serial_clear()

    # Write out a hello world string.
    serial_send("Hello, world!\n")

    # Prompt for input.
    name: const[str] = serial_input("Enter your name: ")
    serial_send(f"Greetings, {name}!\n")

    # Core loop.
    while True:
        pass
