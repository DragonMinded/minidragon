#! /usr/bin/python3
import argparse
import os
import struct
from typing import List, Optional
from core import (
    InvalidInstructionException,
    ParameterOutOfRangeException,
    CodeOutOfRangeException,
    CPUCore,
    assemble,
    disassemble,
    bintoint,
)

CLEAR_LINE = "\033[F\033[K"
BACK_AND_CLEAR_LINE = "\033[F\033[K\033[F"


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
    memory = [0] * 0x8000
    assembled = assemble(getlines(instr))
    for loc, intval in assembled:
        memory[loc] = intval
    return memory


def rununtilhalt(cpu: CPUCore) -> None:
    while True:
        if cpu.ir == 0b00111111:
            return
        cpu.tick()


def bintoint16(binary: int) -> int:
    return struct.unpack("h", struct.pack("H", binary))[0]


def bintoint32(binary: int) -> int:
    return struct.unpack("i", struct.pack("I", binary))[0]


def inttobin16(binary: int) -> int:
    return struct.unpack("H", struct.pack("h", binary))[0]


def inttobin32(binary: int) -> int:
    return struct.unpack("I", struct.pack("i", binary))[0]


def getstring(cpu: CPUCore, location: int) -> str:
    string = ""
    while cpu.ram[location] != 0x00:
        string = string + chr(cpu.ram[location])
        location += 1
    return string


def checkerror(fname: str, error: Exception) -> None:
    try:
        with open(fname, "r") as fp:
            assemble(getlines(fp.read()))
    except Exception as e:
        exception = e
    else:
        _assert(False, f"Expected a {type(error).__name__} exception!")

    _assert(
        type(exception) == type(error),
        f"Expected an exception {type(error).__name__} "
        + f"but got {type(exception).__name__}!",
    )
    _assert(
        exception.args[0] == error.args[0],
        f"Expected a message {error.args[0]!r} but got {exception.args[0]!r}!",
    )


def verifyassembler(only: Optional[str], full: bool) -> None:
    if only is not None and only != "assembler":
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
        InvalidInstructionException(
            "Cannot have more than one parameter for instruction ADDI A, 1"),
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
            "Out of range integer 32 on instruction LOADI 32"
        )
    )
    checkerror(
        "errors/oob2.S",
        ParameterOutOfRangeException(
            "Out of range integer -33 on instruction LOADI -33"
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
            "Out of range integer 32 on instruction JRI 32")
    )
    checkerror(
        "errors/oob6.S",
        ParameterOutOfRangeException(
            "Out of range integer -33 on instruction JRI -33")
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
            "Missing label invalid_label for instruction JRI invalid_label"
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


def verifyloadi(only: Optional[str], full: bool) -> None:
    if only is not None and only != "loadi":
        return

    print("Verifying LOADI...")
    for i in range(-32, 32):
        memory = getmemory(f"""
            LOADI {i}
            HALT
        """)
        cpu = CPUCore(memory)
        rununtilhalt(cpu)
        _assert(bintoint(cpu.a) == i, f"Failed to load {i} into A register!")

        memory = getmemory(f"""
            LOADI {i}
        """)
        if i == 0:
            _assert(
                disassemble(memory[0]) == f"ZERO",
                f"Failed to disassemble LOADI {i}!",
            )
        else:
            _assert(
                disassemble(memory[0]) == f"LOADI {i}",
                f"Failed to disassemble LOADI {i}!",
            )


def verifyaddi(only: Optional[str], full: bool) -> None:
    if only is not None and only != "addi":
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
                disassemble(memory[0]) == f"DEC",
                f"Failed to disassemble ADDI {i}!",
            )
        elif i == 1:
            _assert(
                disassemble(memory[0]) == f"INC",
                f"Failed to disassemble ADDI {i}!",
            )
        else:
            _assert(
                disassemble(memory[0]) == f"ADDI {i}",
                f"Failed to disassemble ADDI {i}!",
            )


