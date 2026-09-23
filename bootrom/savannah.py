from hardware.serial import serial_clear, serial_input, serial_send
from memory import memory_exec


__addr: uint16 = 0


# Filthy trick to determine the first safe byte in RAM.
heap: extern[const[str]]


def savannah_get_int(val: str[32]) -> uint16:
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

        # First check if it's digits 0-9.
        possible_int: uint8 = ord(ch) - ord('0')
        if possible_int < 10:
            accum += possible_int
        else:
            # Now check if it's characters A-F or a-f.
            possible_int = (ord(ch) & 0b11011111) - ord('A')
            if possible_int < 6:
                accum += possible_int + 10

    return accum


def savannah_print_help() -> void:
    serial_send("Available commands:\n\n")
    serial_send(f"\033[1mg addr\033[0m       - go to current address\n")
    serial_send(f"\033[1mx [addr]\033[0m     - execute current address, optionally specifying address first\n")
    serial_send(f"\033[1mr [addr]\033[0m     - read byte at current address, optionally specifying address first\n")
    serial_send(f"\033[1mw [addr] val\033[0m - write byte at current address, optionally specifying address first\n")
    serial_send(f"\033[1md [addr] amt\033[0m - dump bytes at current address, optionally specifying address first\n")
    serial_send(f"\033[1mc\033[0m            - clear the screen\n")
    serial_send(f"\033[1mh/?\033[0m          - show this help\n")
    serial_send("\nAll commands with implicit address increment the address after running.\n")
    serial_send("Prefix any number with # for an integer, or % for a binary number.\n")


def savannah_print_unrecognized(requested: char) -> void:
    serial_send(f"Unrecognized command '{requested}'\n")


def savannah_goto_address(addr: str[32]) -> void:
    global __addr
    __addr = savannah_get_int(addr)


def savannah_exec(addr: str[32]) -> void:
    exec_loc: uint16 = savannah_get_int(addr) if addr else __addr
    memory_exec(exec_loc)


def savannah_read_byte(addr: str[32]) -> void:
    inc: bool = True
    actual: uint16 = __addr

    if addr:
        inc = False
        actual = savannah_get_int(addr)

    val: uint8 = peek(actual)
    if inc:
        global __addr
        __addr += 1

    serial_send(f"{hex(actual)}: {hex(val)}\n")


def savannah_write_byte(addr_and_val: str[32]) -> void:
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
        actual = savannah_get_int(addr)

    val_as_int: uint8 = savannah_get_int(val)
    poke(actual, val_as_int)

    if inc:
        global __addr
        __addr += 1

    serial_send(f"{hex(actual)}: {hex(val_as_int)}\n")


def savannah_dump_bytes(addr_and_amt: str[32]) -> void:
    inc: bool = True
    actual: uint16 = __addr

    addr: str[32] = ""
    amt: str[32] = ""
    seen_space: bool = False
    ch: char

    for ch in addr_and_amt:
        if seen_space:
            amt += ch
        elif ch == " ":
            seen_space = True
        else:
            addr += ch

    if not amt:
        amt = addr
        addr = ""

    if addr:
        inc = False
        actual = savannah_get_int(addr)

    left: uint16 = savannah_get_int(amt)
    spent: uint8 = 0
    off1: uint8 = 8
    off2: uint8 = 8 + (16 * 3)
    start: uint16 = actual
    buf: str[74] = f"{hex(start)}:                                                                 \n"

    while left:
        # First, read the value
        read: uint8 = peek(actual)
        actual += 1
        spent += 1
        if inc:
            global __addr
            __addr += 1

        # Now, output the hex of the value
        hv: str[5] = hex(read)
        buf[off1] = hv[2]
        off1 += 1
        buf[off1] = hv[3]
        off1 += 2

        # Now, if the value is in ASCII range, output it
        if read >= 0x20 and read < 0x7F:
            buf[off2] = chr(read)
        else:
            buf[off2] = '.'
        off2 += 1

        # Now, output it.
        left -= 1
        if spent == 16 or not left:
            serial_send(buf)
            start += 16
            spent = 0
            off1 = 8
            off2 = 8 + (16 * 3)
            buf = f"{hex(start)}:                                                                 \n"


def savannah_init() -> void:
    heaploc: uint16 = cast(uint16, heap)

    serial_send("\nSavannah Monitor for MiniDragon\n")
    serial_send(f"Scratch RAM start at {hex(heaploc)}\n")


def savannah_mainloop() -> void:
    command: const[str[32]] = serial_input(f"\033[1m{hex(__addr)}>\033[0m ", max_length=31)

    if not command:
        return

    requested: char = command[0]
    if requested == "h" or requested == "?":
        savannah_print_help()
        return

    args: const[str[30]] = command[2:]
    if requested == "g":
        savannah_goto_address(args)

    elif requested == "x":
        savannah_exec(args)

    elif requested == "r":
        savannah_read_byte(args)

    elif requested == "w":
        savannah_write_byte(args)

    elif requested == "d":
        savannah_dump_bytes(args)

    elif requested == "c":
        serial_clear()

    else:
        savannah_print_unrecognized(requested)
