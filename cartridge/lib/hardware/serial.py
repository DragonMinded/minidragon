# Returns True if there is a byte waiting to be read on the serial port,
# and False otherwise.
def serial_has_byte() -> extern[bool]: ...


# Read a single byte from the serial port. Note that if there is no byte
# available, it is undefined what value this returns. Check if there is
# a byte with serial_has_byte() first.
def serial_recv_byte() -> extern[uint8]: ...


# Send a single byte out the serial port, waiting until it is okay to send that
# byte. This means calling this will never overrun the transmit buffer.
def serial_send_byte(byte: const[uint8]) -> extern[void]: ...


# Issues a VT-100 command to clear the screen and move cursor home. Also
# makes sure that the text is in normal mode.
def serial_clear() -> extern[void]: ...


# Issues a VT-100 command to set the normal text mode.
def serial_normal() -> extern[void]: ...


# Issues a VT-100 command to set the bold text mode.
def serial_bold() -> extern[void]: ...


# Issues a VT-100 command to set the underline text mode.
def serial_underline() -> extern[void]: ...


# Issues a VT-100 command to set the reverse text mode.
def serial_reverse() -> extern[void]: ...


# Moves the cursor to the specified row and column. This is one-indexed, so 1, 1 would be the upper left
# of the terminal. Remember that a VT-100 has 24 rows and 80 columns.
def serial_move(row: uint8, col: uint8) -> extern[void]: ...


# Given a string, write that data to the serial port. Note that you are
# responsible for adding your own newline to the end, unlile python's
# print().
def serial_send(data: const[str]) -> extern[void]: ...


# Receive a string that is terminated with a newline character. That means
# the remote side hit enter. The newline character itself will not be appended
# to the returned buffer. By default, echos the input back to the client.
def serial_recv(max_length: uint8 = 127, echo_input: bool = True, mask_input: bool = False, allow_empty: bool = True) -> extern[str]: ...


# Given a prompt string, send that prompt over serial, then read input until
# the enter key is pressed, echoing the received characters back to the
# serial connection, and then add a newline to the screen before returning.
def serial_input(prompt: const[str], max_length: uint8 = 127, echo_input: bool = True, mask_input: bool = False, allow_empty: bool = True) -> extern[str]: ...
