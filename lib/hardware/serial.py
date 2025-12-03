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



def serial_send_byte(byte: const[uint8]) -> extern[void]: ...
    # Send a single byte out the serial port, waiting until it is okay to send that
    # byte. This means calling this will never overrun the transmit buffer.


def serial_has_byte() -> bool:
    """
    Returns True if there is a byte waiting to be read on the serial port,
    and False otherwise.
    """

    # The RDRF bit will be set to 1 if the receive data register is full.
    return bool(R6551AP_status_reg & R6551AP_RDRF)


def serial_recv_byte() -> uint8:
    """
    Read a single byte from the serial port. Note that if there is no byte
    available, it is undefined what value this returns. Check if there is
    a byte with serial_has_byte() first.
    """

    return R6551AP_buffer_reg


def serial_clear() -> void:
    """
    Issues a VT-100 command to clear the screen and move cursor home. Also
    makes sure that the text is in normal mode.
    """
    serial_send("\033[2J\033[H\033[0m")


def serial_normal() -> void:
    """
    Issues a VT-100 command to set the normal text mode.
    """
    serial_send("\033[0m")


def serial_bold() -> void:
    """
    Issues a VT-100 command to set the bold text mode.
    """
    serial_send("\033[1m")


def serial_underline() -> void:
    """
    Issues a VT-100 command to set the underline text mode.
    """
    serial_send("\033[4m")


def serial_reverse() -> void:
    """
    Issues a VT-100 command to set the reverse text mode.
    """
    serial_send("\033[7m")


def serial_move(row: uint8, col: uint8) -> void:
    """
    Moves the cursor to the specified row and column. This is one-indexed, so 1, 1 would be the upper left
    of the terminal. Remember that a VT-100 has 24 rows and 80 columns.
    """

    # Cap off our row and column, using unsigned integer wraparound to our advantage. Avoid a costly
    # comparison operation for numbers we know are safe.
    row -= 1
    col -= 1
    if (row & 0xF0) and row > 23:
        row = 23
    if (row & 0xC0) and col > 79:
        col = 79

    # Send the escape sequence to move our cursor.
    serial_send("\033[")
    serial_send(_serial_lut(row))
    serial_send_byte(ord(";"))
    serial_send(_serial_lut(col))
    serial_send_byte(ord("H"))


def _serial_lut(val: uint8) -> extern[const[str]]: ...
    # Look up the string conversion for a particular val given we precalculated these for speed.


def serial_send(data: const[str]) -> void:
    """
    Given a string, write that data to the serial port. Note that you are
    responsible for adding your own newline to the end, unlile python's
    print().
    """

    byte: char
    for byte in data:
        # Flow control must be handled here, so we don't overwhelm the serial terminal.
        if R6551AP_status_reg & R6551AP_RDRF:
            recvd: const[uint8] = R6551AP_buffer_reg

            # Check to ensure we didn't receive an XOFF.
            if recvd == 0x13:
                # We did! Wait until we get an XON.
                while True:
                    while not R6551AP_status_reg & R6551AP_RDRF:
                        pass

                    if R6551AP_buffer_reg == 0x11:
                        break

            # Check if we received an escape code, which means we'll have to consume
            # the entire sequence if we don't want to corrupt a future read.
            elif recvd == 0o33:
                # Don't care about escape sequences sent to us, read until we get to the end.
                while True:
                    while not R6551AP_status_reg & R6551AP_RDRF:
                        pass

                    # Escape codes always start with an escape character, and always end with a letter.
                    # We can check for upper and lowercase letters by always clearing the lowercase bit.
                    # We can save a comparison (which is extremely slow due to being SW implemented) by
                    # subtracting the low comparison value and relying on overflow wraparound to put values
                    # lower than the start above the high comparison.
                    if (R6551AP_buffer_reg & 0b11011111) - ord('A') < 26:
                        break

        serial_send_byte(ord(byte))


def serial_recv(max_length: uint8 = 127, echo_input: bool = True, mask_input: bool = False, allow_empty: bool = True) -> str:
    """
    Receive a string that is terminated with a newline character. That means
    the remote side hit enter. The newline character itself will not be appended
    to the returned buffer. By default, echos the input back to the client.
    """
    accum: str[127] = ""
    length: uint8 = 0

    while True:
        # Wait for a byte to become available.
        while not R6551AP_status_reg & R6551AP_RDRF:
            pass

        # Read that byte, append it unless it's the enter key.
        recvd: char = chr(R6551AP_buffer_reg)
        if recvd == "\033":
            # Don't care about escape sequences sent to us, read until we get to the end.
            while True:
                while not R6551AP_status_reg & R6551AP_RDRF:
                    pass

                # Escape codes always start with an escape character, and always end with a letter.
                # We can check for upper and lowercase letters by always clearing the lowercase bit.
                # We can save a comparison (which is extremely slow due to being SW implemented) by
                # subtracting the low comparison value and relying on overflow wraparound to put values
                # lower than the start above the high comparison.
                if (R6551AP_buffer_reg & 0b11011111) - ord('A') < 26:
                    break

            # Now that we dropped the escape code, try again.
            continue

        if recvd == "\n":
            # Pressed enter, exit the loop if we're allowed to have empty input.
            if allow_empty or length:
                break
            else:
                continue

        if recvd == "\r":
            # Don't care about \r\n, so ignore, \r part.
            continue

        if recvd == "\x13":
            # Got an XOFF, wait until we get an XON to continue.
            while True:
                while not R6551AP_status_reg & R6551AP_RDRF:
                    pass

                if R6551AP_buffer_reg == 0x11:
                    break

            continue

        if recvd == "\x08":
            # Backspace has its own handling.
            if length:
                length -= 1
                accum = accum[:length]

                # Erase last letter.
                if echo_input:
                    serial_send_byte(ord("\x08"))
                    serial_send_byte(ord(" "))
                    serial_send_byte(ord("\x08"))

            continue

        if length != max_length:
            # Echo it back to the serial terminal.
            if echo_input:
                serial_send_byte(ord('*') if mask_input else ord(recvd))

            # Add it to our accumulator.
            accum += recvd
            length += 1

    return accum


def serial_input(prompt: const[str], max_length: uint8 = 127, echo_input: bool = True, mask_input: bool = False, allow_empty: bool = True) -> str:
    """
    Given a prompt string, send that prompt over serial, then read input until
    the enter key is pressed, echoing the received characters back to the
    serial connection, and then add a newline to the screen before returning.
    """
    serial_send(prompt)

    retval: const[str] = serial_recv(max_length, echo_input, mask_input, allow_empty)
    serial_send_byte(ord("\n"))

    return retval