def verifyseta(only: Optional[str], full: bool) -> None:
    if only is not None and only != "seta":
        return

    print("Verifying SETA...")
    for i in range(0, 256):
        memory = getmemory(f"""
            SETA {i}
            HALT
        """)
        cpu = CPUCore(memory)
        rununtilhalt(cpu)
        _assert(cpu.a == i, f"Failed to set A to {i}!")

    for i in range(-128, 128):
        memory = getmemory(f"""
            SETA {i}
            HALT
        """)
        cpu = CPUCore(memory)
        rununtilhalt(cpu)
        _assert(bintoint(cpu.a) == i, f"Failed to set A to {i}!")


def verifysetpc(only: Optional[str], full: bool) -> None:
    if only is not None and only != "setpc":
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


def verifyaddpc(only: Optional[str], full: bool) -> None:
    if only is not None and only != "addpc":
        return

    print("Verifying ADDPC...")
    for i in range(-128, 128):
        memory = getmemory(f"""
            SETPC 12345
            SETA {i}
            ADDPC
            HALT
        """)
        cpu = CPUCore(memory)
        rununtilhalt(cpu)
        _assert(
            cpu.pc[0] == 12345 + i,
            f"Failed to ADDPC against {i}, "
            + f"got {cpu.pc[0]} instead of {12345 + i}",
        )


def verifyneg(only: Optional[str], full: bool) -> None:
    if only is not None and only != "neg":
        return

    print("Verifying NEG...")
    for i in range(-127, 128):
        memory = getmemory(f"""
            SETA {i}
            NEG
            HALT
        """)
        cpu = CPUCore(memory)
        rununtilhalt(cpu)
        _assert(bintoint(cpu.a) == -i, f"Failed to negate A!")


def verifyaddpci(only: Optional[str], full: bool) -> None:
    if only is not None and only != "addpci":
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
                disassemble(memory[0]) == f"INCPC",
                f"Failed to disassemble ADDPCI {i}!",
            )
        else:
            _assert(
                disassemble(memory[0]) == f"ADDPCI {i}",
                f"Failed to disassemble ADDPCI {i}!",
            )


def verifysubpci(only: Optional[str], full: bool) -> None:
    if only is not None and only != "subpci":
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
                disassemble(memory[0]) == f"DECPC",
                f"Failed to disassemble SUBPCI {i}!",
            )
        else:
            _assert(
                disassemble(memory[0]) == f"SUBPCI {i}",
                f"Failed to disassemble SUBPCI {i}!",
            )


def verifyumult(only: Optional[str], full: bool) -> None:
    if only is not None and only != "umult":
        return

    print("Verifying umult...")
    print("0% complete...")

    with open("lib/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/math/multiply.S", "r") as fp:
        multiplylines = fp.readlines()

    cycles = 0
    instructions = 0
    count = 0
    for x in range(0, 16):
        for y in range(0, 16):
            memory = getmemory(os.linesep.join([
                *initlines,
                f"PUSHI {x}",
                f"PUSHI {y}",
                f"CALL umult",
                f"HALT",
                *multiplylines,
            ]))
            cpu = CPUCore(memory)
            rununtilhalt(cpu)
            _assert(
                cpu.a == x * y,
                f"Failed to umult {x} by {y}, "
                + f"got {cpu.a} instead of {x * y}!",
            )
            cycles += cpu.cycles
            instructions += cpu.ticks
            count += 1

        print(f"{CLEAR_LINE}{int((x * 100) / 16)}% complete...")
    print(f"{CLEAR_LINE}Average cycles for umult: {int(cycles/count)}")
    print(f"Average instructions for umult: {int(instructions/count)}")


def verifyudiv(only: Optional[str], full: bool) -> None:
    if only is not None and only != "udiv":
        return

    print("Verifying udiv...")
    print("0% complete...")

    with open("lib/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/math/divide.S", "r") as fp:
        dividelines = fp.readlines()

    cycles = 0
    instructions = 0
    count = 0
    for x in range(0, 128, 1 if full else 7):
        for y in range(1, 128, 1 if full else 5):
            memory = getmemory(os.linesep.join([
                *initlines,
                f"PUSHI {y}",
                f"PUSHI {x}",
                f"CALL udiv",
                f"HALT",
                *dividelines,
            ]))
            cpu = CPUCore(memory)
            rununtilhalt(cpu)
            _assert(
                cpu.a == x // y,
                f"Failed to udiv {x} by {y}, "
                + f"got {cpu.a} instead of {x // y}!",
            )
            remainder = cpu.ram[cpu.pc[0]]
            _assert(
                remainder == x % y,
                f"Failed to udiv {x} by {y}, "
                + f"got {remainder} instead of {x // y}!",
            )
            cycles += cpu.cycles
            instructions += cpu.ticks
            count += 1

        print(f"{CLEAR_LINE}{int((x * 100) / 128)}% complete...")
    print(f"{CLEAR_LINE}Average cycles for udiv: {int(cycles/count)}")
    print(f"Average instructions for udiv: {int(instructions/count)}")


