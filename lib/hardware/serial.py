from math.random import random_step


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

# Our cached cursor location.
_cached_cur_row: uint8
_cached_cur_col: uint8
_cached_cur_valid: bool


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

    # Initialize our cursor cache.
    global _cached_cur_valid
    _cached_cur_valid = False


def _serial_send_byte(byte: const[uint8]) -> extern[void]: ...
    # Serial send byte implementation in assembly for speed.


def serial_send_byte(byte: const[uint8]) -> void:
    # Send a single byte out the serial port, waiting until it is okay to send that
    # byte. This means calling this will never overrun the transmit buffer.
    _serial_send_byte(byte)

    # We might have moved the cursor, so invalidate our cache.
    global _cached_cur_valid
    _cached_cur_valid = False


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

    global _cached_cur_row
    _cached_cur_row = 1

    global _cached_cur_col
    _cached_cur_col = 1

    global _cached_cur_valid
    _cached_cur_valid = True


def serial_normal() -> void:
    """
    Issues a VT-100 command to set the normal text mode.
    """
    serial_send("\033[0m")

    # This doesn't change the cursor, don't invalidate our cache.
    global _cached_cur_valid
    _cached_cur_valid = True


def serial_bold() -> void:
    """
    Issues a VT-100 command to set the bold text mode.
    """
    serial_send("\033[1m")

    # This doesn't change the cursor, don't invalidate our cache.
    global _cached_cur_valid
    _cached_cur_valid = True


def serial_underline() -> void:
    """
    Issues a VT-100 command to set the underline text mode.
    """
    serial_send("\033[4m")

    # This doesn't change the cursor, don't invalidate our cache.
    global _cached_cur_valid
    _cached_cur_valid = True


def serial_reverse() -> void:
    """
    Issues a VT-100 command to set the reverse text mode.
    """
    serial_send("\033[7m")

    # This doesn't change the cursor, don't invalidate our cache.
    global _cached_cur_valid
    _cached_cur_valid = True


def serial_pos_row() -> uint8:
    """
    Retrieves the current row that the cursor occupies on the VT-100.
    """
    if not _cached_cur_valid:
        _serial_pos_fetch()

    return _cached_cur_row


def serial_pos_col() -> uint8:
    """
    Retrieves the current column that the cursor occupies on the VT-100.
    """
    if not _cached_cur_valid:
        _serial_pos_fetch()

    return _cached_cur_col


def _serial_pos_fetch() -> void:
    """
    Fetches the terminal cursor position from the connected VT-100.
    """
    global _cached_cur_row
    global _cached_cur_col
    global _cached_cur_valid

    accum: str[16] = ""
    length: uint8 = 0

    serial_send("\033[6n")

    while True:
        # Wait for a byte to become available.
        while not R6551AP_status_reg & R6551AP_RDRF:
            pass

        # Read until we get an escape back acknowledging the request.
        recvd: char = chr(R6551AP_buffer_reg)
        if recvd == "\033":
            break

    while True:
        # Wait for a byte to become available.
        while not R6551AP_status_reg & R6551AP_RDRF:
            pass

        # Read until we get a character back which signifies that we got the whole thing.
        recvd: char = chr(R6551AP_buffer_reg)
        accum[length] = recvd
        length += 1

        if recvd == 'R':
            break

    # Zero our the "R" which was our end of length message.
    accum[length - 1] = '\0'

    # Now, accumulate the row and column out of the response.
    row: str[4] = ""
    col: str[4] = ""
    state: uint8 = 0
    cur: char
    for cur in accum:
        if ord(cur) - ord('0') < 10:
            if state == 0:
                row += cur
            else:
                col += cur
        elif cur == ';':
            state += 1

    _cached_cur_row = int(row)
    _cached_cur_col = int(col)
    _cached_cur_valid = True


def serial_move(row: uint8, col: uint8) -> void:
    """
    Moves the cursor to the specified row and column. This is one-indexed, so 1, 1 would be the upper left
    of the terminal. Remember that a VT-100 has 24 rows and 80 columns.
    """

    global _cached_cur_row
    global _cached_cur_col
    global _cached_cur_valid

    # Cap off our row and column, using unsigned integer wraparound to our advantage. Avoid a costly
    # comparison operation for numbers we know are safe.
    row -= 1
    col -= 1
    if (row & 0xF0) and row > 23:
        row = 23
    if (row & 0xC0) and col > 79:
        col = 79

    _cached_cur_row = row + 1
    _cached_cur_col = col + 1

    # Send the escape sequence to move our cursor.
    serial_send("\033[")
    serial_send(_serial_lut(row))
    _serial_send_byte(ord(";"))
    serial_send(_serial_lut(col))
    _serial_send_byte(ord("H"))

    # We know where the cursor is, so the cache is valid.
    _cached_cur_valid = True


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

        _serial_send_byte(ord(byte))

    # We might have moved the cursor, so invalidate our cache.
    global _cached_cur_valid
    _cached_cur_valid = False


def serial_recv(
    max_length: uint8 = 255,
    echo_input: bool = True,
    echo_newline: bool = False,
    mask_input: bool = False,
    allow_empty: bool = True,
) -> str[256]:
    """
    Receive a string that is terminated with a newline character. That means
    the remote side hit enter. The newline character itself will not be appended
    to the returned buffer. By default, echos the input back to the client except
    for the newline which is skipped.
    """
    accum: str[256] = ""
    length: uint8 = 0

    while True:
        # Wait for a byte to become available.
        while not R6551AP_status_reg & R6551AP_RDRF:
            random_step()

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

                # Erase last letter.
                if echo_input:
                    _serial_send_byte(ord("\x08"))
                    _serial_send_byte(ord(" "))
                    _serial_send_byte(ord("\x08"))

            continue

        if length != max_length:
            # Echo it back to the serial terminal.
            if echo_input:
                _serial_send_byte(ord('*') if mask_input else ord(recvd))

            # Add it to our accumulator. This technically has a bug where we will
            # overwrite the 0th byte with a null if we're concatenating to the
            # last byte in a 256 byte string. However, since we take a byte length
            # in as our max_length, we can never get to that spot, so this is safe.
            accum[length] = recvd
            length += 1

    # Cap of with a null character.
    accum[length] = "\0"

    if echo_newline:
        _serial_send_byte(ord("\n"))

    if echo_input or echo_newline:
        # We might have moved the cursor, so invalidate our cache.
        global _cached_cur_valid
        _cached_cur_valid = False

    return accum


def serial_input(prompt: const[str], max_length: uint8 = 255, echo_input: bool = True, mask_input: bool = False, allow_empty: bool = True) -> str[256]:
    """
    Given a prompt string, send that prompt over serial, then read input until
    the enter key is pressed, echoing the received characters back to the
    serial connection, and then add a newline to the screen before returning.
    """
    serial_send(prompt)
    return serial_recv(max_length=max_length, echo_input=echo_input, echo_newline=True, mask_input=mask_input, allow_empty=allow_empty)
