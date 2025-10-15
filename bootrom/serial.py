# The read/write buffer for our serial chip.
R6551AP_buffer_reg: extern[uint8]

# The status register.
R6551AP_status_reg: extern[uint8]

# The command register.
R6551AP_command_reg: extern[uint8]

# The control register.
R6551AP_control_reg: extern[uint8]

# Constants defined in the R6551AP datasheet.
R6551AP_TDRE: const[uint8] = 0b00010000
R6551AP_RDRF: const[uint8] = 0b00001000


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


def serial_send_byte(byte: const[uint8]) -> void:
    """
    Send a single byte out the serial port, waiting until it is okay to send that
    byte. This means calling this will never overrun the transmit buffer.
    """

    # Read the status reg, make sure we can transmit. If we can transmit,
    # the TDRE bit will be set to 1 to indicate transmit buffer empty.
    global R6551AP_status_reg

    while not bool(R6551AP_status_reg & R6551AP_TDRE):
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
    return bool(R6551AP_status_reg & R6551AP_RDRF)


def serial_recv_byte() -> uint8:
    """
    Read a single byte from the serial port. Note that if there is no byte
    available, it is undefined what value this returns. Check if there is
    a byte with serial_has_byte() first.
    """

    global R6551AP_buffer_reg
    return R6551AP_buffer_reg


def serial_clear() -> void:
    """
    Issues a VT-100 command to clear the screen and move cursor home.
    """
    serial_send("\033[2J\033[H")


def serial_send(data: const[str]) -> void:
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


def serial_recv(echo_input: bool = True, mask_input: bool = False) -> str:
    """
    Receive a string that is terminated with a newline character. That means
    the remote side hit enter. The newline character itself will not be appended
    to the returned buffer. By default, echos the input back to the client.
    """
    accum: str[255] = ""

    global R6551AP_status_reg
    global R6551AP_buffer_reg

    while True:
        # Wait for a byte to become available.
        while not bool(R6551AP_status_reg & R6551AP_RDRF):
            pass

        # Read that byte, append it unless it's the enter key.
        recvd: char = chr(R6551AP_buffer_reg)
        if recvd == "\n":
            # Pressed enter, exit the loop.
            break
        if recvd == "\r":
            # Don't care about \r\n, so ignore, \r part.
            continue
        if recvd == "\x11" or recvd == "\x13":
            # Actual VT-102 seems to send this to us, need to look at manual to
            # figure out why. For now, ignore it.
            continue

        # Echo it back to the serial terminal.
        if echo_input:
            serial_send_byte(ord('*') if mask_input else ord(recvd))

        # Add it to our accumulator.
        accum += recvd

    return accum


def serial_input(prompt: const[str], echo_input: bool = True, mask_input: bool = False) -> str:
    """
    Given a prompt string, send that prompt over serial, then read input until
    the enter key is pressed, echoing the received characters back to the
    serial connection, and then add a newline to the screen before returning.
    """
    serial_send(prompt)

    retval: const[str] = serial_recv(echo_input, mask_input)
    serial_send("\n")

    return retval