def verifymathadd(only: Optional[str], full: bool) -> None:
    if only is not None and only != "mathadd":
        return

    print("Verifying add...")
    print("0% complete...")

    with open("lib/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/math/add.S", "r") as fp:
        addlines = fp.readlines()

    cycles = 0
    instructions = 0
    count = 0
    for x in range(0, 256, 5 if full else 11):
        for y in range(0, 256, 3 if full else 7):
            memory = getmemory(os.linesep.join([
                *initlines,
                f"PUSHI {x}",
                f"PUSHI {y}",
                f"SETA 123",
                f"CALL add",
                f"HALT",
                *addlines,
            ]))
            cpu = CPUCore(memory)
            rununtilhalt(cpu)
            calculated = cpu.ram[cpu.pc[0]]
            real = (x + y) & 0xFF
            _assert(
                cpu.a == 123,
                f"add changed A register from 123 to {cpu.a}!",
            )
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


def verifyadd16(only: Optional[str], full: bool) -> None:
    if only is not None and only != "add16":
        return

    print("Verifying add16...")
    print("0% complete...")

    with open("lib/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/math/add.S", "r") as fp:
        addlines = fp.readlines()

    cycles = 0
    instructions = 0
    count = 0
    for x in range(0, 65536, 1234 if full else 12345):
        for y in range(0, 65536, 987 if full else 1876):
            memory = getmemory(os.linesep.join([
                *initlines,
                f"PUSHI {x & 0xFF}",
                f"PUSHI {(x >> 8) & 0xFF}",
                f"PUSHI {y & 0xFF}",
                f"PUSHI {(y >> 8) & 0xFF}",
                f"SETA 123",
                f"CALL add16",
                f"HALT",
                *addlines,
            ]))
            cpu = CPUCore(memory)
            rununtilhalt(cpu)
            calculated = (cpu.ram[cpu.pc[0]] << 8) + cpu.ram[cpu.pc[0] + 1]
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


