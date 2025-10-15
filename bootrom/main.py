from serial import serial_init, serial_clear, serial_send, serial_input

def main() -> void:
    # Initialize hardware.
    serial_init()
    serial_clear()

    # Write out a hello world string.
    serial_send("Hello, world!\n")

    # Prompt for input.
    name: const[str] = serial_input("Enter your name: ")

    # Work around compiler but where doing string expressions assigned to const
    # destinations causes the compiler to emit code that tries to strcat into
    # ROM. This can be cleaned up as soon as I fix that compiler bug.
    greetings: str[64] = f"Greetings, {name}!\n"
    serial_send(greetings)

    # Core loop.
    while True:
        pass
