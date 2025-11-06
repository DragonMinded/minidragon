from serial import (
    serial_init,
    serial_clear,
    serial_send,
    serial_input,
)
from fixed import strtofixed, fixedtostr


def main() -> void:
    # Initialize hardware.
    serial_init()
    serial_clear()

    # Grab a fixed point decimal number.
    number1: const[str] = serial_input("Enter a number: ", allow_empty=False)
    fixed1: int32 = strtofixed(number1, 3, 12)

    number2: const[str] = serial_input("Enter another number: ", allow_empty=False)
    fixed2: int32 = strtofixed(number2, 3, 12)

    approx: const[str] = fixedtostr(fixed1 + fixed2, 3, 12)
    serial_send(f"Approximate addition is: {approx}\n")
