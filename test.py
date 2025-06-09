#! /usr/bin/python3
import argparse
import os
import struct
import textwrap
from itertools import chain
from typing import Container, Dict, List, Optional
from core import (
    InvalidInstructionException,
    ParameterOutOfRangeException,
    CodeOutOfRangeException,
    CPUCore,
    assemble,
    disassemble,
    bintoint,
    hexstr,
    parse_and_compile_module,
)


CLEAR_LINE = "\033[F\033[K"
BACK_AND_CLEAR_LINE = "\033[F\033[K\033[F"


verbose: bool = False


def _assert(statement: bool, msg: str) -> None:
    assert statement, msg


def getlines(instr: str) -> List[str]:
    lines: List[str] = []

    for line in instr.split(os.linesep):
        line, *_ = line.split(';')
        line = line.strip()
        if line:
            lines.append(line)
    return lines


def getmemory(instr: str) -> List[int]:
    memory = [0] * 0x10000
    assembled = assemble(getlines(instr))
    for loc, intval in assembled:
        memory[loc] = intval
    return memory


def rununtilhalt(cpu: CPUCore) -> None:
    while True:
        if verbose:
            cpu.print()
            cpu.dump()
            print("")
        if cpu.mnemonic == "HALT":
            return
        cpu.tick()


def bintoint16(binary: int) -> int:
    return int(struct.unpack("h", struct.pack("H", binary))[0])


def bintoint32(binary: int) -> int:
    return int(struct.unpack("i", struct.pack("I", binary))[0])


def inttobin16(binary: int) -> int:
    return int(struct.unpack("H", struct.pack("h", binary))[0])


def inttobin32(binary: int) -> int:
    return int(struct.unpack("I", struct.pack("i", binary))[0])


def getstring(cpu: CPUCore, location: int) -> str:
    string = ""
    while cpu.ram[location] != 0x00:
        string = string + chr(cpu.ram[location])
        location += 1
    return string


def bintostr(cpu: CPUCore, binptr: int, low_range: int, high_range: int) -> str:
    if binptr < low_range or binptr >= high_range:
        raise Exception(f"Address {hexstr(binptr, 4)} outside of valid range {hexstr(low_range, 4)}-{hexstr(high_range, 4)}")
    return getstring(cpu, binptr)


def checkerror(fname: str, error: Exception) -> None:
    try:
        with open(fname, "r") as fp:
            assemble(getlines(fp.read()))
    except Exception as e:
        exception = e
    else:
        _assert(False, f"Expected a {type(error).__name__} exception!")

    _assert(  # noqa
        type(exception) == type(error),
        f"Expected an exception {type(error).__name__} "
        + f"but got {type(exception).__name__}!",
    )
    _assert(
        exception.args[0] == error.args[0],
        f"Expected a message {error.args[0]!r} but got {exception.args[0]!r}!",
    )


