# The read/write buffer for our serial chip.
R6551AP_buffer_reg: extern[uint8]

# The status register.
R6551AP_status_reg: extern[uint8]

# The command register.
R6551AP_command_reg: extern[uint8]

# The control register.
R6551AP_control_reg: extern[uint8]


def serial_init() -> void:
    """
    Initialize the R6551AP to 9600 baud 8N1, using the internal baud generator
    based on an external crystal.
    """

    # Reset the chip by writing to the status reg.
    global R6551AP_status_reg
    R6551AP_status_reg = 0b00000000

    # Initialize with no parity, IRQ disabled, transmitter enabled.
    global R6551AP_command_reg
    R6551AP_command_reg = 0b00001011

    # Initialize to 9600 baud, 1 stop bit, no parity, internal clock.
    global R6551AP_control_reg
    R6551AP_control_reg = 0b00011110


def serial_send_byte(byte: uint8) -> void:
    """
    Send a single byte out the serial port, waiting until it is okay to send that
    byte. This means calling this will never overrun the transmit buffer.
    """

    # Read the status reg, make sure we can transmit. If we can transmit,
    # the TDRE bit will be set to 1 to indicate transmit buffer empty.
    global R6551AP_status_reg
    while not bool(R6551AP_status_reg & 0b00010000):
        pass

    # Actuall write a byte to the serial buffer.
    global R6551AP_buffer_reg
    R6551AP_buffer_reg = byte


def serial_has_byte() -> bool:
    """
    Returns True if there is a byte waiting to be read on the serial port,
    and False otherwise.
    """

    # The RDRF bit will be set to 1 if the receive data register is full.
    global R6551AP_status_reg
    return bool(R6551AP_status_reg & 0b00001000)


def serial_recv_byte() -> uint8:
    """
    Read a single byte from the serial port. Note that if there is no byte
    available, it is undefined what value this returns. Check if there is
    a byte with serial_has_byte() first.
    """

    global R6551AP_buffer_reg
    return R6551AP_buffer_reg


def serial_send(data: str) -> void:
    """
    Given a string, write that data to the serial port. Note that you are
    responsible for adding your own newline to the end, unlile python's
    print().
    """

    offset: uint8 = 0
    while True:
        byte: char = data[offset]
        if not bool(byte):
            return

        serial_send_byte(ord(byte))
        offset += 1


def serial_recv() -> str[255]:
    """
    Receive a string that is terminated with a newline character. That means
    the remote side hit enter.
    """
    return ""
