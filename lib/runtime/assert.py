from hardware.serial import serial_send, serial_send_byte


def assert_print(line: const[str], message: const[str]) -> void:
    """
    Display an assert statement to whatever is available from this stdlib.
    Right now, this is hooked into the VT-100 serial support.
    """

    serial_send(line)
    serial_send(":\n** ASSERT **: ")
    serial_send(message)
    serial_send_byte(ord('\n'))