def verifyadd32(only: Optional[str], full: bool) -> None:
    if only is not None and only != "add32":
        return

    print("Verifying add32...")
    print("0% complete...")

    with open("lib/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/math/add.S", "r") as fp:
        addlines = fp.readlines()

    cycles = 0
    instructions = 0
    count = 0
    for x in range(0, 2**32, 80904192 if full else 809041923):
        for y in range(0, 2**32, 61472769 if full else 122945537):
            memory = getmemory(os.linesep.join([
                *initlines,
                f"PUSHI {x & 0xFF}",
                f"PUSHI {(x >> 8) & 0xFF}",
                f"PUSHI {(x >> 16) & 0xFF}",
                f"PUSHI {(x >> 24) & 0xFF}",
                f"PUSHI {y & 0xFF}",
                f"PUSHI {(y >> 8) & 0xFF}",
                f"PUSHI {(y >> 16) & 0xFF}",
                f"PUSHI {(y >> 24) & 0xFF}",
                f"SETA 123",
                f"CALL add32",
                f"HALT",
                *addlines,
            ]))
            cpu = CPUCore(memory)
            rununtilhalt(cpu)
            calculated = (
                (cpu.ram[cpu.pc[0]] << 24) +
                (cpu.ram[cpu.pc[0] + 1] << 16) +
                (cpu.ram[cpu.pc[0] + 2] << 8) +
                cpu.ram[cpu.pc[0] + 3]
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


def verifyabs(only: Optional[str], full: bool) -> None:
    if only is not None and only != "abs":
        return

    print("Verifying abs...")

    with open("lib/init.S", "r") as fp:
        initlines = fp.readlines()
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
            f"SETA {x}",
            f"CALL abs",
            f"HALT",
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


def verifyabs16(only: Optional[str], full: bool) -> None:
    if only is not None and only != "abs16":
        return

    print("Verifying abs16...")
    print("0% complete...")

    with open("lib/init.S", "r") as fp:
        initlines = fp.readlines()
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
            f"PUSHI {xbin & 0xFF}",
            f"PUSHI {(xbin >> 8) & 0xFF}",
            f"SETA 123",
            f"CALL abs16",
            f"HALT",
            *neglines,
            *abslines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)
        calculated = bintoint16(
            (cpu.ram[cpu.pc[0]] << 8) + cpu.ram[cpu.pc[0] + 1]
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


def verifyabs32(only: Optional[str], full: bool) -> None:
    if only is not None and only != "abs32":
        return

    print("Verifying abs32...")
    print("0% complete...")

    with open("lib/init.S", "r") as fp:
        initlines = fp.readlines()
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
            f"PUSHI {xbin & 0xFF}",
            f"PUSHI {(xbin >> 8) & 0xFF}",
            f"PUSHI {(xbin >> 16) & 0xFF}",
            f"PUSHI {(xbin >> 24) & 0xFF}",
            f"SETA 123",
            f"CALL abs32",
            f"HALT",
            *neglines,
            *abslines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)
        calculated = bintoint32(
            (cpu.ram[cpu.pc[0]] << 24) +
            (cpu.ram[cpu.pc[0] + 1] << 16) +
            (cpu.ram[cpu.pc[0] + 2] << 8) +
            cpu.ram[cpu.pc[0] + 3]
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
            f"{CLEAR_LINE}{int(((x + (2 **31)) * 100) / (2**32))}% complete..."
        )

    print(f"{CLEAR_LINE}Average cycles for abs32: {int(cycles/count)}")
    print(f"Average instructions for abs32: {int(instructions/count)}")