def verifyassembler(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "assembler" not in only:
        return

    print("Verifying assembler...")
    checkerror(
        "errors/invalidinstruction1.S",
        InvalidInstructionException(
            "Unrecognized instruction SHITPOST 5"
        ),
    )
    checkerror(
        "errors/invalidinstruction2.S",
        ParameterOutOfRangeException(
            "Too many parameters for instruction ADDI A, 1"),
    )
    checkerror(
        "errors/overlap1.S",
        CodeOutOfRangeException(
            "Cannot place code/data ADDI 1 into section 0x0100, "
            + "already occupied"
        ),
    )
    checkerror(
        "errors/oob1.S",
        ParameterOutOfRangeException(
            "Out of range integer 256 on instruction LOADI 256"
        )
    )
    checkerror(
        "errors/oob2.S",
        ParameterOutOfRangeException(
            "Out of range integer -129 on instruction LOADI -129"
        )
    )
    checkerror(
        "errors/oob3.S",
        ParameterOutOfRangeException(
            "Out of range integer 32 on instruction JRI 32"
        )
    )
    checkerror(
        "errors/oob4.S",
        ParameterOutOfRangeException(
            "Out of range integer -33 on instruction JRI -33")
    )
    checkerror(
        "errors/oob5.S",
        ParameterOutOfRangeException(
            "Out of range integer 32 on instruction JRI too_far")
    )
    checkerror(
        "errors/oob6.S",
        ParameterOutOfRangeException(
            "Out of range integer -33 on instruction JRI too_far")
    )
    checkerror(
        "errors/oob7.S",
        ParameterOutOfRangeException(
            "Out of range integer 32 on instruction ADDI 32")
    )
    checkerror(
        "errors/oob8.S",
        ParameterOutOfRangeException(
            "Out of range integer -33 on instruction ADDI -33")
    )
    checkerror(
        "errors/missinglabel1.S",
        ParameterOutOfRangeException(
            "Undefined label invalid_label for instruction JRI invalid_label"
        )
    )
    checkerror(
        "errors/invalidparameter1.S",
        ParameterOutOfRangeException(
            "Invalid parameter 123 for instruction NOP 123"
        )
    )
    checkerror(
        "errors/invalidparameter2.S",
        ParameterOutOfRangeException(
            "Invalid parameter 123 for instruction HALT 123"
        )
    )
    checkerror(
        "errors/invalidparameter3.S",
        ParameterOutOfRangeException(
            "Invalid parameter 123 for instruction ZERO 123"
        )
    )
    checkerror(
        "errors/invalidparameter4.S",
        ParameterOutOfRangeException(
            "Invalid parameter 123 for instruction INC 123"
        )
    )
    checkerror(
        "errors/invalidparameter5.S",
        ParameterOutOfRangeException(
            "Invalid parameter 123 for instruction DEC 123"
        )
    )
    checkerror(
        "errors/invalidparameter3.S",
        ParameterOutOfRangeException(
            "Invalid parameter 123 for instruction ZERO 123"
        )
    )


def verifyaddi(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "addi" not in only and "instructions" not in only:
        return

    print("Verifying ADDI...")
    for i in range(-32, 32):
        memory = getmemory(f"""
            LOADI 5
            ADDI {i}
            HALT
        """)
        cpu = CPUCore(memory)
        rununtilhalt(cpu)
        _assert(
            bintoint(cpu.a) == (i + 5),
            f"Failed to add {i} to A register!"
        )

        memory = getmemory(f"""
            ADDI {i}
        """)
        if i == -1:
            _assert(
                disassemble(memory[0]) == "DEC",
                f"Failed to disassemble ADDI {i}!",
            )
        elif i == 1:
            _assert(
                disassemble(memory[0]) == "INC",
                f"Failed to disassemble ADDI {i}!",
            )
        else:
            _assert(
                disassemble(memory[0]) == f"ADDI {i}",
                f"Failed to disassemble ADDI {i}!",
            )


def verifyloadi(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "loadi" not in only and "instructions" not in only:
        return

    print("Verifying LOADI...")
    for i in range(0, 256):
        memory = getmemory(f"""
            LOADI {i}
            HALT
        """)
        cpu = CPUCore(memory)
        rununtilhalt(cpu)
        _assert(cpu.a == i, f"Failed to set A to {i}!")

    for i in range(-128, 128):
        memory = getmemory(f"""
            LOADI {i}
            HALT
        """)
        cpu = CPUCore(memory)
        rununtilhalt(cpu)
        _assert(bintoint(cpu.a) == i, f"Failed to set A to {i}!")


def verifysetpc(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "setpc" not in only and "instructions" not in only:
        return

    print("Verifying SETPC...")
    print("0% complete...")
    for i in range(0, 0xFFFF, 1 if full else 29):
        memory = getmemory(f"""
            SETPC {i}
            HALT
        """)
        cpu = CPUCore(memory)
        rununtilhalt(cpu)
        _assert(cpu.p[0] == (i >> 8) & 0xFF, f"Failed to set PC to {i}!")
        _assert(cpu.c[0] == i & 0xFF, f"Failed to set PC to {i}!")

        if i & 0xFF == 0:
            print(f"{CLEAR_LINE}{int((i * 100) / 0xFFFF)}% complete...")
    print(BACK_AND_CLEAR_LINE)


def verifyaddpc(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "addpc" not in only and "instructions" not in only:
        return

    print("Verifying ADDPC...")
    for i in range(-128, 128):
        memory = getmemory(f"""
            SETPC 12345
            LOADI {i}
            ADDPC
            HALT
        """)
        cpu = CPUCore(memory)
        rununtilhalt(cpu)
        _assert(
            cpu.pc == 12345 + i,
            f"Failed to ADDPC against {i}, "
            + f"got {cpu.pc} instead of {12345 + i}",
        )


def verifyneg(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "neg" not in only and "instructions" not in only:
        return

    print("Verifying NEG...")
    for i in range(-127, 128):
        memory = getmemory(f"""
            LOADI {i}
            NEG
            HALT
        """)
        cpu = CPUCore(memory)
        rununtilhalt(cpu)
        _assert(bintoint(cpu.a) == -i, "Failed to negate A!")


def verifyaddpci(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "addpci" not in only and "instructions" not in only:
        return

    print("Verifying ADDPCI...")
    for i in range(1, 9):
        memory = getmemory(f"""
            SETPC 0x01FA
            ADDPCI {i}
            HALT
        """)
        cpu = CPUCore(memory)
        rununtilhalt(cpu)
        _assert(
            cpu.p[0] == ((0x01FA + i) >> 8) & 0xFF,
            f"Failed to ADDPCI {i}!",
        )
        _assert(cpu.c[0] == (0x01FA + i) & 0xFF, f"Failed to ADDPCI {i}!")

        memory = getmemory(f"""
            ADDPCI {i}
        """)
        if i == 1:
            _assert(
                disassemble(memory[0]) == "INCPC",
                f"Failed to disassemble ADDPCI {i}!",
            )
        else:
            _assert(
                disassemble(memory[0]) == f"ADDPCI {i}",
                f"Failed to disassemble ADDPCI {i}!",
            )


def verifysubpci(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "subpci" not in only and "instructions" not in only:
        return

    print("Verifying SUBPCI...")
    for i in range(1, 9):
        memory = getmemory(f"""
            SETPC 0x0204
            SUBPCI {i}
            HALT
        """)
        cpu = CPUCore(memory)
        rununtilhalt(cpu)
        _assert(
            cpu.p[0] == ((0x0204 - i) >> 8) & 0xFF,
            f"Failed to SUBPCI {i}!",
        )
        _assert(cpu.c[0] == (0x0204 - i) & 0xFF, f"Failed to SUBPCI {i}!")

        memory = getmemory(f"""
            SUBPCI {i}
        """)
        if i == 1:
            _assert(
                disassemble(memory[0]) == "DECPC",
                f"Failed to disassemble SUBPCI {i}!",
            )
        else:
            _assert(
                disassemble(memory[0]) == f"SUBPCI {i}",
                f"Failed to disassemble SUBPCI {i}!",
            )


def verifyshift(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "shift" not in only and "instructions" not in only:
        return

    print("Verifying shifts...")
    for i in range(256):
        for operation in ["SHL", "SHR", "ROL", "ROR", "RCL", "RCR"]:
            if operation == "SHL":
                expected = i << 2
            elif operation == "SHR":
                expected = i >> 2
            elif operation == "ROL":
                expected = (i << 2) | (i >> 6)
            elif operation == "ROR":
                expected = (i >> 2) | (i << 6)
            elif operation == "RCL":
                # Since we will rotate with carry, the first carry gets
                # "swallowed" as we shift in the first time. This is due
                # to the carry flag always starting clear.
                expected = (i << 2) | (i >> 7)
            elif operation == "RCR":
                expected = (i >> 2) | (i << 7)
            expected = expected & 0xFF

            memory = getmemory(f"""
                LOADI {i}
                {operation}
                {operation}
                HALT
            """)
            cpu = CPUCore(memory)
            rununtilhalt(cpu)
            _assert(
                cpu.a == expected,
                f"Failed to {operation} {i} twice, " +
                f"expected {expected} but got {cpu.a}",
            )


def verifymult(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "mult" not in only and "mathlib" not in only:
        return

    print("Verifying mult...")
    print("0% complete...")

    with open("lib/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/start.S", "r") as fp:
        initlines += fp.readlines()
    with open("lib/math/multiply.S", "r") as fp:
        multiplylines = fp.readlines()
    with open("lib/math/add.S", "r") as fp:
        addlines = fp.readlines()

    cycles = 0
    instructions = 0
    count = 0
    zeros: Dict[str, bool] = {'x': False, 'y': False}
    for x in range(0, 256):
        for y in range(0, 256):
            if x == 0 and y != 0:
                if zeros['x']:
                    continue
                zeros['x'] = True
            if x != 0 and y == 0:
                if zeros['y']:
                    continue
                zeros['y'] = True
            if x * y > 255:
                # No sense continuing, the next value will be too large too.
                break
            memory = getmemory(os.linesep.join([
                *initlines,
                "main:",
                f"PUSHI {x}",
                f"PUSHI {y}",
                "CALL mult",
                "HALT",
                *multiplylines,
                *addlines,
            ]))
            cpu = CPUCore(memory)
            rununtilhalt(cpu)
            _assert(
                cpu.a == x * y,
                f"Failed to mult {x} by {y}, "
                + f"got {cpu.a} instead of {x * y}!",
            )
            cycles += cpu.cycles
            instructions += cpu.ticks
            count += 1

        print(f"{CLEAR_LINE}{int((x * 100) / 256)}% complete...")
    print(f"{CLEAR_LINE}Average cycles for mult: {int(cycles/count)}")
    print(f"Average instructions for mult: {int(instructions/count)}")


def verifymult16(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "mult16" not in only and "mathlib" not in only:
        return

    print("Verifying mult16...")
    print("0% complete...")

    with open("lib/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/start.S", "r") as fp:
        initlines += fp.readlines()
    with open("lib/math/multiply.S", "r") as fp:
        multiplylines = fp.readlines()
    with open("lib/math/add.S", "r") as fp:
        addlines = fp.readlines()

    cycles = 0
    instructions = 0
    count = 0
    zeros: Dict[str, bool] = {'x': False, 'y': False}
    xrng = [
        *range(0, 16),
        *range(16, 64, 3),
        *range(64, 65536, 137 if full else 1473)
    ]
    for x in xrng:
        validrange = int(65536 / (x + 1))
        step = int(validrange / 10)
        if step < 1:
            step = 1
        for y in range(0, 65536, step):
            if x == 0 and y != 0:
                if zeros['x']:
                    continue
                zeros['x'] = True
            if x != 0 and y == 0:
                if zeros['y']:
                    continue
                zeros['y'] = True
            if x * y > 65535:
                # No sense continuing, the next value will be too large too.
                break
            memory = getmemory(os.linesep.join([
                *initlines,
                "main:",
                f"PUSHI {x & 0xFF}",
                f"PUSHI {(x >> 8) & 0xFF}",
                f"PUSHI {y & 0xFF}",
                f"PUSHI {(y >> 8) & 0xFF}",
                "LOADI 123",
                "CALL mult16",
                "HALT",
                *multiplylines,
                *addlines,
            ]))
            cpu = CPUCore(memory)
            rununtilhalt(cpu)

            calculated = (cpu.ram[cpu.pc] << 8) + cpu.ram[cpu.pc + 1]
            real = (x * y) & 0xFFFF
            _assert(
                cpu.a == 123,
                f"umut16 changed A register from 123 to {cpu.a}!",
            )
            _assert(
                real == calculated,
                f"Failed to mult16 {x} and {y}, "
                + f"got {calculated} instead of {real}!",
            )
            cycles += cpu.cycles
            instructions += cpu.ticks
            count += 1

        print(f"{CLEAR_LINE}{int((x * 100) / 65536)}% complete...")
    print(f"{CLEAR_LINE}Average cycles for mult16: {int(cycles/count)}")
    print(f"Average instructions for mult16: {int(instructions/count)}")


def verifymult32(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "mult32" not in only and "mathlib" not in only:
        return

    print("Verifying mult32...")
    print("0% complete...")

    with open("lib/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/start.S", "r") as fp:
        initlines += fp.readlines()
    with open("lib/math/multiply.S", "r") as fp:
        multiplylines = fp.readlines()
    with open("lib/math/add.S", "r") as fp:
        addlines = fp.readlines()

    cycles = 0
    instructions = 0
    count = 0
    zeros: Dict[str, bool] = {'x': False, 'y': False}
    xrng = [
        *range(0, 16),
        *range(16, 64, 3),
        *range(64, 65536, 1473 if full else 15479),
        *range(65536, 0x100000000, 0x1C12345 if full else 0x1C776543)
    ]
    for x in xrng:
        validrange = int(0x100000000 / (x + 1))
        step = int(validrange / 10) + 1
        if step < 1:
            step = 1
        for y in range(0, 0x100000000, step):
            if x == 0 and y != 0:
                if zeros['x']:
                    continue
                zeros['x'] = True
            if x != 0 and y == 0:
                if zeros['y']:
                    continue
                zeros['y'] = True
            if x * y > 0xFFFFFFFF:
                # No sense continuing, the next value will be too large too.
                break
            memory = getmemory(os.linesep.join([
                *initlines,
                "main:",
                f"PUSHI {x & 0xFF}",
                f"PUSHI {(x >> 8) & 0xFF}",
                f"PUSHI {(x >> 16) & 0xFF}",
                f"PUSHI {(x >> 24) & 0xFF}",
                f"PUSHI {y & 0xFF}",
                f"PUSHI {(y >> 8) & 0xFF}",
                f"PUSHI {(y >> 16) & 0xFF}",
                f"PUSHI {(y >> 24) & 0xFF}",
                "LOADI 123",
                "CALL mult32",
                "HALT",
                *multiplylines,
                *addlines,
            ]))
            cpu = CPUCore(memory)
            rununtilhalt(cpu)

            calculated = (
                (cpu.ram[cpu.pc] << 24) +
                (cpu.ram[cpu.pc + 1] << 16) +
                (cpu.ram[cpu.pc + 2] << 8) +
                cpu.ram[cpu.pc + 3]
            )
            real = (x * y) & 0xFFFFFFFF
            _assert(
                cpu.a == 123,
                f"umut16 changed A register from 123 to {cpu.a}!",
            )
            _assert(
                real == calculated,
                f"Failed to mult32 {x} and {y}, "
                + f"got {calculated} instead of {real}!",
            )
            cycles += cpu.cycles
            instructions += cpu.ticks
            count += 1

        print(f"{CLEAR_LINE}{int((x * 100) / 0x100000000)}% complete...")
    print(f"{CLEAR_LINE}Average cycles for mult32: {int(cycles/count)}")
    print(f"Average instructions for mult32: {int(instructions/count)}")


def verifyudiv(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "udiv" not in only and "mathlib" not in only:
        return

    print("Verifying udiv...")
    print("0% complete...")

    with open("lib/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/start.S", "r") as fp:
        initlines += fp.readlines()
    with open("lib/math/divide.S", "r") as fp:
        dividelines = fp.readlines()
    with open("lib/math/cmp.S", "r") as fp:
        cmplines = fp.readlines()
    with open("lib/math/add.S", "r") as fp:
        addlines = fp.readlines()
    with open("lib/math/neg.S", "r") as fp:
        neglines = fp.readlines()

    cycles = 0
    instructions = 0
    count = 0
    for dividend in range(0, 256, 7 if full else 37):
        for divisor in range(1, 256, 5 if full else 23):
            memory = getmemory(os.linesep.join([
                *initlines,
                "main:",
                f"PUSHI {dividend}",
                f"PUSHI {divisor}",
                "LOADI 123",
                "CALL udiv",
                "HALT",
                *dividelines,
                *cmplines,
                *addlines,
                *neglines,
            ]))
            cpu = CPUCore(memory)
            rununtilhalt(cpu)
            quotient = cpu.ram[cpu.pc + 1]
            remainder = cpu.ram[cpu.pc]
            _assert(
                quotient == dividend // divisor,
                f"Failed to udiv {dividend} by {divisor}, "
                + f"got {cpu.a} instead of {dividend // divisor}!",
            )
            _assert(
                remainder == dividend % divisor,
                f"Failed to udiv {dividend} by {divisor}, "
                + f"got {remainder} instead of {dividend % divisor}!",
            )
            _assert(
                cpu.a == 123,
                f"udiv16 changed A register from 123 to {cpu.a}!",
            )
            cycles += cpu.cycles
            instructions += cpu.ticks
            count += 1

        print(f"{CLEAR_LINE}{int((dividend * 100) / 256)}% complete...")
    print(f"{CLEAR_LINE}Average cycles for udiv: {int(cycles/count)}")
    print(f"Average instructions for udiv: {int(instructions/count)}")


def verifyudiv16(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "udiv16" not in only and "mathlib" not in only:
        return

    print("Verifying udiv16...")
    print("0% complete...")

    with open("lib/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/start.S", "r") as fp:
        initlines += fp.readlines()
    with open("lib/math/divide.S", "r") as fp:
        dividelines = fp.readlines()
    with open("lib/math/cmp.S", "r") as fp:
        cmplines = fp.readlines()
    with open("lib/math/add.S", "r") as fp:
        addlines = fp.readlines()
    with open("lib/math/neg.S", "r") as fp:
        neglines = fp.readlines()

    cycles = 0
    instructions = 0
    count = 0
    for dividend in range(0, 65536, 1234 if full else 6543):
        for divisor in range(
            1 + (dividend // 13),
            65536,
            (987 if full else 9876) - (dividend // 19)
        ):
            memory = getmemory(os.linesep.join([
                *initlines,
                "main:",
                f"PUSHI {dividend & 0xFF}",
                f"PUSHI {(dividend >> 8) & 0xFF}",
                f"PUSHI {divisor & 0xFF}",
                f"PUSHI {(divisor >> 8) & 0xFF}",
                "LOADI 123",
                "CALL udiv16",
                "HALT",
                *dividelines,
                *cmplines,
                *addlines,
                *neglines,
            ]))
            cpu = CPUCore(memory)
            rununtilhalt(cpu)
            quotient = (cpu.ram[cpu.pc + 2] << 8) + cpu.ram[cpu.pc + 3]
            remainder = (cpu.ram[cpu.pc] << 8) + cpu.ram[cpu.pc + 1]
            _assert(
                quotient == dividend // divisor,
                f"Failed to udiv16 {dividend} by {divisor}, "
                + f"got {quotient} instead of {dividend // divisor}!",
            )
            _assert(
                remainder == dividend % divisor,
                f"Failed to udiv16 {dividend} by {divisor}, "
                + f"got {remainder} instead of {dividend % divisor}!",
            )
            _assert(
                cpu.a == 123,
                f"udiv16 changed A register from 123 to {cpu.a}!",
            )
            cycles += cpu.cycles
            instructions += cpu.ticks
            count += 1

        print(f"{CLEAR_LINE}{int((dividend * 100) / 65536)}% complete...")
    print(f"{CLEAR_LINE}Average cycles for udiv16: {int(cycles/count)}")
    print(f"Average instructions for udiv16: {int(instructions/count)}")


def verifyudiv32(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "udiv32" not in only and "mathlib" not in only:
        return

    print("Verifying udiv32...")
    print("0% complete...")

    with open("lib/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/start.S", "r") as fp:
        initlines += fp.readlines()
    with open("lib/math/divide.S", "r") as fp:
        dividelines = fp.readlines()
    with open("lib/math/cmp.S", "r") as fp:
        cmplines = fp.readlines()
    with open("lib/math/add.S", "r") as fp:
        addlines = fp.readlines()
    with open("lib/math/neg.S", "r") as fp:
        neglines = fp.readlines()

    cycles = 0
    instructions = 0
    count = 0
    for bump, dividend in enumerate(range(0, 2**32, 80904192 if full else 809041923)):
        for divisor in range(
            1 + bump,
            2**32,
            122945537 if full else 245880537
        ):
            memory = getmemory(os.linesep.join([
                *initlines,
                "main:",
                f"PUSHI {dividend & 0xFF}",
                f"PUSHI {(dividend >> 8) & 0xFF}",
                f"PUSHI {(dividend >> 16) & 0xFF}",
                f"PUSHI {(dividend >> 24) & 0xFF}",
                f"PUSHI {divisor & 0xFF}",
                f"PUSHI {(divisor >> 8) & 0xFF}",
                f"PUSHI {(divisor >> 16) & 0xFF}",
                f"PUSHI {(divisor >> 24) & 0xFF}",
                "LOADI 123",
                "CALL udiv32",
                "HALT",
                *dividelines,
                *cmplines,
                *addlines,
                *neglines,
            ]))
            cpu = CPUCore(memory)
            rununtilhalt(cpu)
            quotient = (
                (cpu.ram[cpu.pc + 4] << 24) +
                (cpu.ram[cpu.pc + 5] << 16) +
                (cpu.ram[cpu.pc + 6] << 8) +
                (cpu.ram[cpu.pc + 7])
            )
            remainder = (
                (cpu.ram[cpu.pc + 0] << 24) +
                (cpu.ram[cpu.pc + 1] << 16) +
                (cpu.ram[cpu.pc + 2] << 8) +
                (cpu.ram[cpu.pc + 3])
            )
            _assert(
                quotient == dividend // divisor,
                f"Failed to udiv32 {dividend} by {divisor}, "
                + f"got {quotient} instead of {dividend // divisor}!",
            )
            _assert(
                remainder == dividend % divisor,
                f"Failed to udiv32 {dividend} by {divisor}, "
                + f"got {remainder} instead of {dividend % divisor}!",
            )
            _assert(
                cpu.a == 123,
                f"udiv32 changed A register from 123 to {cpu.a}!",
            )
            cycles += cpu.cycles
            instructions += cpu.ticks
            count += 1

        print(f"{CLEAR_LINE}{int((dividend * 100) / 2**32)}% complete...")
    print(f"{CLEAR_LINE}Average cycles for udiv32: {int(cycles/count)}")
    print(f"Average instructions for udiv32: {int(instructions/count)}")


def verifymathadd(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "mathadd" not in only and "mathlib" not in only:
        return

    print("Verifying add...")
    print("0% complete...")

    with open("lib/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/start.S", "r") as fp:
        initlines += fp.readlines()
    with open("lib/math/add.S", "r") as fp:
        addlines = fp.readlines()

    cycles = 0
    instructions = 0
    count = 0
    for x in range(0, 256, 5 if full else 11):
        for y in range(0, 256, 3 if full else 7):
            memory = getmemory(os.linesep.join([
                *initlines,
                "main:",
                f"PUSHI {x}",
                f"PUSHI {y}",
                "CALL add",
                "HALT",
                *addlines,
            ]))
            cpu = CPUCore(memory)
            rununtilhalt(cpu)
            calculated = cpu.a
            real = (x + y) & 0xFF
            _assert(
                real == calculated,
                f"Failed to add {x} and {y}, "
                + f"got {calculated} instead of {real}!",
            )
            cycles += cpu.cycles
            instructions += cpu.ticks
            count += 1

        print(f"{CLEAR_LINE}{int((x * 100) / 256)}% complete...")
    print(f"{CLEAR_LINE}Average cycles for add: {int(cycles/count)}")
    print(f"Average instructions for add: {int(instructions/count)}")


def verifyadd16(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "add16" not in only and "mathlib" not in only:
        return

    print("Verifying add16...")
    print("0% complete...")

    with open("lib/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/start.S", "r") as fp:
        initlines += fp.readlines()
    with open("lib/math/add.S", "r") as fp:
        addlines = fp.readlines()

    cycles = 0
    instructions = 0
    count = 0
    for x in range(0, 65536, 1234 if full else 12345):
        for y in range(0, 65536, 987 if full else 1876):
            memory = getmemory(os.linesep.join([
                *initlines,
                "main:",
                f"PUSHI {x & 0xFF}",
                f"PUSHI {(x >> 8) & 0xFF}",
                f"PUSHI {y & 0xFF}",
                f"PUSHI {(y >> 8) & 0xFF}",
                "LOADI 123",
                "CALL add16",
                "HALT",
                *addlines,
            ]))
            cpu = CPUCore(memory)
            rununtilhalt(cpu)
            calculated = (cpu.ram[cpu.pc] << 8) + cpu.ram[cpu.pc + 1]
            real = (x + y) & 0xFFFF
            _assert(
                cpu.a == 123,
                f"add16 changed A register from 123 to {cpu.a}!",
            )
            _assert(
                real == calculated,
                f"Failed to add16 {x} and {y}, "
                + f"got {calculated} instead of {real}!",
            )
            cycles += cpu.cycles
            instructions += cpu.ticks
            count += 1

        print(f"{CLEAR_LINE}{int((x * 100) / 65536)}% complete...")
    print(f"{CLEAR_LINE}Average cycles for add16: {int(cycles/count)}")
    print(f"Average instructions for add16: {int(instructions/count)}")


def verifyadd32(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "add32" not in only and "mathlib" not in only:
        return

    print("Verifying add32...")
    print("0% complete...")

    with open("lib/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/start.S", "r") as fp:
        initlines += fp.readlines()
    with open("lib/math/add.S", "r") as fp:
        addlines = fp.readlines()

    cycles = 0
    instructions = 0
    count = 0
    for x in range(0, 2**32, 80904192 if full else 809041923):
        for y in range(0, 2**32, 61472769 if full else 122945537):
            memory = getmemory(os.linesep.join([
                *initlines,
                "main:",
                f"PUSHI {x & 0xFF}",
                f"PUSHI {(x >> 8) & 0xFF}",
                f"PUSHI {(x >> 16) & 0xFF}",
                f"PUSHI {(x >> 24) & 0xFF}",
                f"PUSHI {y & 0xFF}",
                f"PUSHI {(y >> 8) & 0xFF}",
                f"PUSHI {(y >> 16) & 0xFF}",
                f"PUSHI {(y >> 24) & 0xFF}",
                "LOADI 123",
                "CALL add32",
                "HALT",
                *addlines,
            ]))
            cpu = CPUCore(memory)
            rununtilhalt(cpu)
            calculated = (
                (cpu.ram[cpu.pc] << 24) +
                (cpu.ram[cpu.pc + 1] << 16) +
                (cpu.ram[cpu.pc + 2] << 8) +
                cpu.ram[cpu.pc + 3]
            )
            real = (x + y) & 0xFFFFFFFF
            _assert(
                cpu.a == 123,
                f"add32 changed A register from 123 to {cpu.a}!",
            )
            _assert(
                real == calculated,
                f"Failed to add32 {x} and {y}, "
                + f"got {calculated} instead of {real}!",
            )
            cycles += cpu.cycles
            instructions += cpu.ticks
            count += 1

        print(f"{CLEAR_LINE}{int((x * 100) / (2**32))}% complete...")
    print(f"{CLEAR_LINE}Average cycles for add32: {int(cycles/count)}")
    print(f"Average instructions for add32: {int(instructions/count)}")


def verifyabs(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "abs" not in only and "mathlib" not in only:
        return

    print("Verifying abs...")

    with open("lib/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/start.S", "r") as fp:
        initlines += fp.readlines()
    with open("lib/math/neg.S", "r") as fp:
        neglines = fp.readlines()
    with open("lib/math/abs.S", "r") as fp:
        abslines = fp.readlines()

    cycles = 0
    instructions = 0
    count = 0
    for x in range(-127, 128):
        memory = getmemory(os.linesep.join([
            *initlines,
            "main:",
            f"LOADI {x}",
            "CALL abs",
            "HALT",
            *neglines,
            *abslines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)
        _assert(
            cpu.a == abs(x),
            f"Failed to abs({x}), got {cpu.a} instead of {x}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    print(f"Average cycles for abs: {int(cycles/count)}")
    print(f"Average instructions for abs: {int(instructions/count)}")


def verifyabs16(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "abs16" not in only and "mathlib" not in only:
        return

    print("Verifying abs16...")
    print("0% complete...")

    with open("lib/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/start.S", "r") as fp:
        initlines += fp.readlines()
    with open("lib/math/neg.S", "r") as fp:
        neglines = fp.readlines()
    with open("lib/math/abs.S", "r") as fp:
        abslines = fp.readlines()

    cycles = 0
    instructions = 0
    count = 0
    for x in range(-32767, 32768, 79 if full else 763):
        xbin = inttobin16(x)
        memory = getmemory(os.linesep.join([
            *initlines,
            "main:",
            f"PUSHI {xbin & 0xFF}",
            f"PUSHI {(xbin >> 8) & 0xFF}",
            "LOADI 123",
            "CALL abs16",
            "HALT",
            *neglines,
            *abslines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)
        calculated = bintoint16(
            (cpu.ram[cpu.pc] << 8) + cpu.ram[cpu.pc + 1]
        )
        real = abs(x)
        _assert(
            cpu.a == 123,
            f"abs16 changed A register from 123 to {cpu.a}!",
        )
        _assert(
            real == calculated,
            f"Failed to abs16 {x}, "
            + f"got {calculated} instead of {real}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1
        print(f"{CLEAR_LINE}{int(((x + 32767) * 100) / 65536)}% complete...")

    print(f"{CLEAR_LINE}Average cycles for abs16: {int(cycles/count)}")
    print(f"Average instructions for abs16: {int(instructions/count)}")


def verifyabs32(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "abs32" not in only and "mathlib" not in only:
        return

    print("Verifying abs32...")
    print("0% complete...")

    with open("lib/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/start.S", "r") as fp:
        initlines += fp.readlines()
    with open("lib/math/neg.S", "r") as fp:
        neglines = fp.readlines()
    with open("lib/math/abs.S", "r") as fp:
        abslines = fp.readlines()

    cycles = 0
    instructions = 0
    count = 0
    for x in range(
        -(2**31 - 1),
        (2**31),
        (2**22 + 3) if full else (2**25 + 3)
    ):
        xbin = inttobin32(x)
        memory = getmemory(os.linesep.join([
            *initlines,
            "main:",
            f"PUSHI {xbin & 0xFF}",
            f"PUSHI {(xbin >> 8) & 0xFF}",
            f"PUSHI {(xbin >> 16) & 0xFF}",
            f"PUSHI {(xbin >> 24) & 0xFF}",
            "LOADI 123",
            "CALL abs32",
            "HALT",
            *neglines,
            *abslines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)
        calculated = bintoint32(
            (cpu.ram[cpu.pc] << 24) +
            (cpu.ram[cpu.pc + 1] << 16) +
            (cpu.ram[cpu.pc + 2] << 8) +
            cpu.ram[cpu.pc + 3]
        )
        real = abs(x)
        _assert(
            cpu.a == 123,
            f"abs32 changed A register from 123 to {cpu.a}!",
        )
        _assert(
            real == calculated,
            f"Failed to abs32 {x}, "
            + f"got {calculated} instead of {real}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1
        print(
            f"{CLEAR_LINE}{int(((x + (2 ** 31)) * 100) / (2 ** 32))}% complete..."
        )

    print(f"{CLEAR_LINE}Average cycles for abs32: {int(cycles/count)}")
    print(f"Average instructions for abs32: {int(instructions/count)}")


def verifyucmp(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "ucmp" not in only and "mathlib" not in only:
        return

    print("Verifying ucmp...")
    print("0% complete...")

    with open("lib/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/start.S", "r") as fp:
        initlines += fp.readlines()
    with open("lib/math/cmp.S", "r") as fp:
        cmplines = fp.readlines()

    cycles = 0
    instructions = 0
    count = 0
    for a in range(0, 256, 5 if full else 11):
        for b in range(0, 256, 3 if full else 7):
            memory = getmemory(os.linesep.join([
                *initlines,
                "main:",
                f"PUSHI {a}",
                f"PUSHI {b}",
                "CALL ucmp",
                "HALT",
                *cmplines,
            ]))
            cpu = CPUCore(memory)
            rununtilhalt(cpu)
            if a < b:
                answer = -1
            elif a == b:
                answer = 0
            elif a > b:
                answer = 1
            _assert(
                cpu.ram[cpu.pc + 1] == a,
                f"ucmp changed stack value from {a} "
                + f"to {cpu.ram[cpu.pc + 1]}!",
            )
            _assert(
                cpu.ram[cpu.pc] == b,
                f"ucmp changed stack value from {b} to {cpu.ram[cpu.pc]}!",
            )
            _assert(
                bintoint(cpu.a) == answer,
                f"Failed to ucmp({a}, {b}), "
                + f"got {bintoint(cpu.a)} instead of {answer}!",
            )
            cycles += cpu.cycles
            instructions += cpu.ticks
            count += 1

        print(f"{CLEAR_LINE}{int((a * 100) / 256)}% complete...")
    print(f"{CLEAR_LINE}Average cycles for ucmp: {int(cycles/count)}")
    print(f"Average instructions for ucmp: {int(instructions/count)}")


def verifyucmp16(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "ucmp16" not in only and "mathlib" not in only:
        return

    print("Verifying ucmp16...")
    print("0% complete...")

    with open("lib/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/start.S", "r") as fp:
        initlines += fp.readlines()
    with open("lib/math/cmp.S", "r") as fp:
        cmplines = fp.readlines()

    cycles = 0
    instructions = 0
    count = 0
    for a in range(0, 65536, 1281 if full else 2817):
        for b in range(0, 65536, 767 if full else 1791):
            memory = getmemory(os.linesep.join([
                *initlines,
                "main:",
                f"PUSHI {a & 0xFF}",
                f"PUSHI {(a >> 8) & 0xFF}",
                f"PUSHI {b & 0xFF}",
                f"PUSHI {(b >> 8) & 0xFF}",
                "CALL ucmp16",
                "HALT",
                *cmplines,
            ]))
            cpu = CPUCore(memory)
            rununtilhalt(cpu)
            if a < b:
                answer = -1
            elif a == b:
                answer = 0
            elif a > b:
                answer = 1
            astack = ((cpu.ram[cpu.pc + 2] << 8) + cpu.ram[cpu.pc + 3])
            _assert(
                astack == a,
                f"ucmp16 changed stack value from {a} to {astack}!",
            )
            bstack = ((cpu.ram[cpu.pc] << 8) + cpu.ram[cpu.pc + 1])
            _assert(
                bstack == b,
                f"ucmp16 changed stack value from {b} to {bstack}!",
            )
            _assert(
                bintoint(cpu.a) == answer,
                f"Failed to ucmp16({a}, {b}), "
                + f"got {bintoint(cpu.a)} instead of {answer}!",
            )
            cycles += cpu.cycles
            instructions += cpu.ticks
            count += 1

        print(f"{CLEAR_LINE}{int((a * 100) / 65536)}% complete...")
    print(f"{CLEAR_LINE}Average cycles for ucmp16: {int(cycles/count)}")
    print(f"Average instructions for ucmp16: {int(instructions/count)}")


def verifyucmp32(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "ucmp32" not in only and "mathlib" not in only:
        return

    print("Verifying ucmp32...")
    print("0% complete...")

    with open("lib/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/start.S", "r") as fp:
        initlines += fp.readlines()
    with open("lib/math/cmp.S", "r") as fp:
        cmplines = fp.readlines()

    def _verify_ucmp32(a: int, b: int) -> CPUCore:
        memory = getmemory(os.linesep.join([
            *initlines,
            "main:",
            f"PUSHI {a & 0xFF}",
            f"PUSHI {(a >> 8) & 0xFF}",
            f"PUSHI {(a >> 16) & 0xFF}",
            f"PUSHI {(a >> 24) & 0xFF}",
            f"PUSHI {b & 0xFF}",
            f"PUSHI {(b >> 8) & 0xFF}",
            f"PUSHI {(b >> 16) & 0xFF}",
            f"PUSHI {(b >> 24) & 0xFF}",
            "CALL ucmp32",
            "HALT",
            *cmplines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)
        if a < b:
            answer = -1
        elif a == b:
            answer = 0
        elif a > b:
            answer = 1
        astack = (
            (cpu.ram[cpu.pc + 4] << 24) +
            (cpu.ram[cpu.pc + 5] << 16) +
            (cpu.ram[cpu.pc + 6] << 8) +
            cpu.ram[cpu.pc + 7]
        )
        _assert(
            astack == a,
            f"ucmp32 changed stack value from {a} to {astack}!",
        )
        bstack = (
            (cpu.ram[cpu.pc] << 24) +
            (cpu.ram[cpu.pc + 1] << 16) +
            (cpu.ram[cpu.pc + 2] << 8) +
            cpu.ram[cpu.pc + 3]
        )
        _assert(
            bstack == b,
            f"ucmp32 changed stack value from {b} to {bstack}!",
        )
        _assert(
            bintoint(cpu.a) == answer,
            f"Failed to ucmp32({a}, {b}), "
            + f"got {bintoint(cpu.a)} instead of {answer}!",
        )
        return cpu

    for a in [0, 2**6, 2**13, 2**21, 2**29]:
        for b in [0, 2**6, 2**13, 2**21, 2**29]:
            _verify_ucmp32(a, b)

    cycles = 0
    instructions = 0
    count = 0
    for a in range(0, 2**32, 2**26 + 2**13 + 19):
        for b in range(
            0, 2**32, (2**26 + 2**13 + 7)
            if full
            else (2**28 + 2**13 + 11)
        ):
            cpu = _verify_ucmp32(a, b)
            cycles += cpu.cycles
            instructions += cpu.ticks
            count += 1

        print(f"{CLEAR_LINE}{int((a * 100) / (2**32))}% complete...")
    print(f"{CLEAR_LINE}Average cycles for ucmp32: {int(cycles/count)}")
    print(f"Average instructions for ucmp32: {int(instructions/count)}")


def verifycmp(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "cmp" not in only and "mathlib" not in only:
        return

    print("Verifying cmp...")
    print("0% complete...")

    with open("lib/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/start.S", "r") as fp:
        initlines += fp.readlines()
    with open("lib/math/cmp.S", "r") as fp:
        cmplines = fp.readlines()

    cycles = 0
    instructions = 0
    count = 0
    for a in range(-128, 127, 5 if full else 11):
        for b in range(-128, 127, 3 if full else 7):
            memory = getmemory(os.linesep.join([
                *initlines,
                "main:",
                f"PUSHI {a}",
                f"PUSHI {b}",
                "CALL cmp",
                "HALT",
                *cmplines,
            ]))
            cpu = CPUCore(memory)
            rununtilhalt(cpu)
            if a < b:
                answer = -1
            elif a == b:
                answer = 0
            elif a > b:
                answer = 1
            _assert(
                bintoint(cpu.ram[cpu.pc + 1]) == a,
                f"cmp changed stack value from {a} "
                + f"to {bintoint(cpu.ram[cpu.pc + 1])}!",
            )
            _assert(
                bintoint(cpu.ram[cpu.pc]) == b,
                f"cmp changed stack value from {b} to {bintoint(cpu.ram[cpu.pc])}!",
            )
            _assert(
                bintoint(cpu.a) == answer,
                f"Failed to cmp({a}, {b}), "
                + f"got {bintoint(cpu.a)} instead of {answer}!",
            )
            cycles += cpu.cycles
            instructions += cpu.ticks
            count += 1

        print(f"{CLEAR_LINE}{int(((a + 128) * 100) / 256)}% complete...")
    print(f"{CLEAR_LINE}Average cycles for cmp: {int(cycles/count)}")
    print(f"Average instructions for cmp: {int(instructions/count)}")


def verifycmp16(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "cmp16" not in only and "mathlib" not in only:
        return

    print("Verifying cmp16...")
    print("0% complete...")

    with open("lib/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/start.S", "r") as fp:
        initlines += fp.readlines()
    with open("lib/math/cmp.S", "r") as fp:
        cmplines = fp.readlines()

    cycles = 0
    instructions = 0
    count = 0
    for a in range(-32768, 32767, 1281 if full else 2817):
        for b in range(-32768, 32767, 767 if full else 1791):
            memory = getmemory(os.linesep.join([
                *initlines,
                "main:",
                f"PUSHI {a & 0xFF}",
                f"PUSHI {(a >> 8) & 0xFF}",
                f"PUSHI {b & 0xFF}",
                f"PUSHI {(b >> 8) & 0xFF}",
                "CALL cmp16",
                "HALT",
                *cmplines,
            ]))
            cpu = CPUCore(memory)
            rununtilhalt(cpu)
            if a < b:
                answer = -1
            elif a == b:
                answer = 0
            elif a > b:
                answer = 1
            astack = bintoint16((cpu.ram[cpu.pc + 2] << 8) + cpu.ram[cpu.pc + 3])
            _assert(
                astack == a,
                f"cmp16 changed stack value from {a} to {astack}!",
            )
            bstack = bintoint16((cpu.ram[cpu.pc] << 8) + cpu.ram[cpu.pc + 1])
            _assert(
                bstack == b,
                f"cmp16 changed stack value from {b} to {bstack}!",
            )
            _assert(
                bintoint(cpu.a) == answer,
                f"Failed to cmp16({a}, {b}), "
                + f"got {bintoint(cpu.a)} instead of {answer}!",
            )
            cycles += cpu.cycles
            instructions += cpu.ticks
            count += 1

        print(f"{CLEAR_LINE}{int(((a + 32768) * 100) / 65536)}% complete...")
    print(f"{CLEAR_LINE}Average cycles for cmp16: {int(cycles/count)}")
    print(f"Average instructions for cmp16: {int(instructions/count)}")


def verifycmp32(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "cmp32" not in only and "mathlib" not in only:
        return

    print("Verifying cmp32...")
    print("0% complete...")

    with open("lib/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/start.S", "r") as fp:
        initlines += fp.readlines()
    with open("lib/math/cmp.S", "r") as fp:
        cmplines = fp.readlines()

    def _verify_cmp32(a: int, b: int) -> CPUCore:
        memory = getmemory(os.linesep.join([
            *initlines,
            "main:",
            f"PUSHI {a & 0xFF}",
            f"PUSHI {(a >> 8) & 0xFF}",
            f"PUSHI {(a >> 16) & 0xFF}",
            f"PUSHI {(a >> 24) & 0xFF}",
            f"PUSHI {b & 0xFF}",
            f"PUSHI {(b >> 8) & 0xFF}",
            f"PUSHI {(b >> 16) & 0xFF}",
            f"PUSHI {(b >> 24) & 0xFF}",
            "CALL cmp32",
            "HALT",
            *cmplines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)
        if a < b:
            answer = -1
        elif a == b:
            answer = 0
        elif a > b:
            answer = 1
        astack = bintoint32(
            (cpu.ram[cpu.pc + 4] << 24) +
            (cpu.ram[cpu.pc + 5] << 16) +
            (cpu.ram[cpu.pc + 6] << 8) +
            cpu.ram[cpu.pc + 7]
        )
        _assert(
            astack == a,
            f"cmp32 changed stack value from {a} to {astack}!",
        )
        bstack = bintoint32(
            (cpu.ram[cpu.pc] << 24) +
            (cpu.ram[cpu.pc + 1] << 16) +
            (cpu.ram[cpu.pc + 2] << 8) +
            cpu.ram[cpu.pc + 3]
        )
        _assert(
            bstack == b,
            f"cmp32 changed stack value from {b} to {bstack}!",
        )
        _assert(
            bintoint(cpu.a) == answer,
            f"Failed to cmp32({a}, {b}), "
            + f"got {bintoint(cpu.a)} instead of {answer}!",
        )
        return cpu

    cycles = 0
    instructions = 0
    count = 0
    for a in [-2**29, -2**21, -2**13, -2**6, 0, 2**6, 2**13, 2**21, 2**29]:
        for b in [-2**29, -2**21, -2**13, -2**6, 0, 2**6, 2**13, 2**21, 2**29]:
            cpu = _verify_cmp32(a, b)
            cycles += cpu.cycles
            instructions += cpu.ticks
            count += 1
            print(f"{CLEAR_LINE}{int(((a + 2**31) * 100) / (2**32))}% complete...")

    print(f"{CLEAR_LINE}Average cycles for cmp32: {int(cycles/count)}")
    print(f"Average instructions for ucmp32: {int(instructions/count)}")


def verifyumin(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "umin" not in only and "mathlib" not in only:
        return

    print("Verifying umin...")
    print("0% complete...")

    with open("lib/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/start.S", "r") as fp:
        initlines += fp.readlines()
    with open("lib/math/cmp.S", "r") as fp:
        cmplines = fp.readlines()

    cycles = 0
    instructions = 0
    count = 0
    for a in range(0, 256, 5 if full else 11):
        for b in range(0, 256, 3 if full else 7):
            memory = getmemory(os.linesep.join([
                *initlines,
                "main:",
                f"PUSHI {a}",
                f"PUSHI {b}",
                "CALL umin",
                "HALT",
                *cmplines,
            ]))
            cpu = CPUCore(memory)
            rununtilhalt(cpu)
            answer = min(a, b)
            _assert(
                cpu.ram[cpu.pc + 1] == a,
                f"umin changed stack value from {a} "
                + f"to {cpu.ram[cpu.pc + 1]}!",
            )
            _assert(
                cpu.ram[cpu.pc] == b,
                f"umin changed stack value from {b} to {cpu.ram[cpu.pc]}!",
            )
            _assert(
                cpu.a == answer,
                f"Failed to umin({a}, {b}), "
                + f"got {cpu.a} instead of {answer}!",
            )
            cycles += cpu.cycles
            instructions += cpu.ticks
            count += 1

        print(f"{CLEAR_LINE}{int((a * 100) / 256)}% complete...")
    print(f"{CLEAR_LINE}Average cycles for umin: {int(cycles/count)}")
    print(f"Average instructions for umin: {int(instructions/count)}")


def verifyumin16(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "umin16" not in only and "mathlib" not in only:
        return

    print("Verifying umin16...")
    print("0% complete...")

    with open("lib/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/start.S", "r") as fp:
        initlines += fp.readlines()
    with open("lib/math/cmp.S", "r") as fp:
        cmplines = fp.readlines()

    cycles = 0
    instructions = 0
    count = 0
    for a in range(0, 65536, 1281 if full else 2817):
        for b in range(0, 65536, 767 if full else 1791):
            memory = getmemory(os.linesep.join([
                *initlines,
                "main:",
                f"PUSHI {a & 0xFF}",
                f"PUSHI {(a >> 8) & 0xFF}",
                f"PUSHI {b & 0xFF}",
                f"PUSHI {(b >> 8) & 0xFF}",
                "LOADI 123",
                "CALL umin16",
                "HALT",
                *cmplines,
            ]))
            cpu = CPUCore(memory)
            rununtilhalt(cpu)
            answer = min(a, b)
            _assert(
                cpu.a == 123,
                f"umin16 changed accumulator value from {123} to {cpu.a}!",
            )
            result = ((cpu.ram[cpu.pc] << 8) + cpu.ram[cpu.pc + 1])
            _assert(
                result == answer,
                f"Failed to umin16({a}, {b}), "
                + f"got {answer} instead of {result}!",
            )
            cycles += cpu.cycles
            instructions += cpu.ticks
            count += 1

        print(f"{CLEAR_LINE}{int((a * 100) / 65536)}% complete...")
    print(f"{CLEAR_LINE}Average cycles for umin16: {int(cycles/count)}")
    print(f"Average instructions for umin16: {int(instructions/count)}")


def verifyumin32(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "umin32" not in only and "mathlib" not in only:
        return

    print("Verifying umin32...")
    print("0% complete...")

    with open("lib/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/start.S", "r") as fp:
        initlines += fp.readlines()
    with open("lib/math/cmp.S", "r") as fp:
        cmplines = fp.readlines()

    def _verify_umin32(a: int, b: int) -> CPUCore:
        memory = getmemory(os.linesep.join([
            *initlines,
            "main:",
            f"PUSHI {a & 0xFF}",
            f"PUSHI {(a >> 8) & 0xFF}",
            f"PUSHI {(a >> 16) & 0xFF}",
            f"PUSHI {(a >> 24) & 0xFF}",
            f"PUSHI {b & 0xFF}",
            f"PUSHI {(b >> 8) & 0xFF}",
            f"PUSHI {(b >> 16) & 0xFF}",
            f"PUSHI {(b >> 24) & 0xFF}",
            "LOADI 123",
            "CALL umin32",
            "HALT",
            *cmplines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)
        answer = min(a, b)
        result = (
            (cpu.ram[cpu.pc] << 24) +
            (cpu.ram[cpu.pc + 1] << 16) +
            (cpu.ram[cpu.pc + 2] << 8) +
            cpu.ram[cpu.pc + 3]
        )
        _assert(
            cpu.a == 123,
            f"umin32 changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            result == answer,
            f"Failed to umin32({a}, {b}), "
            + f"got {result} instead of {answer}!",
        )
        return cpu

    for a in [0, 2**6, 2**13, 2**21, 2**29]:
        for b in [0, 2**6, 2**13, 2**21, 2**29]:
            _verify_umin32(a, b)

    cycles = 0
    instructions = 0
    count = 0
    for a in range(0, 2**32, 2**26 + 2**13 + 19):
        for b in range(
            0, 2**32, (2**26 + 2**13 + 7)
            if full
            else (2**28 + 2**13 + 11)
        ):
            cpu = _verify_umin32(a, b)
            cycles += cpu.cycles
            instructions += cpu.ticks
            count += 1

        print(f"{CLEAR_LINE}{int((a * 100) / (2**32))}% complete...")
    print(f"{CLEAR_LINE}Average cycles for umin32: {int(cycles/count)}")
    print(f"Average instructions for umin32: {int(instructions/count)}")


def verifyumax(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "umax" not in only and "mathlib" not in only:
        return

    print("Verifying umax...")
    print("0% complete...")

    with open("lib/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/start.S", "r") as fp:
        initlines += fp.readlines()
    with open("lib/math/cmp.S", "r") as fp:
        cmplines = fp.readlines()

    cycles = 0
    instructions = 0
    count = 0
    for a in range(0, 256, 5 if full else 11):
        for b in range(0, 256, 3 if full else 7):
            memory = getmemory(os.linesep.join([
                *initlines,
                "main:",
                f"PUSHI {a}",
                f"PUSHI {b}",
                "CALL umax",
                "HALT",
                *cmplines,
            ]))
            cpu = CPUCore(memory)
            rununtilhalt(cpu)
            answer = max(a, b)
            _assert(
                cpu.ram[cpu.pc + 1] == a,
                f"umax changed stack value from {a} "
                + f"to {cpu.ram[cpu.pc + 1]}!",
            )
            _assert(
                cpu.ram[cpu.pc] == b,
                f"umax changed stack value from {b} to {cpu.ram[cpu.pc]}!",
            )
            _assert(
                cpu.a == answer,
                f"Failed to umax({a}, {b}), "
                + f"got {cpu.a} instead of {answer}!",
            )
            cycles += cpu.cycles
            instructions += cpu.ticks
            count += 1

        print(f"{CLEAR_LINE}{int((a * 100) / 256)}% complete...")
    print(f"{CLEAR_LINE}Average cycles for umax: {int(cycles/count)}")
    print(f"Average instructions for umax: {int(instructions/count)}")


def verifyumax16(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "umax16" not in only and "mathlib" not in only:
        return

    print("Verifying umax16...")
    print("0% complete...")

    with open("lib/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/start.S", "r") as fp:
        initlines += fp.readlines()
    with open("lib/math/cmp.S", "r") as fp:
        cmplines = fp.readlines()

    cycles = 0
    instructions = 0
    count = 0
    for a in range(0, 65536, 1281 if full else 2817):
        for b in range(0, 65536, 767 if full else 1791):
            memory = getmemory(os.linesep.join([
                *initlines,
                "main:",
                f"PUSHI {a & 0xFF}",
                f"PUSHI {(a >> 8) & 0xFF}",
                f"PUSHI {b & 0xFF}",
                f"PUSHI {(b >> 8) & 0xFF}",
                "LOADI 123",
                "CALL umax16",
                "HALT",
                *cmplines,
            ]))
            cpu = CPUCore(memory)
            rununtilhalt(cpu)
            answer = max(a, b)
            _assert(
                cpu.a == 123,
                f"umax16 changed accumulator value from {123} to {cpu.a}!",
            )
            result = ((cpu.ram[cpu.pc] << 8) + cpu.ram[cpu.pc + 1])
            _assert(
                result == answer,
                f"Failed to umax16({a}, {b}), "
                + f"got {answer} instead of {result}!",
            )
            cycles += cpu.cycles
            instructions += cpu.ticks
            count += 1

        print(f"{CLEAR_LINE}{int((a * 100) / 65536)}% complete...")
    print(f"{CLEAR_LINE}Average cycles for umax16: {int(cycles/count)}")
    print(f"Average instructions for umax16: {int(instructions/count)}")


def verifyumax32(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "umax32" not in only and "mathlib" not in only:
        return

    print("Verifying umax32...")
    print("0% complete...")

    with open("lib/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/start.S", "r") as fp:
        initlines += fp.readlines()
    with open("lib/math/cmp.S", "r") as fp:
        cmplines = fp.readlines()

    def _verify_umax32(a: int, b: int) -> CPUCore:
        memory = getmemory(os.linesep.join([
            *initlines,
            "main:",
            f"PUSHI {a & 0xFF}",
            f"PUSHI {(a >> 8) & 0xFF}",
            f"PUSHI {(a >> 16) & 0xFF}",
            f"PUSHI {(a >> 24) & 0xFF}",
            f"PUSHI {b & 0xFF}",
            f"PUSHI {(b >> 8) & 0xFF}",
            f"PUSHI {(b >> 16) & 0xFF}",
            f"PUSHI {(b >> 24) & 0xFF}",
            "LOADI 123",
            "CALL umax32",
            "HALT",
            *cmplines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)
        answer = max(a, b)
        result = (
            (cpu.ram[cpu.pc] << 24) +
            (cpu.ram[cpu.pc + 1] << 16) +
            (cpu.ram[cpu.pc + 2] << 8) +
            cpu.ram[cpu.pc + 3]
        )
        _assert(
            cpu.a == 123,
            f"umax32 changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            result == answer,
            f"Failed to umax32({a}, {b}), "
            + f"got {result} instead of {answer}!",
        )
        return cpu

    for a in [0, 2**6, 2**13, 2**21, 2**29]:
        for b in [0, 2**6, 2**13, 2**21, 2**29]:
            _verify_umax32(a, b)

    cycles = 0
    instructions = 0
    count = 0
    for a in range(0, 2**32, 2**26 + 2**13 + 19):
        for b in range(
            0, 2**32, (2**26 + 2**13 + 7)
            if full
            else (2**28 + 2**13 + 11)
        ):
            cpu = _verify_umax32(a, b)
            cycles += cpu.cycles
            instructions += cpu.ticks
            count += 1

        print(f"{CLEAR_LINE}{int((a * 100) / (2**32))}% complete...")
    print(f"{CLEAR_LINE}Average cycles for umax32: {int(cycles/count)}")
    print(f"Average instructions for umax32: {int(instructions/count)}")


def verifymathneg(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "mathneg" not in only and "mathlib" not in only:
        return

    print("Verifying neg...")
    print("0% complete...")

    with open("lib/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/start.S", "r") as fp:
        initlines += fp.readlines()
    with open("lib/math/neg.S", "r") as fp:
        neglines = fp.readlines()

    cycles = 0
    instructions = 0
    count = 0
    for x in range(-127, 128):
        memory = getmemory(os.linesep.join([
            *initlines,
            "main:",
            f"PUSHI {x}",
            "CALL neg",
            "HALT",
            *neglines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)
        calculated = bintoint(cpu.a)
        real = -x
        _assert(
            real == calculated,
            f"Failed to neg {x}, "
            + f"got {calculated} instead of {real}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1
        print(f"{CLEAR_LINE}{int(((x + 127) * 100) / 256)}% complete...")

    print(f"{CLEAR_LINE}Average cycles for neg: {int(cycles/count)}")
    print(f"Average instructions for neg: {int(instructions/count)}")


def verifyneg16(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "neg16" not in only and "mathlib" not in only:
        return

    print("Verifying neg16...")
    print("0% complete...")

    with open("lib/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/start.S", "r") as fp:
        initlines += fp.readlines()
    with open("lib/math/neg.S", "r") as fp:
        neglines = fp.readlines()

    cycles = 0
    instructions = 0
    count = 0
    for x in range(-32767, 32768, 79 if full else 763):
        xbin = inttobin16(x)
        memory = getmemory(os.linesep.join([
            *initlines,
            "main:",
            f"PUSHI {xbin & 0xFF}",
            f"PUSHI {(xbin >> 8) & 0xFF}",
            "LOADI 123",
            "CALL neg16",
            "HALT",
            *neglines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)
        calculated = bintoint16(
            (cpu.ram[cpu.pc] << 8) + cpu.ram[cpu.pc + 1]
        )
        real = -x
        _assert(
            cpu.a == 123,
            f"neg16 changed A register from 123 to {cpu.a}!",
        )
        _assert(
            real == calculated,
            f"Failed to neg16 {x}, "
            + f"got {calculated} instead of {real}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1
        print(f"{CLEAR_LINE}{int(((x + 32767) * 100) / 65536)}% complete...")

    print(f"{CLEAR_LINE}Average cycles for neg16: {int(cycles/count)}")
    print(f"Average instructions for neg16: {int(instructions/count)}")


def verifyneg32(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "neg32" not in only and "mathlib" not in only:
        return

    print("Verifying neg32...")
    print("0% complete...")

    with open("lib/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/start.S", "r") as fp:
        initlines += fp.readlines()
    with open("lib/math/neg.S", "r") as fp:
        neglines = fp.readlines()

    cycles = 0
    instructions = 0
    count = 0
    for x in range(
        -(2**31 - 1),
        (2**31),
        (2**22 + 3) if full else (2**25 + 3)
    ):
        xbin = inttobin32(x)
        memory = getmemory(os.linesep.join([
            *initlines,
            "main:",
            f"PUSHI {xbin & 0xFF}",
            f"PUSHI {(xbin >> 8) & 0xFF}",
            f"PUSHI {(xbin >> 16) & 0xFF}",
            f"PUSHI {(xbin >> 24) & 0xFF}",
            "LOADI 123",
            "CALL neg32",
            "HALT",
            *neglines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)
        calculated = bintoint32(
            (cpu.ram[cpu.pc] << 24) +
            (cpu.ram[cpu.pc + 1] << 16) +
            (cpu.ram[cpu.pc + 2] << 8) +
            cpu.ram[cpu.pc + 3]
        )
        real = -x
        _assert(
            cpu.a == 123,
            f"neg32 changed A register from 123 to {cpu.a}!",
        )
        _assert(
            real == calculated,
            f"Failed to neg32 {x}, "
            + f"got {calculated} instead of {real}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1
        print(
            f"{CLEAR_LINE}{int(((x + (2 ** 31)) * 100) / (2 ** 32))}% complete..."
        )

    print(f"{CLEAR_LINE}Average cycles for neg32: {int(cycles/count)}")
    print(f"Average instructions for neg32: {int(instructions/count)}")


def verifystrlen(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "strlen" not in only and "stringlib" not in only:
        return

    print("Verifying strlen...")

    with open("lib/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/start.S", "r") as fp:
        initlines += fp.readlines()
    with open("lib/string/strlen.S", "r") as fp:
        liblines = fp.readlines()

    cycles = 0
    instructions = 0
    count = 0
    for string in [
        "a test",
        "the quick brown fox jumps over the lazy dog",
        "",
        "whatever this is",
    ]:
        memory = getmemory(os.linesep.join([
            *initlines,
            ".org 0x1000",
            "string:",
            *[f".char {c!r}" for c in string],
            ".byte 0x00",
            "main:",
            "SWAP PC, SPC",
            "SETPC string",
            "SWAP PC, SPC",
            "PUSH SPC",
            "CALL strlen",
            "HALT",
            *liblines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)
        stack_input = (cpu.ram[cpu.pc] << 8) + cpu.ram[cpu.pc + 1]
        _assert(
            stack_input == 0x1000,
            f"strlen changed stack input from {0x1000} to {stack_input}!",
        )
        _assert(
            cpu.a == len(string),
            f"Failed to strlen({string!r}), "
            + f"got {cpu.a} instead of {len(string)}",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    print(f"Average cycles for strlen: {int(cycles/count)}")
    print(f"Average instructions for strlen: {int(instructions/count)}")


def verifystrcpy(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "strcpy" not in only and "stringlib" not in only:
        return

    print("Verifying strcpy...")

    with open("lib/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/start.S", "r") as fp:
        initlines += fp.readlines()
    with open("lib/string/strcpy.S", "r") as fp:
        liblines = fp.readlines()

    cycles = 0
    instructions = 0
    count = 0
    for string in [
        "a test",
        "the quick brown fox jumps over the lazy dog",
        "",
        "whatever this is",
    ]:
        memory = getmemory(os.linesep.join([
            *initlines,
            ".org 0x1000",
            "string:",
            *[f".char {c!r}" for c in string],
            ".byte 0x00",
            "main:",
            "SWAP PC, SPC",
            "SETPC string",
            "SWAP PC, SPC",
            "PUSH SPC",
            "PUSHI 0x00",
            "PUSHI 0x20",
            "LOADI 123",
            "CALL strcpy",
            "HALT",
            *liblines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)
        _assert(
            cpu.a == 123,
            f"strcpy changed A register from 123 to {cpu.a}!",
        )
        stack_dest = (cpu.ram[cpu.pc] << 8) + cpu.ram[cpu.pc + 1]
        stack_source = (cpu.ram[cpu.pc + 2] << 8) + cpu.ram[cpu.pc + 3]
        _assert(
            stack_source == 0x1000,
            f"strcpy changed stack source from {0x1000} to {stack_source}!",
        )
        _assert(
            stack_dest == 0x2000,
            f"strcpy changed stack source from {0x2000} to {stack_dest}!",
        )
        _assert(
            getstring(cpu, 0x2000) == string,
            f"Failed to strcpy(&{string!r}, 0x2000), "
            + f"got {getstring(cpu, 0x2000)!r} instead of {string!r}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    print(f"Average cycles for strcpy: {int(cycles/count)}")
    print(f"Average instructions for strcpy: {int(instructions/count)}")


def verifystrcat(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "strcat" not in only and "stringlib" not in only:
        return

    print("Verifying strcat...")

    with open("lib/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/start.S", "r") as fp:
        initlines += fp.readlines()
    with open("lib/string/strcat.S", "r") as fp:
        liblines = fp.readlines()

    cycles = 0
    instructions = 0
    count = 0
    for concatenation in [
        " and more",
        "",
    ]:
        for string in [
            "a test",
            "the quick brown fox jumps over the lazy dog",
            "",
            "whatever this is",
        ]:
            memory = getmemory(os.linesep.join([
                *initlines,
                ".org 0x1000",
                "concatenation:",
                *[f".char {c!r}" for c in concatenation],
                ".byte 0x00",
                ".org 0x2000",
                "string:",
                *[f".char {c!r}" for c in string],
                ".byte 0x00",
                ".org 0x3000",
                "main:",
                "SWAP PC, SPC",
                "SETPC concatenation",
                "SWAP PC, SPC",
                "PUSH SPC",
                "SWAP PC, SPC",
                "SETPC string",
                "SWAP PC, SPC",
                "PUSH SPC",
                "LOADI 123",
                "CALL strcat",
                "HALT",
                *liblines,
            ]))
            cpu = CPUCore(memory)
            rununtilhalt(cpu)
            _assert(
                cpu.a == 123,
                f"strcat changed A register from 123 to {cpu.a}!",
            )
            stack_dest = (cpu.ram[cpu.pc] << 8) + cpu.ram[cpu.pc + 1]
            stack_source = (
                (cpu.ram[cpu.pc + 2] << 8) + cpu.ram[cpu.pc + 3]
            )
            _assert(
                stack_source == 0x1000,
                f"strcat changed stack source from {0x1000} "
                + f"to {stack_source}!",
            )
            _assert(
                stack_dest == 0x2000,
                f"strcat changed stack source from {0x2000} to {stack_dest}!",
            )
            _assert(
                getstring(cpu, 0x2000) == (string + concatenation),
                f"Failed to strcat(&{concatenation!r}, &{string!r}), "
                + f"got {getstring(cpu, 0x2000)!r} "
                + f"instead of {(string + concatenation)!r}!",
            )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    print(f"Average cycles for strcat: {int(cycles/count)}")
    print(f"Average instructions for strcat: {int(instructions/count)}")


def verifystrcmp(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "strcmp" not in only and "stringlib" not in only:
        return

    print("Verifying strcmp...")

    with open("lib/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/start.S", "r") as fp:
        initlines += fp.readlines()
    with open("lib/math/cmp.S", "r") as fp:
        cmplines = fp.readlines()
    with open("lib/string/strcmp.S", "r") as fp:
        liblines = fp.readlines()

    cycles = 0
    instructions = 0
    count = 0
    for source in [
        "a test",
        "the quick brown fox jumps over the lazy dog",
        "",
        "whatever this is",
    ]:
        for destination in [
            "a test",
            "the quick brown fox jumps over the lazy dog",
            "",
            "whatever this is",
        ]:
            memory = getmemory(os.linesep.join([
                *initlines,
                ".org 0x1000",
                "source:",
                *[f".char {c!r}" for c in source],
                ".byte 0x00",
                ".org 0x2000",
                "destination:",
                *[f".char {c!r}" for c in destination],
                ".byte 0x00",
                ".org 0x3000",
                "main:",
                "SWAP PC, SPC",
                "SETPC source",
                "SWAP PC, SPC",
                "PUSH SPC",
                "SWAP PC, SPC",
                "SETPC destination",
                "SWAP PC, SPC",
                "PUSH SPC",
                "CALL strcmp",
                "HALT",
                *liblines,
                *cmplines,
            ]))
            cpu = CPUCore(memory)
            rununtilhalt(cpu)

            if source < destination:
                answer = -1
            elif source == destination:
                answer = 0
            elif source > destination:
                answer = 1
            stack_dest = (cpu.ram[cpu.pc] << 8) + cpu.ram[cpu.pc + 1]
            stack_source = (
                (cpu.ram[cpu.pc + 2] << 8) + cpu.ram[cpu.pc + 3]
            )
            _assert(
                stack_source == 0x1000,
                f"strcmp changed stack source from {0x1000} "
                + f"to {stack_source}!",
            )
            _assert(
                stack_dest == 0x2000,
                f"strcmp changed stack source from {0x2000} to {stack_dest}!",
            )
            _assert(
                bintoint(cpu.a) == answer,
                f"Failed to strcmp(&{source!r}, &{destination!r}), "
                + f"got {bintoint(cpu.a)} instead of {answer}!",
            )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    print(f"Average cycles for strcmp: {int(cycles/count)}")
    print(f"Average instructions for strcmp: {int(instructions/count)}")


def verifyitoa(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "itoa" not in only and "stringlib" not in only:
        return

    print("Verifying itoa...")
    print("0% complete...")

    with open("lib/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/start.S", "r") as fp:
        initlines += fp.readlines()
    with open("lib/math/divide.S", "r") as fp:
        dividelines = fp.readlines()
    with open("lib/conversion/itoa.S", "r") as fp:
        itoalines = fp.readlines()
    with open("lib/math/cmp.S", "r") as fp:
        cmplines = fp.readlines()
    with open("lib/math/add.S", "r") as fp:
        addlines = fp.readlines()
    with open("lib/math/neg.S", "r") as fp:
        neglines = fp.readlines()

    cycles = 0
    instructions = 0
    count = 0
    for x in sorted(chain([0], range(-128, 128, 1 if full else 7))):
        memory = getmemory(os.linesep.join([
            *initlines,
            "main:",
            "PUSHI 0x00",
            "PUSHI 0x10",
            f"LOADI {x}",
            "CALL itoa",
            "HALT",
            *itoalines,
            *dividelines,
            *cmplines,
            *addlines,
            *neglines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        _assert(
            bintoint(cpu.a) == x,
            f"itoa changed A register from {x} to {cpu.a}!",
        )
        stack_input = (cpu.ram[cpu.pc] << 8) + cpu.ram[cpu.pc + 1]
        _assert(
            stack_input == 0x1000,
            f"itoa changed stack input from {0x1000} to {stack_input}!",
        )
        _assert(
            getstring(cpu, 0x1000) == str(x),
            f"Failed to itoa({x}), "
            + f"got {getstring(cpu, 0x1000)} instead of {str(x)}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

        print(f"{CLEAR_LINE}{int(((x + 128) * 100) / 256)}% complete...")
    print(f"{CLEAR_LINE}Average cycles for itoa: {int(cycles/count)}")
    print(f"Average instructions for itoa: {int(instructions/count)}")


def verifyitoa16(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "itoa16" not in only and "stringlib" not in only:
        return

    print("Verifying itoa16...")
    print("0% complete...")

    with open("lib/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/start.S", "r") as fp:
        initlines += fp.readlines()
    with open("lib/math/divide.S", "r") as fp:
        dividelines = fp.readlines()
    with open("lib/conversion/itoa.S", "r") as fp:
        itoalines = fp.readlines()
    with open("lib/math/cmp.S", "r") as fp:
        cmplines = fp.readlines()
    with open("lib/math/add.S", "r") as fp:
        addlines = fp.readlines()
    with open("lib/math/neg.S", "r") as fp:
        neglines = fp.readlines()

    cycles = 0
    instructions = 0
    count = 0
    for x in sorted(chain([0], range(-32767, 32768, 123 if full else 2763))):
        xbin = inttobin16(x)
        memory = getmemory(os.linesep.join([
            *initlines,
            "main:",
            f"PUSHI {xbin & 0xFF}",
            f"PUSHI {(xbin >> 8) & 0xFF}",
            "PUSHI 0x00",
            "PUSHI 0x10",
            "LOADI 123",
            "CALL itoa16",
            "HALT",
            *itoalines,
            *dividelines,
            *cmplines,
            *addlines,
            *neglines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        _assert(
            cpu.a == 123,
            f"itoa16 changed accumulator value from {123} to {cpu.a}!",
        )
        stack_input = ((cpu.ram[cpu.pc] << 8) + cpu.ram[cpu.pc + 1])
        original_number = (
            (cpu.ram[cpu.pc + 2] << 8) + cpu.ram[cpu.pc + 3]
        )
        _assert(
            stack_input == 0x1000,
            f"itoa16 changed stack input from {0x1000} to {stack_input}!",
        )
        _assert(
            getstring(cpu, 0x1000) == str(x),
            f"Failed to itoa({x}), "
            + f"got {getstring(cpu, 0x1000)} instead of {str(x)}!",
        )
        _assert(
            bintoint16(original_number) == x,
            f"itoa16 changed original number input from {x} to {bintoint16(original_number)}!"
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

        print(f"{CLEAR_LINE}{int(((x + 32767) * 100) / 65536)}% complete...")

    print(f"{CLEAR_LINE}Average cycles for itoa16: {int(cycles/count)}")
    print(f"Average instructions for itoa16: {int(instructions/count)}")


def verifyitoa32(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "itoa32" not in only and "stringlib" not in only:
        return

    print("Verifying itoa32...")
    print("0% complete...")

    with open("lib/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/start.S", "r") as fp:
        initlines += fp.readlines()
    with open("lib/math/divide.S", "r") as fp:
        dividelines = fp.readlines()
    with open("lib/conversion/itoa.S", "r") as fp:
        itoalines = fp.readlines()
    with open("lib/math/cmp.S", "r") as fp:
        cmplines = fp.readlines()
    with open("lib/math/add.S", "r") as fp:
        addlines = fp.readlines()
    with open("lib/math/neg.S", "r") as fp:
        neglines = fp.readlines()

    cycles = 0
    instructions = 0
    count = 0
    for x in sorted(chain([0], range(-2147483648, 2147483647, 8060929 if full else 381075969))):
        xbin = inttobin32(x)
        memory = getmemory(os.linesep.join([
            *initlines,
            "main:",
            f"PUSHI {xbin & 0xFF}",
            f"PUSHI {(xbin >> 8) & 0xFF}",
            f"PUSHI {(xbin >> 16) & 0xFF}",
            f"PUSHI {(xbin >> 24) & 0xFF}",
            "PUSHI 0x00",
            "PUSHI 0x10",
            "LOADI 123",
            "CALL itoa32",
            "HALT",
            *itoalines,
            *dividelines,
            *cmplines,
            *addlines,
            *neglines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        _assert(
            cpu.a == 123,
            f"itoa32 changed accumulator value from {123} to {cpu.a}!",
        )
        stack_input = ((cpu.ram[cpu.pc] << 8) + cpu.ram[cpu.pc + 1])
        original_number = (
            (cpu.ram[cpu.pc + 2] << 24) +
            (cpu.ram[cpu.pc + 3] << 16) +
            (cpu.ram[cpu.pc + 4] << 8) +
            (cpu.ram[cpu.pc + 5] << 0)
        )
        _assert(
            stack_input == 0x1000,
            f"itoa32 changed stack input from {0x1000} to {stack_input}!",
        )
        _assert(
            getstring(cpu, 0x1000) == str(x),
            f"Failed to itoa({x}), "
            + f"got {getstring(cpu, 0x1000)} instead of {str(x)}!",
        )
        _assert(
            bintoint32(original_number) == x,
            f"itoa32 changed original number input from {x} to {bintoint32(original_number)}!"
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

        print(f"{CLEAR_LINE}{int(((x + 2147483647) * 100) / 2**32)}% complete...")

    print(f"{CLEAR_LINE}Average cycles for itoa32: {int(cycles/count)}")
    print(f"Average instructions for itoa32: {int(instructions/count)}")


def verifyatoi(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "atoi" not in only and "stringlib" not in only:
        return

    print("Verifying atoi...")
    print("0% complete...")

    with open("lib/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/start.S", "r") as fp:
        initlines += fp.readlines()
    with open("lib/math/multiply.S", "r") as fp:
        multiplylines = fp.readlines()
    with open("lib/math/add.S", "r") as fp:
        addlines = fp.readlines()
    with open("lib/math/neg.S", "r") as fp:
        neglines = fp.readlines()
    with open("lib/conversion/atoi.S", "r") as fp:
        atoilines = fp.readlines()

    cycles = 0
    instructions = 0
    count = 0
    for x in sorted(chain([0], range(-128, 128, 1 if full else 7))):
        if x < 0:
            prefixes = {"", " ", "  "}
        else:
            prefixes = {"", " ", "  ", "+", " +", "  +"}

        for prefix in prefixes:
            numstr = f"{prefix}{x}"
            for suffix in {"", " and some", "!"}:
                memory = getmemory(os.linesep.join([
                    *initlines,
                    ".org 0x1000",
                    "string:",
                    *[f".char {c!r}" for c in numstr],
                    *[f".char {c!r}" for c in suffix],
                    ".byte 0x00",
                    "main:",
                    "SWAP PC, SPC",
                    "SETPC string",
                    "SWAP PC, SPC",
                    "PUSH SPC",
                    "CALL atoi",
                    "HALT",
                    *atoilines,
                    *multiplylines,
                    *addlines,
                    *neglines,
                ]))
                cpu = CPUCore(memory)
                rununtilhalt(cpu)

                stack_input = (
                    (cpu.ram[cpu.pc] << 8) + cpu.ram[cpu.pc + 1]
                )
                _assert(
                    stack_input == (0x1000 + len(numstr)),
                    f"atoi expected stack {hex(0x1000 + len(numstr))} "
                    + f"but got {hex(stack_input)}!",
                )
                _assert(
                    bintoint(cpu.a) == x,
                    f"Failed to atoi({numstr}), "
                    + f"got {bintoint(cpu.a)} instead of {x}!",
                )
                cycles += cpu.cycles
                instructions += cpu.ticks
                count += 1

        print(f"{CLEAR_LINE}{int(((x + 128) * 100) / 256)}% complete...")

    print(f"{CLEAR_LINE}Average cycles for atoi: {int(cycles/count)}")
    print(f"Average instructions for atoi: {int(instructions/count)}")


def verifyatoi16(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "atoi16" not in only and "stringlib" not in only:
        return

    print("Verifying atoi16...")
    print("0% complete...")

    with open("lib/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/start.S", "r") as fp:
        initlines += fp.readlines()
    with open("lib/math/multiply.S", "r") as fp:
        multiplylines = fp.readlines()
    with open("lib/math/add.S", "r") as fp:
        addlines = fp.readlines()
    with open("lib/math/neg.S", "r") as fp:
        neglines = fp.readlines()
    with open("lib/conversion/atoi.S", "r") as fp:
        atoilines = fp.readlines()

    cycles = 0
    instructions = 0
    count = 0
    for x in sorted(chain([0], range(-32767, 32768, 123 if full else 2763))):
        if x < 0:
            prefixes = {"", " ", "  "}
        else:
            prefixes = {"", " ", "  ", "+", " +", "  +"}

        for prefix in prefixes:
            numstr = f"{prefix}{x}"
            for suffix in {"", " and some", "!"}:
                memory = getmemory(os.linesep.join([
                    *initlines,
                    ".org 0x1000",
                    "string:",
                    *[f".char {c!r}" for c in numstr],
                    *[f".char {c!r}" for c in suffix],
                    ".byte 0x00",
                    "main:",
                    "SWAP PC, SPC",
                    "SETPC string",
                    "SWAP PC, SPC",
                    "PUSH SPC",
                    # Doesn't matter the contents, just need to make room.
                    "SUBPCI 2",
                    # Just make sure we don't clobber A.
                    "LOADI 123",
                    "CALL atoi16",
                    "HALT",
                    *atoilines,
                    *multiplylines,
                    *addlines,
                    *neglines,
                ]))
                cpu = CPUCore(memory)
                rununtilhalt(cpu)

                _assert(
                    cpu.a == 123,
                    f"atoi16 changed accumulator value from {123} to {cpu.a}!",
                )
                result = ((cpu.ram[cpu.pc] << 8) + cpu.ram[cpu.pc + 1])
                stack_input = (
                    (cpu.ram[cpu.pc + 2] << 8) + cpu.ram[cpu.pc + 3]
                )
                _assert(
                    stack_input == (0x1000 + len(numstr)),
                    f"atoi expected stack {hex(0x1000 + len(numstr))} "
                    + f"but got {hex(stack_input)}!",
                )
                _assert(
                    bintoint16(result) == x,
                    f"Failed to atoi16({numstr}), "
                    + f"got {bintoint16(result)} instead of {x}!",
                )
                cycles += cpu.cycles
                instructions += cpu.ticks
                count += 1

        print(f"{CLEAR_LINE}{int(((x + 32767) * 100) / 65536)}% complete...")

    print(f"{CLEAR_LINE}Average cycles for atoi16: {int(cycles/count)}")
    print(f"Average instructions for atoi16: {int(instructions/count)}")


def verifyatoi32(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "atoi32" not in only and "stringlib" not in only:
        return

    print("Verifying atoi32...")
    print("0% complete...")

    with open("lib/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/start.S", "r") as fp:
        initlines += fp.readlines()
    with open("lib/math/multiply.S", "r") as fp:
        multiplylines = fp.readlines()
    with open("lib/math/add.S", "r") as fp:
        addlines = fp.readlines()
    with open("lib/math/neg.S", "r") as fp:
        neglines = fp.readlines()
    with open("lib/conversion/atoi.S", "r") as fp:
        atoilines = fp.readlines()

    cycles = 0
    instructions = 0
    count = 0
    for x in sorted(chain([0], range(-2147483648, 2147483647, 8060929 if full else 381075969))):
        if x < 0:
            prefixes = {"", " ", "  "}
        else:
            prefixes = {"", " ", "  ", "+", " +", "  +"}

        for prefix in prefixes:
            numstr = f"{prefix}{x}"
            for suffix in {"", " and some", "!"}:
                memory = getmemory(os.linesep.join([
                    *initlines,
                    ".org 0x1000",
                    "string:",
                    *[f".char {c!r}" for c in numstr],
                    *[f".char {c!r}" for c in suffix],
                    ".byte 0x00",
                    "main:",
                    "SWAP PC, SPC",
                    "SETPC string",
                    "SWAP PC, SPC",
                    "PUSH SPC",
                    # Doesn't matter the contents, just need to make room.
                    "SUBPCI 4",
                    # Just make sure we don't clobber A.
                    "LOADI 123",
                    "CALL atoi32",
                    "HALT",
                    *atoilines,
                    *multiplylines,
                    *addlines,
                    *neglines,
                ]))
                cpu = CPUCore(memory)
                rununtilhalt(cpu)

                _assert(
                    cpu.a == 123,
                    f"atoi32 changed accumulator value from {123} to {cpu.a}!",
                )
                result = (
                    (cpu.ram[cpu.pc + 0] << 24) +
                    (cpu.ram[cpu.pc + 1] << 16) +
                    (cpu.ram[cpu.pc + 2] << 8) +
                    (cpu.ram[cpu.pc + 3])
                )
                stack_input = (
                    (cpu.ram[cpu.pc + 4] << 8) +
                    (cpu.ram[cpu.pc + 5])
                )
                _assert(
                    stack_input == (0x1000 + len(numstr)),
                    f"atoi expected stack {hex(0x1000 + len(numstr))} "
                    + f"but got {hex(stack_input)}!",
                )
                _assert(
                    bintoint32(result) == x,
                    f"Failed to atoi32({numstr}), "
                    + f"got {bintoint32(result)} instead of {x}!",
                )
                cycles += cpu.cycles
                instructions += cpu.ticks
                count += 1

        print(f"{CLEAR_LINE}{int(((x + 2147483647) * 100) / 2**32)}% complete...")

    print(f"{CLEAR_LINE}Average cycles for atoi32: {int(cycles/count)}")
    print(f"Average instructions for atoi32: {int(instructions/count)}")


def verifystaticreturn(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "staticreturn" not in only and "compiler" not in only:
        return

    print("Verifying staticreturn...")

    with open("lib/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/start.S", "r") as fp:
        initlines += fp.readlines()

    cycles = 0
    instructions = 0
    count = 0
    for x in [37, -37, 123, 255, 0, 42]:
        # A normal static return requires the caller to allocate space on the stack for any
        # return value pieces that don't fit in the original parameters.
        memory = getmemory(os.linesep.join([
            *initlines,
            *parse_and_compile_module("staticreturn", textwrap.dedent(f"""
                def staticreturn() -> int8:
                    return {x}
            """)).code,
            "main:",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            "LOADI 123",
            "DECPC",
            "CALL staticreturn",
            "HALT",
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        _assert(
            cpu.a == 123,
            f"staticreturn changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"staticreturn changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"staticreturn changed V value from {222} to {cpu.v}!",
        )
        result = cpu.ram[cpu.pc + 0]
        if x > 127:
            _assert(
                result == x,
                "Failed to staticreturn, "
                + f"got {result} instead of {x}!",
            )
        else:
            _assert(
                bintoint(result) == x,
                "Failed to staticreturn, "
                + f"got {bintoint(result)} instead of {x}!",
            )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    print(f"Average cycles for staticreturn: {int(cycles/count)}")
    print(f"Average instructions for staticreturn: {int(instructions/count)}")

    print("Verifying staticreturn without padding...")

    cycles = 0
    instructions = 0
    count = 0
    for x in [37, -37, 123, 255, 0, 42]:
        # A nopad return shuffles things in place to ensure that the return value gets moved properly.
        memory = getmemory(os.linesep.join([
            *initlines,
            *parse_and_compile_module("staticreturn", textwrap.dedent(f"""
                def staticreturn() -> nopad[int8]:
                    return {x}
            """)).code,
            "main:",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            "LOADI 123",
            "CALL staticreturn",
            "HALT",
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        _assert(
            cpu.a == 123,
            f"staticreturn changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"staticreturn changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"staticreturn changed V value from {222} to {cpu.v}!",
        )
        result = cpu.ram[cpu.pc + 0]
        if x > 127:
            _assert(
                result == x,
                "Failed to staticreturn, "
                + f"got {result} instead of {x}!",
            )
        else:
            _assert(
                bintoint(result) == x,
                "Failed to staticreturn, "
                + f"got {bintoint(result)} instead of {x}!",
            )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    print(f"Average cycles for staticreturn: {int(cycles/count)}")
    print(f"Average instructions for staticreturn: {int(instructions/count)}")


def verifydowncast(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "downcast" not in only and "compiler" not in only:
        return

    print("Verifying downcast...")

    with open("lib/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/start.S", "r") as fp:
        initlines += fp.readlines()

    cycles = 0
    instructions = 0
    count = 0
    for x in [37, -37, 89, 0, 42, -42, -1024, 1024, 555, -555, 12345, -12345, 54321]:
        memory = getmemory(os.linesep.join([
            *initlines,
            *parse_and_compile_module("downcast", textwrap.dedent("""
                def func(param1: int16) -> nopad[int8]:
                    return param1
            """)).code,
            "main:",
            f"PUSHI {x & 0xFF}",
            f"PUSHI {(x >> 8) & 0xFF}",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            "LOADI 123",
            "CALL func",
            "HALT",
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        _assert(
            cpu.a == 123,
            f"downcast changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"downcast changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"downcast changed V value from {222} to {cpu.v}!",
        )
        result = bintoint(cpu.ram[cpu.pc])
        expected = bintoint(x & 0xFF)
        _assert(
            result == expected,
            "Failed to downcast, "
            + f"got {result} instead of {expected}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    for x in [37, -37, 89, 0, 42, -42, -1024, 1024, 555, -555, 12345, -12345, 54321, 123456789, 987654321, 0xDEADBEEF, 0xCAFEBABE]:
        memory = getmemory(os.linesep.join([
            *initlines,
            *parse_and_compile_module("downcast", textwrap.dedent("""
                def func(param1: int32) -> nopad[int8]:
                    return param1
            """)).code,
            "main:",
            f"PUSHI {x & 0xFF}",
            f"PUSHI {(x >> 8) & 0xFF}",
            f"PUSHI {(x >> 16) & 0xFF}",
            f"PUSHI {(x >> 24) & 0xFF}",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            "LOADI 123",
            "CALL func",
            "HALT",
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        _assert(
            cpu.a == 123,
            f"downcast changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"downcast changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"downcast changed V value from {222} to {cpu.v}!",
        )
        result = bintoint(cpu.ram[cpu.pc])
        expected = bintoint(x & 0xFF)
        _assert(
            result == expected,
            "Failed to downcast, "
            + f"got {result} instead of {expected}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    for x in [0xDEADBEEF, 37, -37, 89, 0, 42, -42, -1024, 1024, 555, -555, 12345, -12345, 54321, 123456789, 987654321, 0xDEADBEEF, 0xCAFEBABE]:
        memory = getmemory(os.linesep.join([
            *initlines,
            *parse_and_compile_module("downcast", textwrap.dedent("""
                def func(param1: int32) -> nopad[int16]:
                    return param1
            """)).code,
            "main:",
            f"PUSHI {x & 0xFF}",
            f"PUSHI {(x >> 8) & 0xFF}",
            f"PUSHI {(x >> 16) & 0xFF}",
            f"PUSHI {(x >> 24) & 0xFF}",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            "LOADI 123",
            "CALL func",
            "HALT",
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        _assert(
            cpu.a == 123,
            f"downcast changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"downcast changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"downcast changed V value from {222} to {cpu.v}!",
        )
        result = bintoint16(
            (cpu.ram[cpu.pc] << 8) + cpu.ram[cpu.pc + 1]
        )
        expected = bintoint16(x & 0xFFFF)
        _assert(
            result == expected,
            "Failed to downcast, "
            + f"got {result} instead of {expected}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    print(f"Average cycles for downcast: {int(cycles/count)}")
    print(f"Average instructions for downcast: {int(instructions/count)}")


def verifyupcast(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "upcast" not in only and "compiler" not in only:
        return

    print("Verifying upcast...")

    with open("lib/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/start.S", "r") as fp:
        initlines += fp.readlines()

    cycles = 0
    instructions = 0
    count = 0
    for x in [37, -37, 89, 0, 42, -42]:
        memory = getmemory(os.linesep.join([
            *initlines,
            *parse_and_compile_module("upcast", textwrap.dedent("""
                def func(param1: int8) -> nopad[int16]:
                    return param1
            """)).code,
            "main:",
            f"LOADI {x}",
            "PUSH A",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            "LOADI 123",
            "CALL func",
            "HALT",
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        _assert(
            cpu.a == 123,
            f"upcast changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"upcast changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"upcast changed V value from {222} to {cpu.v}!",
        )
        result = bintoint16(
            (cpu.ram[cpu.pc] << 8) + cpu.ram[cpu.pc + 1]
        )
        expected = x
        _assert(
            result == expected,
            "Failed to upcast, "
            + f"got {result} instead of {expected}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    for x in [37, -37, 89, 0, 42, -42]:
        memory = getmemory(os.linesep.join([
            *initlines,
            *parse_and_compile_module("upcast", textwrap.dedent("""
                def func(param1: int8) -> nopad[int32]:
                    return param1
            """)).code,
            "main:",
            f"LOADI {x}",
            "PUSH A",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            "LOADI 123",
            "CALL func",
            "HALT",
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        _assert(
            cpu.a == 123,
            f"upcast changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"upcast changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"upcast changed V value from {222} to {cpu.v}!",
        )
        result = bintoint32(
            (cpu.ram[cpu.pc + 0] << 24) +
            (cpu.ram[cpu.pc + 1] << 16) +
            (cpu.ram[cpu.pc + 2] << 8) +
            (cpu.ram[cpu.pc + 3])
        )
        expected = x
        _assert(
            result == expected,
            "Failed to upcast, "
            + f"got {result} instead of {expected}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    for x in [37, -37, 89, 0, 42, -42, -1024, 1024, 555, -555, 12345, -12345, 32000, -32000]:
        memory = getmemory(os.linesep.join([
            *initlines,
            *parse_and_compile_module("upcast", textwrap.dedent("""
                def func(param1: int16) -> nopad[int32]:
                    return param1
            """)).code,
            "main:",
            f"PUSHI {x & 0xFF}",
            f"PUSHI {(x >> 8) & 0xFF}",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            "LOADI 123",
            "CALL func",
            "HALT",
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        _assert(
            cpu.a == 123,
            f"upcast changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"upcast changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"upcast changed V value from {222} to {cpu.v}!",
        )
        result = bintoint32(
            (cpu.ram[cpu.pc + 0] << 24) +
            (cpu.ram[cpu.pc + 1] << 16) +
            (cpu.ram[cpu.pc + 2] << 8) +
            (cpu.ram[cpu.pc + 3])
        )
        expected = x
        _assert(
            result == expected,
            "Failed to upcast, "
            + f"got {result} instead of {expected}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    print(f"Average cycles for upcast: {int(cycles/count)}")
    print(f"Average instructions for upcast: {int(instructions/count)}")


def verifyunsignedupcast(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "unsignedupcast" not in only and "compiler" not in only:
        return

    print("Verifying unsignedupcast...")

    with open("lib/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/start.S", "r") as fp:
        initlines += fp.readlines()

    cycles = 0
    instructions = 0
    count = 0
    for x in [37, 89, 0, 42, 128, 255]:
        memory = getmemory(os.linesep.join([
            *initlines,
            *parse_and_compile_module("unsignedupcast", textwrap.dedent("""
                def func(param1: uint8) -> nopad[uint16]:
                    return param1
            """)).code,
            "main:",
            f"LOADI {x}",
            "PUSH A",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            "LOADI 123",
            "CALL func",
            "HALT",
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        _assert(
            cpu.a == 123,
            f"unsignedupcast changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"unsignedupcast changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"unsignedupcast changed V value from {222} to {cpu.v}!",
        )
        result = (
            (cpu.ram[cpu.pc] << 8) + cpu.ram[cpu.pc + 1]
        )
        expected = x
        _assert(
            result == expected,
            "Failed to unsignedupcast, "
            + f"got {result} instead of {expected}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    for x in [37, 89, 0, 42, 128, 255]:
        memory = getmemory(os.linesep.join([
            *initlines,
            *parse_and_compile_module("unsignedupcast", textwrap.dedent("""
                def func(param1: uint8) -> nopad[uint32]:
                    return param1
            """)).code,
            "main:",
            f"LOADI {x}",
            "PUSH A",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            "LOADI 123",
            "CALL func",
            "HALT",
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        _assert(
            cpu.a == 123,
            f"unsignedupcast changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"unsignedupcast changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"unsignedupcast changed V value from {222} to {cpu.v}!",
        )
        result = (
            (cpu.ram[cpu.pc + 0] << 24) +
            (cpu.ram[cpu.pc + 1] << 16) +
            (cpu.ram[cpu.pc + 2] << 8) +
            (cpu.ram[cpu.pc + 3])
        )
        expected = x
        _assert(
            result == expected,
            "Failed to unsignedupcast, "
            + f"got {result} instead of {expected}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    for x in [37, 89, 0, 42, 128, 255, 1024, 555, 12345, 32768, 65535]:
        memory = getmemory(os.linesep.join([
            *initlines,
            *parse_and_compile_module("unsignedupcast", textwrap.dedent("""
                def func(param1: uint16) -> nopad[uint32]:
                    return param1
            """)).code,
            "main:",
            f"PUSHI {x & 0xFF}",
            f"PUSHI {(x >> 8) & 0xFF}",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            "LOADI 123",
            "CALL func",
            "HALT",
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        _assert(
            cpu.a == 123,
            f"unsignedupcast changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"unsignedupcast changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"unsignedupcast changed V value from {222} to {cpu.v}!",
        )
        result = bintoint32(
            (cpu.ram[cpu.pc + 0] << 24) +
            (cpu.ram[cpu.pc + 1] << 16) +
            (cpu.ram[cpu.pc + 2] << 8) +
            (cpu.ram[cpu.pc + 3])
        )
        expected = x
        _assert(
            result == expected,
            "Failed to unsignedupcast, "
            + f"got {result} instead of {expected}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    print(f"Average cycles for unsignedupcast: {int(cycles/count)}")
    print(f"Average instructions for unsignedupcast: {int(instructions/count)}")


def verifyechoparam(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "echoparam" not in only and "compiler" not in only:
        return

    print("Verifying echoparam...")

    with open("lib/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/start.S", "r") as fp:
        initlines += fp.readlines()

    cycles = 0
    instructions = 0
    count = 0
    for x in [37, -37, 99, 0, 42, -42]:
        memory = getmemory(os.linesep.join([
            *initlines,
            *parse_and_compile_module("echoparam", textwrap.dedent("""
                def echoparam(param1: int8) -> int8:
                    return param1
            """)).code,
            "main:",
            f"LOADI {x}",
            "PUSH A",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            "LOADI 123",
            "CALL echoparam",
            "HALT",
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        _assert(
            cpu.a == 123,
            f"echoparam changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"echoparam changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"echoparam changed V value from {222} to {cpu.v}!",
        )
        result = cpu.ram[cpu.pc + 0]
        _assert(
            bintoint(result) == x,
            "Failed to echoparam, "
            + f"got {bintoint(result)} instead of {x}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    print(f"Average cycles for echoparam: {int(cycles/count)}")
    print(f"Average instructions for echoparam: {int(instructions/count)}")

    print("Verifying echoparam without padding...")

    cycles = 0
    instructions = 0
    count = 0
    for x in [37, -37, 99, 0, 42, -42]:
        memory = getmemory(os.linesep.join([
            *initlines,
            *parse_and_compile_module("echoparam", textwrap.dedent("""
                def echoparam(param1: int8) -> nopad[int8]:
                    return param1
            """)).code,
            "main:",
            f"LOADI {x}",
            "PUSH A",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            "LOADI 123",
            "CALL echoparam",
            "HALT",
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        _assert(
            cpu.a == 123,
            f"echoparam changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"echoparam changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"echoparam changed V value from {222} to {cpu.v}!",
        )
        result = cpu.ram[cpu.pc + 0]
        _assert(
            bintoint(result) == x,
            "Failed to echoparam, "
            + f"got {bintoint(result)} instead of {x}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    print(f"Average cycles for echoparam: {int(cycles/count)}")
    print(f"Average instructions for echoparam: {int(instructions/count)}")


def verifyaddandreturn(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "addandreturn" not in only and "compiler" not in only:
        return

    print("Verifying addandreturn...")

    with open("lib/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/start.S", "r") as fp:
        initlines += fp.readlines()
    with open("lib/math/add.S", "r") as fp:
        addlines = fp.readlines()

    cycles = 0
    instructions = 0
    count = 0
    for x in [0, 37, -37, 99, 42, -42]:
        memory = getmemory(os.linesep.join([
            *initlines,
            *parse_and_compile_module("addandreturn", textwrap.dedent("""
                def addandreturn(param1: int8) -> int8:
                    return param1 + 15
            """)).code,
            "main:",
            f"LOADI {x}",
            "PUSH A",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            "LOADI 123",
            "CALL addandreturn",
            "HALT",
            *addlines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        _assert(
            cpu.a == 123,
            f"addandreturn changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"addandreturn changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"addandreturn changed V value from {222} to {cpu.v}!",
        )
        result = cpu.ram[cpu.pc + 0]
        _assert(
            bintoint(result) == x + 15,
            "Failed to addandreturn, "
            + f"got {bintoint(result)} instead of {x + 15}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    for x in [0, 37, -37, 89, 42, -42, -1024, 1024, 555, -555, 12345, -12345, 9999, -9999]:
        memory = getmemory(os.linesep.join([
            *initlines,
            *parse_and_compile_module("addandreturn", textwrap.dedent("""
                def addandreturn(param1: int16) -> int16:
                    return param1 + 12345
            """)).code,
            "main:",
            f"PUSHI {x & 0xFF}",
            f"PUSHI {(x >> 8) & 0xFF}",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            "LOADI 123",
            "CALL addandreturn",
            "HALT",
            *addlines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        _assert(
            cpu.a == 123,
            f"addandreturn changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"addandreturn changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"addandreturn changed V value from {222} to {cpu.v}!",
        )
        result = bintoint16(
            (cpu.ram[cpu.pc] << 8) + cpu.ram[cpu.pc + 1]
        )
        expected = x + 12345
        _assert(
            result == expected,
            "Failed to addandreturn, "
            + f"got {result} instead of {expected}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    for x in [0, 37, -37, 89, 42, -42, -1024, 1024, 555, -555, 12345, -12345, 32000, -32000, 1234567890, -1234567890]:
        memory = getmemory(os.linesep.join([
            *initlines,
            *parse_and_compile_module("addandreturn", textwrap.dedent("""
                def addandreturn(param1: int32) -> int32:
                    return param1 + 123456
            """)).code,
            "main:",
            f"PUSHI {x & 0xFF}",
            f"PUSHI {(x >> 8) & 0xFF}",
            f"PUSHI {(x >> 16) & 0xFF}",
            f"PUSHI {(x >> 24) & 0xFF}",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            "LOADI 123",
            "CALL addandreturn",
            "HALT",
            *addlines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        _assert(
            cpu.a == 123,
            f"addandreturn changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"addandreturn changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"addandreturn changed V value from {222} to {cpu.v}!",
        )
        result = bintoint32(
            (cpu.ram[cpu.pc + 0] << 24) +
            (cpu.ram[cpu.pc + 1] << 16) +
            (cpu.ram[cpu.pc + 2] << 8) +
            (cpu.ram[cpu.pc + 3] << 0)
        )
        expected = x + 123456
        _assert(
            result == expected,
            "Failed to addandreturn, "
            + f"got {result} instead of {expected}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    print(f"Average cycles for addandreturn: {int(cycles/count)}")
    print(f"Average instructions for addandreturn: {int(instructions/count)}")
    print("Verifying addandreturn with reversed parameters...")

    cycles = 0
    instructions = 0
    count = 0
    for x in [0, 37, -37, 99, 42, -42]:
        memory = getmemory(os.linesep.join([
            *initlines,
            *parse_and_compile_module("addandreturn", textwrap.dedent("""
                def addandreturn(param1: int8) -> int8:
                    return 15 + param1
            """)).code,
            "main:",
            f"LOADI {x}",
            "PUSH A",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            "LOADI 123",
            "CALL addandreturn",
            "HALT",
            *addlines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        _assert(
            cpu.a == 123,
            f"addandreturn changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"addandreturn changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"addandreturn changed V value from {222} to {cpu.v}!",
        )
        result = cpu.ram[cpu.pc + 0]
        _assert(
            bintoint(result) == x + 15,
            "Failed to addandreturn, "
            + f"got {bintoint(result)} instead of {x + 15}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    print(f"Average cycles for addandreturn: {int(cycles/count)}")
    print(f"Average instructions for addandreturn: {int(instructions/count)}")
    print("Verifying addandreturn without padding...")

    cycles = 0
    instructions = 0
    count = 0
    for x in [0, 37, -37, 99, 42, -42]:
        # A nopad return shuffles things in place to ensure that the return value gets moved properly.
        memory = getmemory(os.linesep.join([
            *initlines,
            *parse_and_compile_module("addandreturn", textwrap.dedent("""
                def addandreturn(param1: int8) -> nopad[int8]:
                    return param1 + 15
            """)).code,
            "main:",
            f"LOADI {x}",
            "PUSH A",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            "LOADI 123",
            "CALL addandreturn",
            "HALT",
            *addlines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        _assert(
            cpu.a == 123,
            f"addandreturn changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"addandreturn changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"addandreturn changed V value from {222} to {cpu.v}!",
        )
        result = cpu.ram[cpu.pc + 0]
        if x > 127:
            _assert(
                result == x,
                "Failed to addandreturn, "
                + f"got {result} instead of {x}!",
            )
        else:
            _assert(
                bintoint(result) == x + 15,
                "Failed to addandreturn, "
                + f"got {bintoint(result)} instead of {x}!",
            )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    print(f"Average cycles for addandreturn: {int(cycles/count)}")
    print(f"Average instructions for addandreturn: {int(instructions/count)}")


def verifysubtractandreturn(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "subtractandreturn" not in only and "compiler" not in only:
        return

    print("Verifying subtractandreturn...")

    with open("lib/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/start.S", "r") as fp:
        initlines += fp.readlines()
    with open("lib/math/add.S", "r") as fp:
        addlines = fp.readlines()
    with open("lib/math/neg.S", "r") as fp:
        neglines = fp.readlines()

    cycles = 0
    instructions = 0
    count = 0
    for x in [0, 37, -37, 99, 42, -42]:
        memory = getmemory(os.linesep.join([
            *initlines,
            *parse_and_compile_module("subtractandreturn", textwrap.dedent("""
                def subtractandreturn(param1: int8) -> int8:
                    return param1 - 15
            """)).code,
            "main:",
            f"LOADI {x}",
            "PUSH A",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            "LOADI 123",
            "CALL subtractandreturn",
            "HALT",
            *addlines,
            *neglines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        _assert(
            cpu.a == 123,
            f"subtractandreturn changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"subtractandreturn changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"subtractandreturn changed V value from {222} to {cpu.v}!",
        )
        result = cpu.ram[cpu.pc + 0]
        _assert(
            bintoint(result) == x - 15,
            "Failed to subtractandreturn, "
            + f"got {bintoint(result)} instead of {x - 15}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    for x in [0, 37, -37, 89, 42, -42, -1024, 1024, 555, -555, 12345, -12345, 9999, -9999]:
        memory = getmemory(os.linesep.join([
            *initlines,
            *parse_and_compile_module("subtractandreturn", textwrap.dedent("""
                def subtractandreturn(param1: int16) -> int16:
                    return param1 - 12345
            """)).code,
            "main:",
            f"PUSHI {x & 0xFF}",
            f"PUSHI {(x >> 8) & 0xFF}",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            "LOADI 123",
            "CALL subtractandreturn",
            "HALT",
            *addlines,
            *neglines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        _assert(
            cpu.a == 123,
            f"subtractandreturn changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"subtractandreturn changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"subtractandreturn changed V value from {222} to {cpu.v}!",
        )
        result = bintoint16(
            (cpu.ram[cpu.pc] << 8) + cpu.ram[cpu.pc + 1]
        )
        expected = x - 12345
        _assert(
            result == expected,
            "Failed to subtractandreturn, "
            + f"got {result} instead of {expected}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    for x in [0, 37, -37, 89, 42, -42, -1024, 1024, 555, -555, 12345, -12345, 32000, -32000, 1234567890, -1234567890]:
        memory = getmemory(os.linesep.join([
            *initlines,
            *parse_and_compile_module("subtractandreturn", textwrap.dedent("""
                def subtractandreturn(param1: int32) -> int32:
                    return param1 - 123456
            """)).code,
            "main:",
            f"PUSHI {x & 0xFF}",
            f"PUSHI {(x >> 8) & 0xFF}",
            f"PUSHI {(x >> 16) & 0xFF}",
            f"PUSHI {(x >> 24) & 0xFF}",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            "LOADI 123",
            "CALL subtractandreturn",
            "HALT",
            *addlines,
            *neglines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        _assert(
            cpu.a == 123,
            f"subtractandreturn changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"subtractandreturn changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"subtractandreturn changed V value from {222} to {cpu.v}!",
        )
        result = bintoint32(
            (cpu.ram[cpu.pc + 0] << 24) +
            (cpu.ram[cpu.pc + 1] << 16) +
            (cpu.ram[cpu.pc + 2] << 8) +
            (cpu.ram[cpu.pc + 3] << 0)
        )
        expected = x - 123456
        _assert(
            result == expected,
            "Failed to subtractandreturn, "
            + f"got {result} instead of {expected}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    print(f"Average cycles for subtractandreturn: {int(cycles/count)}")
    print(f"Average instructions for subtractandreturn: {int(instructions/count)}")
    print("Verifying subtractandreturn with reversed parameters...")

    cycles = 0
    instructions = 0
    count = 0
    for x in [37, -37, 99, 0, 42, -42]:
        memory = getmemory(os.linesep.join([
            *initlines,
            *parse_and_compile_module("subtractandreturn", textwrap.dedent("""
                def subtractandreturn(param1: int8) -> int8:
                    return 15 - param1
            """)).code,
            "main:",
            f"LOADI {x}",
            "PUSH A",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            "LOADI 123",
            "CALL subtractandreturn",
            "HALT",
            *addlines,
            *neglines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        _assert(
            cpu.a == 123,
            f"subtractandreturn changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"subtractandreturn changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"subtractandreturn changed V value from {222} to {cpu.v}!",
        )
        result = cpu.ram[cpu.pc + 0]
        _assert(
            bintoint(result) == 15 - x,
            "Failed to subtractandreturn, "
            + f"got {bintoint(result)} instead of {15 - x}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    print(f"Average cycles for subtractandreturn: {int(cycles/count)}")
    print(f"Average instructions for subtractandreturn: {int(instructions/count)}")
    print("Verifying subtractandreturn without padding...")

    cycles = 0
    instructions = 0
    count = 0
    for x in [37, -37, 99, 0, 42, -42]:
        # A nopad return shuffles things in place to ensure that the return value gets moved properly.
        memory = getmemory(os.linesep.join([
            *initlines,
            *parse_and_compile_module("subtractandreturn", textwrap.dedent("""
                def subtractandreturn(param1: int8) -> nopad[int8]:
                    return param1 - 15
            """)).code,
            "main:",
            f"LOADI {x}",
            "PUSH A",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            "LOADI 123",
            "CALL subtractandreturn",
            "HALT",
            *addlines,
            *neglines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        _assert(
            cpu.a == 123,
            f"subtractandreturn changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"subtractandreturn changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"subtractandreturn changed V value from {222} to {cpu.v}!",
        )
        result = cpu.ram[cpu.pc + 0]
        if x > 127:
            _assert(
                result == x,
                "Failed to subtractandreturn, "
                + f"got {result} instead of {x}!",
            )
        else:
            _assert(
                bintoint(result) == x - 15,
                "Failed to subtractandreturn, "
                + f"got {bintoint(result)} instead of {x}!",
            )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    print(f"Average cycles for subtractandreturn: {int(cycles/count)}")
    print(f"Average instructions for subtractandreturn: {int(instructions/count)}")


def verifymultiplyandreturn(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "multiplyandreturn" not in only and "compiler" not in only:
        return

    print("Verifying multiplyandreturn unsigned...")

    with open("lib/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/start.S", "r") as fp:
        initlines += fp.readlines()
    with open("lib/math/add.S", "r") as fp:
        addlines = fp.readlines()
    with open("lib/math/multiply.S", "r") as fp:
        multiplylines = fp.readlines()

    cycles = 0
    instructions = 0
    count = 0
    for x in [0, 37, 99, 42]:
        memory = getmemory(os.linesep.join([
            *initlines,
            *parse_and_compile_module("multiplyandreturn", textwrap.dedent("""
                def multiplyandreturn(param1: uint8) -> uint8:
                    return param1 * 3
            """)).code,
            "main:",
            f"LOADI {x}",
            "PUSH A",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            "LOADI 123",
            "CALL multiplyandreturn",
            "HALT",
            *addlines,
            *multiplylines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        _assert(
            cpu.a == 123,
            f"multiplyandreturn changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"multiplyandreturn changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"multiplyandreturn changed V value from {222} to {cpu.v}!",
        )
        result = cpu.ram[cpu.pc + 0]
        expected = (x * 3) & 0xFF
        _assert(
            result == expected,
            "Failed to multiplyandreturn, "
            + f"got {result} instead of {expected}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    for x in [0, 37, 89, 42, 1024, 555, 12345, 9999]:
        memory = getmemory(os.linesep.join([
            *initlines,
            *parse_and_compile_module("multiplyandreturn", textwrap.dedent("""
                def multiplyandreturn(param1: uint16) -> uint16:
                    return param1 * 31
            """)).code,
            "main:",
            f"PUSHI {x & 0xFF}",
            f"PUSHI {(x >> 8) & 0xFF}",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            "LOADI 123",
            "CALL multiplyandreturn",
            "HALT",
            *addlines,
            *multiplylines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        _assert(
            cpu.a == 123,
            f"multiplyandreturn changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"multiplyandreturn changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"multiplyandreturn changed V value from {222} to {cpu.v}!",
        )
        result = (
            (cpu.ram[cpu.pc] << 8) + cpu.ram[cpu.pc + 1]
        )
        expected = (x * 31) & 0xFFFF
        _assert(
            result == expected,
            "Failed to multiplyandreturn, "
            + f"got {result} instead of {expected}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    for x in [0, 37, 89, 42, 1024, 555, 12345, 32000, 1234567890]:
        memory = getmemory(os.linesep.join([
            *initlines,
            *parse_and_compile_module("multiplyandreturn", textwrap.dedent("""
                def multiplyandreturn(param1: uint32) -> uint32:
                    return param1 * 491
            """)).code,
            "main:",
            f"PUSHI {x & 0xFF}",
            f"PUSHI {(x >> 8) & 0xFF}",
            f"PUSHI {(x >> 16) & 0xFF}",
            f"PUSHI {(x >> 24) & 0xFF}",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            "LOADI 123",
            "CALL multiplyandreturn",
            "HALT",
            *addlines,
            *multiplylines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        _assert(
            cpu.a == 123,
            f"multiplyandreturn changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"multiplyandreturn changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"multiplyandreturn changed V value from {222} to {cpu.v}!",
        )
        result = (
            (cpu.ram[cpu.pc + 0] << 24) +
            (cpu.ram[cpu.pc + 1] << 16) +
            (cpu.ram[cpu.pc + 2] << 8) +
            (cpu.ram[cpu.pc + 3] << 0)
        )
        expected = (x * 491) & 0xFFFFFFFF
        _assert(
            result == expected,
            "Failed to multiplyandreturn, "
            + f"got {result} instead of {expected}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    print(f"Average cycles for multiplyandreturn: {int(cycles/count)}")
    print(f"Average instructions for multiplyandreturn: {int(instructions/count)}")
    print("Verifying multiplyandreturn signed...")

    cycles = 0
    instructions = 0
    count = 0
    for x in [0, 37, -37, 99, 42, -42]:
        memory = getmemory(os.linesep.join([
            *initlines,
            *parse_and_compile_module("multiplyandreturn", textwrap.dedent("""
                def multiplyandreturn(param1: int8) -> int8:
                    return param1 * 3
            """)).code,
            "main:",
            f"LOADI {x}",
            "PUSH A",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            "LOADI 123",
            "CALL multiplyandreturn",
            "HALT",
            *addlines,
            *multiplylines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        _assert(
            cpu.a == 123,
            f"multiplyandreturn changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"multiplyandreturn changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"multiplyandreturn changed V value from {222} to {cpu.v}!",
        )
        result = bintoint(cpu.ram[cpu.pc + 0])
        expected = bintoint((x * 3) & 0xFF)
        _assert(
            result == expected,
            "Failed to multiplyandreturn, "
            + f"got {result} instead of {expected}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    for x in [0, 37, -37, 89, 42, -42, -1024, 1024, 555, -555, 12345, -12345, 9999, -9999]:
        memory = getmemory(os.linesep.join([
            *initlines,
            *parse_and_compile_module("multiplyandreturn", textwrap.dedent("""
                def multiplyandreturn(param1: int16) -> int16:
                    return param1 * 31
            """)).code,
            "main:",
            f"PUSHI {x & 0xFF}",
            f"PUSHI {(x >> 8) & 0xFF}",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            "LOADI 123",
            "CALL multiplyandreturn",
            "HALT",
            *addlines,
            *multiplylines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        _assert(
            cpu.a == 123,
            f"multiplyandreturn changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"multiplyandreturn changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"multiplyandreturn changed V value from {222} to {cpu.v}!",
        )
        result = bintoint16(
            (cpu.ram[cpu.pc] << 8) + cpu.ram[cpu.pc + 1]
        )
        expected = bintoint16((x * 31) & 0xFFFF)
        _assert(
            result == expected,
            "Failed to multiplyandreturn, "
            + f"got {result} instead of {expected}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    for x in [0, 37, -37, 89, 42, -42, -1024, 1024, 555, -555, 12345, -12345, 32000, -32000, 1234567890, -1234567890]:
        memory = getmemory(os.linesep.join([
            *initlines,
            *parse_and_compile_module("multiplyandreturn", textwrap.dedent("""
                def multiplyandreturn(param1: int32) -> int32:
                    return param1 * 491
            """)).code,
            "main:",
            f"PUSHI {x & 0xFF}",
            f"PUSHI {(x >> 8) & 0xFF}",
            f"PUSHI {(x >> 16) & 0xFF}",
            f"PUSHI {(x >> 24) & 0xFF}",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            "LOADI 123",
            "CALL multiplyandreturn",
            "HALT",
            *addlines,
            *multiplylines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        _assert(
            cpu.a == 123,
            f"multiplyandreturn changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"multiplyandreturn changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"multiplyandreturn changed V value from {222} to {cpu.v}!",
        )
        result = bintoint32(
            (cpu.ram[cpu.pc + 0] << 24) +
            (cpu.ram[cpu.pc + 1] << 16) +
            (cpu.ram[cpu.pc + 2] << 8) +
            (cpu.ram[cpu.pc + 3] << 0)
        )
        expected = bintoint32((x * 491) & 0xFFFFFFFF)
        _assert(
            result == expected,
            "Failed to multiplyandreturn, "
            + f"got {result} instead of {expected}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    print(f"Average cycles for multiplyandreturn: {int(cycles/count)}")
    print(f"Average instructions for multiplyandreturn: {int(instructions/count)}")


def verifydivideandreturn(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "divideandreturn" not in only and "compiler" not in only:
        return

    print("Verifying divideandreturn unsigned...")

    with open("lib/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/start.S", "r") as fp:
        initlines += fp.readlines()
    with open("lib/math/cmp.S", "r") as fp:
        cmplines = fp.readlines()
    with open("lib/math/neg.S", "r") as fp:
        neglines = fp.readlines()
    with open("lib/math/add.S", "r") as fp:
        addlines = fp.readlines()
    with open("lib/math/divide.S", "r") as fp:
        divlines = fp.readlines()

    cycles = 0
    instructions = 0
    count = 0
    for x in [0, 37, 99, 42]:
        memory = getmemory(os.linesep.join([
            *initlines,
            *parse_and_compile_module("divideandreturn", textwrap.dedent("""
                def divideandreturn(param1: uint8) -> uint8:
                    return param1 // 3
            """)).code,
            "main:",
            f"LOADI {x}",
            "PUSH A",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            "LOADI 123",
            "CALL divideandreturn",
            "HALT",
            *cmplines,
            *neglines,
            *addlines,
            *divlines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        _assert(
            cpu.a == 123,
            f"divideandreturn changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"divideandreturn changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"divideandreturn changed V value from {222} to {cpu.v}!",
        )
        result = cpu.ram[cpu.pc + 0]
        expected = (x // 3) & 0xFF
        _assert(
            result == expected,
            "Failed to divideandreturn, "
            + f"got {result} instead of {expected}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    for x in [0, 37, 89, 42, 1024, 555, 12345, 9999]:
        memory = getmemory(os.linesep.join([
            *initlines,
            *parse_and_compile_module("divideandreturn", textwrap.dedent("""
                def divideandreturn(param1: uint16) -> uint16:
                    return param1 // 31
            """)).code,
            "main:",
            f"PUSHI {x & 0xFF}",
            f"PUSHI {(x >> 8) & 0xFF}",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            "LOADI 123",
            "CALL divideandreturn",
            "HALT",
            *cmplines,
            *neglines,
            *addlines,
            *divlines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        _assert(
            cpu.a == 123,
            f"divideandreturn changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"divideandreturn changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"divideandreturn changed V value from {222} to {cpu.v}!",
        )
        result = (
            (cpu.ram[cpu.pc] << 8) + cpu.ram[cpu.pc + 1]
        )
        expected = (x // 31) & 0xFFFF
        _assert(
            result == expected,
            "Failed to divideandreturn, "
            + f"got {result} instead of {expected}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    for x in [0, 37, 89, 42, 1024, 555, 12345, 32000, 1234567890]:
        memory = getmemory(os.linesep.join([
            *initlines,
            *parse_and_compile_module("divideandreturn", textwrap.dedent("""
                def divideandreturn(param1: uint32) -> uint32:
                    return param1 // 491
            """)).code,
            "main:",
            f"PUSHI {x & 0xFF}",
            f"PUSHI {(x >> 8) & 0xFF}",
            f"PUSHI {(x >> 16) & 0xFF}",
            f"PUSHI {(x >> 24) & 0xFF}",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            "LOADI 123",
            "CALL divideandreturn",
            "HALT",
            *cmplines,
            *neglines,
            *addlines,
            *divlines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        _assert(
            cpu.a == 123,
            f"divideandreturn changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"divideandreturn changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"divideandreturn changed V value from {222} to {cpu.v}!",
        )
        result = (
            (cpu.ram[cpu.pc + 0] << 24) +
            (cpu.ram[cpu.pc + 1] << 16) +
            (cpu.ram[cpu.pc + 2] << 8) +
            (cpu.ram[cpu.pc + 3] << 0)
        )
        expected = (x // 491) & 0xFFFFFFFF
        _assert(
            result == expected,
            "Failed to divideandreturn, "
            + f"got {result} instead of {expected}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    print(f"Average cycles for divideandreturn: {int(cycles/count)}")
    print(f"Average instructions for divideandreturn: {int(instructions/count)}")

    # If we support signed division, these tests can be enabled.
    if False:
        print("Verifying divideandreturn signed...")

        cycles = 0
        instructions = 0
        count = 0
        for x in [0, 37, -37, 99, 42, -42]:
            memory = getmemory(os.linesep.join([
                *initlines,
                *parse_and_compile_module("divideandreturn", textwrap.dedent("""
                    def divideandreturn(param1: int8) -> int8:
                        return param1 // 3
                """)).code,
                "main:",
                f"LOADI {x}",
                "PUSH A",
                "LOADI 111",
                "MOV A, U",
                "LOADI 222",
                "MOV A, V",
                "LOADI 123",
                "CALL divideandreturn",
                "HALT",
                *cmplines,
                *neglines,
                *addlines,
                *divlines,
            ]))
            cpu = CPUCore(memory)
            rununtilhalt(cpu)

            _assert(
                cpu.a == 123,
                f"divideandreturn changed accumulator value from {123} to {cpu.a}!",
            )
            _assert(
                cpu.u == 111,
                f"divideandreturn changed U value from {111} to {cpu.u}!",
            )
            _assert(
                cpu.v == 222,
                f"divideandreturn changed V value from {222} to {cpu.v}!",
            )
            result = bintoint(cpu.ram[cpu.pc + 0])
            expected = (x // 3)
            _assert(
                result == expected,
                "Failed to divideandreturn, "
                + f"got {result} instead of {expected}!",
            )
            cycles += cpu.cycles
            instructions += cpu.ticks
            count += 1

        for x in [0, 37, -37, 89, 42, -42, -1024, 1024, 555, -555, 12345, -12345, 9999, -9999]:
            memory = getmemory(os.linesep.join([
                *initlines,
                *parse_and_compile_module("divideandreturn", textwrap.dedent("""
                    def divideandreturn(param1: int16) -> int16:
                        return param1 // 31
                """)).code,
                "main:",
                f"PUSHI {x & 0xFF}",
                f"PUSHI {(x >> 8) & 0xFF}",
                "LOADI 111",
                "MOV A, U",
                "LOADI 222",
                "MOV A, V",
                "LOADI 123",
                "CALL divideandreturn",
                "HALT",
                *cmplines,
                *neglines,
                *addlines,
                *divlines,
            ]))
            cpu = CPUCore(memory)
            rununtilhalt(cpu)

            _assert(
                cpu.a == 123,
                f"divideandreturn changed accumulator value from {123} to {cpu.a}!",
            )
            _assert(
                cpu.u == 111,
                f"divideandreturn changed U value from {111} to {cpu.u}!",
            )
            _assert(
                cpu.v == 222,
                f"divideandreturn changed V value from {222} to {cpu.v}!",
            )
            result = bintoint16(
                (cpu.ram[cpu.pc] << 8) + cpu.ram[cpu.pc + 1]
            )
            expected = (x // 31)
            _assert(
                result == expected,
                "Failed to divideandreturn, "
                + f"got {result} instead of {expected}!",
            )
            cycles += cpu.cycles
            instructions += cpu.ticks
            count += 1

        for x in [0, 37, -37, 89, 42, -42, -1024, 1024, 555, -555, 12345, -12345, 32000, -32000, 1234567890, -1234567890]:
            memory = getmemory(os.linesep.join([
                *initlines,
                *parse_and_compile_module("divideandreturn", textwrap.dedent("""
                    def divideandreturn(param1: int32) -> int32:
                        return param1 // 491
                """)).code,
                "main:",
                f"PUSHI {x & 0xFF}",
                f"PUSHI {(x >> 8) & 0xFF}",
                f"PUSHI {(x >> 16) & 0xFF}",
                f"PUSHI {(x >> 24) & 0xFF}",
                "LOADI 111",
                "MOV A, U",
                "LOADI 222",
                "MOV A, V",
                "LOADI 123",
                "CALL divideandreturn",
                "HALT",
                *cmplines,
                *neglines,
                *addlines,
                *divlines,
            ]))
            cpu = CPUCore(memory)
            rununtilhalt(cpu)

            _assert(
                cpu.a == 123,
                f"divideandreturn changed accumulator value from {123} to {cpu.a}!",
            )
            _assert(
                cpu.u == 111,
                f"divideandreturn changed U value from {111} to {cpu.u}!",
            )
            _assert(
                cpu.v == 222,
                f"divideandreturn changed V value from {222} to {cpu.v}!",
            )
            result = bintoint32(
                (cpu.ram[cpu.pc + 0] << 24) +
                (cpu.ram[cpu.pc + 1] << 16) +
                (cpu.ram[cpu.pc + 2] << 8) +
                (cpu.ram[cpu.pc + 3] << 0)
            )
            expected = (x // 491)
            _assert(
                result == expected,
                "Failed to divideandreturn, "
                + f"got {result} instead of {expected}!",
            )
            cycles += cpu.cycles
            instructions += cpu.ticks
            count += 1

        print(f"Average cycles for divideandreturn: {int(cycles/count)}")
        print(f"Average instructions for divideandreturn: {int(instructions/count)}")


def verifymoduloandreturn(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "moduloandreturn" not in only and "compiler" not in only:
        return

    print("Verifying moduloandreturn unsigned...")

    with open("lib/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/start.S", "r") as fp:
        initlines += fp.readlines()
    with open("lib/math/cmp.S", "r") as fp:
        cmplines = fp.readlines()
    with open("lib/math/neg.S", "r") as fp:
        neglines = fp.readlines()
    with open("lib/math/add.S", "r") as fp:
        addlines = fp.readlines()
    with open("lib/math/divide.S", "r") as fp:
        divlines = fp.readlines()

    cycles = 0
    instructions = 0
    count = 0
    for x in [0, 37, 99, 42]:
        memory = getmemory(os.linesep.join([
            *initlines,
            *parse_and_compile_module("moduloandreturn", textwrap.dedent("""
                def moduloandreturn(param1: uint8) -> uint8:
                    return param1 % 3
            """)).code,
            "main:",
            f"LOADI {x}",
            "PUSH A",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            "LOADI 123",
            "CALL moduloandreturn",
            "HALT",
            *cmplines,
            *neglines,
            *addlines,
            *divlines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        _assert(
            cpu.a == 123,
            f"moduloandreturn changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"moduloandreturn changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"moduloandreturn changed V value from {222} to {cpu.v}!",
        )
        result = cpu.ram[cpu.pc + 0]
        expected = (x % 3) & 0xFF
        _assert(
            result == expected,
            "Failed to moduloandreturn, "
            + f"got {result} instead of {expected}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    for x in [0, 37, 89, 42, 1024, 555, 12345, 9999]:
        memory = getmemory(os.linesep.join([
            *initlines,
            *parse_and_compile_module("moduloandreturn", textwrap.dedent("""
                def moduloandreturn(param1: uint16) -> uint16:
                    return param1 % 31
            """)).code,
            "main:",
            f"PUSHI {x & 0xFF}",
            f"PUSHI {(x >> 8) & 0xFF}",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            "LOADI 123",
            "CALL moduloandreturn",
            "HALT",
            *cmplines,
            *neglines,
            *addlines,
            *divlines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        _assert(
            cpu.a == 123,
            f"moduloandreturn changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"moduloandreturn changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"moduloandreturn changed V value from {222} to {cpu.v}!",
        )
        result = (
            (cpu.ram[cpu.pc] << 8) + cpu.ram[cpu.pc + 1]
        )
        expected = (x % 31) & 0xFFFF
        _assert(
            result == expected,
            "Failed to moduloandreturn, "
            + f"got {result} instead of {expected}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    for x in [0, 37, 89, 42, 1024, 555, 12345, 32000, 1234567890]:
        memory = getmemory(os.linesep.join([
            *initlines,
            *parse_and_compile_module("moduloandreturn", textwrap.dedent("""
                def moduloandreturn(param1: uint32) -> uint32:
                    return param1 % 491
            """)).code,
            "main:",
            f"PUSHI {x & 0xFF}",
            f"PUSHI {(x >> 8) & 0xFF}",
            f"PUSHI {(x >> 16) & 0xFF}",
            f"PUSHI {(x >> 24) & 0xFF}",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            "LOADI 123",
            "CALL moduloandreturn",
            "HALT",
            *cmplines,
            *neglines,
            *addlines,
            *divlines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        _assert(
            cpu.a == 123,
            f"moduloandreturn changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"moduloandreturn changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"moduloandreturn changed V value from {222} to {cpu.v}!",
        )
        result = (
            (cpu.ram[cpu.pc + 0] << 24) +
            (cpu.ram[cpu.pc + 1] << 16) +
            (cpu.ram[cpu.pc + 2] << 8) +
            (cpu.ram[cpu.pc + 3] << 0)
        )
        expected = (x % 491) & 0xFFFFFFFF
        _assert(
            result == expected,
            "Failed to moduloandreturn, "
            + f"got {result} instead of {expected}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    print(f"Average cycles for moduloandreturn: {int(cycles/count)}")
    print(f"Average instructions for moduloandreturn: {int(instructions/count)}")

    # If we support signed modulo, these tests can be enabled.
    if False:
        print("Verifying moduloandreturn signed...")

        cycles = 0
        instructions = 0
        count = 0
        for x in [0, 37, -37, 99, 42, -42]:
            memory = getmemory(os.linesep.join([
                *initlines,
                *parse_and_compile_module("moduloandreturn", textwrap.dedent("""
                    def moduloandreturn(param1: int8) -> int8:
                        return param1 % 3
                """)).code,
                "main:",
                f"LOADI {x}",
                "PUSH A",
                "LOADI 111",
                "MOV A, U",
                "LOADI 222",
                "MOV A, V",
                "LOADI 123",
                "CALL moduloandreturn",
                "HALT",
                *cmplines,
                *neglines,
                *addlines,
                *divlines,
            ]))
            cpu = CPUCore(memory)
            rununtilhalt(cpu)

            _assert(
                cpu.a == 123,
                f"moduloandreturn changed accumulator value from {123} to {cpu.a}!",
            )
            _assert(
                cpu.u == 111,
                f"moduloandreturn changed U value from {111} to {cpu.u}!",
            )
            _assert(
                cpu.v == 222,
                f"moduloandreturn changed V value from {222} to {cpu.v}!",
            )
            result = bintoint(cpu.ram[cpu.pc + 0])
            expected = (x % 3)
            _assert(
                result == expected,
                "Failed to moduloandreturn, "
                + f"got {result} instead of {expected}!",
            )
            cycles += cpu.cycles
            instructions += cpu.ticks
            count += 1

        for x in [0, 37, -37, 89, 42, -42, -1024, 1024, 555, -555, 12345, -12345, 9999, -9999]:
            memory = getmemory(os.linesep.join([
                *initlines,
                *parse_and_compile_module("moduloandreturn", textwrap.dedent("""
                    def moduloandreturn(param1: int16) -> int16:
                        return param1 % 31
                """)).code,
                "main:",
                f"PUSHI {x & 0xFF}",
                f"PUSHI {(x >> 8) & 0xFF}",
                "LOADI 111",
                "MOV A, U",
                "LOADI 222",
                "MOV A, V",
                "LOADI 123",
                "CALL moduloandreturn",
                "HALT",
                *cmplines,
                *neglines,
                *addlines,
                *divlines,
            ]))
            cpu = CPUCore(memory)
            rununtilhalt(cpu)

            _assert(
                cpu.a == 123,
                f"moduloandreturn changed accumulator value from {123} to {cpu.a}!",
            )
            _assert(
                cpu.u == 111,
                f"moduloandreturn changed U value from {111} to {cpu.u}!",
            )
            _assert(
                cpu.v == 222,
                f"moduloandreturn changed V value from {222} to {cpu.v}!",
            )
            result = bintoint16(
                (cpu.ram[cpu.pc] << 8) + cpu.ram[cpu.pc + 1]
            )
            expected = (x % 31)
            _assert(
                result == expected,
                "Failed to moduloandreturn, "
                + f"got {result} instead of {expected}!",
            )
            cycles += cpu.cycles
            instructions += cpu.ticks
            count += 1

        for x in [0, 37, -37, 89, 42, -42, -1024, 1024, 555, -555, 12345, -12345, 32000, -32000, 1234567890, -1234567890]:
            memory = getmemory(os.linesep.join([
                *initlines,
                *parse_and_compile_module("moduloandreturn", textwrap.dedent("""
                    def moduloandreturn(param1: int32) -> int32:
                        return param1 % 491
                """)).code,
                "main:",
                f"PUSHI {x & 0xFF}",
                f"PUSHI {(x >> 8) & 0xFF}",
                f"PUSHI {(x >> 16) & 0xFF}",
                f"PUSHI {(x >> 24) & 0xFF}",
                "LOADI 111",
                "MOV A, U",
                "LOADI 222",
                "MOV A, V",
                "LOADI 123",
                "CALL moduloandreturn",
                "HALT",
                *cmplines,
                *neglines,
                *addlines,
                *divlines,
            ]))
            cpu = CPUCore(memory)
            rununtilhalt(cpu)

            _assert(
                cpu.a == 123,
                f"moduloandreturn changed accumulator value from {123} to {cpu.a}!",
            )
            _assert(
                cpu.u == 111,
                f"moduloandreturn changed U value from {111} to {cpu.u}!",
            )
            _assert(
                cpu.v == 222,
                f"moduloandreturn changed V value from {222} to {cpu.v}!",
            )
            result = bintoint32(
                (cpu.ram[cpu.pc + 0] << 24) +
                (cpu.ram[cpu.pc + 1] << 16) +
                (cpu.ram[cpu.pc + 2] << 8) +
                (cpu.ram[cpu.pc + 3] << 0)
            )
            expected = (x % 491)
            _assert(
                result == expected,
                "Failed to moduloandreturn, "
                + f"got {result} instead of {expected}!",
            )
            cycles += cpu.cycles
            instructions += cpu.ticks
            count += 1

        print(f"Average cycles for moduloandreturn: {int(cycles/count)}")
        print(f"Average instructions for moduloandreturn: {int(instructions/count)}")


def verifybitwiseand(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "bitwiseand" not in only and "compiler" not in only:
        return

    print("Verifying bitwiseand...")

    with open("lib/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/start.S", "r") as fp:
        initlines += fp.readlines()

    cycles = 0
    instructions = 0
    count = 0
    for x in [37, -37, 99, 0, 42, -42]:
        memory = getmemory(os.linesep.join([
            *initlines,
            *parse_and_compile_module("bitwiseand", textwrap.dedent("""
                def bitwiseand(param1: int8) -> int8:
                    return param1 & 0x3C
            """)).code,
            "main:",
            f"LOADI {x}",
            "PUSH A",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            "LOADI 123",
            "CALL bitwiseand",
            "HALT",
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        _assert(
            cpu.a == 123,
            f"bitwiseand changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"bitwiseand changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"bitwiseand changed V value from {222} to {cpu.v}!",
        )
        result = cpu.ram[cpu.pc + 0]
        expected = (x & 0x3C) & 0xFF
        _assert(
            result == expected,
            "Failed to bitwiseand, "
            + f"got {bintoint(result)} instead of {expected}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    for x in [0, 37, -37, 89, 42, -42, -1024, 1024, 555, -555, 12345, -12345, 32000, -32000]:
        memory = getmemory(os.linesep.join([
            *initlines,
            *parse_and_compile_module("bitwiseand", textwrap.dedent("""
                def bitwiseand(param1: int16) -> int16:
                    return param1 & 0xA53C
            """)).code,
            "main:",
            f"PUSHI {x & 0xFF}",
            f"PUSHI {(x >> 8) & 0xFF}",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            "LOADI 123",
            "CALL bitwiseand",
            "HALT",
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        _assert(
            cpu.a == 123,
            f"bitwiseand changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"bitwiseand changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"bitwiseand changed V value from {222} to {cpu.v}!",
        )
        result = (cpu.ram[cpu.pc + 0] << 8) + cpu.ram[cpu.pc + 1]
        expected = (x & 0xA53C) & 0xFFFF
        _assert(
            result == expected,
            "Failed to bitwiseand, "
            + f"got {result} instead of {expected}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    for x in [0, 37, -37, 89, 42, -42, -1024, 1024, 555, -555, 12345, -12345, 32000, -32000, 1234567890, -1234567890]:
        memory = getmemory(os.linesep.join([
            *initlines,
            *parse_and_compile_module("bitwiseand", textwrap.dedent("""
                def bitwiseand(param1: int32) -> int32:
                    return param1 & 0x3CA5963C
            """)).code,
            "main:",
            f"PUSHI {x & 0xFF}",
            f"PUSHI {(x >> 8) & 0xFF}",
            f"PUSHI {(x >> 16) & 0xFF}",
            f"PUSHI {(x >> 24) & 0xFF}",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            "LOADI 123",
            "CALL bitwiseand",
            "HALT",
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        _assert(
            cpu.a == 123,
            f"bitwiseand changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"bitwiseand changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"bitwiseand changed V value from {222} to {cpu.v}!",
        )
        result = (
            (cpu.ram[cpu.pc + 0] << 24) +
            (cpu.ram[cpu.pc + 1] << 16) +
            (cpu.ram[cpu.pc + 2] << 8) +
            (cpu.ram[cpu.pc + 3] << 0)
        )
        expected = (x & 0x3CA5963C) & 0xFFFFFFFF
        _assert(
            result == expected,
            "Failed to bitwiseand, "
            + f"got {result} instead of {expected}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    print(f"Average cycles for bitwiseand: {int(cycles/count)}")
    print(f"Average instructions for bitwiseand: {int(instructions/count)}")


def verifybitwiseor(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "bitwiseor" not in only and "compiler" not in only:
        return

    print("Verifying bitwiseor...")

    with open("lib/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/start.S", "r") as fp:
        initlines += fp.readlines()

    cycles = 0
    instructions = 0
    count = 0
    for x in [37, -37, 99, 0, 42, -42]:
        memory = getmemory(os.linesep.join([
            *initlines,
            *parse_and_compile_module("bitwiseor", textwrap.dedent("""
                def bitwiseor(param1: int8) -> int8:
                    return param1 | 0x3C
            """)).code,
            "main:",
            f"LOADI {x}",
            "PUSH A",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            "LOADI 123",
            "CALL bitwiseor",
            "HALT",
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        _assert(
            cpu.a == 123,
            f"bitwiseor changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"bitwiseor changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"bitwiseor changed V value from {222} to {cpu.v}!",
        )
        result = cpu.ram[cpu.pc + 0]
        expected = (x | 0x3C) & 0xFF
        _assert(
            result == expected,
            "Failed to bitwiseor, "
            + f"got {result} instead of {expected}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    for x in [0, 37, -37, 89, 42, -42, -1024, 1024, 555, -555, 12345, -12345, 32000, -32000]:
        memory = getmemory(os.linesep.join([
            *initlines,
            *parse_and_compile_module("bitwiseor", textwrap.dedent("""
                def bitwiseor(param1: int16) -> int16:
                    return param1 | 0xA53C
            """)).code,
            "main:",
            f"PUSHI {x & 0xFF}",
            f"PUSHI {(x >> 8) & 0xFF}",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            "LOADI 123",
            "CALL bitwiseor",
            "HALT",
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        _assert(
            cpu.a == 123,
            f"bitwiseor changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"bitwiseor changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"bitwiseor changed V value from {222} to {cpu.v}!",
        )
        result = (cpu.ram[cpu.pc + 0] << 8) + cpu.ram[cpu.pc + 1]
        expected = (x | 0xA53C) & 0xFFFF
        _assert(
            result == expected,
            "Failed to bitwiseor, "
            + f"got {result} instead of {expected}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    for x in [0, 37, -37, 89, 42, -42, -1024, 1024, 555, -555, 12345, -12345, 32000, -32000, 1234567890, -1234567890]:
        memory = getmemory(os.linesep.join([
            *initlines,
            *parse_and_compile_module("bitwiseor", textwrap.dedent("""
                def bitwiseor(param1: int32) -> int32:
                    return param1 | 0x3CA5963C
            """)).code,
            "main:",
            f"PUSHI {x & 0xFF}",
            f"PUSHI {(x >> 8) & 0xFF}",
            f"PUSHI {(x >> 16) & 0xFF}",
            f"PUSHI {(x >> 24) & 0xFF}",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            "LOADI 123",
            "CALL bitwiseor",
            "HALT",
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        _assert(
            cpu.a == 123,
            f"bitwiseor changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"bitwiseor changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"bitwiseor changed V value from {222} to {cpu.v}!",
        )
        result = (
            (cpu.ram[cpu.pc + 0] << 24) +
            (cpu.ram[cpu.pc + 1] << 16) +
            (cpu.ram[cpu.pc + 2] << 8) +
            (cpu.ram[cpu.pc + 3] << 0)
        )
        expected = (x | 0x3CA5963C) & 0xFFFFFFFF
        _assert(
            result == expected,
            "Failed to bitwiseor, "
            + f"got {result} instead of {expected}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    print(f"Average cycles for bitwiseor: {int(cycles/count)}")
    print(f"Average instructions for bitwiseor: {int(instructions/count)}")


def verifybitwisexor(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "bitwisexor" not in only and "compiler" not in only:
        return

    print("Verifying bitwisexor...")

    with open("lib/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/start.S", "r") as fp:
        initlines += fp.readlines()

    cycles = 0
    instructions = 0
    count = 0
    for x in [37, -37, 99, 0, 42, -42]:
        memory = getmemory(os.linesep.join([
            *initlines,
            *parse_and_compile_module("bitwisexor", textwrap.dedent("""
                def bitwisexor(param1: int8) -> int8:
                    return param1 ^ 0x3C
            """)).code,
            "main:",
            f"LOADI {x}",
            "PUSH A",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            "LOADI 123",
            "CALL bitwisexor",
            "HALT",
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        _assert(
            cpu.a == 123,
            f"bitwisexor changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"bitwisexor changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"bitwisexor changed V value from {222} to {cpu.v}!",
        )
        result = cpu.ram[cpu.pc + 0]
        expected = (x ^ 0x3C) & 0xFF
        _assert(
            result == expected,
            "Failed to bitwisexor, "
            + f"got {result} instead of {expected}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    for x in [0, 37, -37, 89, 42, -42, -1024, 1024, 555, -555, 12345, -12345, 32000, -32000]:
        memory = getmemory(os.linesep.join([
            *initlines,
            *parse_and_compile_module("bitwisexor", textwrap.dedent("""
                def bitwisexor(param1: int16) -> int16:
                    return param1 ^ 0xA53C
            """)).code,
            "main:",
            f"PUSHI {x & 0xFF}",
            f"PUSHI {(x >> 8) & 0xFF}",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            "LOADI 123",
            "CALL bitwisexor",
            "HALT",
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        _assert(
            cpu.a == 123,
            f"bitwisexor changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"bitwisexor changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"bitwisexor changed V value from {222} to {cpu.v}!",
        )
        result = (cpu.ram[cpu.pc + 0] << 8) + cpu.ram[cpu.pc + 1]
        expected = (x ^ 0xA53C) & 0xFFFF
        _assert(
            result == expected,
            "Failed to bitwisexor, "
            + f"got {result} instead of {expected}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    for x in [0, 37, -37, 89, 42, -42, -1024, 1024, 555, -555, 12345, -12345, 32000, -32000, 1234567890, -1234567890]:
        memory = getmemory(os.linesep.join([
            *initlines,
            *parse_and_compile_module("bitwisexor", textwrap.dedent("""
                def bitwisexor(param1: int32) -> int32:
                    return param1 ^ 0x3CA5963C
            """)).code,
            "main:",
            f"PUSHI {x & 0xFF}",
            f"PUSHI {(x >> 8) & 0xFF}",
            f"PUSHI {(x >> 16) & 0xFF}",
            f"PUSHI {(x >> 24) & 0xFF}",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            "LOADI 123",
            "CALL bitwisexor",
            "HALT",
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        _assert(
            cpu.a == 123,
            f"bitwisexor changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"bitwisexor changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"bitwisexor changed V value from {222} to {cpu.v}!",
        )
        result = (
            (cpu.ram[cpu.pc + 0] << 24) +
            (cpu.ram[cpu.pc + 1] << 16) +
            (cpu.ram[cpu.pc + 2] << 8) +
            (cpu.ram[cpu.pc + 3] << 0)
        )
        expected = (x ^ 0x3CA5963C) & 0xFFFFFFFF
        _assert(
            result == expected,
            "Failed to bitwisexor, "
            + f"got {result} instead of {expected}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    print(f"Average cycles for bitwisexor: {int(cycles/count)}")
    print(f"Average instructions for bitwisexor: {int(instructions/count)}")


def verifybitwisenot(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "bitwisenot" not in only and "compiler" not in only:
        return

    print("Verifying bitwisenot...")

    with open("lib/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/start.S", "r") as fp:
        initlines += fp.readlines()

    cycles = 0
    instructions = 0
    count = 0
    for x in [37, -37, 89, 0, 42, -42]:
        memory = getmemory(os.linesep.join([
            *initlines,
            *parse_and_compile_module("bitwisenot", textwrap.dedent("""
                def bitwisenot(param1: int8) -> int8:
                    return ~param1
            """)).code,
            "main:",
            f"LOADI {x}",
            "PUSH A",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            "LOADI 123",
            "CALL bitwisenot",
            "HALT",
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        _assert(
            cpu.a == 123,
            f"bitwisenot changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"bitwisenot changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"bitwisenot changed V value from {222} to {cpu.v}!",
        )
        result = cpu.ram[cpu.pc + 0]
        expected = (~x) & 0xFF
        _assert(
            result == expected,
            "Failed to bitwisenot, "
            + f"got {result} instead of {expected}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    for x in [37, -37, 89, 0, 42, -42, -1024, 1024, 555, -555, 12345, -12345, 32000, -32000]:
        memory = getmemory(os.linesep.join([
            *initlines,
            *parse_and_compile_module("bitwisenot", textwrap.dedent("""
                def bitwisenot(param1: int16) -> int16:
                    return ~param1
            """)).code,
            "main:",
            f"PUSHI {x & 0xFF}",
            f"PUSHI {(x >> 8) & 0xFF}",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            "LOADI 123",
            "CALL bitwisenot",
            "HALT",
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        _assert(
            cpu.a == 123,
            f"bitwisenot changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"bitwisenot changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"bitwisenot changed V value from {222} to {cpu.v}!",
        )
        result = (cpu.ram[cpu.pc + 0] << 8) + cpu.ram[cpu.pc + 1]
        expected = (~x) & 0xFFFF
        _assert(
            result == expected,
            "Failed to bitwisenot, "
            + f"got {result} instead of {expected}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    for x in [37, -37, 89, 0, 42, -42, -1024, 1024, 555, -555, 12345, -12345, 32000, -32000, 1234567890, -1234567890]:
        memory = getmemory(os.linesep.join([
            *initlines,
            *parse_and_compile_module("bitwisenot", textwrap.dedent("""
                def bitwisenot(param1: int32) -> int32:
                    return ~param1
            """)).code,
            "main:",
            f"PUSHI {x & 0xFF}",
            f"PUSHI {(x >> 8) & 0xFF}",
            f"PUSHI {(x >> 16) & 0xFF}",
            f"PUSHI {(x >> 24) & 0xFF}",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            "LOADI 123",
            "CALL bitwisenot",
            "HALT",
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        _assert(
            cpu.a == 123,
            f"bitwisenot changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"bitwisenot changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"bitwisenot changed V value from {222} to {cpu.v}!",
        )
        result = (
            (cpu.ram[cpu.pc + 0] << 24) +
            (cpu.ram[cpu.pc + 1] << 16) +
            (cpu.ram[cpu.pc + 2] << 8) +
            (cpu.ram[cpu.pc + 3] << 0)
        )
        expected = (~x) & 0xFFFFFFFF
        _assert(
            result == expected,
            "Failed to bitwisenot, "
            + f"got {result} instead of {expected}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    print(f"Average cycles for bitwisenot: {int(cycles/count)}")
    print(f"Average instructions for bitwisenot: {int(instructions/count)}")


def verifynegation(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "negation" not in only and "compiler" not in only:
        return

    print("Verifying negation...")

    with open("lib/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/start.S", "r") as fp:
        initlines += fp.readlines()
    with open("lib/math/neg.S", "r") as fp:
        neglines = fp.readlines()

    cycles = 0
    instructions = 0
    count = 0
    for x in [37, -37, 89, 0, 42, -42]:
        memory = getmemory(os.linesep.join([
            *initlines,
            *parse_and_compile_module("negation", textwrap.dedent("""
                def negation(param1: int8) -> int8:
                    return -param1
            """)).code,
            "main:",
            f"LOADI {x}",
            "PUSH A",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            "LOADI 123",
            "CALL negation",
            "HALT",
            *neglines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        _assert(
            cpu.a == 123,
            f"negation changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"negation changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"negation changed V value from {222} to {cpu.v}!",
        )
        result = cpu.ram[cpu.pc + 0]
        expected = -x
        _assert(
            bintoint(result) == expected,
            "Failed to negation, "
            + f"got {bintoint(result)} instead of {expected}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    for x in [37, -37, 89, 0, 42, -42, -1024, 1024, 555, -555, 12345, -12345, 32000, -32000]:
        memory = getmemory(os.linesep.join([
            *initlines,
            *parse_and_compile_module("negation", textwrap.dedent("""
                def negation(param1: int16) -> int16:
                    return -param1
            """)).code,
            "main:",
            f"PUSHI {x & 0xFF}",
            f"PUSHI {(x >> 8) & 0xFF}",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            "LOADI 123",
            "CALL negation",
            "HALT",
            *neglines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        _assert(
            cpu.a == 123,
            f"negation changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"negation changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"negation changed V value from {222} to {cpu.v}!",
        )
        result = bintoint16(
            (cpu.ram[cpu.pc] << 8) + cpu.ram[cpu.pc + 1]
        )
        expected = -x
        _assert(
            result == expected,
            "Failed to negation, "
            + f"got {result} instead of {expected}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    for x in [37, -37, 89, 0, 42, -42, -1024, 1024, 555, -555, 12345, -12345, 32000, -32000, 1234567890, -1234567890]:
        memory = getmemory(os.linesep.join([
            *initlines,
            *parse_and_compile_module("negation", textwrap.dedent("""
                def negation(param1: int32) -> int32:
                    return -param1
            """)).code,
            "main:",
            f"PUSHI {x & 0xFF}",
            f"PUSHI {(x >> 8) & 0xFF}",
            f"PUSHI {(x >> 16) & 0xFF}",
            f"PUSHI {(x >> 24) & 0xFF}",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            "LOADI 123",
            "CALL negation",
            "HALT",
            *neglines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        _assert(
            cpu.a == 123,
            f"negation changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"negation changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"negation changed V value from {222} to {cpu.v}!",
        )
        result = bintoint32(
            (cpu.ram[cpu.pc + 0] << 24) +
            (cpu.ram[cpu.pc + 1] << 16) +
            (cpu.ram[cpu.pc + 2] << 8) +
            (cpu.ram[cpu.pc + 3] << 0)
        )
        expected = -x
        _assert(
            result == expected,
            "Failed to negation, "
            + f"got {result} instead of {expected}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    print(f"Average cycles for negation: {int(cycles/count)}")
    print(f"Average instructions for negation: {int(instructions/count)}")


def verifycomplexexpression(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "complexexpression" not in only and "compiler" not in only:
        return

    print("Verifying complexexpression...")

    with open("lib/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/start.S", "r") as fp:
        initlines += fp.readlines()
    with open("lib/math/add.S", "r") as fp:
        addlines = fp.readlines()

    cycles = 0
    instructions = 0
    count = 0
    for x in [37, -37, 89, 0, 42, -42]:
        for y in [1, 2, 3, -4, -5, -6]:
            for z in [13, -13, 22, -22]:
                memory = getmemory(os.linesep.join([
                    *initlines,
                    *parse_and_compile_module("complexexpression", textwrap.dedent("""
                        def complexexpression(param1: int8, param2: int8, param3: int8) -> int8:
                            return param1 + (param2 - param3) + 7
                    """)).code,
                    "main:",
                    f"LOADI {x}",
                    "PUSH A",
                    f"LOADI {y}",
                    "PUSH A",
                    f"LOADI {z}",
                    "PUSH A",
                    "LOADI 111",
                    "MOV A, U",
                    "LOADI 222",
                    "MOV A, V",
                    "LOADI 123",
                    "CALL complexexpression",
                    "HALT",
                    *addlines,
                ]))
                cpu = CPUCore(memory)
                rununtilhalt(cpu)

                _assert(
                    cpu.a == 123,
                    f"complexexpression changed accumulator value from {123} to {cpu.a}!",
                )
                _assert(
                    cpu.u == 111,
                    f"complexexpression changed U value from {111} to {cpu.u}!",
                )
                _assert(
                    cpu.v == 222,
                    f"complexexpression changed V value from {222} to {cpu.v}!",
                )
                result = cpu.ram[cpu.pc + 0]
                expected = x + (y - z) + 7
                _assert(
                    bintoint(result) == expected,
                    "Failed to complexexpression, "
                    + f"got {bintoint(result)} instead of {expected}!",
                )
                cycles += cpu.cycles
                instructions += cpu.ticks
                count += 1

    print(f"Average cycles for complexexpression: {int(cycles/count)}")
    print(f"Average instructions for complexexpression: {int(instructions/count)}")


def verifyvoidfunctioncall(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "voidfunctioncall" not in only and "compiler" not in only:
        return

    print("Verifying voidfunctioncall...")

    with open("lib/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/start.S", "r") as fp:
        startlines = fp.readlines()
    with open("lib/data.S", "r") as fp:
        datalines = fp.readlines()
    with open("lib/heap.S", "r") as fp:
        heaplines = fp.readlines()

    cycles = 0
    instructions = 0
    count = 0

    for val in [0, 37, 42, 69, 123, 234]:
        # Verify that we can call void functions.
        sections = parse_and_compile_module("voidfunctions", textwrap.dedent("""
            global_var: uint8 = 0xA5

            def set_global(val: uint8) -> void:
                global global_var
                global_var = val

            def get_global() -> uint8:
                return global_var

            def passthrough_global(val: uint8) -> uint8:
                set_global(val)
                return ~get_global()
        """))
        memory = getmemory(os.linesep.join([
            *initlines,
            *sections.init,
            *startlines,
            *sections.code,
            "main:",
            f"PUSHI {val}",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            "LOADI 123",
            "CALL passthrough_global",
            "HALT",
            *datalines,
            *sections.data,
            *heaplines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        _assert(
            cpu.a == 123,
            f"globalvariablewrite changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"globalvariablewrite changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"globalvariablewrite changed V value from {222} to {cpu.v}!",
        )
        result = cpu.ram[cpu.pc]
        expected = (~val) & 0xFF
        _assert(
            result == expected,
            "Failed to voidfunctions, "
            + f"got {result} instead of {expected}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    print(f"Average cycles for voidfunctioncall: {int(cycles/count)}")
    print(f"Average instructions for voidfunctioncall: {int(instructions/count)}")


def verifylocalvariables(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "localvariables" not in only and "compiler" not in only:
        return

    print("Verifying localvariables...")

    with open("lib/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/start.S", "r") as fp:
        initlines += fp.readlines()
    with open("lib/math/add.S", "r") as fp:
        addlines = fp.readlines()

    cycles = 0
    instructions = 0
    count = 0
    for x in [37, -37, 89, 0, 42, -42]:
        memory = getmemory(os.linesep.join([
            *initlines,
            *parse_and_compile_module("localvariables", textwrap.dedent("""
                def localvariables(param1: int8) -> int8:
                    SOME_CONST: const[int8] = 10

                    # Do some simple variable stuff.
                    var: int8 = param1 + 2
                    var = var + SOME_CONST

                    # Return it.
                    return var + 3
            """)).code,
            "main:",
            f"LOADI {x}",
            "PUSH A",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            "LOADI 123",
            "CALL localvariables",
            "HALT",
            *addlines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        _assert(
            cpu.a == 123,
            f"localvariables changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"localvariables changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"localvariables changed V value from {222} to {cpu.v}!",
        )
        result = cpu.ram[cpu.pc + 0]
        expected = x + 15
        _assert(
            bintoint(result) == expected,
            "Failed to localvariables, "
            + f"got {bintoint(result)} instead of {expected}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    print(f"Average cycles for localvariables: {int(cycles/count)}")
    print(f"Average instructions for localvariables: {int(instructions/count)}")


def verifyfunctioncall(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "functioncall" not in only and "compiler" not in only:
        return

    print("Verifying functioncall...")

    with open("lib/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/start.S", "r") as fp:
        initlines += fp.readlines()
    with open("lib/math/add.S", "r") as fp:
        addlines = fp.readlines()

    cycles = 0
    instructions = 0
    count = 0
    for x in [37, -37, 89, 0, 42, -42]:
        memory = getmemory(os.linesep.join([
            *initlines,
            *parse_and_compile_module("functioncall", textwrap.dedent("""
                def add_10_to_two_params(param1: int8, param2: int8) -> int8:
                    CONST_VALUE: int8 = 10
                    return param1 + param2 + CONST_VALUE

                # Also verifying that types can be narrowed and expanded properly.
                def func(param1: int16) -> int16:
                    return add_10_to_two_params(param1, 5)
            """)).code,
            "main:",
            f"PUSHI {x & 0xFF}",
            f"PUSHI {(x >> 8) & 0xFF}",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            "LOADI 123",
            "CALL func",
            "HALT",
            *addlines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        _assert(
            cpu.a == 123,
            f"functioncall changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"functioncall changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"functioncall changed V value from {222} to {cpu.v}!",
        )
        result = bintoint16(
            (cpu.ram[cpu.pc] << 8) + cpu.ram[cpu.pc + 1]
        )
        expected = x + 15
        _assert(
            result == expected,
            "Failed to functioncall, "
            + f"got {result} instead of {expected}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    print(f"Average cycles for functioncall: {int(cycles/count)}")
    print(f"Average instructions for functioncall: {int(instructions/count)}")


def verifycomplexfunctioncall(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "complexfunctioncall" not in only and "compiler" not in only:
        return

    print("Verifying complexfunctioncall...")

    with open("lib/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/start.S", "r") as fp:
        initlines += fp.readlines()
    with open("lib/math/add.S", "r") as fp:
        addlines = fp.readlines()

    cycles = 0
    instructions = 0
    count = 0
    for x in [37, -37, 89, 0, 42, -42]:
        memory = getmemory(os.linesep.join([
            *initlines,
            *parse_and_compile_module("complexfunctioncall", textwrap.dedent("""
                def add_10_to_two_params(param1: int8, param2: int8) -> int8:
                    CONST_VALUE: int8 = 10
                    return param1 + param2 + CONST_VALUE

                def be_in_the_way(param1: int8, param2: int8) -> int8:
                    return add_10_to_two_params(param1 + 2, param2 + 3)

                def func(param1: int8) -> int8:
                    local_var: int8 = be_in_the_way(param1, 7) - 2
                    return local_var - 5
            """)).code,
            "main:",
            f"LOADI {x}",
            "PUSH A",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            "LOADI 123",
            "CALL func",
            "HALT",
            *addlines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        _assert(
            cpu.a == 123,
            f"complexfunctioncall changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"complexfunctioncall changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"complexfunctioncall changed V value from {222} to {cpu.v}!",
        )
        result = cpu.ram[cpu.pc + 0]
        expected = x + 15
        _assert(
            bintoint(result) == expected,
            "Failed to complexfunctioncall, "
            + f"got {bintoint(result)} instead of {expected}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    print(f"Average cycles for complexfunctioncall: {int(cycles/count)}")
    print(f"Average instructions for complexfunctioncall: {int(instructions/count)}")


def verifysimplebooleans(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "simplebooleans" not in only and "compiler" not in only:
        return

    print("Verifying simplebooleans...")

    with open("lib/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/start.S", "r") as fp:
        initlines += fp.readlines()

    cycles = 0
    instructions = 0
    count = 0
    for val in [False, True]:
        memory = getmemory(os.linesep.join([
            *initlines,
            *parse_and_compile_module("simplebooleans", textwrap.dedent(f"""
                def func() -> bool:
                    return {val}
            """)).code,
            "main:",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            "LOADI 123",
            "DECPC",
            "CALL func",
            "HALT",
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        _assert(
            cpu.a == 123,
            f"simplebooleans changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"simplebooleans changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"simplebooleans changed V value from {222} to {cpu.v}!",
        )
        _assert(
            cpu.ram[cpu.pc + 0] in {0x00, 0xFF},
            f"compulted boolean was invalid value {cpu.ram[cpu.pc + 0]}!",
        )
        result = bool(cpu.ram[cpu.pc + 0])
        expected = val
        _assert(
            result == expected,
            "Failed to simplebooleans, "
            + f"got {result} instead of {expected}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    print(f"Average cycles for simplebooleans: {int(cycles/count)}")
    print(f"Average instructions for simplebooleans: {int(instructions/count)}")


def verifybooleanischeck(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "booleanischeck" not in only and "compiler" not in only:
        return

    print("Verifying booleanischeck...")

    with open("lib/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/start.S", "r") as fp:
        initlines += fp.readlines()

    cycles = 0
    instructions = 0
    count = 0
    for res in [False, True]:
        for val in [False, True]:
            memory = getmemory(os.linesep.join([
                *initlines,
                *parse_and_compile_module("booleanischeck", textwrap.dedent(f"""
                    def func(val: bool) -> bool:
                        return val is {res}
                """)).code,
                "main:",
                f"PUSHI {'0xFF' if val else '0x00'}",
                "LOADI 111",
                "MOV A, U",
                "LOADI 222",
                "MOV A, V",
                "LOADI 123",
                "CALL func",
                "HALT",
            ]))
            cpu = CPUCore(memory)
            rununtilhalt(cpu)

            _assert(
                cpu.a == 123,
                f"booleanischeck changed accumulator value from {123} to {cpu.a}!",
            )
            _assert(
                cpu.u == 111,
                f"booleanischeck changed U value from {111} to {cpu.u}!",
            )
            _assert(
                cpu.v == 222,
                f"booleanischeck changed V value from {222} to {cpu.v}!",
            )
            _assert(
                cpu.ram[cpu.pc + 0] in {0x00, 0xFF},
                f"compulted boolean was invalid value {cpu.ram[cpu.pc + 0]}!",
            )
            result = bool(cpu.ram[cpu.pc + 0])
            expected = val == res
            _assert(
                result == expected,
                "Failed to booleanischeck, "
                + f"got {result} instead of {expected}!",
            )
            cycles += cpu.cycles
            instructions += cpu.ticks
            count += 1

    print(f"Average cycles for booleanischeck: {int(cycles/count)}")
    print(f"Average instructions for booleanischeck: {int(instructions/count)}")


def verifybooleanexpressions(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "booleanexpressions" not in only and "compiler" not in only:
        return

    print("Verifying booleanexpressions...")

    with open("lib/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/start.S", "r") as fp:
        initlines += fp.readlines()

    cycles = 0
    instructions = 0
    count = 0
    for op in ["and", "or"]:
        for a, b in [(False, False), (False, True), (True, False), (True, True)]:
            memory = getmemory(os.linesep.join([
                *initlines,
                *parse_and_compile_module("booleanexpressions", textwrap.dedent(f"""
                    def func(op1: bool, op2: bool) -> bool:
                        return op1 {op} op2
                """)).code,
                "main:",
                f"PUSHI {'0xFF' if a else '0x00'}",
                f"PUSHI {'0xFF' if b else '0x00'}",
                "LOADI 111",
                "MOV A, U",
                "LOADI 222",
                "MOV A, V",
                "LOADI 123",
                "CALL func",
                "HALT",
            ]))
            cpu = CPUCore(memory)
            rununtilhalt(cpu)

            _assert(
                cpu.a == 123,
                f"booleanexpressions changed accumulator value from {123} to {cpu.a}!",
            )
            _assert(
                cpu.u == 111,
                f"booleanexpressions changed U value from {111} to {cpu.u}!",
            )
            _assert(
                cpu.v == 222,
                f"booleanexpressions changed V value from {222} to {cpu.v}!",
            )
            _assert(
                cpu.ram[cpu.pc + 0] in {0x00, 0xFF},
                f"compulted boolean was invalid value {cpu.ram[cpu.pc + 0]}!",
            )
            result = bool(cpu.ram[cpu.pc + 0])
            expected = eval(f"{a} {op} {b}")
            _assert(
                result == expected,
                "Failed to booleanexpressions, "
                + f"got {result} instead of {expected}!",
            )
            cycles += cpu.cycles
            instructions += cpu.ticks
            count += 1

    for val in [False, True]:
        memory = getmemory(os.linesep.join([
            *initlines,
            *parse_and_compile_module("booleanexpressions", textwrap.dedent("""
                def func(op: bool) -> bool:
                    return not op
            """)).code,
            "main:",
            f"PUSHI {'0xFF' if val else '0x00'}",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            "LOADI 123",
            "CALL func",
            "HALT",
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        _assert(
            cpu.a == 123,
            f"booleanexpressions changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"booleanexpressions changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"booleanexpressions changed V value from {222} to {cpu.v}!",
        )
        _assert(
            cpu.ram[cpu.pc + 0] in {0x00, 0xFF},
            f"compulted boolean was invalid value {cpu.ram[cpu.pc + 0]}!",
        )
        result = bool(cpu.ram[cpu.pc + 0])
        expected = not val
        _assert(
            result == expected,
            "Failed to booleanexpressions, "
            + f"got {result} instead of {expected}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    print(f"Average cycles for booleanexpressions: {int(cycles/count)}")
    print(f"Average instructions for booleanexpressions: {int(instructions/count)}")


def verifyternaryexpressions(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "ternaryexpressions" not in only and "compiler" not in only:
        return

    print("Verifying ternaryexpressions...")

    with open("lib/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/start.S", "r") as fp:
        initlines += fp.readlines()

    cycles = 0
    instructions = 0
    count = 0
    for a in [-5, 0, 5]:
        for b in [-7, 0, 7]:
            for val in [False, True]:
                memory = getmemory(os.linesep.join([
                    *initlines,
                    *parse_and_compile_module("ternaryexpressions", textwrap.dedent("""
                        def func(a: int8, b: int8, op: bool) -> int8:
                            return (a + 5) if op else (b - 7)
                    """)).code,
                    "main:",
                    f"PUSHI {a}",
                    f"PUSHI {b}",
                    f"PUSHI {'0xFF' if val else '0x00'}",
                    "LOADI 111",
                    "MOV A, U",
                    "LOADI 222",
                    "MOV A, V",
                    "LOADI 123",
                    "CALL func",
                    "HALT",
                ]))
                cpu = CPUCore(memory)
                rununtilhalt(cpu)

                _assert(
                    cpu.a == 123,
                    f"ternaryexpressions changed accumulator value from {123} to {cpu.a}!",
                )
                _assert(
                    cpu.u == 111,
                    f"ternaryexpressions changed U value from {111} to {cpu.u}!",
                )
                _assert(
                    cpu.v == 222,
                    f"ternaryexpressions changed V value from {222} to {cpu.v}!",
                )
                result = bintoint(cpu.ram[cpu.pc + 0])
                expected = (a + 5) if val else (b - 7)
                _assert(
                    result == expected,
                    "Failed to ternaryexpressions, "
                    + f"got {result} instead of {expected}!",
                )
                cycles += cpu.cycles
                instructions += cpu.ticks
                count += 1

    print(f"Average cycles for ternaryexpressions: {int(cycles/count)}")
    print(f"Average instructions for ternaryexpressions: {int(instructions/count)}")


def verifyequalityexpression(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "equalityexpression" not in only and "compiler" not in only:
        return

    print("Verifying equalityexpression...")

    with open("lib/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/start.S", "r") as fp:
        initlines += fp.readlines()

    cycles = 0
    instructions = 0
    count = 0
    for val1 in [-10, 0, 10, 57, -57, 123]:
        for val2 in [-10, 0, 10, 57, -57, 123]:
            for secondtype in ["int8", "int16", "int32"]:
                memory = getmemory(os.linesep.join([
                    *initlines,
                    *parse_and_compile_module("equalityexpression", textwrap.dedent(f"""
                        def func(val1: int8, val2: {secondtype}) -> bool:
                            return val1 == val2
                    """)).code,
                    "main:",
                    f"PUSHI {val1}",
                    f"PUSHI {val2 & 0xFF}",
                    f"PUSHI {(val2 >> 8) & 0xFF}" if secondtype in {"int16", "int32"} else "",
                    f"PUSHI {(val2 >> 16) & 0xFF}" if secondtype == "int32" else "",
                    f"PUSHI {(val2 >> 24) & 0xFF}" if secondtype == "int32" else "",
                    "LOADI 111",
                    "MOV A, U",
                    "LOADI 222",
                    "MOV A, V",
                    "LOADI 123",
                    "CALL func",
                    "HALT",
                ]))
                cpu = CPUCore(memory)
                rununtilhalt(cpu)

                _assert(
                    cpu.a == 123,
                    f"equalityexpression changed accumulator value from {123} to {cpu.a}!",
                )
                _assert(
                    cpu.u == 111,
                    f"equalityexpression changed U value from {111} to {cpu.u}!",
                )
                _assert(
                    cpu.v == 222,
                    f"equalityexpression changed V value from {222} to {cpu.v}!",
                )
                _assert(
                    cpu.ram[cpu.pc + 0] in {0x00, 0xFF},
                    f"compulted boolean was invalid value {cpu.ram[cpu.pc + 0]}!",
                )
                result = bool(cpu.ram[cpu.pc + 0])
                expected = val1 == val2
                _assert(
                    result == expected,
                    "Failed to equalityexpression, "
                    + f"got {result} instead of {expected}!",
                )
                cycles += cpu.cycles
                instructions += cpu.ticks
                count += 1

    for val1 in [0x0000, 0x00FF, 0xFF00, 0xFFFF, 12345]:
        for val2 in [0x0000, 0x00FF, 0xFF00, 0xFFFF, 12345]:
            memory = getmemory(os.linesep.join([
                *initlines,
                *parse_and_compile_module("equalityexpression", textwrap.dedent("""
                    def func(val1: int16, val2: int16) -> bool:
                        return val1 == val2
                """)).code,
                "main:",
                f"PUSHI {val1 & 0xFF}",
                f"PUSHI {(val1 >> 8) & 0xFF}",
                f"PUSHI {val2 & 0xFF}",
                f"PUSHI {(val2 >> 8) & 0xFF}",
                "LOADI 111",
                "MOV A, U",
                "LOADI 222",
                "MOV A, V",
                "LOADI 123",
                "CALL func",
                "HALT",
            ]))
            cpu = CPUCore(memory)
            rununtilhalt(cpu)

            _assert(
                cpu.a == 123,
                f"equalityexpression changed accumulator value from {123} to {cpu.a}!",
            )
            _assert(
                cpu.u == 111,
                f"equalityexpression changed U value from {111} to {cpu.u}!",
            )
            _assert(
                cpu.v == 222,
                f"equalityexpression changed V value from {222} to {cpu.v}!",
            )
            _assert(
                cpu.ram[cpu.pc + 0] in {0x00, 0xFF},
                f"compulted boolean was invalid value {cpu.ram[cpu.pc + 0]}!",
            )
            result = bool(cpu.ram[cpu.pc + 0])
            expected = val1 == val2
            _assert(
                result == expected,
                "Failed to equalityexpression, "
                + f"got {result} instead of {expected}!",
            )
            cycles += cpu.cycles
            instructions += cpu.ticks
            count += 1

    for val1 in [0x0000, 0x000000FF, 0x0000FF00, 0x00FF0000, 0xFF000000, 0xFF00FF00, 0x00FF00FF, 1234567890]:
        for val2 in [0x0000, 0x000000FF, 0x0000FF00, 0x00FF0000, 0xFF000000, 0xFF00FF00, 0x00FF00FF, 1234567890]:
            memory = getmemory(os.linesep.join([
                *initlines,
                *parse_and_compile_module("equalityexpression", textwrap.dedent("""
                    def func(val1: int32, val2: int32) -> bool:
                        return val1 == val2
                """)).code,
                "main:",
                f"PUSHI {val1 & 0xFF}",
                f"PUSHI {(val1 >> 8) & 0xFF}",
                f"PUSHI {(val1 >> 16) & 0xFF}",
                f"PUSHI {(val1 >> 24) & 0xFF}",
                f"PUSHI {val2 & 0xFF}",
                f"PUSHI {(val2 >> 8) & 0xFF}",
                f"PUSHI {(val2 >> 16) & 0xFF}",
                f"PUSHI {(val2 >> 24) & 0xFF}",
                "LOADI 111",
                "MOV A, U",
                "LOADI 222",
                "MOV A, V",
                "LOADI 123",
                "CALL func",
                "HALT",
            ]))
            cpu = CPUCore(memory)
            rununtilhalt(cpu)

            _assert(
                cpu.a == 123,
                f"equalityexpression changed accumulator value from {123} to {cpu.a}!",
            )
            _assert(
                cpu.u == 111,
                f"equalityexpression changed U value from {111} to {cpu.u}!",
            )
            _assert(
                cpu.v == 222,
                f"equalityexpression changed V value from {222} to {cpu.v}!",
            )
            _assert(
                cpu.ram[cpu.pc + 0] in {0x00, 0xFF},
                f"compulted boolean was invalid value {cpu.ram[cpu.pc + 0]}!",
            )
            result = bool(cpu.ram[cpu.pc + 0])
            expected = val1 == val2
            _assert(
                result == expected,
                "Failed to equalityexpression, "
                + f"got {result} instead of {expected}!",
            )
            cycles += cpu.cycles
            instructions += cpu.ticks
            count += 1

    for val1 in [-10, 0, 10, 57, -57, 123]:
        for val2 in [-10, 0, 10, 57, -57, 123]:
            memory = getmemory(os.linesep.join([
                *initlines,
                *parse_and_compile_module("equalityexpression", textwrap.dedent(f"""
                    def func(val1: int8) -> bool:
                        return val1 == {val2}
                """)).code,
                "main:",
                f"PUSHI {val1}",
                "LOADI 111",
                "MOV A, U",
                "LOADI 222",
                "MOV A, V",
                "LOADI 123",
                "CALL func",
                "HALT",
            ]))
            cpu = CPUCore(memory)
            rununtilhalt(cpu)

            _assert(
                cpu.a == 123,
                f"equalityexpression changed accumulator value from {123} to {cpu.a}!",
            )
            _assert(
                cpu.u == 111,
                f"equalityexpression changed U value from {111} to {cpu.u}!",
            )
            _assert(
                cpu.v == 222,
                f"equalityexpression changed V value from {222} to {cpu.v}!",
            )
            _assert(
                cpu.ram[cpu.pc + 0] in {0x00, 0xFF},
                f"compulted boolean was invalid value {cpu.ram[cpu.pc + 0]}!",
            )
            result = bool(cpu.ram[cpu.pc + 0])
            expected = val1 == val2
            _assert(
                result == expected,
                "Failed to equalityexpression, "
                + f"got {result} instead of {expected}!",
            )
            cycles += cpu.cycles
            instructions += cpu.ticks
            count += 1

    for val1 in [0x0000, 0x00FF, 0xFF00, 0xFFFF, 12345]:
        for val2 in [0x0000, 0x00FF, 0xFF00, 0xFFFF, 12345]:
            memory = getmemory(os.linesep.join([
                *initlines,
                *parse_and_compile_module("equalityexpression", textwrap.dedent(f"""
                    def func(val1: int16) -> bool:
                        return val1 == {val2}
                """)).code,
                "main:",
                f"PUSHI {val1 & 0xFF}",
                f"PUSHI {(val1 >> 8) & 0xFF}",
                "LOADI 111",
                "MOV A, U",
                "LOADI 222",
                "MOV A, V",
                "LOADI 123",
                "CALL func",
                "HALT",
            ]))
            cpu = CPUCore(memory)
            rununtilhalt(cpu)

            _assert(
                cpu.a == 123,
                f"equalityexpression changed accumulator value from {123} to {cpu.a}!",
            )
            _assert(
                cpu.u == 111,
                f"equalityexpression changed U value from {111} to {cpu.u}!",
            )
            _assert(
                cpu.v == 222,
                f"equalityexpression changed V value from {222} to {cpu.v}!",
            )
            _assert(
                cpu.ram[cpu.pc + 0] in {0x00, 0xFF},
                f"compulted boolean was invalid value {cpu.ram[cpu.pc + 0]}!",
            )
            result = bool(cpu.ram[cpu.pc + 0])
            expected = val1 == val2
            _assert(
                result == expected,
                "Failed to equalityexpression, "
                + f"got {result} instead of {expected}!",
            )
            cycles += cpu.cycles
            instructions += cpu.ticks
            count += 1

    for val1 in [0x0000, 0x000000FF, 0x0000FF00, 0x00FF0000, 0xFF000000, 0xFF00FF00, 0x00FF00FF, 1234567890]:
        for val2 in [0x0000, 0x000000FF, 0x0000FF00, 0x00FF0000, 0xFF000000, 0xFF00FF00, 0x00FF00FF, 1234567890]:
            memory = getmemory(os.linesep.join([
                *initlines,
                *parse_and_compile_module("equalityexpression", textwrap.dedent(f"""
                    def func(val1: int32) -> bool:
                        return val1 == {val2}
                """)).code,
                "main:",
                f"PUSHI {val1 & 0xFF}",
                f"PUSHI {(val1 >> 8) & 0xFF}",
                f"PUSHI {(val1 >> 16) & 0xFF}",
                f"PUSHI {(val1 >> 24) & 0xFF}",
                "LOADI 111",
                "MOV A, U",
                "LOADI 222",
                "MOV A, V",
                "LOADI 123",
                "CALL func",
                "HALT",
            ]))
            cpu = CPUCore(memory)
            rununtilhalt(cpu)

            _assert(
                cpu.a == 123,
                f"equalityexpression changed accumulator value from {123} to {cpu.a}!",
            )
            _assert(
                cpu.u == 111,
                f"equalityexpression changed U value from {111} to {cpu.u}!",
            )
            _assert(
                cpu.v == 222,
                f"equalityexpression changed V value from {222} to {cpu.v}!",
            )
            _assert(
                cpu.ram[cpu.pc + 0] in {0x00, 0xFF},
                f"compulted boolean was invalid value {cpu.ram[cpu.pc + 0]}!",
            )
            result = bool(cpu.ram[cpu.pc + 0])
            expected = val1 == val2
            _assert(
                result == expected,
                "Failed to equalityexpression, "
                + f"got {result} instead of {expected}!",
            )
            cycles += cpu.cycles
            instructions += cpu.ticks
            count += 1

    print(f"Average cycles for equalityexpression: {int(cycles/count)}")
    print(f"Average instructions for equalityexpression: {int(instructions/count)}")


def verifyinequalityexpression(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "inequalityexpression" not in only and "compiler" not in only:
        return

    print("Verifying inequalityexpression...")

    with open("lib/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/start.S", "r") as fp:
        initlines += fp.readlines()

    cycles = 0
    instructions = 0
    count = 0
    for val1 in [-10, 0, 10, 57, -57, 123]:
        for val2 in [-10, 0, 10, 57, -57, 123]:
            memory = getmemory(os.linesep.join([
                *initlines,
                *parse_and_compile_module("inequalityexpression", textwrap.dedent("""
                    def func(val1: int8, val2: int8) -> bool:
                        return val1 != val2
                """)).code,
                "main:",
                f"PUSHI {val1}",
                f"PUSHI {val2}",
                "LOADI 111",
                "MOV A, U",
                "LOADI 222",
                "MOV A, V",
                "LOADI 123",
                "CALL func",
                "HALT",
            ]))
            cpu = CPUCore(memory)
            rununtilhalt(cpu)

            _assert(
                cpu.a == 123,
                f"inequalityexpression changed accumulator value from {123} to {cpu.a}!",
            )
            _assert(
                cpu.u == 111,
                f"inequalityexpression changed U value from {111} to {cpu.u}!",
            )
            _assert(
                cpu.v == 222,
                f"inequalityexpression changed V value from {222} to {cpu.v}!",
            )
            _assert(
                cpu.ram[cpu.pc + 0] in {0x00, 0xFF},
                f"compulted boolean was invalid value {cpu.ram[cpu.pc + 0]}!",
            )
            result = bool(cpu.ram[cpu.pc + 0])
            expected = val1 != val2
            _assert(
                result == expected,
                "Failed to inequalityexpression, "
                + f"got {result} instead of {expected}!",
            )
            cycles += cpu.cycles
            instructions += cpu.ticks
            count += 1

    for val1 in [0x0000, 0x00FF, 0xFF00, 0xFFFF, 12345]:
        for val2 in [0x0000, 0x00FF, 0xFF00, 0xFFFF, 12345]:
            memory = getmemory(os.linesep.join([
                *initlines,
                *parse_and_compile_module("inequalityexpression", textwrap.dedent("""
                    def func(val1: int16, val2: int16) -> bool:
                        return val1 != val2
                """)).code,
                "main:",
                f"PUSHI {val1 & 0xFF}",
                f"PUSHI {(val1 >> 8) & 0xFF}",
                f"PUSHI {val2 & 0xFF}",
                f"PUSHI {(val2 >> 8) & 0xFF}",
                "LOADI 111",
                "MOV A, U",
                "LOADI 222",
                "MOV A, V",
                "LOADI 123",
                "CALL func",
                "HALT",
            ]))
            cpu = CPUCore(memory)
            rununtilhalt(cpu)

            _assert(
                cpu.a == 123,
                f"inequalityexpression changed accumulator value from {123} to {cpu.a}!",
            )
            _assert(
                cpu.u == 111,
                f"inequalityexpression changed U value from {111} to {cpu.u}!",
            )
            _assert(
                cpu.v == 222,
                f"inequalityexpression changed V value from {222} to {cpu.v}!",
            )
            _assert(
                cpu.ram[cpu.pc + 0] in {0x00, 0xFF},
                f"compulted boolean was invalid value {cpu.ram[cpu.pc + 0]}!",
            )
            result = bool(cpu.ram[cpu.pc + 0])
            expected = val1 != val2
            _assert(
                result == expected,
                "Failed to inequalityexpression, "
                + f"got {result} instead of {expected}!",
            )
            cycles += cpu.cycles
            instructions += cpu.ticks
            count += 1

    for val1 in [0x0000, 0x000000FF, 0x0000FF00, 0x00FF0000, 0xFF000000, 0xFF00FF00, 0x00FF00FF, 1234567890]:
        for val2 in [0x0000, 0x000000FF, 0x0000FF00, 0x00FF0000, 0xFF000000, 0xFF00FF00, 0x00FF00FF, 1234567890]:
            memory = getmemory(os.linesep.join([
                *initlines,
                *parse_and_compile_module("inequalityexpression", textwrap.dedent("""
                    def func(val1: int32, val2: int32) -> bool:
                        return val1 != val2
                """)).code,
                "main:",
                f"PUSHI {val1 & 0xFF}",
                f"PUSHI {(val1 >> 8) & 0xFF}",
                f"PUSHI {(val1 >> 16) & 0xFF}",
                f"PUSHI {(val1 >> 24) & 0xFF}",
                f"PUSHI {val2 & 0xFF}",
                f"PUSHI {(val2 >> 8) & 0xFF}",
                f"PUSHI {(val2 >> 16) & 0xFF}",
                f"PUSHI {(val2 >> 24) & 0xFF}",
                "LOADI 111",
                "MOV A, U",
                "LOADI 222",
                "MOV A, V",
                "LOADI 123",
                "CALL func",
                "HALT",
            ]))
            cpu = CPUCore(memory)
            rununtilhalt(cpu)

            _assert(
                cpu.a == 123,
                f"inequalityexpression changed accumulator value from {123} to {cpu.a}!",
            )
            _assert(
                cpu.u == 111,
                f"inequalityexpression changed U value from {111} to {cpu.u}!",
            )
            _assert(
                cpu.v == 222,
                f"inequalityexpression changed V value from {222} to {cpu.v}!",
            )
            _assert(
                cpu.ram[cpu.pc + 0] in {0x00, 0xFF},
                f"compulted boolean was invalid value {cpu.ram[cpu.pc + 0]}!",
            )
            result = bool(cpu.ram[cpu.pc + 0])
            expected = val1 != val2
            _assert(
                result == expected,
                "Failed to inequalityexpression, "
                + f"got {result} instead of {expected}!",
            )
            cycles += cpu.cycles
            instructions += cpu.ticks
            count += 1

    for val1 in [-10, 0, 10, 57, -57, 123]:
        for val2 in [-10, 0, 10, 57, -57, 123]:
            memory = getmemory(os.linesep.join([
                *initlines,
                *parse_and_compile_module("inequalityexpression", textwrap.dedent(f"""
                    def func(val1: int8) -> bool:
                        return val1 != {val2}
                """)).code,
                "main:",
                f"PUSHI {val1}",
                "LOADI 111",
                "MOV A, U",
                "LOADI 222",
                "MOV A, V",
                "LOADI 123",
                "CALL func",
                "HALT",
            ]))
            cpu = CPUCore(memory)
            rununtilhalt(cpu)

            _assert(
                cpu.a == 123,
                f"inequalityexpression changed accumulator value from {123} to {cpu.a}!",
            )
            _assert(
                cpu.u == 111,
                f"inequalityexpression changed U value from {111} to {cpu.u}!",
            )
            _assert(
                cpu.v == 222,
                f"inequalityexpression changed V value from {222} to {cpu.v}!",
            )
            _assert(
                cpu.ram[cpu.pc + 0] in {0x00, 0xFF},
                f"compulted boolean was invalid value {cpu.ram[cpu.pc + 0]}!",
            )
            result = bool(cpu.ram[cpu.pc + 0])
            expected = val1 != val2
            _assert(
                result == expected,
                "Failed to inequalityexpression, "
                + f"got {result} instead of {expected}!",
            )
            cycles += cpu.cycles
            instructions += cpu.ticks
            count += 1

    for val1 in [0x0000, 0x00FF, 0xFF00, 0xFFFF, 12345]:
        for val2 in [0x0000, 0x00FF, 0xFF00, 0xFFFF, 12345]:
            memory = getmemory(os.linesep.join([
                *initlines,
                *parse_and_compile_module("inequalityexpression", textwrap.dedent(f"""
                    def func(val1: int16) -> bool:
                        return val1 != {val2}
                """)).code,
                "main:",
                f"PUSHI {val1 & 0xFF}",
                f"PUSHI {(val1 >> 8) & 0xFF}",
                "LOADI 111",
                "MOV A, U",
                "LOADI 222",
                "MOV A, V",
                "LOADI 123",
                "CALL func",
                "HALT",
            ]))
            cpu = CPUCore(memory)
            rununtilhalt(cpu)

            _assert(
                cpu.a == 123,
                f"inequalityexpression changed accumulator value from {123} to {cpu.a}!",
            )
            _assert(
                cpu.u == 111,
                f"inequalityexpression changed U value from {111} to {cpu.u}!",
            )
            _assert(
                cpu.v == 222,
                f"inequalityexpression changed V value from {222} to {cpu.v}!",
            )
            _assert(
                cpu.ram[cpu.pc + 0] in {0x00, 0xFF},
                f"compulted boolean was invalid value {cpu.ram[cpu.pc + 0]}!",
            )
            result = bool(cpu.ram[cpu.pc + 0])
            expected = val1 != val2
            _assert(
                result == expected,
                "Failed to inequalityexpression, "
                + f"got {result} instead of {expected}!",
            )
            cycles += cpu.cycles
            instructions += cpu.ticks
            count += 1

    for val1 in [0x0000, 0x000000FF, 0x0000FF00, 0x00FF0000, 0xFF000000, 0xFF00FF00, 0x00FF00FF, 1234567890]:
        for val2 in [0x0000, 0x000000FF, 0x0000FF00, 0x00FF0000, 0xFF000000, 0xFF00FF00, 0x00FF00FF, 1234567890]:
            memory = getmemory(os.linesep.join([
                *initlines,
                *parse_and_compile_module("inequalityexpression", textwrap.dedent(f"""
                    def func(val1: int32) -> bool:
                        return val1 != {val2}
                """)).code,
                "main:",
                f"PUSHI {val1 & 0xFF}",
                f"PUSHI {(val1 >> 8) & 0xFF}",
                f"PUSHI {(val1 >> 16) & 0xFF}",
                f"PUSHI {(val1 >> 24) & 0xFF}",
                "LOADI 111",
                "MOV A, U",
                "LOADI 222",
                "MOV A, V",
                "LOADI 123",
                "CALL func",
                "HALT",
            ]))
            cpu = CPUCore(memory)
            rununtilhalt(cpu)

            _assert(
                cpu.a == 123,
                f"inequalityexpression changed accumulator value from {123} to {cpu.a}!",
            )
            _assert(
                cpu.u == 111,
                f"inequalityexpression changed U value from {111} to {cpu.u}!",
            )
            _assert(
                cpu.v == 222,
                f"inequalityexpression changed V value from {222} to {cpu.v}!",
            )
            _assert(
                cpu.ram[cpu.pc + 0] in {0x00, 0xFF},
                f"compulted boolean was invalid value {cpu.ram[cpu.pc + 0]}!",
            )
            result = bool(cpu.ram[cpu.pc + 0])
            expected = val1 != val2
            _assert(
                result == expected,
                "Failed to inequalityexpression, "
                + f"got {result} instead of {expected}!",
            )
            cycles += cpu.cycles
            instructions += cpu.ticks
            count += 1

    print(f"Average cycles for inequalityexpression: {int(cycles/count)}")
    print(f"Average instructions for inequalityexpression: {int(instructions/count)}")


def verifyalligatorexpression(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "alligatorexpression" not in only and "compiler" not in only:
        return

    print("Verifying alligatorexpression...")

    with open("lib/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/start.S", "r") as fp:
        initlines += fp.readlines()
    with open("lib/math/cmp.S", "r") as fp:
        cmplines = fp.readlines()

    cycles = 0
    instructions = 0
    count = 0
    for val1 in [0, 10, 57, 123, 234, 255]:
        for val2 in [0, 10, 57, 123, 234, 255]:
            for secondtype in ["uint8", "uint16", "uint32"]:
                for operator in ["<=", "<", ">=", ">="]:
                    memory = getmemory(os.linesep.join([
                        *initlines,
                        *parse_and_compile_module("alligatorexpression", textwrap.dedent(f"""
                            def func(val1: uint8, val2: {secondtype}) -> bool:
                                return val1 {operator} val2
                        """)).code,
                        "main:",
                        f"PUSHI {val1}",
                        f"PUSHI {val2 & 0xFF}",
                        f"PUSHI {(val2 >> 8) & 0xFF}" if secondtype in {"uint16", "uint32"} else "",
                        f"PUSHI {(val2 >> 16) & 0xFF}" if secondtype == "uint32" else "",
                        f"PUSHI {(val2 >> 24) & 0xFF}" if secondtype == "uint32" else "",
                        "LOADI 111",
                        "MOV A, U",
                        "LOADI 222",
                        "MOV A, V",
                        "LOADI 123",
                        "CALL func",
                        "HALT",
                        *cmplines,
                    ]))
                    cpu = CPUCore(memory)
                    rununtilhalt(cpu)

                    _assert(
                        cpu.a == 123,
                        f"alligatorexpression changed accumulator value from {123} to {cpu.a}!",
                    )
                    _assert(
                        cpu.u == 111,
                        f"alligatorexpression changed U value from {111} to {cpu.u}!",
                    )
                    _assert(
                        cpu.v == 222,
                        f"alligatorexpression changed V value from {222} to {cpu.v}!",
                    )
                    _assert(
                        cpu.ram[cpu.pc + 0] in {0x00, 0xFF},
                        f"compulted boolean was invalid value {cpu.ram[cpu.pc + 0]}!",
                    )
                    result = bool(cpu.ram[cpu.pc + 0])
                    expected = eval(f"{val1} {operator} {val2}")
                    _assert(
                        result == expected,
                        "Failed to alligatorexpression, "
                        + f"got {result} instead of {expected} for {val1} {operator} {val2}!",
                    )
                    cycles += cpu.cycles
                    instructions += cpu.ticks
                    count += 1

    for val1 in [-10, 0, 10, 57, -57, 123]:
        for val2 in [-10, 0, 10, 57, -57, 123]:
            for secondtype in ["int8", "int16", "int32"]:
                for operator in ["<=", "<", ">=", ">="]:
                    memory = getmemory(os.linesep.join([
                        *initlines,
                        *parse_and_compile_module("alligatorexpression", textwrap.dedent(f"""
                            def func(val1: int8, val2: {secondtype}) -> bool:
                                return val1 {operator} val2
                        """)).code,
                        "main:",
                        f"PUSHI {val1}",
                        f"PUSHI {val2 & 0xFF}",
                        f"PUSHI {(val2 >> 8) & 0xFF}" if secondtype in {"int16", "int32"} else "",
                        f"PUSHI {(val2 >> 16) & 0xFF}" if secondtype == "int32" else "",
                        f"PUSHI {(val2 >> 24) & 0xFF}" if secondtype == "int32" else "",
                        "LOADI 111",
                        "MOV A, U",
                        "LOADI 222",
                        "MOV A, V",
                        "LOADI 123",
                        "CALL func",
                        "HALT",
                        *cmplines,
                    ]))
                    cpu = CPUCore(memory)
                    rununtilhalt(cpu)

                    _assert(
                        cpu.a == 123,
                        f"alligatorexpression changed accumulator value from {123} to {cpu.a}!",
                    )
                    _assert(
                        cpu.u == 111,
                        f"alligatorexpression changed U value from {111} to {cpu.u}!",
                    )
                    _assert(
                        cpu.v == 222,
                        f"alligatorexpression changed V value from {222} to {cpu.v}!",
                    )
                    _assert(
                        cpu.ram[cpu.pc + 0] in {0x00, 0xFF},
                        f"compulted boolean was invalid value {cpu.ram[cpu.pc + 0]}!",
                    )
                    result = bool(cpu.ram[cpu.pc + 0])
                    expected = eval(f"{val1} {operator} {val2}")
                    _assert(
                        result == expected,
                        "Failed to alligatorexpression, "
                        + f"got {result} instead of {expected} for {val1} {operator} {val2}!",
                    )
                    cycles += cpu.cycles
                    instructions += cpu.ticks
                    count += 1

    print(f"Average cycles for alligatorexpression: {int(cycles/count)}")
    print(f"Average instructions for alligatorexpression: {int(instructions/count)}")


def verifyglobalvariableread(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "globalvariableread" not in only and "compiler" not in only:
        return

    print("Verifying globalvariableread...")

    with open("lib/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/start.S", "r") as fp:
        startlines = fp.readlines()
    with open("lib/data.S", "r") as fp:
        datalines = fp.readlines()
    with open("lib/heap.S", "r") as fp:
        heaplines = fp.readlines()
    with open("lib/math/add.S", "r") as fp:
        addlines = fp.readlines()

    cycles = 0
    instructions = 0
    count = 0

    for val in [0, 37, -37, 42, -42]:
        # First, attempt to initialize a global variable and then read it's value later.
        # This code should trigger an 8-bit register read of the variable instead of using
        # the stack.
        sections = parse_and_compile_module("globalvariableread", textwrap.dedent(f"""
            global_variable: int8 = {val}
            def get_global_variable() -> int8:
                return global_variable
        """))
        memory = getmemory(os.linesep.join([
            *initlines,
            *sections.init,
            *startlines,
            *sections.code,
            "main:",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            "LOADI 123",
            "DECPC",
            "CALL get_global_variable",
            "HALT",
            *datalines,
            *sections.data,
            *heaplines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        _assert(
            cpu.a == 123,
            f"globalvariableread changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"globalvariableread changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"globalvariableread changed V value from {222} to {cpu.v}!",
        )
        result = bintoint(cpu.ram[cpu.pc + 0])
        _assert(
            result == val,
            "Failed to globalvariableread, "
            + f"got {result} instead of {val}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    for val in [0, 37, 42, 123, 234, 255]:
        # First, attempt to initialize a global variable and then read it's value later.
        # This code should trigger an 8-bit register read of the variable instead of using
        # the stack.
        sections = parse_and_compile_module("globalvariableread", textwrap.dedent(f"""
            global_variable: uint8 = {val}
            def get_global_variable() -> nopad[uint8]:
                return global_variable
        """))
        memory = getmemory(os.linesep.join([
            *initlines,
            *sections.init,
            *startlines,
            *sections.code,
            "main:",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            "LOADI 123",
            "CALL get_global_variable",
            "HALT",
            *datalines,
            *sections.data,
            *heaplines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        _assert(
            cpu.a == 123,
            f"globalvariableread changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"globalvariableread changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"globalvariableread changed V value from {222} to {cpu.v}!",
        )
        result = cpu.ram[cpu.pc + 0]
        _assert(
            result == val,
            "Failed to globalvariableread, "
            + f"got {result} instead of {val}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    for global_width in ["int8", "int16", "int32"]:
        for function_width in ["int8", "int16", "int32"]:
            for val in [0, 37, -37, 42, -42]:
                add_val = {
                    "int8": 15,
                    "int16": 1337,
                    "int32": 123456789,
                }[function_width]

                # Now, attempt to read an initialized global variable and perform math against it.
                sections = parse_and_compile_module("globalvariableread", textwrap.dedent(f"""
                    global_variable: {global_width} = {val}
                    def get_global_variable() -> nopad[{function_width}]:
                        return global_variable + {add_val}
                """))
                memory = getmemory(os.linesep.join([
                    *initlines,
                    *sections.init,
                    *startlines,
                    *addlines,
                    *sections.code,
                    "main:",
                    "LOADI 111",
                    "MOV A, U",
                    "LOADI 222",
                    "MOV A, V",
                    "LOADI 123",
                    "CALL get_global_variable",
                    "HALT",
                    *datalines,
                    *sections.data,
                    *heaplines,
                ]))
                cpu = CPUCore(memory)
                rununtilhalt(cpu)

                _assert(
                    cpu.a == 123,
                    f"globalvariableread changed accumulator value from {123} to {cpu.a}!",
                )
                _assert(
                    cpu.u == 111,
                    f"globalvariableread changed U value from {111} to {cpu.u}!",
                )
                _assert(
                    cpu.v == 222,
                    f"globalvariableread changed V value from {222} to {cpu.v}!",
                )
                if function_width == "int8":
                    result = bintoint(cpu.ram[cpu.pc + 0])
                elif function_width == "int16":
                    result = bintoint16(
                        (cpu.ram[cpu.pc] << 8) + cpu.ram[cpu.pc + 1]
                    )
                elif function_width == "int32":
                    result = bintoint32(
                        (cpu.ram[cpu.pc] << 24) +
                        (cpu.ram[cpu.pc + 1] << 16) +
                        (cpu.ram[cpu.pc + 2] << 8) +
                        cpu.ram[cpu.pc + 3]
                    )
                else:
                    result = 0xDEADBEEF
                expected = val + add_val
                _assert(
                    result == expected,
                    f"Failed to globalvariableread from {global_width} to {function_width}, "
                    + f"got {result} instead of {expected}!",
                )
                cycles += cpu.cycles
                instructions += cpu.ticks
                count += 1

    for global_width in ["uint8", "uint16", "uint32"]:
        for function_width in ["uint8", "uint16", "uint32"]:
            for val in [0, 37, 42, 69, 123, 234]:
                add_val = {
                    "uint8": 15,
                    "uint16": 1337,
                    "uint32": 123456789,
                }[function_width]

                # Now, attempt to read an initialized global variable and perform math against it.
                sections = parse_and_compile_module("globalvariableread", textwrap.dedent(f"""
                    global_variable: {global_width} = {val}
                    def get_global_variable() -> nopad[{function_width}]:
                        return global_variable + {add_val}
                """))
                memory = getmemory(os.linesep.join([
                    *initlines,
                    *sections.init,
                    *startlines,
                    *addlines,
                    *sections.code,
                    "main:",
                    "LOADI 111",
                    "MOV A, U",
                    "LOADI 222",
                    "MOV A, V",
                    "LOADI 123",
                    "CALL get_global_variable",
                    "HALT",
                    *datalines,
                    *sections.data,
                    *heaplines,
                ]))
                cpu = CPUCore(memory)
                rununtilhalt(cpu)

                _assert(
                    cpu.a == 123,
                    f"globalvariableread changed accumulator value from {123} to {cpu.a}!",
                )
                _assert(
                    cpu.u == 111,
                    f"globalvariableread changed U value from {111} to {cpu.u}!",
                )
                _assert(
                    cpu.v == 222,
                    f"globalvariableread changed V value from {222} to {cpu.v}!",
                )
                if function_width == "uint8":
                    result = (cpu.ram[cpu.pc + 0])
                elif function_width == "uint16":
                    result = (
                        (cpu.ram[cpu.pc] << 8) + cpu.ram[cpu.pc + 1]
                    )
                elif function_width == "uint32":
                    result = (
                        (cpu.ram[cpu.pc] << 24) +
                        (cpu.ram[cpu.pc + 1] << 16) +
                        (cpu.ram[cpu.pc + 2] << 8) +
                        cpu.ram[cpu.pc + 3]
                    )
                else:
                    result = 0xDEADBEEF
                expected = val + add_val
                _assert(
                    result == expected,
                    f"Failed to globalvariableread from {global_width} to {function_width}, "
                    + f"got {result} instead of {expected}!",
                )
                cycles += cpu.cycles
                instructions += cpu.ticks
                count += 1

    print(f"Average cycles for globalvariableread: {int(cycles/count)}")
    print(f"Average instructions for globalvariableread: {int(instructions/count)}")


def verifyglobalvariablewrite(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "globalvariablewrite" not in only and "compiler" not in only:
        return

    print("Verifying globalvariablewrite...")

    with open("lib/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/start.S", "r") as fp:
        startlines = fp.readlines()
    with open("lib/data.S", "r") as fp:
        datalines = fp.readlines()
    with open("lib/heap.S", "r") as fp:
        heaplines = fp.readlines()
    with open("lib/math/add.S", "r") as fp:
        addlines = fp.readlines()

    cycles = 0
    instructions = 0
    count = 0

    for global_width in ["int8", "int16", "int32"]:
        for val in [0, 37, -37, 42, -42]:
            sections = parse_and_compile_module("globalvariablewrite", textwrap.dedent(f"""
                global_variable: {global_width} = 0
                def set_global_variable() -> void:
                    global global_variable
                    global_variable = {val}
            """))
            memory = getmemory(os.linesep.join([
                *initlines,
                *sections.init,
                *startlines,
                *addlines,
                *sections.code,
                "main:",
                "LOADI 111",
                "MOV A, U",
                "LOADI 222",
                "MOV A, V",
                "LOADI 123",
                "CALL set_global_variable",
                "HALT",
                *datalines,
                *sections.data,
                *heaplines,
            ]))
            cpu = CPUCore(memory)
            rununtilhalt(cpu)

            _assert(
                cpu.a == 123,
                f"globalvariablewrite changed accumulator value from {123} to {cpu.a}!",
            )
            _assert(
                cpu.u == 111,
                f"globalvariablewrite changed U value from {111} to {cpu.u}!",
            )
            _assert(
                cpu.v == 222,
                f"globalvariablewrite changed V value from {222} to {cpu.v}!",
            )
            if global_width == "int8":
                result = bintoint(cpu.ram[0x8000])
            elif global_width == "int16":
                result = bintoint16(
                    (cpu.ram[0x8000] << 8) + cpu.ram[0x8001]
                )
            elif global_width == "int32":
                result = bintoint32(
                    (cpu.ram[0x8000] << 24) +
                    (cpu.ram[0x8001] << 16) +
                    (cpu.ram[0x8002] << 8) +
                    cpu.ram[0x8003]
                )
            else:
                result = 0xDEADBEEF
            expected = val
            _assert(
                result == expected,
                f"Failed to globalvariablewrite at {global_width}, "
                + f"got {result} instead of {expected}!",
            )
            cycles += cpu.cycles
            instructions += cpu.ticks
            count += 1

    for global_width in ["uint8", "uint16", "uint32"]:
        for val in [0, 37, 42, 69, 123, 234]:
            sections = parse_and_compile_module("globalvariablewrite", textwrap.dedent(f"""
                global_variable: {global_width} = 0
                def set_global_variable() -> void:
                    global global_variable
                    global_variable = {val}
            """))
            memory = getmemory(os.linesep.join([
                *initlines,
                *sections.init,
                *startlines,
                *addlines,
                *sections.code,
                "main:",
                "LOADI 111",
                "MOV A, U",
                "LOADI 222",
                "MOV A, V",
                "LOADI 123",
                "CALL set_global_variable",
                "HALT",
                *datalines,
                *sections.data,
                *heaplines,
            ]))
            cpu = CPUCore(memory)
            rununtilhalt(cpu)

            _assert(
                cpu.a == 123,
                f"globalvariablewrite changed accumulator value from {123} to {cpu.a}!",
            )
            _assert(
                cpu.u == 111,
                f"globalvariablewrite changed U value from {111} to {cpu.u}!",
            )
            _assert(
                cpu.v == 222,
                f"globalvariablewrite changed V value from {222} to {cpu.v}!",
            )
            if global_width == "uint8":
                result = (cpu.ram[0x8000])
            elif global_width == "uint16":
                result = (
                    (cpu.ram[0x8000] << 8) + cpu.ram[0x8001]
                )
            elif global_width == "uint32":
                result = (
                    (cpu.ram[0x8000] << 24) +
                    (cpu.ram[0x8001] << 16) +
                    (cpu.ram[0x8002] << 8) +
                    cpu.ram[0x8003]
                )
            else:
                result = 0xDEADBEEF
            expected = val
            _assert(
                result == expected,
                f"Failed to globalvariablewrite at {global_width}, "
                + f"got {result} instead of {expected}!",
            )
            cycles += cpu.cycles
            instructions += cpu.ticks
            count += 1

    # Verify extern support while we're in here.
    sections = parse_and_compile_module("globalvariablewrite", textwrap.dedent("""
        global_variable: extern[uint32] = 0xFFFFFFFF
        def set_global_variable() -> void:
            global global_variable
            global_variable = 0xCAFEBABE
    """))
    memory = getmemory(os.linesep.join([
        *initlines,
        *sections.init,
        *startlines,
        *addlines,
        *sections.code,
        "main:",
        "LOADI 111",
        "MOV A, U",
        "LOADI 222",
        "MOV A, V",
        "LOADI 123",
        "CALL set_global_variable",
        "HALT",
        *datalines,
        *sections.data,
        *heaplines,
        ".org 0x8573",
        "global_variable:",
    ]))
    cpu = CPUCore(memory)
    rununtilhalt(cpu)

    _assert(
        cpu.a == 123,
        f"globalvariablewrite changed accumulator value from {123} to {cpu.a}!",
    )
    _assert(
        cpu.u == 111,
        f"globalvariablewrite changed U value from {111} to {cpu.u}!",
    )
    _assert(
        cpu.v == 222,
        f"globalvariablewrite changed V value from {222} to {cpu.v}!",
    )
    original = (
        (cpu.ram[0x8000] << 24) +
        (cpu.ram[0x8001] << 16) +
        (cpu.ram[0x8002] << 8) +
        cpu.ram[0x8003]
    )
    _assert(
        original == 0x0,
        f"globalvariablewrite changed original variable location from {0x0} to {hex(original)}!",
    )
    result = (
        (cpu.ram[0x8573] << 24) +
        (cpu.ram[0x8574] << 16) +
        (cpu.ram[0x8575] << 8) +
        cpu.ram[0x8576]
    )
    expected = 0xCAFEBABE
    _assert(
        result == expected,
        f"Failed to globalvariablewrite at {global_width}, "
        + f"got {result} instead of {expected}!",
    )
    cycles += cpu.cycles
    instructions += cpu.ticks
    count += 1

    print(f"Average cycles for globalvariablewrite: {int(cycles/count)}")
    print(f"Average instructions for globalvariablewrite: {int(instructions/count)}")


def verifyifstatements(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "ifstatements" not in only and "compiler" not in only:
        return

    print("Verifying ifstatements...")

    with open("lib/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/start.S", "r") as fp:
        startlines = fp.readlines()
    with open("lib/data.S", "r") as fp:
        datalines = fp.readlines()
    with open("lib/heap.S", "r") as fp:
        heaplines = fp.readlines()
    with open("lib/math/cmp.S", "r") as fp:
        cmplines = fp.readlines()

    cycles = 0
    instructions = 0
    count = 0

    # First, test if statements with no else case, both when they return and when they
    # expect to naturally flow out past the indented block.
    for input_val, expected in [(True, 15), (False, -25)]:
        sections = parse_and_compile_module("ifstatements", textwrap.dedent("""
            def simpleif(condition: bool) -> int8:
                if condition:
                    return 15
                return -25
        """))
        memory = getmemory(os.linesep.join([
            *initlines,
            *sections.init,
            *startlines,
            *sections.code,
            "main:",
            f"PUSHI {0xFF if input_val else 0x00}",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            "LOADI 123",
            "CALL simpleif",
            "HALT",
            *datalines,
            *sections.data,
            *heaplines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        _assert(
            cpu.a == 123,
            f"ifstatements changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"ifstatements changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"ifstatements changed V value from {222} to {cpu.v}!",
        )
        result = bintoint(cpu.ram[cpu.pc])
        _assert(
            result == expected,
            "Failed to ifstatements simple, "
            + f"got {result} instead of {expected}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    for input_val, expected in [(True, 15), (False, -25)]:
        sections = parse_and_compile_module("ifstatements", textwrap.dedent("""
            def simpleif(condition: bool) -> int8:
                retval: int8 = -25
                if condition:
                    retval = 15
                return retval
        """))
        memory = getmemory(os.linesep.join([
            *initlines,
            *sections.init,
            *startlines,
            *sections.code,
            "main:",
            f"PUSHI {0xFF if input_val else 0x00}",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            "LOADI 123",
            "CALL simpleif",
            "HALT",
            *datalines,
            *sections.data,
            *heaplines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        _assert(
            cpu.a == 123,
            f"ifstatements changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"ifstatements changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"ifstatements changed V value from {222} to {cpu.v}!",
        )
        result = bintoint(cpu.ram[cpu.pc])
        _assert(
            result == expected,
            "Failed to ifstatements simple, "
            + f"got {result} instead of {expected}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    # Now, test if statements with a single else case, both when they return and when they
    # expect to naturally flow out past the indented block.
    for input_val, expected in [(True, 15), (False, -25)]:
        sections = parse_and_compile_module("ifstatements", textwrap.dedent("""
            def ifelseif(condition: bool) -> int8:
                if condition:
                    return 15
                else:
                    return -25
        """))
        memory = getmemory(os.linesep.join([
            *initlines,
            *sections.init,
            *startlines,
            *sections.code,
            "main:",
            f"PUSHI {0xFF if input_val else 0x00}",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            "LOADI 123",
            "CALL ifelseif",
            "HALT",
            *datalines,
            *sections.data,
            *heaplines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        _assert(
            cpu.a == 123,
            f"ifstatements changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"ifstatements changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"ifstatements changed V value from {222} to {cpu.v}!",
        )
        result = bintoint(cpu.ram[cpu.pc])
        _assert(
            result == expected,
            "Failed to ifstatements ifelse, "
            + f"got {result} instead of {expected}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    for input_val, expected in [(True, 15), (False, -25)]:
        sections = parse_and_compile_module("ifstatements", textwrap.dedent("""
            def ifelseif(condition: bool) -> int8:
                retval: int8
                if condition:
                    retval = 15
                else:
                    retval = -25
                return retval
        """))
        memory = getmemory(os.linesep.join([
            *initlines,
            *sections.init,
            *startlines,
            *sections.code,
            "main:",
            f"PUSHI {0xFF if input_val else 0x00}",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            "LOADI 123",
            "CALL ifelseif",
            "HALT",
            *datalines,
            *sections.data,
            *heaplines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        _assert(
            cpu.a == 123,
            f"ifstatements changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"ifstatements changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"ifstatements changed V value from {222} to {cpu.v}!",
        )
        result = bintoint(cpu.ram[cpu.pc])
        _assert(
            result == expected,
            "Failed to ifstatements ifelse, "
            + f"got {result} instead of {expected}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    # Now, test if statements with a bunch of elif cases but no else case, both when they
    # return and when they expect to naturally flow out past the indented block.
    for input_val_int, expected in [(3, 5), (7, 10), (13, 15), (17, 20)]:
        sections = parse_and_compile_module("ifstatements", textwrap.dedent("""
            def ifelif(var: int8) -> int8:
                if var < 5:
                    return 5
                elif var < 10:
                    return 10
                elif var < 15:
                    return 15
                return 20
        """))
        memory = getmemory(os.linesep.join([
            *initlines,
            *sections.init,
            *startlines,
            *cmplines,
            *sections.code,
            "main:",
            f"PUSHI {input_val_int}",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            "LOADI 123",
            "CALL ifelif",
            "HALT",
            *datalines,
            *sections.data,
            *heaplines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        _assert(
            cpu.a == 123,
            f"ifstatements changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"ifstatements changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"ifstatements changed V value from {222} to {cpu.v}!",
        )
        result = bintoint(cpu.ram[cpu.pc])
        _assert(
            result == expected,
            "Failed to ifstatements ifelif, "
            + f"got {result} instead of {expected}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    for input_val_int, expected in [(3, 5), (7, 10), (13, 15), (17, 20)]:
        sections = parse_and_compile_module("ifstatements", textwrap.dedent("""
            def ifelif(var: int8) -> int8:
                retval: int8 = 20
                if var < 5:
                    retval = 5
                elif var < 10:
                    retval = 10
                elif var < 15:
                    retval = 15
                return retval
        """))
        memory = getmemory(os.linesep.join([
            *initlines,
            *sections.init,
            *startlines,
            *cmplines,
            *sections.code,
            "main:",
            f"PUSHI {input_val_int}",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            "LOADI 123",
            "CALL ifelif",
            "HALT",
            *datalines,
            *sections.data,
            *heaplines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        _assert(
            cpu.a == 123,
            f"ifstatements changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"ifstatements changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"ifstatements changed V value from {222} to {cpu.v}!",
        )
        result = bintoint(cpu.ram[cpu.pc])
        _assert(
            result == expected,
            "Failed to ifstatements ifelif, "
            + f"got {result} instead of {expected}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    # Finally, test if statements with a bunch of elif cases but no else case, both when they
    # return and when they expect to naturally flow out past the indented block.
    for input_val_int, expected in [(3, 5), (7, 10), (13, 15), (17, 20)]:
        sections = parse_and_compile_module("ifstatements", textwrap.dedent("""
            def ifelifelse(var: int8) -> int8:
                if var < 5:
                    return 5
                elif var < 10:
                    return 10
                elif var < 15:
                    return 15
                else:
                    return 20
        """))
        memory = getmemory(os.linesep.join([
            *initlines,
            *sections.init,
            *startlines,
            *cmplines,
            *sections.code,
            "main:",
            f"PUSHI {input_val_int}",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            "LOADI 123",
            "CALL ifelifelse",
            "HALT",
            *datalines,
            *sections.data,
            *heaplines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        _assert(
            cpu.a == 123,
            f"ifstatements changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"ifstatements changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"ifstatements changed V value from {222} to {cpu.v}!",
        )
        result = bintoint(cpu.ram[cpu.pc])
        _assert(
            result == expected,
            "Failed to ifstatements ifelifelse, "
            + f"got {result} instead of {expected}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    for input_val_int, expected in [(3, 5), (7, 10), (13, 15), (17, 20)]:
        sections = parse_and_compile_module("ifstatements", textwrap.dedent("""
            def ifelifelse(var: int8) -> int8:
                retval: int8
                if var < 5:
                    retval = 5
                elif var < 10:
                    retval = 10
                elif var < 15:
                    retval = 15
                else:
                    retval = 20
                return retval
        """))
        memory = getmemory(os.linesep.join([
            *initlines,
            *sections.init,
            *startlines,
            *cmplines,
            *sections.code,
            "main:",
            f"PUSHI {input_val_int}",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            "LOADI 123",
            "CALL ifelifelse",
            "HALT",
            *datalines,
            *sections.data,
            *heaplines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        _assert(
            cpu.a == 123,
            f"ifstatements changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"ifstatements changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"ifstatements changed V value from {222} to {cpu.v}!",
        )
        result = bintoint(cpu.ram[cpu.pc])
        _assert(
            result == expected,
            "Failed to ifstatements ifelifelse, "
            + f"got {result} instead of {expected}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    # And just for shiggles, let's test nested if statements as well.
    for input_val_int, expected in [(3, 5), (7, 10), (13, 15), (17, 20)]:
        sections = parse_and_compile_module("ifstatements", textwrap.dedent("""
            def ifelifelse(var: int8) -> int8:
                if var < 5:
                    return 5
                else:
                    if var < 10:
                        return 10
                    else:
                        if var < 15:
                            return 15
                        else:
                            return 20
        """))
        memory = getmemory(os.linesep.join([
            *initlines,
            *sections.init,
            *startlines,
            *cmplines,
            *sections.code,
            "main:",
            f"PUSHI {input_val_int}",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            "LOADI 123",
            "CALL ifelifelse",
            "HALT",
            *datalines,
            *sections.data,
            *heaplines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        _assert(
            cpu.a == 123,
            f"ifstatements changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"ifstatements changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"ifstatements changed V value from {222} to {cpu.v}!",
        )
        result = bintoint(cpu.ram[cpu.pc])
        _assert(
            result == expected,
            "Failed to ifstatements ifelifelse, "
            + f"got {result} instead of {expected}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    for input_val_int, expected in [(3, 5), (7, 10), (13, 15), (17, 20)]:
        sections = parse_and_compile_module("ifstatements", textwrap.dedent("""
            def ifelifelse(var: int8) -> int8:
                retval: int8
                if var < 5:
                    retval = 5
                else:
                    if var < 10:
                        retval = 10
                    else:
                        if var < 15:
                            retval = 15
                        else:
                            retval = 20
                return retval
        """))
        memory = getmemory(os.linesep.join([
            *initlines,
            *sections.init,
            *startlines,
            *cmplines,
            *sections.code,
            "main:",
            f"PUSHI {input_val_int}",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            "LOADI 123",
            "CALL ifelifelse",
            "HALT",
            *datalines,
            *sections.data,
            *heaplines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        _assert(
            cpu.a == 123,
            f"ifstatements changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"ifstatements changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"ifstatements changed V value from {222} to {cpu.v}!",
        )
        result = bintoint(cpu.ram[cpu.pc])
        _assert(
            result == expected,
            "Failed to ifstatements ifelifelse, "
            + f"got {result} instead of {expected}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    print(f"Average cycles for ifstatements: {int(cycles/count)}")
    print(f"Average instructions for ifstatements: {int(instructions/count)}")


def verifywhilestatements(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "whilestatements" not in only and "compiler" not in only:
        return

    print("Verifying whilestatements...")

    with open("lib/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/start.S", "r") as fp:
        startlines = fp.readlines()
    with open("lib/data.S", "r") as fp:
        datalines = fp.readlines()
    with open("lib/heap.S", "r") as fp:
        heaplines = fp.readlines()
    with open("lib/math/cmp.S", "r") as fp:
        cmplines = fp.readlines()

    cycles = 0
    instructions = 0
    count = 0

    # First, run the simplest while loops we can and verify that the calculation is correct.
    if True:
        sections = parse_and_compile_module("whilestatements", textwrap.dedent("""
            def simple_while() -> int8:
                x: int8 = 0
                y: int8 = 0
                while x < 5:
                    y += x
                    x += 1
                return y
        """))
        memory = getmemory(os.linesep.join([
            *initlines,
            *sections.init,
            *startlines,
            *cmplines,
            *sections.code,
            "main:",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            "LOADI 123",
            "DECPC",
            "CALL simple_while",
            "HALT",
            *datalines,
            *sections.data,
            *heaplines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        _assert(
            cpu.a == 123,
            f"whilestatements changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"whilestatements changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"whilestatements changed V value from {222} to {cpu.v}!",
        )
        result = bintoint(cpu.ram[cpu.pc])
        expected = (0 + 1 + 2 + 3 + 4)
        _assert(
            result == expected,
            "Failed to whilestatements simple, "
            + f"got {result} instead of {expected}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    # Now, run a while loop with no termination that exits via a break statement.
    if True:
        sections = parse_and_compile_module("whilestatements", textwrap.dedent("""
            def break_while() -> int8:
                x: int8 = 0
                y: int8 = 0
                while True:
                    y += x
                    x += 1
                    if x > 5:
                        break
                return y
        """))
        memory = getmemory(os.linesep.join([
            *initlines,
            *sections.init,
            *startlines,
            *cmplines,
            *sections.code,
            "main:",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            "LOADI 123",
            "DECPC",
            "CALL break_while",
            "HALT",
            *datalines,
            *sections.data,
            *heaplines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        _assert(
            cpu.a == 123,
            f"whilestatements changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"whilestatements changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"whilestatements changed V value from {222} to {cpu.v}!",
        )
        result = bintoint(cpu.ram[cpu.pc])
        expected = (0 + 1 + 2 + 3 + 4 + 5)
        _assert(
            result == expected,
            "Failed to whilestatements break, "
            + f"got {result} instead of {expected}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    # Now, run the a while loop that uses continue statements.
    if True:
        sections = parse_and_compile_module("whilestatements", textwrap.dedent("""
            def continue_while() -> int8:
                x: int8 = 0
                y: int8 = 0
                while x < 10:
                    if x >= 5:
                        x += 1
                        continue

                    y += x
                    x += 1
                return y
        """))
        memory = getmemory(os.linesep.join([
            *initlines,
            *sections.init,
            *startlines,
            *cmplines,
            *sections.code,
            "main:",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            "LOADI 123",
            "DECPC",
            "CALL continue_while",
            "HALT",
            *datalines,
            *sections.data,
            *heaplines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        _assert(
            cpu.a == 123,
            f"whilestatements changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"whilestatements changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"whilestatements changed V value from {222} to {cpu.v}!",
        )
        result = bintoint(cpu.ram[cpu.pc])
        expected = (0 + 1 + 2 + 3 + 4)
        _assert(
            result == expected,
            "Failed to whilestatements continue, "
            + f"got {result} instead of {expected}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    # Finally, test else handling when exiting a loop.
    for should_exit in [True, False]:
        sections = parse_and_compile_module("whilestatements", textwrap.dedent("""
            def while_with_else(should_exit: bool) -> int8:
                x: int8 = 0
                y: int8 = 0
                while x < 10:
                    if x >= 5:
                        if should_exit:
                            break
                        else:
                            x += 1
                            continue

                    y += x
                    x += 1
                else:
                    y += 30
                return y
        """))
        memory = getmemory(os.linesep.join([
            *initlines,
            *sections.init,
            *startlines,
            *cmplines,
            *sections.code,
            "main:",
            f"PUSHI {'0xFF' if should_exit else '0x00'}",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            "LOADI 123",
            "CALL while_with_else",
            "HALT",
            *datalines,
            *sections.data,
            *heaplines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        _assert(
            cpu.a == 123,
            f"whilestatements changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"whilestatements changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"whilestatements changed V value from {222} to {cpu.v}!",
        )
        result = bintoint(cpu.ram[cpu.pc])
        expected = (0 + 1 + 2 + 3 + 4) + (0 if should_exit else 30)
        _assert(
            result == expected,
            "Failed to whilestatements else, "
            + f"got {result} instead of {expected}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    print(f"Average cycles for whilestatements: {int(cycles/count)}")
    print(f"Average instructions for whilestatements: {int(instructions/count)}")


def verifyforstatements(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "forstatements" not in only and "compiler" not in only:
        return

    print("Verifying forstatements...")

    with open("lib/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/start.S", "r") as fp:
        startlines = fp.readlines()
    with open("lib/data.S", "r") as fp:
        datalines = fp.readlines()
    with open("lib/heap.S", "r") as fp:
        heaplines = fp.readlines()
    with open("lib/math/cmp.S", "r") as fp:
        cmplines = fp.readlines()

    cycles = 0
    instructions = 0
    count = 0

    # First, run the simplest for loops we can and verify that the calculation is correct.
    for rangeval, expected in [("5", (0 + 1 + 2 + 3 + 4)), ("1, 7", (1 + 2 + 3 + 4 + 5 + 6)), ("0, 10, 2", (0 + 2 + 4 + 6 + 8))]:
        sections = parse_and_compile_module("forstatements", textwrap.dedent(f"""
            def simple_for() -> int8:
                retval: int8 = 0

                x: int8
                for x in range({rangeval}):
                    retval += x

                return retval
        """))
        memory = getmemory(os.linesep.join([
            *initlines,
            *sections.init,
            *startlines,
            *cmplines,
            *sections.code,
            "main:",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            "LOADI 123",
            "DECPC",
            "CALL simple_for",
            "HALT",
            *datalines,
            *sections.data,
            *heaplines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        _assert(
            cpu.a == 123,
            f"forstatements changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"forstatements changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"forstatements changed V value from {222} to {cpu.v}!",
        )
        result = bintoint(cpu.ram[cpu.pc])
        _assert(
            result == expected,
            "Failed to forstatements simple, "
            + f"got {result} instead of {expected}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    # Now, run through the same loops but introduce a continue statement to ensure that this works as intended.
    for rangeval, expected in [("5", (0 + 2 + 4)), ("1, 7", (2 + 4 + 6)), ("0, 10, 2", (0 + 2 + 4 + 6 + 8))]:
        sections = parse_and_compile_module("forstatements", textwrap.dedent(f"""
            def simple_for() -> int8:
                retval: int8 = 0

                x: int8
                for x in range({rangeval}):
                    if x & 1 != 0:
                        continue

                    retval += x

                return retval
        """))
        memory = getmemory(os.linesep.join([
            *initlines,
            *sections.init,
            *startlines,
            *cmplines,
            *sections.code,
            "main:",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            "LOADI 123",
            "DECPC",
            "CALL simple_for",
            "HALT",
            *datalines,
            *sections.data,
            *heaplines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        _assert(
            cpu.a == 123,
            f"forstatements changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"forstatements changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"forstatements changed V value from {222} to {cpu.v}!",
        )
        result = bintoint(cpu.ram[cpu.pc])
        _assert(
            result == expected,
            "Failed to forstatements continue, "
            + f"got {result} instead of {expected}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    # Now, run the through the same loops again, breaking out early and verifying that that works.
    for rangeval, expected in [("5", (0 + 1 + 2 + 3)), ("3, 9", (3 + 4)), ("1, 11, 2", (1 + 3 + 5))]:
        sections = parse_and_compile_module("forstatements", textwrap.dedent(f"""
            def simple_for() -> int8:
                retval: int8 = 0

                x: int8
                for x in range({rangeval}):
                    if retval > 5:
                        break

                    retval += x

                return retval
        """))
        memory = getmemory(os.linesep.join([
            *initlines,
            *sections.init,
            *startlines,
            *cmplines,
            *sections.code,
            "main:",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            "LOADI 123",
            "DECPC",
            "CALL simple_for",
            "HALT",
            *datalines,
            *sections.data,
            *heaplines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        _assert(
            cpu.a == 123,
            f"forstatements changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"forstatements changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"forstatements changed V value from {222} to {cpu.v}!",
        )
        result = bintoint(cpu.ram[cpu.pc])
        _assert(
            result == expected,
            "Failed to forstatements break, "
            + f"got {result} instead of {expected}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    # Now, check the scoping of the loop variable. We differ from python here in that we end up
    # getting to the final value whereas python would always return the x value of the previous
    # iteration. Fixing that does not seem worth it given the extra stack shenanigans it would take.
    for rangeval, expected in [("5", 5), ("1, 7", 7), ("0, 10, 2", 10)]:
        sections = parse_and_compile_module("forstatements", textwrap.dedent(f"""
            def simple_for() -> int8:
                x: int8
                for x in range({rangeval}):
                    pass

                return x
        """))
        memory = getmemory(os.linesep.join([
            *initlines,
            *sections.init,
            *startlines,
            *cmplines,
            *sections.code,
            "main:",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            "LOADI 123",
            "DECPC",
            "CALL simple_for",
            "HALT",
            *datalines,
            *sections.data,
            *heaplines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        _assert(
            cpu.a == 123,
            f"forstatements changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"forstatements changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"forstatements changed V value from {222} to {cpu.v}!",
        )
        result = bintoint(cpu.ram[cpu.pc])
        _assert(
            result == expected,
            "Failed to forstatements loop counter, "
            + f"got {result} instead of {expected}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    for rangeval, expected in [("5", 4), ("1, 7", 4), ("0, 10, 2", 4)]:
        sections = parse_and_compile_module("forstatements", textwrap.dedent(f"""
            def simple_for() -> int8:
                x: int8
                for x in range({rangeval}):
                    if x > 3:
                        break

                return x
        """))
        memory = getmemory(os.linesep.join([
            *initlines,
            *sections.init,
            *startlines,
            *cmplines,
            *sections.code,
            "main:",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            "LOADI 123",
            "DECPC",
            "CALL simple_for",
            "HALT",
            *datalines,
            *sections.data,
            *heaplines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        _assert(
            cpu.a == 123,
            f"forstatements changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"forstatements changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"forstatements changed V value from {222} to {cpu.v}!",
        )
        result = bintoint(cpu.ram[cpu.pc])
        _assert(
            result == expected,
            "Failed to forstatements loop counter, "
            + f"got {result} instead of {expected}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    for rangeval, expected in [("5", 5), ("1, 7", 7), ("0, 10, 2", 10)]:
        sections = parse_and_compile_module("forstatements", textwrap.dedent(f"""
            def simple_for() -> int8:
                x: int8
                for x in range({rangeval}):
                    continue

                return x
        """))
        memory = getmemory(os.linesep.join([
            *initlines,
            *sections.init,
            *startlines,
            *cmplines,
            *sections.code,
            "main:",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            "LOADI 123",
            "DECPC",
            "CALL simple_for",
            "HALT",
            *datalines,
            *sections.data,
            *heaplines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        _assert(
            cpu.a == 123,
            f"forstatements changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"forstatements changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"forstatements changed V value from {222} to {cpu.v}!",
        )
        result = bintoint(cpu.ram[cpu.pc])
        _assert(
            result == expected,
            "Failed to forstatements loop counter, "
            + f"got {result} instead of {expected}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    # Finally, run through the same algorithm and exit with break sometimes, and without others, to test else handling.
    for should_exit in [True, False]:
        for rangeval, expected_before in [("5", (0 + 1 + 2 + 3)), ("3, 9", (3 + 4)), ("1, 11, 2", (1 + 3 + 5))]:
            sections = parse_and_compile_module("forstatements", textwrap.dedent(f"""
                def simple_for(should_exit: bool) -> int8:
                    retval: int8 = 0

                    x: int8
                    for x in range({rangeval}):
                        if retval > 5:
                            if should_exit:
                                break
                            else:
                                continue

                        retval += x
                    else:
                        retval += 45

                    return retval
            """))
            memory = getmemory(os.linesep.join([
                *initlines,
                *sections.init,
                *startlines,
                *cmplines,
                *sections.code,
                "main:",
                f"PUSHI {'0xFF' if should_exit else '0x00'}",
                "LOADI 111",
                "MOV A, U",
                "LOADI 222",
                "MOV A, V",
                "LOADI 123",
                "CALL simple_for",
                "HALT",
                *datalines,
                *sections.data,
                *heaplines,
            ]))
            cpu = CPUCore(memory)
            rununtilhalt(cpu)

            _assert(
                cpu.a == 123,
                f"forstatements changed accumulator value from {123} to {cpu.a}!",
            )
            _assert(
                cpu.u == 111,
                f"forstatements changed U value from {111} to {cpu.u}!",
            )
            _assert(
                cpu.v == 222,
                f"forstatements changed V value from {222} to {cpu.v}!",
            )
            result = bintoint(cpu.ram[cpu.pc])
            expected = expected_before + (0 if should_exit else 45)
            _assert(
                result == expected,
                "Failed to forstatements else, "
                + f"got {result} instead of {expected}!",
            )
            cycles += cpu.cycles
            instructions += cpu.ticks
            count += 1

    print(f"Average cycles for forstatements: {int(cycles/count)}")
    print(f"Average instructions for forstatements: {int(instructions/count)}")


def verifystringreturn(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "stringreturn" not in only and "compiler" not in only:
        return

    print("Verifying stringreturn...")

    with open("lib/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/start.S", "r") as fp:
        startlines = fp.readlines()
    with open("lib/data.S", "r") as fp:
        datalines = fp.readlines()
    with open("lib/heap.S", "r") as fp:
        heaplines = fp.readlines()

    cycles = 0
    instructions = 0
    count = 0

    # First, see if we can return a global constant string, and that we get the right value.
    if True:
        sections = parse_and_compile_module("stringreturn", textwrap.dedent("""
            STRING_CONST: const[string] = "This is a test."

            def return_string() -> string:
                return STRING_CONST
        """))
        memory = getmemory(os.linesep.join([
            *initlines,
            *sections.init,
            *startlines,
            *sections.code,
            "main:",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            "LOADI 123",
            "SUBPCI 2",
            "CALL return_string",
            "HALT",
            *datalines,
            *sections.data,
            *heaplines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        _assert(
            cpu.a == 123,
            f"stringreturn changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"stringreturn changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"stringreturn changed V value from {222} to {cpu.v}!",
        )
        result = bintostr(cpu, (cpu.ram[cpu.pc] << 8) + cpu.ram[cpu.pc + 1], 0x0000, 0x4000)
        expected = "This is a test."
        _assert(
            result == expected,
            "Failed to stringreturn simple, "
            + f"got {result} instead of {expected}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    print(f"Average cycles for stringreturn: {int(cycles/count)}")
    print(f"Average instructions for stringreturn: {int(instructions/count)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="A test harness for MiniDragon.",
    )
    parser.add_argument(
        "-f",
        "--full",
        help="Verify full suite.",
        action="store_true",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        help="Display verbose execution details.",
        action="store_true",
    )
    parser.add_argument(
        "-o",
        "--only",
        help="Only run this test (comma separated values allowed).",
        type=str,
        default=None,
    )
    args = parser.parse_args()
    only = {
        x.strip() for x in args.only.lower().split(',')
    } if args.only else None

    # Make sure we can debug.
    verbose = args.verbose

    # Verify assembler errors
    verifyassembler(only, args.full)

    # Raw instruction verification
    verifyaddi(only, args.full)
    verifyloadi(only, args.full)
    verifysetpc(only, args.full)
    verifyaddpc(only, args.full)
    verifyneg(only, args.full)
    verifyaddpci(only, args.full)
    verifysubpci(only, args.full)
    verifyshift(only, args.full)

    # Math library verification
    verifymathadd(only, args.full)
    verifyadd16(only, args.full)
    verifyadd32(only, args.full)
    verifymult(only, args.full)
    verifymult16(only, args.full)
    verifymult32(only, args.full)
    verifyudiv(only, args.full)
    verifyudiv16(only, args.full)
    verifyudiv32(only, args.full)
    verifyabs(only, args.full)
    verifyabs16(only, args.full)
    verifyabs32(only, args.full)
    verifyucmp(only, args.full)
    verifyucmp16(only, args.full)
    verifyucmp32(only, args.full)
    verifycmp(only, args.full)
    verifycmp16(only, args.full)
    verifycmp32(only, args.full)
    verifyumin(only, args.full)
    verifyumin16(only, args.full)
    verifyumin32(only, args.full)
    verifyumax(only, args.full)
    verifyumax16(only, args.full)
    verifyumax32(only, args.full)
    verifymathneg(only, args.full)
    verifyneg16(only, args.full)
    verifyneg32(only, args.full)

    # String library verification
    verifystrlen(only, args.full)
    verifystrcpy(only, args.full)
    verifystrcat(only, args.full)
    verifystrcmp(only, args.full)

    # Conversion library verification
    verifyitoa(only, args.full)
    verifyitoa16(only, args.full)
    verifyitoa32(only, args.full)
    verifyatoi(only, args.full)
    verifyatoi16(only, args.full)
    verifyatoi32(only, args.full)

    # Compiler verifications
    verifystaticreturn(only, args.full)
    verifyupcast(only, args.full)
    verifyunsignedupcast(only, args.full)
    verifydowncast(only, args.full)
    verifyechoparam(only, args.full)
    verifyaddandreturn(only, args.full)
    verifysubtractandreturn(only, args.full)
    verifymultiplyandreturn(only, args.full)
    verifydivideandreturn(only, args.full)
    verifymoduloandreturn(only, args.full)
    verifybitwiseand(only, args.full)
    verifybitwiseor(only, args.full)
    verifybitwisexor(only, args.full)
    verifybitwisenot(only, args.full)
    verifynegation(only, args.full)
    verifycomplexexpression(only, args.full)
    verifyvoidfunctioncall(only, args.full)
    verifylocalvariables(only, args.full)
    verifyfunctioncall(only, args.full)
    verifycomplexfunctioncall(only, args.full)
    verifysimplebooleans(only, args.full)
    verifybooleanischeck(only, args.full)
    verifybooleanexpressions(only, args.full)
    verifyternaryexpressions(only, args.full)
    verifyequalityexpression(only, args.full)
    verifyinequalityexpression(only, args.full)
    verifyalligatorexpression(only, args.full)
    verifyglobalvariableread(only, args.full)
    verifyglobalvariablewrite(only, args.full)
    verifyifstatements(only, args.full)
    verifywhilestatements(only, args.full)
    verifyforstatements(only, args.full)
    verifystringreturn(only, args.full)
