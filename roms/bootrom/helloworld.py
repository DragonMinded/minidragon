from hardware.serial import (
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
    serial_send("Hello, world!\n\n")

    # Prompt for input.
    name: const[str] = serial_input("Enter your name: ", allow_empty=False)
    serial_send(f"Greetings, {name}!\n")
    serial_send(f"Your name was {len(name)} character(s) long!\n\n")

    # Prompt for input.
    secret: const[str] = serial_input("Enter a secret: ", mask_input=True)
    if secret:
        serial_send(f"Your secret was {secret}.\n\n")
    else:
        serial_send(f"You didn't tell me a secret!\n\n")

    # Do some silly stuff.
    serial_bold()
    serial_send("This should be bold.\n")
    serial_normal()
    serial_underline()
    serial_send("This should be underline.\n")
    serial_normal()
    serial_reverse()
    serial_send("This should be reversed.\n")
    serial_normal()
