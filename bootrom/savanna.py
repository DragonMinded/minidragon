from hardware.serial import serial_input, serial_send


__addr: uint16 = 0
__BOLD: const[str] = "\033[1m"
__NORMAL: const[str] = "\033[0m"


def savanna_get_int(val: str[32]) -> uint16:
    if val[0] == "#":
        # Decimal number.
        val[0] = " "
        return int(val)

    if val[0] == "%":
        # Binary number.
        accum: uint16 = 0
        ch: char
        for ch in val:
            accum <<= 1
            if ch == "1":
                accum |= 1

        return accum

    # Hex number
    accum: uint16 = 0
    ch: char
    for ch in val:
        accum <<= 4

        possible_int: uint8 = ord(ch) - ord('0')
        if possible_int < 10:
            accum += possible_int
        else:
            possible_int = (ord(ch) & 0b11011111) - ord('A')
            if possible_int < 6:
                accum += possible_int + 10
    return accum


def savanna_print_help() -> void:
    serial_send("Available commands:\n\n")
    serial_send(f"{__BOLD}g addr{__NORMAL}       - go to current address\n")
    serial_send(f"{__BOLD}r [addr]{__NORMAL}     - read byte at current address, optionally specifying address first\n")
    serial_send(f"{__BOLD}w [addr] val{__NORMAL} - write byte at current address, optionally specifying address first\n")
    serial_send(f"{__BOLD}h/?     {__NORMAL}     - show this help\n")
    serial_send("\nAll commands with implicit address increment the address after running.\n")
    serial_send("Prefix any number with # for an integer, or % for a binary number.\n")


def savanna_print_unrecognized(requested: char) -> void:
    serial_send(f"Unrecognized command '{requested}'\n")


def savanna_goto_address(addr: str[32]) -> void:
    global __addr
    __addr = savanna_get_int(addr)


def savanna_read_byte(addr: str[32]) -> void:
    inc: bool = True
    actual: uint16 = __addr

    if addr:
        inc = False
        actual = savanna_get_int(addr)

    val: uint8 = peek(actual)
    if inc:
        global __addr
        __addr += 1

    serial_send(f"{hex(actual)}: {hex(val)}\n")


def savanna_write_byte(addr_and_val: str[32]) -> void:
    inc: bool = True
    actual: uint16 = __addr

    addr: str[32] = ""
    val: str[32] = ""
    seen_space: bool = False
    ch: char

    for ch in addr_and_val:
        if seen_space:
            val += ch
        elif ch == " ":
            seen_space = True
        else:
            addr += ch

    if not val:
        val = addr
        addr = ""

    if addr:
        inc = False
        actual = savanna_get_int(addr)

    val_as_int: uint8 = savanna_get_int(val)
    poke(actual, val_as_int)

    if inc:
        global __addr
        __addr += 1

    serial_send(f"{hex(actual)}: {hex(val_as_int)}\n")


def savanna_mainloop() -> void:
    command: const[str[32]] = serial_input(f"{__BOLD}{hex(__addr)}>{__NORMAL} ", max_length=31)

    if not command:
        return

    requested: char = command[0]
    if requested == "h" or requested == "?":
        savanna_print_help()

    elif requested == "g":
        savanna_goto_address(command[2:])

    elif requested == "r":
        savanna_read_byte(command[2:])

    elif requested == "w":
        savanna_write_byte(command[2:])

    else:
        savanna_print_unrecognized(requested)
