__last_bytes_consumed: uint8 = 0
__memory_op_lut: const[str[33]] = "ATOPATOCPTOACTOAATOUATOVUTOAVTOA"
__stack_op_lut: const[str[65]] = "ADDPC\x00\x00\x00POPIP\x00\x00\x00PUSHSPC\x00POPSPC\x00\x00LOADA\x00\x00\x00STOREA\x00\x00"
__reg_op_lut: const[str[65]] = "LOADU\x00\x00\x00STOREU\x00\x00LOADV\x00\x00\x00STOREV\x00\x00SWAPAU\x00\x00SWAPAV\x00\x00SWAPUV\x00\x00SWAPPC\x00\x00"


ASSEMBLER_ERROR_NONE: const[uint8] = 0
ASSEMBLER_ERROR_UNRECOGNIZED_INSTRUCTION: const[uint8] = 1
ASSEMBLER_ERROR_PARAM_OUT_OF_RANGE: const[uint8] = 2
ASSEMBLER_ERROR_MISSING_PARAM: const[uint8] = 3


def assembler_bytes_consumed() -> uint8:
    return __last_bytes_consumed


def assembler_parse_int(val: const[str[30]]) -> uint16:
    if val[0] == "#":
        # Decimal number.
        return int(val[1:])

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


def assembler_assemble(dst: uint16, line: const[str[30]]) -> uint8:
    # We need to recognize the mnemonic that is contained in the line. We do that
    # by implementing a manually unrolled radix tree for speed, because doing a
    # strcmp against every recognized instruction would be insanely slow.
    chr0: char = line[0]
    chr1: char = line[1]
    chr2: char = line[2]
    chr3: char = line[3]
    chr4: char = line[4]
    assembled: uint8 = 0

    # We're going to need to update this, and default to 0 assuming the
    # parse was invalid.
    global __last_bytes_consumed
    __last_bytes_consumed = 0

    if chr1 == 'T' and chr2 == 'O' and chr4 == '\x00':
        # XTOY instructions, figure out which one it is here. They're all
        # one byte long so we can handle this in a big radix unroll.
        if chr0 == 'A':
            # Series of instructions here.
            if chr3 == 'P':
                # ATOP
                assembled = 0b11101000
            elif chr3 == 'C':
                # ATOC
                assembled = 0b11101001
            elif chr3 == 'U':
                # ATOU
                assembled = 0b11101100
            elif chr3 == 'V':
                # ATOV
                assembled = 0b11101101
            else:
                return ASSEMBLER_ERROR_UNRECOGNIZED_INSTRUCTION

        elif chr3 == 'A':
            if chr0 == 'P':
                # PTOA
                assembled = 0b11101010
            elif chr0 == 'C':
                # CTOA
                assembled = 0b11101011
            elif chr0 == 'U':
                # UTOA
                assembled = 0b11101110
            elif chr0 == 'V':
                # VTOA
                assembled = 0b11101111
            else:
                return ASSEMBLER_ERROR_UNRECOGNIZED_INSTRUCTION

        else:
            return ASSEMBLER_ERROR_UNRECOGNIZED_INSTRUCTION

    elif chr0 == 'A':
        if chr1 == 'N' and chr2 == 'D':
            # AND, ANDU, ANDV
            if chr3 == '\x00':
                assembled = 0b10011011
            elif chr3 == 'U' and chr4 == '\x00':
                assembled = 0b10001011
            elif chr3 == 'V' and chr4 == '\x00':
                assembled = 0b10010011
            else:
                return ASSEMBLER_ERROR_UNRECOGNIZED_INSTRUCTION

        elif chr1 == 'D':
            # Variety of ADD instructions.
            if chr2 == 'D':
                if chr3 == '\x00':
                    # ADD
                    assembled = 0b10011001
                elif chr3 == 'U' and chr4 == '\x00':
                    # ADDU
                    assembled = 0b10001001
                elif chr3 == 'V' and chr4 == '\x00':
                    # ADDV
                    assembled = 0b10010001
                elif chr3 == 'I':
                    # ADDI
                    if chr4 != ' ':
                        return ASSEMBLER_ERROR_MISSING_PARAM

                    addiop: int8 = assembler_parse_int(line[5:])
                    addibounds: uint8 = addiop & 0b11100000

                    if addibounds != 0b11100000 and addibounds != 0b00000000:
                        return ASSEMBLER_ERROR_PARAM_OUT_OF_RANGE

                    assembled = 0b01000000 | (addiop & 0b00111111)

                elif chr3 == 'P' and chr4 == 'C':
                    chr5: char = line[5]
                    if chr5 == '\x00':
                        # ADDPC
                        assembled = 0b11111010
                    elif chr5 == 'I':
                        # ADDPCI
                        if line[6] != ' ':
                            return ASSEMBLER_ERROR_MISSING_PARAM

                        addpciop: uint8 = assembler_parse_int(line[7:]) - 1
                        if addpciop & 0b11100000:
                            return ASSEMBLER_ERROR_PARAM_OUT_OF_RANGE

                        assembled = 0b11000000 | addpciop

                    else:
                        return ASSEMBLER_ERROR_UNRECOGNIZED_INSTRUCTION

                else:
                    return ASSEMBLER_ERROR_UNRECOGNIZED_INSTRUCTION

            # Variety of ADC instructions.
            elif chr2 == 'C':
                if chr3 == '\x00':
                    # ADC
                    assembled = 0b10011010
                elif chr3 == 'U' and chr4 == '\x00':
                    # ADCU
                    assembled = 0b10001010
                elif chr3 == 'V' and chr4 == '\x00':
                    # ADCV
                    assembled = 0b10010010
                else:
                    return ASSEMBLER_ERROR_UNRECOGNIZED_INSTRUCTION

        else:
            return ASSEMBLER_ERROR_UNRECOGNIZED_INSTRUCTION

    elif chr0 == 'I':
        # INV instruction is the only one here.
        if chr1 == 'N' and chr2 == 'V' and chr3 == '\x00':
            assembled = 0b11110000

        else:
            return ASSEMBLER_ERROR_UNRECOGNIZED_INSTRUCTION

    elif chr0 == 'J':
        # Only JRI lives here.
        if chr1 == 'R' and chr2 == 'I':
            if chr3 != ' ':
                return ASSEMBLER_ERROR_MISSING_PARAM

            jriop: int8 = assembler_parse_int(line[4:]) - 1
            jribounds: uint8 = jriop & 0b11100000

            if jribounds != 0b11100000 and jribounds != 0b00000000:
                return ASSEMBLER_ERROR_PARAM_OUT_OF_RANGE

            assembled = jriop & 0b00111111

        else:
            return ASSEMBLER_ERROR_UNRECOGNIZED_INSTRUCTION

    elif chr0 == 'L':
        # Various LOAD and LNGJUMP instructions live here.
        if chr1 == 'O' and chr2 == 'A' and chr3 == 'D':
            # Just grab the actual byte value for the instruction.
            if chr4 == 'U' and line[5] == '\x00':
                # LOADU
                assembled = 0b11100000
                __last_bytes_consumed = 1
            elif chr4 == 'V' and line[5] == '\x00':
                # LOADV
                assembled = 0b11100010
                __last_bytes_consumed = 1
            elif chr4 == 'A' and line[5] == '\x00':
                # LOADA
                assembled = 0b11111110
                __last_bytes_consumed = 1

            # This is a special case, where we need to load immediate
            # and that immediate goes into the next slot. So, write
            # the instruction to the destination and increment it, and
            # set the assembled to the parsed value
            elif chr4 == 'I':
                # LOADI
                if line[5] != ' ':
                    return ASSEMBLER_ERROR_MISSING_PARAM

                __last_bytes_consumed = 2

                assembled = assembler_parse_int(line[6:])
                poke(dst, 0b11111001)
                dst += 1

            else:
                return ASSEMBLER_ERROR_UNRECOGNIZED_INSTRUCTION

            poke(dst, assembled)
            return ASSEMBLER_ERROR_NONE

        elif chr1 == 'N' and chr2 == 'G' and chr3 == 'J' and chr4 == 'U' and line[5] == 'M' and line[6] == 'P':
            if line[7] != ' ':
                return ASSEMBLER_ERROR_MISSING_PARAM

            # LNGJUMP instruction, get the value to jump to.
            lngjumpop: uint16 = assembler_parse_int(line[8:])
            poke(dst, 0b11111000)
            poke(dst + 1, lngjumpop)
            __last_bytes_consumed = 3
            return ASSEMBLER_ERROR_NONE

        else:
            return ASSEMBLER_ERROR_UNRECOGNIZED_INSTRUCTION

    elif chr0 == 'O':
        # OR, ORU, ORV
        if chr1 != 'R':
            return ASSEMBLER_ERROR_UNRECOGNIZED_INSTRUCTION

        if chr2 == '\x00':
            assembled = 0b10011100
        elif chr2 == 'U' and chr3 == '\x00':
            assembled = 0b10001100
        elif chr2 == 'V' and chr3 == '\x00':
            assembled = 0b10010100
        else:
            return ASSEMBLER_ERROR_UNRECOGNIZED_INSTRUCTION

    elif chr0 == 'P':
        chr5: char = line[5]
        chr6: char = line[6]

        if chr1 == 'U' and chr2 == 'S' and chr3 == 'H':
            # PUSHIP, PUSHSPC
            if chr4 == 'I' and chr5 == 'P':
                if chr6 != ' ':
                    return ASSEMBLER_ERROR_MISSING_PARAM

                # Need to grab parameter.
                pushipop: int8 = assembler_parse_int(line[6:])
                if pushipop & 0b11111000:
                    return ASSEMBLER_ERROR_PARAM_OUT_OF_RANGE

                assembled = 0b10000000 | pushipop

            elif chr4 == 'S' and chr5 == 'P' and chr6 == 'C' and line[7] == '\x00':
                assembled = 0b11111100

            else:
                return ASSEMBLER_ERROR_UNRECOGNIZED_INSTRUCTION

        elif chr1 == 'O' and chr2 == 'P':
            # POPIP, POPSPC
            if chr3 == 'I' and chr4 == 'P' and chr5 == '\x00':
                assembled = 0b11111011

            elif chr3 == 'S' and chr4 == 'P' and chr5 == 'C' and chr6 == '\x00':
                assembled = 0b11111101

            else:
                return ASSEMBLER_ERROR_UNRECOGNIZED_INSTRUCTION

        else:
            return ASSEMBLER_ERROR_UNRECOGNIZED_INSTRUCTION

    elif chr0 == 'R':
        if chr3 != '\x00':
            return ASSEMBLER_ERROR_UNRECOGNIZED_INSTRUCTION

        # ROL, ROR, RCL, RCR
        if chr1 == 'O':
            assembled = 0b10001110
        elif chr1 == 'C':
            assembled = 0b10010110
        else:
            return ASSEMBLER_ERROR_UNRECOGNIZED_INSTRUCTION

        if chr2 == 'L':
            pass
        elif chr2 == 'R':
            assembled |= 1
        else:
            return ASSEMBLER_ERROR_UNRECOGNIZED_INSTRUCTION

    elif chr0 == 'S':
        chr5: char = line[5]
        chr6: char = line[6]

        if chr1 == 'H' and chr3 == '\x00':
            if chr2 == 'L':
                # SHL
                assembled = 0b10011110
            elif chr2 == 'R':
                # SHL
                assembled = 0b10011111
            else:
                return ASSEMBLER_ERROR_UNRECOGNIZED_INSTRUCTION

        elif chr1 == 'T' and chr2 == 'O' and chr3 == 'R' and chr4 == 'E' and chr6 == '\x00':
            if chr5 == 'U':
                # STOREU
                assembled = 0b11100001
            elif chr5 == 'V':
                # STOREV
                assembled = 0b11100011
            elif chr5 == 'A':
                # STOREA
                assembled = 0b11111111
            else:
                return ASSEMBLER_ERROR_UNRECOGNIZED_INSTRUCTION

        elif chr1 == 'W' and chr2 == 'A' and chr3 == 'P' and chr6 == '\x00':
            if chr4 == 'A' and chr5 == 'U':
                #SWAPAU
                assembled = 0b11100100
            elif chr4 == 'A' and chr5 == 'V':
                #SWAPAU
                assembled = 0b11100101
            elif chr4 == 'U' and chr5 == 'V':
                #SWAPUV
                assembled = 0b11100110
            elif chr4 == 'P' and chr5 == 'C':
                #SWAPPC
                assembled = 0b11100111
            else:
                return ASSEMBLER_ERROR_UNRECOGNIZED_INSTRUCTION

        elif chr1 == 'U' and chr2 == 'B' and chr3 == 'P' and chr4 == 'C' and chr5 == 'I':
            if chr6 != ' ':
                return ASSEMBLER_ERROR_MISSING_PARAM

            # SUBPCI
            assembled = assembler_parse_int(line[7:])
            if not assembled:
                return ASSEMBLER_ERROR_PARAM_OUT_OF_RANGE

            assembled = (~assembled) + 1
            if assembled & 0xE0 != 0xE0:
                return ASSEMBLER_ERROR_PARAM_OUT_OF_RANGE

            assembled = 0b10100000 | (assembled & 0x1F)

        elif chr1 == 'K' and chr2 == 'I' and chr3 == 'P' and chr4 == 'I' and chr5 == 'F':
            if chr6 != ' ':
                return ASSEMBLER_ERROR_MISSING_PARAM

            # SKIPIF
            skipifprm: const[str] = line[7:]
            if skipifprm == "CF":
                assembled = 0b11110010
            elif skipifprm == "!CF":
                assembled = 0b11110011
            elif skipifprm == "ZF":
                assembled = 0b11110100
            elif skipifprm == "!ZF":
                assembled = 0b11110101
            else:
                return ASSEMBLER_ERROR_PARAM_OUT_OF_RANGE

        else:
            return ASSEMBLER_ERROR_UNRECOGNIZED_INSTRUCTION

    elif chr0 == 'X':
        # XOR, XORU, XORV
        if chr1 != 'O' or chr2 != 'R':
            return ASSEMBLER_ERROR_UNRECOGNIZED_INSTRUCTION

        if chr3 == '\x00':
            assembled = 0b10011101
        elif chr3 == 'U' and chr4 == '\x00':
            assembled = 0b10001101
        elif chr3 == 'V' and chr4 == '\x00':
            assembled = 0b10010101
        else:
            return ASSEMBLER_ERROR_UNRECOGNIZED_INSTRUCTION

    else:
        return ASSEMBLER_ERROR_UNRECOGNIZED_INSTRUCTION

    poke(dst, assembled)
    __last_bytes_consumed = 1
    return ASSEMBLER_ERROR_NONE


def assembler_disassemble(src: uint16) -> str[16]:
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

        return peek(regop_offset, 7)

    if mask == 0b11101000:
        memop_offset: uint16 = (instruction & 0b00000111)
        memop_offset <<= 2
        memop_offset += cast(uint16, __memory_op_lut)

        return peek(memop_offset, 4)

    if mask == 0b11111000:
        stkop_offset: uint16 = (instruction & 0b00000111) - 2
        stkop_offset <<= 3
        stkop_offset += cast(uint16, __stack_op_lut)

        return peek(stkop_offset, 7)

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
