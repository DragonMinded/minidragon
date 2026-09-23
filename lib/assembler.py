__last_bytes_consumed: uint8 = 0
__memory_op_lut: const[str[33]] = "ATOPATOCPTOACTOAATOUATOVUTOAVTOA"
__stack_op_lut: const[str[65]] = "ADDPC\x00\x00\x00POPIP\x00\x00\x00PUSHSPC\x00POPSPC\x00\x00LOADA\x00\x00\x00STOREA\x00\x00"
__reg_op_lut: const[str[65]] = "LOADU\x00\x00\x00STOREU\x00\x00LOADV\x00\x00\x00STOREV\x00\x00SWAPAU\x00\x00SWAPAV\x00\x00SWAPUV\x00\x00SWAPPC\x00\x00"


def assembler_assemble(dst: uint16, line: const[str[64]]) -> uint8:
    # TODO: Actually assemble something.
    return 0


def assembler_bytes_consumed() -> uint8:
    return __last_bytes_consumed


def assembler_disassemble(src: uint16) -> str[64]:
    # We'll need to update this throughout.
    global __last_bytes_consumed

    # First, look up the byte at the value
    instruction: uint8 = peek(src)
    __last_bytes_consumed = 1

    # We'll use this repeatedly to check set bits for decoding
    mask: uint8 = instruction & 0b11000000

    # We'll need the operand (6 bits sign extended) for several instructions.
    operand: int8 = instruction & 0b00111111
    if operand & 0b00100000:
        operand |= 0b11000000

    if mask == 0b00000000:
        # JRI instruction
        if operand:
            return f"JRI #{operand + 1}"
        else:
            return "NOP"

    if mask == 0b01000000:
        # ADDI instruction
        return f"ADDI #{operand}"

    mask = instruction & 0b11100000
    if mask == 0b10000000:
        # First group of instructions, most likely to be arithmetic, but source
        # register "0" is PUSHIP.
        source: uint8 = instruction & 0b00011000
        if source == 0b00000:
            # PUSHIP instruction
            return f"PUSHIP #{operand}"

        operation: uint8 = instruction & 0b00000111
        if operation == 0:
            # Currently invalid, might one day be a CMP.
            return f".byte {hex(instruction)}"

        ret: str[5] = "   "
        if operation == 6 or operation == 7:
            # Shift/rotate/rotate carry.
            ret[2] = "L" if operation == 6 else "R"

            if source == 0b01000:
                ret[0] = "R"
                ret[1] = "O"
            elif source == 0b10000:
                ret[0] = "R"
                ret[1] = "C"
            elif source == 0b11000:
                ret[0] = "S"
                ret[1] = "H"

            return ret

        if operation == 1:
            ret = "ADD"
        elif operation == 2:
            ret = "ADC"
        elif operation == 3:
            ret = "AND"
        elif operation == 4:
            ret = "OR"
        elif operation == 5:
            ret = "XOR"

        srcind: char = "\x00"
        if source == 0b01000:
            srcind = "U"
        elif source == 0b10000:
            srcind = "V"

        ret += srcind
        return ret

    if mask == 0b10100000:
        # SUBPCI
        if operand == -1:
            return "DECPC"
        else:
            return f"SUBPCI #{-operand}"

    if mask == 0b11000000:
        # ADDPCI
        if operand:
            return f"ADDPCI #{operand + 1}"
        else:
            return f"INCPC"

    if instruction == 0b11111000:
        # LNGJUMP, takes the next two bytes as an operand.
        dst: uint16 = peek(src + 1)
        __last_bytes_consumed += 2

        return f"LNGJUMP {hex(dst)}"

    if instruction == 0b11111001:
        # LOADI, takes the next byte as an operand.
        imm: uint8 = peek(src + 1)
        __last_bytes_consumed += 1

        return f"LOADI {hex(imm)}"

    # The rest of these are just simple lookups.
    mask = instruction & 0b11111000

    if mask == 0b11100000:
        regop_offset: uint16 = (instruction & 0b00000111)
        regop_offset <<= 3
        regop_offset += cast(uint16, __reg_op_lut)

        regop: str[8] = peek(regop_offset, 7)
        return regop

    if mask == 0b11101000:
        memop_offset: uint16 = (instruction & 0b00000111)
        memop_offset <<= 2
        memop_offset += cast(uint16, __memory_op_lut)

        memop: str[5] = peek(memop_offset, 4)
        return memop

    if mask == 0b11111000:
        stkop_offset: uint16 = (instruction & 0b00000111) - 2
        stkop_offset <<= 3
        stkop_offset += cast(uint16, __stack_op_lut)

        stkop: str[8] = peek(stkop_offset, 7)
        return stkop

    # The rest of these really can't easily be put in a LUT without wasting
    # a lot of space, so just use if statements.
    if instruction == 0b11110000 or instruction == 0b11110110:
        return "INV"

    if instruction == 0b11110010:
        return "SKIPIF CF"
    if instruction == 0b11110011:
        return "SKIPIF !CF"
    if instruction == 0b11110100:
        return "SKIPIF ZF"
    if instruction == 0b11110101:
        return "SKIPIF !ZF"

    # The last two instructions are possibly NEG in the future, but invalid right now.
    return f".byte {hex(instruction)}"