def verifyucmp(only: Optional[str], full: bool) -> None:
    if only is not None and only != "ucmp":
        return

    print("Verifying ucmp...")
    print("0% complete...")

    with open("lib/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/math/cmp.S", "r") as fp:
        cmplines = fp.readlines()

    cycles = 0
    instructions = 0
    count = 0
    for a in range(0, 256, 5 if full else 11):
        for b in range(0, 256, 3 if full else 7):
            memory = getmemory(os.linesep.join([
                *initlines,
                f"PUSHI {a}",
                f"PUSHI {b}",
                f"CALL ucmp",
                f"HALT",
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
                cpu.ram[cpu.pc[0] + 1] == a,
                f"ucmp changed stack value from {a} "
                + f"to {cpu.ram[cpu.pc[0] + 1]}!",
            )
            _assert(
                cpu.ram[cpu.pc[0]] == b,
                f"ucmp changed stack value from {b} to {cpu.ram[cpu.pc[0]]}!",
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


def verifyucmp16(only: Optional[str], full: bool) -> None:
    if only is not None and only != "ucmp16":
        return

    print("Verifying ucmp16...")
    print("0% complete...")

    with open("lib/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/math/cmp.S", "r") as fp:
        cmplines = fp.readlines()

    cycles = 0
    instructions = 0
    count = 0
    for a in range(0, 65536, 1281 if full else 2817):
        for b in range(0, 65536, 767 if full else 1791):
            memory = getmemory(os.linesep.join([
                *initlines,
                f"PUSHI {a & 0xFF}",
                f"PUSHI {(a >> 8) & 0xFF}",
                f"PUSHI {b & 0xFF}",
                f"PUSHI {(b >> 8) & 0xFF}",
                f"CALL ucmp16",
                f"HALT",
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
            astack = ((cpu.ram[cpu.pc[0] + 2] << 8) + cpu.ram[cpu.pc[0] + 3])
            _assert(
                astack == a,
                f"ucmp16 changed stack value from {a} to {astack}!",
            )
            bstack = ((cpu.ram[cpu.pc[0]] << 8) + cpu.ram[cpu.pc[0] + 1])
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


def verifyucmp32(only: Optional[str], full: bool) -> None:
    if only is not None and only != "ucmp32":
        return

    print("Verifying ucmp32...")
    print("0% complete...")

    with open("lib/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/math/cmp.S", "r") as fp:
        cmplines = fp.readlines()

    def _verify_ucmp32(a: int, b: int) -> CPUCore:
        memory = getmemory(os.linesep.join([
            *initlines,
            f"PUSHI {a & 0xFF}",
            f"PUSHI {(a >> 8) & 0xFF}",
            f"PUSHI {(a >> 16) & 0xFF}",
            f"PUSHI {(a >> 24) & 0xFF}",
            f"PUSHI {b & 0xFF}",
            f"PUSHI {(b >> 8) & 0xFF}",
            f"PUSHI {(b >> 16) & 0xFF}",
            f"PUSHI {(b >> 24) & 0xFF}",
            f"CALL ucmp32",
            f"HALT",
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
            (cpu.ram[cpu.pc[0] + 4] << 24) +
            (cpu.ram[cpu.pc[0] + 5] << 16) +
            (cpu.ram[cpu.pc[0] + 6] << 8) +
            cpu.ram[cpu.pc[0] + 7]
        )
        _assert(
            astack == a,
            f"ucmp32 changed stack value from {a} to {astack}!",
        )
        bstack = (
            (cpu.ram[cpu.pc[0]] << 24) +
            (cpu.ram[cpu.pc[0] + 1] << 16) +
            (cpu.ram[cpu.pc[0] + 2] << 8) +
            cpu.ram[cpu.pc[0] + 3]
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


def verifyumin(only: Optional[str], full: bool) -> None:
    if only is not None and only != "umin":
        return

    print("Verifying umin...")
    print("0% complete...")

    with open("lib/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/math/cmp.S", "r") as fp:
        cmplines = fp.readlines()

    cycles = 0
    instructions = 0
    count = 0
    for a in range(0, 256, 5 if full else 11):
        for b in range(0, 256, 3 if full else 7):
            memory = getmemory(os.linesep.join([
                *initlines,
                f"PUSHI {a}",
                f"PUSHI {b}",
                f"CALL umin",
                f"HALT",
                *cmplines,
            ]))
            cpu = CPUCore(memory)
            rununtilhalt(cpu)
            answer = min(a, b)
            _assert(
                cpu.ram[cpu.pc[0] + 1] == a,
                f"umin changed stack value from {a} "
                + f"to {cpu.ram[cpu.pc[0] + 1]}!",
            )
            _assert(
                cpu.ram[cpu.pc[0]] == b,
                f"umin changed stack value from {b} to {cpu.ram[cpu.pc[0]]}!",
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


def verifyumin16(only: Optional[str], full: bool) -> None:
    if only is not None and only != "umin16":
        return

    print("Verifying umin16...")
    print("0% complete...")

    with open("lib/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/math/cmp.S", "r") as fp:
        cmplines = fp.readlines()

    cycles = 0
    instructions = 0
    count = 0
    for a in range(0, 65536, 1281 if full else 2817):
        for b in range(0, 65536, 767 if full else 1791):
            memory = getmemory(os.linesep.join([
                *initlines,
                f"PUSHI {a & 0xFF}",
                f"PUSHI {(a >> 8) & 0xFF}",
                f"PUSHI {b & 0xFF}",
                f"PUSHI {(b >> 8) & 0xFF}",
                f"SETA 123",
                f"CALL umin16",
                f"HALT",
                *cmplines,
            ]))
            cpu = CPUCore(memory)
            rununtilhalt(cpu)
            answer = min(a, b)
            _assert(
                cpu.a == 123,
                f"umin16 changed accumulator value from {123} to {cpu.a}!",
            )
            result = ((cpu.ram[cpu.pc[0]] << 8) + cpu.ram[cpu.pc[0] + 1])
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


def verifyumin32(only: Optional[str], full: bool) -> None:
    if only is not None and only != "umin32":
        return

    print("Verifying umin32...")
    print("0% complete...")

    with open("lib/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/math/cmp.S", "r") as fp:
        cmplines = fp.readlines()

    def _verify_umin32(a: int, b: int) -> CPUCore:
        memory = getmemory(os.linesep.join([
            *initlines,
            f"PUSHI {a & 0xFF}",
            f"PUSHI {(a >> 8) & 0xFF}",
            f"PUSHI {(a >> 16) & 0xFF}",
            f"PUSHI {(a >> 24) & 0xFF}",
            f"PUSHI {b & 0xFF}",
            f"PUSHI {(b >> 8) & 0xFF}",
            f"PUSHI {(b >> 16) & 0xFF}",
            f"PUSHI {(b >> 24) & 0xFF}",
            f"SETA 123",
            f"CALL umin32",
            f"HALT",
            *cmplines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)
        answer = min(a, b)
        result = (
            (cpu.ram[cpu.pc[0]] << 24) +
            (cpu.ram[cpu.pc[0] + 1] << 16) +
            (cpu.ram[cpu.pc[0] + 2] << 8) +
            cpu.ram[cpu.pc[0] + 3]
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


def verifyumax(only: Optional[str], full: bool) -> None:
    if only is not None and only != "umax":
        return

    print("Verifying umax...")
    print("0% complete...")

    with open("lib/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/math/cmp.S", "r") as fp:
        cmplines = fp.readlines()

    cycles = 0
    instructions = 0
    count = 0
    for a in range(0, 256, 5 if full else 11):
        for b in range(0, 256, 3 if full else 7):
            memory = getmemory(os.linesep.join([
                *initlines,
                f"PUSHI {a}",
                f"PUSHI {b}",
                f"CALL umax",
                f"HALT",
                *cmplines,
            ]))
            cpu = CPUCore(memory)
            rununtilhalt(cpu)
            answer = max(a, b)
            _assert(
                cpu.ram[cpu.pc[0] + 1] == a,
                f"umax changed stack value from {a} "
                + f"to {cpu.ram[cpu.pc[0] + 1]}!",
            )
            _assert(
                cpu.ram[cpu.pc[0]] == b,
                f"umax changed stack value from {b} to {cpu.ram[cpu.pc[0]]}!",
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


def verifyumax16(only: Optional[str], full: bool) -> None:
    if only is not None and only != "umax16":
        return

    print("Verifying umax16...")
    print("0% complete...")

    with open("lib/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/math/cmp.S", "r") as fp:
        cmplines = fp.readlines()

    cycles = 0
    instructions = 0
    count = 0
    for a in range(0, 65536, 1281 if full else 2817):
        for b in range(0, 65536, 767 if full else 1791):
            memory = getmemory(os.linesep.join([
                *initlines,
                f"PUSHI {a & 0xFF}",
                f"PUSHI {(a >> 8) & 0xFF}",
                f"PUSHI {b & 0xFF}",
                f"PUSHI {(b >> 8) & 0xFF}",
                f"SETA 123",
                f"CALL umax16",
                f"HALT",
                *cmplines,
            ]))
            cpu = CPUCore(memory)
            rununtilhalt(cpu)
            answer = max(a, b)
            _assert(
                cpu.a == 123,
                f"umax16 changed accumulator value from {123} to {cpu.a}!",
            )
            result = ((cpu.ram[cpu.pc[0]] << 8) + cpu.ram[cpu.pc[0] + 1])
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


def verifyumax32(only: Optional[str], full: bool) -> None:
    if only is not None and only != "umax32":
        return

    print("Verifying umax32...")
    print("0% complete...")

    with open("lib/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/math/cmp.S", "r") as fp:
        cmplines = fp.readlines()

    def _verify_umax32(a: int, b: int) -> CPUCore:
        memory = getmemory(os.linesep.join([
            *initlines,
            f"PUSHI {a & 0xFF}",
            f"PUSHI {(a >> 8) & 0xFF}",
            f"PUSHI {(a >> 16) & 0xFF}",
            f"PUSHI {(a >> 24) & 0xFF}",
            f"PUSHI {b & 0xFF}",
            f"PUSHI {(b >> 8) & 0xFF}",
            f"PUSHI {(b >> 16) & 0xFF}",
            f"PUSHI {(b >> 24) & 0xFF}",
            f"SETA 123",
            f"CALL umax32",
            f"HALT",
            *cmplines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)
        answer = max(a, b)
        result = (
            (cpu.ram[cpu.pc[0]] << 24) +
            (cpu.ram[cpu.pc[0] + 1] << 16) +
            (cpu.ram[cpu.pc[0] + 2] << 8) +
            cpu.ram[cpu.pc[0] + 3]
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


def verifymathneg(only: Optional[str], full: bool) -> None:
    if only is not None and only != "mathneg":
        return

    print("Verifying neg...")
    print("0% complete...")

    with open("lib/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/math/neg.S", "r") as fp:
        neglines = fp.readlines()

    cycles = 0
    instructions = 0
    count = 0
    for x in range(-127, 128):
        memory = getmemory(os.linesep.join([
            *initlines,
            f"PUSHI {x}",
            f"SETA 123",
            f"CALL neg",
            f"HALT",
            *neglines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)
        calculated = bintoint(cpu.ram[cpu.pc[0]])
        real = -x
        _assert(
            cpu.a == 123,
            f"neg changed A register from 123 to {cpu.a}!",
        )
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


def verifyneg16(only: Optional[str], full: bool) -> None:
    if only is not None and only != "neg16":
        return

    print("Verifying neg16...")
    print("0% complete...")

    with open("lib/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/math/neg.S", "r") as fp:
        neglines = fp.readlines()

    cycles = 0
    instructions = 0
    count = 0
    for x in range(-32767, 32768, 79 if full else 763):
        xbin = inttobin16(x)
        memory = getmemory(os.linesep.join([
            *initlines,
            f"PUSHI {xbin & 0xFF}",
            f"PUSHI {(xbin >> 8) & 0xFF}",
            f"SETA 123",
            f"CALL neg16",
            f"HALT",
            *neglines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)
        calculated = bintoint16(
            (cpu.ram[cpu.pc[0]] << 8) + cpu.ram[cpu.pc[0] + 1]
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


def verifyneg32(only: Optional[str], full: bool) -> None:
    if only is not None and only != "neg32":
        return

    print("Verifying neg32...")
    print("0% complete...")

    with open("lib/init.S", "r") as fp:
        initlines = fp.readlines()
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
            f"PUSHI {xbin & 0xFF}",
            f"PUSHI {(xbin >> 8) & 0xFF}",
            f"PUSHI {(xbin >> 16) & 0xFF}",
            f"PUSHI {(xbin >> 24) & 0xFF}",
            f"SETA 123",
            f"CALL neg32",
            f"HALT",
            *neglines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)
        calculated = bintoint32(
            (cpu.ram[cpu.pc[0]] << 24) +
            (cpu.ram[cpu.pc[0] + 1] << 16) +
            (cpu.ram[cpu.pc[0] + 2] << 8) +
            cpu.ram[cpu.pc[0] + 3]
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
            f"{CLEAR_LINE}{int(((x + (2 **31)) * 100) / (2**32))}% complete..."
        )

    print(f"{CLEAR_LINE}Average cycles for neg32: {int(cycles/count)}")
    print(f"Average instructions for neg32: {int(instructions/count)}")


def verifystrlen(only: Optional[str], full: bool) -> None:
    if only is not None and only != "strlen":
        return

    print("Verifying strlen...")

    with open("lib/init.S", "r") as fp:
        initlines = fp.readlines()
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
            "LNGJUMP code",
            ".org 0x1000",
            "string:",
            *[f".char {c!r}" for c in string],
            ".byte 0x00",
            "code:",
            "SWAP",
            "SETPC string",
            "SWAP",
            "PUSHSPC",
            "CALL strlen",
            "HALT",
            *liblines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)
        stack_input = (cpu.ram[cpu.pc[0]] << 8) + cpu.ram[cpu.pc[0] + 1]
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


def verifystrcpy(only: Optional[str], full: bool) -> None:
    if only is not None and only != "strcpy":
        return

    print("Verifying strcpy...")

    with open("lib/init.S", "r") as fp:
        initlines = fp.readlines()
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
            "LNGJUMP code",
            ".org 0x1000",
            "string:",
            *[f".char {c!r}" for c in string],
            ".byte 0x00",
            "code:",
            "SWAP",
            "SETPC string",
            "SWAP",
            "PUSHSPC",
            "PUSHI 0x00",
            "PUSHI 0x20",
            "SETA 123",
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
        stack_dest = (cpu.ram[cpu.pc[0]] << 8) + cpu.ram[cpu.pc[0] + 1]
        stack_source = (cpu.ram[cpu.pc[0] + 2] << 8) + cpu.ram[cpu.pc[0] + 3]
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


def verifystrcat(only: Optional[str], full: bool) -> None:
    if only is not None and only != "strcat":
        return

    print("Verifying strcat...")

    with open("lib/init.S", "r") as fp:
        initlines = fp.readlines()
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
                "LNGJUMP code",
                ".org 0x1000",
                "concatenation:",
                *[f".char {c!r}" for c in concatenation],
                ".byte 0x00",
                ".org 0x2000",
                "string:",
                *[f".char {c!r}" for c in string],
                ".byte 0x00",
                ".org 0x3000",
                "code:",
                "SWAP",
                "SETPC concatenation",
                "SWAP",
                "PUSHSPC",
                "SWAP",
                "SETPC string",
                "SWAP",
                "PUSHSPC",
                "SETA 123",
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
            stack_dest = (cpu.ram[cpu.pc[0]] << 8) + cpu.ram[cpu.pc[0] + 1]
            stack_source = (
                (cpu.ram[cpu.pc[0] + 2] << 8) + cpu.ram[cpu.pc[0] + 3]
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


def verifystrcmp(only: Optional[str], full: bool) -> None:
    if only is not None and only != "strcmp":
        return

    print("Verifying strcmp...")

    with open("lib/init.S", "r") as fp:
        initlines = fp.readlines()
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
                "LNGJUMP code",
                ".org 0x1000",
                "source:",
                *[f".char {c!r}" for c in source],
                ".byte 0x00",
                ".org 0x2000",
                "destination:",
                *[f".char {c!r}" for c in destination],
                ".byte 0x00",
                ".org 0x3000",
                "code:",
                "SWAP",
                "SETPC source",
                "SWAP",
                "PUSHSPC",
                "SWAP",
                "SETPC destination",
                "SWAP",
                "PUSHSPC",
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
            stack_dest = (cpu.ram[cpu.pc[0]] << 8) + cpu.ram[cpu.pc[0] + 1]
            stack_source = (
                (cpu.ram[cpu.pc[0] + 2] << 8) + cpu.ram[cpu.pc[0] + 3]
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


def verifyitoa(only: Optional[str], full: bool) -> None:
    if only is not None and only != "itoa":
        return

    print("Verifying itoa...")
    print("0% complete...")

    with open("lib/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/math/divide.S", "r") as fp:
        dividelines = fp.readlines()
    with open("lib/conversion/itoa.S", "r") as fp:
        itoalines = fp.readlines()

    cycles = 0
    instructions = 0
    count = 0
    for x in range(-128, 128, 1 if full else 7):
        memory = getmemory(os.linesep.join([
            *initlines,
            f"PUSHI 0x00",
            f"PUSHI 0x10",
            f"SETA {x}",
            f"CALL itoa",
            f"HALT",
            *itoalines,
            *dividelines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        _assert(
            bintoint(cpu.a) == x,
            f"itoa changed A register from {x} to {cpu.a}!",
        )
        stack_input = (cpu.ram[cpu.pc[0]] << 8) + cpu.ram[cpu.pc[0] + 1]
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
        "-o",
        "--only",
        help="Only run this test.",
        type=str,
        default=None,
    )
    args = parser.parse_args()
    only = args.only.lower() if args.only else None

    # Verify assembler errors
    verifyassembler(only, args.full)

    # Raw instruction verification
    verifyloadi(only, args.full)
    verifyaddi(only, args.full)
    verifyseta(only, args.full)
    verifysetpc(only, args.full)
    verifyaddpc(only, args.full)
    verifyneg(only, args.full)
    verifyaddpci(only, args.full)
    verifysubpci(only, args.full)

    # Math library verification
    verifymathadd(only, args.full)
    verifyadd16(only, args.full)
    verifyadd32(only, args.full)
    verifyumult(only, args.full)
    verifyudiv(only, args.full)
    verifyabs(only, args.full)
    verifyabs16(only, args.full)
    verifyabs32(only, args.full)
    verifyucmp(only, args.full)
    verifyucmp16(only, args.full)
    verifyucmp32(only, args.full)
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
