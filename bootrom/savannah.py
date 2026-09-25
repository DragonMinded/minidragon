from assembler import (
    assembler_assemble,
    assembler_disassemble,
    assembler_bytes_consumed,
    assembler_parse_int,
    ASSEMBLER_ERROR_NONE,
    ASSEMBLER_ERROR_UNRECOGNIZED_INSTRUCTION,
    ASSEMBLER_ERROR_PARAM_OUT_OF_RANGE,
    ASSEMBLER_ERROR_MISSING_PARAM,
)
from hardware.serial import serial_clear, serial_input, serial_send
from memory import memory_exec


__addr: uint16 = 0


# Filthy trick to determine the first safe byte in RAM.
heap: extern[const[str]]


def savannah_print_help() -> void:
    serial_send("Available commands:\n\n")
    serial_send(f"\033[1mg addr\033[0m         - go to current address\n")
    serial_send(f"\033[1mx [addr]\033[0m       - execute current address, optionally specifying address first\n")
    serial_send(f"\033[1mr [addr]\033[0m       - read byte at current address, optionally specifying address first\n")
    serial_send(f"\033[1mw [addr] val\033[0m   - write byte at current address, optionally specifying address first\n")
    serial_send(f"\033[1md [addr] amt\033[0m   - dump bytes at current address, optionally specifying address first\n")
    serial_send(f"\033[1ma instruction\033[0m  - assemble instruction at current address\n")
    serial_send(f"\033[1ml [[addr] amt]\033[0m - list instructions at current address, optionally specifying address first\n")
    serial_send(f"\033[1mc\033[0m              - clear the screen\n")
    serial_send(f"\033[1mh/?\033[0m            - show this help\n")
    serial_send("\nAll commands with implicit address increment the address after running.\n")
    serial_send("Prefix any number with # for an integer, or % for a binary number.\n")


def savannah_print_unrecognized(requested: char) -> void:
    serial_send(f"Unrecognized command '{requested}'\n")


def savannah_goto_address(addr: const[str[30]]) -> void:
    global __addr
    __addr = assembler_parse_int(addr)


def savannah_exec(addr: const[str[30]]) -> void:
    exec_loc: uint16 = assembler_parse_int(addr) if addr else __addr
    memory_exec(exec_loc)


def savannah_read_byte(addr: const[str[30]]) -> void:
    inc: bool = True
    actual: uint16 = __addr

    if addr:
        inc = False
        actual = assembler_parse_int(addr)

    val: uint8 = peek(actual)
    if inc:
        global __addr
        __addr += 1

    serial_send(f"{hex(actual)}: {hex(val)}\n")


def savannah_write_byte(addr_and_val: const[str[30]]) -> void:
    inc: bool = True
    actual: uint16 = __addr

    addr: str[30] = ""
    val: str[30] = ""
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
        actual = assembler_parse_int(addr)

    val_as_int: uint8 = assembler_parse_int(val)
    poke(actual, val_as_int)

    if inc:
        global __addr
        __addr += 1

    serial_send(f"{hex(actual)}: {hex(val_as_int)}\n")


def savannah_dump_bytes(addr_and_amt: const[str[30]]) -> void:
    inc: bool = True
    actual: uint16 = __addr

    addr: str[30] = ""
    amt: str[30] = ""
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
        actual = assembler_parse_int(addr)

    left: uint16 = assembler_parse_int(amt)
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


def savannah_assemble_instruction(instruction: const[str[30]]) -> void:
    global __addr

    result: uint8 = assembler_assemble(__addr, instruction)
    __addr += assembler_bytes_consumed()

    if result == ASSEMBLER_ERROR_NONE:
        # Success!
        serial_send("OK\n")
    elif result == ASSEMBLER_ERROR_UNRECOGNIZED_INSTRUCTION:
        # Bad instruction
        serial_send("Unrecognized instruction\n")
    elif result == ASSEMBLER_ERROR_PARAM_OUT_OF_RANGE:
        # Bad parameter for instruction
        serial_send("Parameter out of range for instruction\n")
    elif result == ASSEMBLER_ERROR_MISSING_PARAM:
        # Missing parameter for instruction
        serial_send("Parameter missing for instruction\n")
    else:
        # Unknown
        serial_send("Unknown error\n")


def savannah_list_instructions(addr_and_amt: const[str[30]]) -> void:
    inc: bool = True
    actual: uint16 = __addr

    addr: str[30] = ""
    amt: str[30] = ""
    if addr_and_amt:
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
            actual = assembler_parse_int(addr)
    else:
        # Default to decoding one instruction
        amt = "1"

    left: uint16 = assembler_parse_int(amt)

    while left:
        # First, disassemble the current address.
        disassembly: const[str[64]] = assembler_disassemble(actual)
        consumed: uint8 = assembler_bytes_consumed()
        serial_send(f"{hex(actual)}: {disassembly}\n")

        # Now, skip past what we disassembled.
        actual += consumed
        left -= 1

        # And increment the global address if we should.
        if inc:
            global __addr
            __addr += consumed


def savannah_init() -> void:
    heaploc: uint16 = cast(uint16, heap)

    serial_send("\nSavannah Monitor for MiniDragon\n")
    serial_send(f"Scratch RAM start at {hex(heaploc)}\n")


def savannah_mainloop() -> void:
    command: const[str[32]] = serial_input(f"\033[1m{hex(__addr)}>\033[0m ", max_length=31)

    if not command:
        return

    requested: char = command[0]
    if requested == "h" or requested == 'H' or requested == "?":
        savannah_print_help()
        return

    args: const[str] = command[2:]
    if requested == "g" or requested == 'G':
        savannah_goto_address(args)

    elif requested == "x" or requested == 'X':
        savannah_exec(args)

    elif requested == "r" or requested == 'R':
        savannah_read_byte(args)

    elif requested == "w" or requested == 'W':
        savannah_write_byte(args)

    elif requested == "d" or requested == 'D':
        savannah_dump_bytes(args)

    elif requested == "a" or requested == 'A':
        savannah_assemble_instruction(args)

    elif requested == "l" or requested == 'L':
        savannah_list_instructions(args)

    elif requested == "c" or requested == 'C':
        serial_clear()

    else:
        savannah_print_unrecognized(requested)
