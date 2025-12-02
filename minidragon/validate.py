import argparse
import os
import struct
import textwrap
from itertools import chain
from typing import Any, Container, Dict, List, Optional

from .compiler import CompilerSettings, Compiler, Sections
from .core import CPUCore, assemble, disassemble
from .exception import (
    InvalidInstructionException,
    ParameterOutOfRangeException,
    CodeOutOfRangeException,
)
from .util import bintoint, hexstr, sanitize


CLEAR_LINE = "\033[F\033[K"
BACK_AND_CLEAR_LINE = "\033[F\033[K\033[F"


verbose: bool = False
highlight_changes: bool = False
print_code: bool = False
settings: CompilerSettings = CompilerSettings()


def parse_and_compile_module(module: str, code: str, settings: CompilerSettings) -> Sections:
    compiler = Compiler(settings)
    return compiler.parse_and_compile_module(module, code)


def _assert(statement: bool, msg: str) -> None:
    assert statement, msg


def getlines(instr: str) -> List[str]:
    lines: List[str] = []

    for line in instr.split(os.linesep):
        line = sanitize(line)
        if line:
            lines.append(line)
    return lines


def getmemory(instr: str) -> List[int]:
    if print_code:
        lines = instr.split(os.linesep)
        lines = [line for line in lines if line.strip()]
        print("Assembly Printout")
        print("=================")
        print(os.linesep.join(lines))
        print("")

    memory = [0] * 0x10000
    assembled = assemble(getlines(instr))
    for loc, intval in assembled:
        memory[loc] = intval
    return memory


def rununtilhalt(cpu: CPUCore) -> None:
    while True:
        if verbose:
            cpu.print(highlight_changes)
            cpu.dump(highlight_changes)
            cpu.mark()
            print("")
        if cpu.mnemonic == "HALT":
            return
        cpu.tick()


def assertmemory(name: str, old: List[int], new: List[int]) -> None:
    # Only the bits of memory that are considered ROM.
    for i in range(0, 0x4000):
        if old[i] != new[i]:
            _assert(False, f"{name} changed memory address {hexstr(i, 4)} from {hexstr(old[i], 2)} to {hexstr(new[i], 2)}!")


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


def bintochar(binary: int) -> str:
    if binary < 0 or binary > 255:
        raise Exception(f"Invalid non-ascii character conversion {hexstr(binary, 2)}")
    return chr(binary)


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


def verifymult8(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "mult8" not in only and "mathlib" not in only:
        return

    print("Verifying mult8...")
    print("0% complete...")

    with open("lib/runtime/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/runtime/start.S", "r") as fp:
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
                "CALL mult8",
                "HALT",
                *multiplylines,
                *addlines,
            ]))
            cpu = CPUCore(memory)
            rununtilhalt(cpu)
            _assert(
                cpu.a == x * y,
                f"Failed to mult8 {x} by {y}, "
                + f"got {cpu.a} instead of {x * y}!",
            )
            cycles += cpu.cycles
            instructions += cpu.ticks
            count += 1

        print(f"{CLEAR_LINE}{int((x * 100) / 256)}% complete...")
    print(f"{CLEAR_LINE}Average cycles for mult8: {int(cycles/count)}")
    print(f"Average instructions for mult8: {int(instructions/count)}")


def verifymult16(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "mult16" not in only and "mathlib" not in only:
        return

    print("Verifying mult16...")
    print("0% complete...")

    with open("lib/runtime/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/runtime/start.S", "r") as fp:
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

    with open("lib/runtime/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/runtime/start.S", "r") as fp:
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


def verifyudiv8(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "udiv8" not in only and "mathlib" not in only:
        return

    print("Verifying udiv8...")
    print("0% complete...")

    with open("lib/runtime/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/runtime/start.S", "r") as fp:
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
                "CALL udiv8",
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
                f"Failed to udiv8 {dividend} by {divisor}, "
                + f"got {cpu.a} instead of {dividend // divisor}!",
            )
            _assert(
                remainder == dividend % divisor,
                f"Failed to udiv8 {dividend} by {divisor}, "
                + f"got {remainder} instead of {dividend % divisor}!",
            )
            _assert(
                cpu.a == 123,
                f"udiv8 changed A register from 123 to {cpu.a}!",
            )
            cycles += cpu.cycles
            instructions += cpu.ticks
            count += 1

        print(f"{CLEAR_LINE}{int((dividend * 100) / 256)}% complete...")
    print(f"{CLEAR_LINE}Average cycles for udiv8: {int(cycles/count)}")
    print(f"Average instructions for udiv8: {int(instructions/count)}")


def verifyudiv16(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "udiv16" not in only and "mathlib" not in only:
        return

    print("Verifying udiv16...")
    print("0% complete...")

    with open("lib/runtime/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/runtime/start.S", "r") as fp:
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

    with open("lib/runtime/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/runtime/start.S", "r") as fp:
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


def verifylshift8(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "lshift8" not in only and "mathlib" not in only:
        return

    print("Verifying lshift8...")
    print("0% complete...")

    with open("lib/runtime/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/runtime/start.S", "r") as fp:
        initlines += fp.readlines()
    with open("lib/math/shift.S", "r") as fp:
        shiftlines = fp.readlines()

    cycles = 0
    instructions = 0
    count = 0
    for x in range(0, 256, 5 if full else 11):
        for y in range(0, 8):
            memory = getmemory(os.linesep.join([
                *initlines,
                "main:",
                f"PUSHI {x}",
                f"LOADI {y}",
                "CALL lshift8",
                "HALT",
                *shiftlines,
            ]))
            cpu = CPUCore(memory)
            rununtilhalt(cpu)
            calculated = cpu.a
            real = (x << y) & 0xFF
            _assert(
                real == calculated,
                f"Failed to {x} << {y}, "
                + f"got {calculated} instead of {real}!",
            )
            cycles += cpu.cycles
            instructions += cpu.ticks
            count += 1

        print(f"{CLEAR_LINE}{int((x * 100) / 256)}% complete...")
    print(f"{CLEAR_LINE}Average cycles for lshift8: {int(cycles/count)}")
    print(f"Average instructions for lshift8: {int(instructions/count)}")


def verifylshift16(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "lshift16" not in only and "mathlib" not in only:
        return

    print("Verifying lshift16...")
    print("0% complete...")

    with open("lib/runtime/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/runtime/start.S", "r") as fp:
        initlines += fp.readlines()
    with open("lib/math/shift.S", "r") as fp:
        shiftlines = fp.readlines()

    cycles = 0
    instructions = 0
    count = 0
    for x in range(0, 65536, 1234 if full else 12345):
        for y in range(0, 16):
            memory = getmemory(os.linesep.join([
                *initlines,
                "main:",
                f"PUSHI {x & 0xFF}",
                f"PUSHI {(x >> 8) & 0xFF}",
                f"LOADI {y}",
                "CALL lshift16",
                "HALT",
                *shiftlines,
            ]))
            cpu = CPUCore(memory)
            rununtilhalt(cpu)
            calculated = (cpu.ram[cpu.pc] << 8) + cpu.ram[cpu.pc + 1]
            real = (x << y) & 0xFFFF
            _assert(
                real == calculated,
                f"Failed to {x} << {y}, "
                + f"got {calculated} instead of {real}!",
            )
            cycles += cpu.cycles
            instructions += cpu.ticks
            count += 1

        print(f"{CLEAR_LINE}{int((x * 100) / 65536)}% complete...")
    print(f"{CLEAR_LINE}Average cycles for lshift16: {int(cycles/count)}")
    print(f"Average instructions for lshift16: {int(instructions/count)}")


def verifylshift32(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "lshift32" not in only and "mathlib" not in only:
        return

    print("Verifying lshift32...")
    print("0% complete...")

    with open("lib/runtime/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/runtime/start.S", "r") as fp:
        initlines += fp.readlines()
    with open("lib/math/shift.S", "r") as fp:
        shiftlines = fp.readlines()

    cycles = 0
    instructions = 0
    count = 0
    for x in range(0, 2**32, 80904192 if full else 809041923):
        for y in range(0, 32):
            memory = getmemory(os.linesep.join([
                *initlines,
                "main:",
                f"PUSHI {x & 0xFF}",
                f"PUSHI {(x >> 8) & 0xFF}",
                f"PUSHI {(x >> 16) & 0xFF}",
                f"PUSHI {(x >> 24) & 0xFF}",
                f"LOADI {y}",
                "CALL lshift32",
                "HALT",
                *shiftlines,
            ]))
            cpu = CPUCore(memory)
            rununtilhalt(cpu)
            calculated = (
                (cpu.ram[cpu.pc] << 24) +
                (cpu.ram[cpu.pc + 1] << 16) +
                (cpu.ram[cpu.pc + 2] << 8) +
                cpu.ram[cpu.pc + 3]
            )
            real = (x << y) & 0xFFFFFFFF
            _assert(
                real == calculated,
                f"Failed to {x} << {y}, "
                + f"got {calculated} instead of {real}!",
            )
            cycles += cpu.cycles
            instructions += cpu.ticks
            count += 1

        print(f"{CLEAR_LINE}{int((x * 100) / (2**32))}% complete...")
    print(f"{CLEAR_LINE}Average cycles for lshift32: {int(cycles/count)}")
    print(f"Average instructions for lshift32: {int(instructions/count)}")


def verifyrshift8(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "rshift8" not in only and "mathlib" not in only:
        return

    print("Verifying rshift8...")
    print("0% complete...")

    with open("lib/runtime/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/runtime/start.S", "r") as fp:
        initlines += fp.readlines()
    with open("lib/math/shift.S", "r") as fp:
        shiftlines = fp.readlines()

    cycles = 0
    instructions = 0
    count = 0
    for x in range(0, 256, 5 if full else 11):
        for y in range(0, 8):
            memory = getmemory(os.linesep.join([
                *initlines,
                "main:",
                f"PUSHI {x}",
                f"LOADI {y}",
                "CALL rshift8",
                "HALT",
                *shiftlines,
            ]))
            cpu = CPUCore(memory)
            rununtilhalt(cpu)
            calculated = cpu.a
            real = (x >> y) & 0xFF
            _assert(
                real == calculated,
                f"Failed to {x} << {y}, "
                + f"got {calculated} instead of {real}!",
            )
            cycles += cpu.cycles
            instructions += cpu.ticks
            count += 1

        print(f"{CLEAR_LINE}{int((x * 100) / 256)}% complete...")
    print(f"{CLEAR_LINE}Average cycles for rshift8: {int(cycles/count)}")
    print(f"Average instructions for rshift8: {int(instructions/count)}")


def verifyrshift16(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "rshift16" not in only and "mathlib" not in only:
        return

    print("Verifying rshift16...")
    print("0% complete...")

    with open("lib/runtime/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/runtime/start.S", "r") as fp:
        initlines += fp.readlines()
    with open("lib/math/shift.S", "r") as fp:
        shiftlines = fp.readlines()

    cycles = 0
    instructions = 0
    count = 0
    for x in range(0, 65536, 1234 if full else 12345):
        for y in range(0, 16):
            memory = getmemory(os.linesep.join([
                *initlines,
                "main:",
                f"PUSHI {x & 0xFF}",
                f"PUSHI {(x >> 8) & 0xFF}",
                f"LOADI {y}",
                "CALL rshift16",
                "HALT",
                *shiftlines,
            ]))
            cpu = CPUCore(memory)
            rununtilhalt(cpu)
            calculated = (cpu.ram[cpu.pc] << 8) + cpu.ram[cpu.pc + 1]
            real = (x >> y) & 0xFFFF
            _assert(
                real == calculated,
                f"Failed to {x} << {y}, "
                + f"got {calculated} instead of {real}!",
            )
            cycles += cpu.cycles
            instructions += cpu.ticks
            count += 1

        print(f"{CLEAR_LINE}{int((x * 100) / 65536)}% complete...")
    print(f"{CLEAR_LINE}Average cycles for rshift16: {int(cycles/count)}")
    print(f"Average instructions for rshift16: {int(instructions/count)}")


def verifyrshift32(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "rshift32" not in only and "mathlib" not in only:
        return

    print("Verifying rshift32...")
    print("0% complete...")

    with open("lib/runtime/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/runtime/start.S", "r") as fp:
        initlines += fp.readlines()
    with open("lib/math/shift.S", "r") as fp:
        shiftlines = fp.readlines()

    cycles = 0
    instructions = 0
    count = 0
    for x in range(0, 2**32, 80904192 if full else 809041923):
        for y in range(0, 32):
            memory = getmemory(os.linesep.join([
                *initlines,
                "main:",
                f"PUSHI {x & 0xFF}",
                f"PUSHI {(x >> 8) & 0xFF}",
                f"PUSHI {(x >> 16) & 0xFF}",
                f"PUSHI {(x >> 24) & 0xFF}",
                f"LOADI {y}",
                "CALL rshift32",
                "HALT",
                *shiftlines,
            ]))
            cpu = CPUCore(memory)
            rununtilhalt(cpu)
            calculated = (
                (cpu.ram[cpu.pc] << 24) +
                (cpu.ram[cpu.pc + 1] << 16) +
                (cpu.ram[cpu.pc + 2] << 8) +
                cpu.ram[cpu.pc + 3]
            )
            real = (x >> y) & 0xFFFFFFFF
            _assert(
                real == calculated,
                f"Failed to {x} << {y}, "
                + f"got {calculated} instead of {real}!",
            )
            cycles += cpu.cycles
            instructions += cpu.ticks
            count += 1

        print(f"{CLEAR_LINE}{int((x * 100) / (2**32))}% complete...")
    print(f"{CLEAR_LINE}Average cycles for rshift32: {int(cycles/count)}")
    print(f"Average instructions for rshift32: {int(instructions/count)}")


def verifyadd8(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "add8" not in only and "mathlib" not in only:
        return

    print("Verifying add8...")
    print("0% complete...")

    with open("lib/runtime/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/runtime/start.S", "r") as fp:
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
                "CALL add8",
                "HALT",
                *addlines,
            ]))
            cpu = CPUCore(memory)
            rununtilhalt(cpu)
            calculated = cpu.a
            real = (x + y) & 0xFF
            _assert(
                real == calculated,
                f"Failed to add8 {x} and {y}, "
                + f"got {calculated} instead of {real}!",
            )
            cycles += cpu.cycles
            instructions += cpu.ticks
            count += 1

        print(f"{CLEAR_LINE}{int((x * 100) / 256)}% complete...")
    print(f"{CLEAR_LINE}Average cycles for add8: {int(cycles/count)}")
    print(f"Average instructions for add8: {int(instructions/count)}")


def verifyadd16(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "add16" not in only and "mathlib" not in only:
        return

    print("Verifying add16...")
    print("0% complete...")

    with open("lib/runtime/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/runtime/start.S", "r") as fp:
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

    with open("lib/runtime/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/runtime/start.S", "r") as fp:
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


def verifyabs8(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "abs8" not in only and "mathlib" not in only:
        return

    print("Verifying abs8...")

    with open("lib/runtime/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/runtime/start.S", "r") as fp:
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
            "CALL abs8",
            "HALT",
            *neglines,
            *abslines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)
        _assert(
            cpu.a == abs(x),
            f"Failed to abs8({x}), got {cpu.a} instead of {x}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    print(f"Average cycles for abs8: {int(cycles/count)}")
    print(f"Average instructions for abs8: {int(instructions/count)}")


def verifyabs16(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "abs16" not in only and "mathlib" not in only:
        return

    print("Verifying abs16...")
    print("0% complete...")

    with open("lib/runtime/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/runtime/start.S", "r") as fp:
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

    with open("lib/runtime/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/runtime/start.S", "r") as fp:
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


def verifyucmp8(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "ucmp8" not in only and "mathlib" not in only:
        return

    print("Verifying ucmp8...")
    print("0% complete...")

    with open("lib/runtime/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/runtime/start.S", "r") as fp:
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
                "CALL ucmp8",
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
                f"ucmp8 changed stack value from {a} "
                + f"to {cpu.ram[cpu.pc + 1]}!",
            )
            _assert(
                cpu.ram[cpu.pc] == b,
                f"ucmp8 changed stack value from {b} to {cpu.ram[cpu.pc]}!",
            )
            _assert(
                bintoint(cpu.a) == answer,
                f"Failed to ucmp8({a}, {b}), "
                + f"got {bintoint(cpu.a)} instead of {answer}!",
            )
            cycles += cpu.cycles
            instructions += cpu.ticks
            count += 1

        print(f"{CLEAR_LINE}{int((a * 100) / 256)}% complete...")
    print(f"{CLEAR_LINE}Average cycles for ucmp8: {int(cycles/count)}")
    print(f"Average instructions for ucmp8: {int(instructions/count)}")


def verifyucmp16(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "ucmp16" not in only and "mathlib" not in only:
        return

    print("Verifying ucmp16...")
    print("0% complete...")

    with open("lib/runtime/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/runtime/start.S", "r") as fp:
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

    with open("lib/runtime/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/runtime/start.S", "r") as fp:
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


def verifycmp8(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "cmp8" not in only and "mathlib" not in only:
        return

    print("Verifying cmp8...")
    print("0% complete...")

    with open("lib/runtime/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/runtime/start.S", "r") as fp:
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
                "CALL cmp8",
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
                f"cmp8 changed stack value from {a} "
                + f"to {bintoint(cpu.ram[cpu.pc + 1])}!",
            )
            _assert(
                bintoint(cpu.ram[cpu.pc]) == b,
                f"cmp8 changed stack value from {b} to {bintoint(cpu.ram[cpu.pc])}!",
            )
            _assert(
                bintoint(cpu.a) == answer,
                f"Failed to cmp8({a}, {b}), "
                + f"got {bintoint(cpu.a)} instead of {answer}!",
            )
            cycles += cpu.cycles
            instructions += cpu.ticks
            count += 1

        print(f"{CLEAR_LINE}{int(((a + 128) * 100) / 256)}% complete...")
    print(f"{CLEAR_LINE}Average cycles for cmp8: {int(cycles/count)}")
    print(f"Average instructions for cmp8: {int(instructions/count)}")


def verifycmp16(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "cmp16" not in only and "mathlib" not in only:
        return

    print("Verifying cmp16...")
    print("0% complete...")

    with open("lib/runtime/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/runtime/start.S", "r") as fp:
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

    with open("lib/runtime/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/runtime/start.S", "r") as fp:
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


def verifyumin8(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "umin8" not in only and "mathlib" not in only:
        return

    print("Verifying umin8...")
    print("0% complete...")

    with open("lib/runtime/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/runtime/start.S", "r") as fp:
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
                "CALL umin8",
                "HALT",
                *cmplines,
            ]))
            cpu = CPUCore(memory)
            rununtilhalt(cpu)
            answer = min(a, b)
            _assert(
                cpu.ram[cpu.pc + 1] == a,
                f"umin8 changed stack value from {a} "
                + f"to {cpu.ram[cpu.pc + 1]}!",
            )
            _assert(
                cpu.ram[cpu.pc] == b,
                f"umin8 changed stack value from {b} to {cpu.ram[cpu.pc]}!",
            )
            _assert(
                cpu.a == answer,
                f"Failed to umin8({a}, {b}), "
                + f"got {cpu.a} instead of {answer}!",
            )
            cycles += cpu.cycles
            instructions += cpu.ticks
            count += 1

        print(f"{CLEAR_LINE}{int((a * 100) / 256)}% complete...")
    print(f"{CLEAR_LINE}Average cycles for umin8: {int(cycles/count)}")
    print(f"Average instructions for umin8: {int(instructions/count)}")


def verifyumin16(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "umin16" not in only and "mathlib" not in only:
        return

    print("Verifying umin16...")
    print("0% complete...")

    with open("lib/runtime/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/runtime/start.S", "r") as fp:
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

    with open("lib/runtime/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/runtime/start.S", "r") as fp:
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


def verifyumax8(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "umax8" not in only and "mathlib" not in only:
        return

    print("Verifying umax8...")
    print("0% complete...")

    with open("lib/runtime/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/runtime/start.S", "r") as fp:
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
                "CALL umax8",
                "HALT",
                *cmplines,
            ]))
            cpu = CPUCore(memory)
            rununtilhalt(cpu)
            answer = max(a, b)
            _assert(
                cpu.ram[cpu.pc + 1] == a,
                f"umax8 changed stack value from {a} "
                + f"to {cpu.ram[cpu.pc + 1]}!",
            )
            _assert(
                cpu.ram[cpu.pc] == b,
                f"umax8 changed stack value from {b} to {cpu.ram[cpu.pc]}!",
            )
            _assert(
                cpu.a == answer,
                f"Failed to umax8({a}, {b}), "
                + f"got {cpu.a} instead of {answer}!",
            )
            cycles += cpu.cycles
            instructions += cpu.ticks
            count += 1

        print(f"{CLEAR_LINE}{int((a * 100) / 256)}% complete...")
    print(f"{CLEAR_LINE}Average cycles for umax8: {int(cycles/count)}")
    print(f"Average instructions for umax8: {int(instructions/count)}")


def verifyumax16(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "umax16" not in only and "mathlib" not in only:
        return

    print("Verifying umax16...")
    print("0% complete...")

    with open("lib/runtime/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/runtime/start.S", "r") as fp:
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

    with open("lib/runtime/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/runtime/start.S", "r") as fp:
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


def verifymin8(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "min8" not in only and "mathlib" not in only:
        return

    print("Verifying min8...")
    print("0% complete...")

    with open("lib/runtime/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/runtime/start.S", "r") as fp:
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
                "CALL min8",
                "HALT",
                *cmplines,
            ]))
            cpu = CPUCore(memory)
            rununtilhalt(cpu)
            answer = min(a, b)
            _assert(
                bintoint(cpu.ram[cpu.pc + 1]) == a,
                f"min8 changed stack value from {a} "
                + f"to {cpu.ram[cpu.pc + 1]}!",
            )
            _assert(
                bintoint(cpu.ram[cpu.pc]) == b,
                f"min8 changed stack value from {b} to {cpu.ram[cpu.pc]}!",
            )
            _assert(
                bintoint(cpu.a) == answer,
                f"Failed to min8({a}, {b}), "
                + f"got {bintoint(cpu.a)} instead of {answer}!",
            )
            cycles += cpu.cycles
            instructions += cpu.ticks
            count += 1

        print(f"{CLEAR_LINE}{int(((a + 128) * 100) / 256)}% complete...")
    print(f"{CLEAR_LINE}Average cycles for min8: {int(cycles/count)}")
    print(f"Average instructions for min8: {int(instructions/count)}")


def verifymin16(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "min16" not in only and "mathlib" not in only:
        return

    print("Verifying min16...")
    print("0% complete...")

    with open("lib/runtime/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/runtime/start.S", "r") as fp:
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
                "LOADI 123",
                "CALL min16",
                "HALT",
                *cmplines,
            ]))
            cpu = CPUCore(memory)
            rununtilhalt(cpu)
            answer = min(a, b)
            _assert(
                cpu.a == 123,
                f"min16 changed accumulator value from {123} to {cpu.a}!",
            )
            result = bintoint16((cpu.ram[cpu.pc] << 8) + cpu.ram[cpu.pc + 1])
            _assert(
                result == answer,
                f"Failed to min16({a}, {b}), "
                + f"got {answer} instead of {result}!",
            )
            cycles += cpu.cycles
            instructions += cpu.ticks
            count += 1

        print(f"{CLEAR_LINE}{int(((a + 32768) * 100) / 65536)}% complete...")
    print(f"{CLEAR_LINE}Average cycles for min16: {int(cycles/count)}")
    print(f"Average instructions for min16: {int(instructions/count)}")


def verifymin32(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "min32" not in only and "mathlib" not in only:
        return

    print("Verifying min32...")
    print("0% complete...")

    with open("lib/runtime/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/runtime/start.S", "r") as fp:
        initlines += fp.readlines()
    with open("lib/math/cmp.S", "r") as fp:
        cmplines = fp.readlines()

    def _verify_min32(a: int, b: int) -> CPUCore:
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
            "CALL min32",
            "HALT",
            *cmplines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)
        answer = min(a, b)
        result = bintoint32(
            (cpu.ram[cpu.pc] << 24) +
            (cpu.ram[cpu.pc + 1] << 16) +
            (cpu.ram[cpu.pc + 2] << 8) +
            cpu.ram[cpu.pc + 3]
        )
        _assert(
            cpu.a == 123,
            f"min32 changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            result == answer,
            f"Failed to min32({a}, {b}), "
            + f"got {result} instead of {answer}!",
        )
        return cpu

    cycles = 0
    instructions = 0
    count = 0
    for a in range(-(2**31), (2**31) - 1, 2**26 + 2**13 + 19):
        for b in range(
            -(2**31), (2**31) - 1, (2**26 + 2**13 + 7)
            if full
            else (2**28 + 2**13 + 11)
        ):
            cpu = _verify_min32(a, b)
            cycles += cpu.cycles
            instructions += cpu.ticks
            count += 1

        print(f"{CLEAR_LINE}{int(((a + 2**31) * 100) / (2**32))}% complete...")
    print(f"{CLEAR_LINE}Average cycles for min32: {int(cycles/count)}")
    print(f"Average instructions for min32: {int(instructions/count)}")


def verifymax8(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "max8" not in only and "mathlib" not in only:
        return

    print("Verifying max8...")
    print("0% complete...")

    with open("lib/runtime/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/runtime/start.S", "r") as fp:
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
                "CALL max8",
                "HALT",
                *cmplines,
            ]))
            cpu = CPUCore(memory)
            rununtilhalt(cpu)
            answer = max(a, b)
            _assert(
                bintoint(cpu.ram[cpu.pc + 1]) == a,
                f"max8 changed stack value from {a} "
                + f"to {cpu.ram[cpu.pc + 1]}!",
            )
            _assert(
                bintoint(cpu.ram[cpu.pc]) == b,
                f"max8 changed stack value from {b} to {cpu.ram[cpu.pc]}!",
            )
            _assert(
                bintoint(cpu.a) == answer,
                f"Failed to max8({a}, {b}), "
                + f"got {bintoint(cpu.a)} instead of {answer}!",
            )
            cycles += cpu.cycles
            instructions += cpu.ticks
            count += 1

        print(f"{CLEAR_LINE}{int(((a + 128) * 100) / 256)}% complete...")
    print(f"{CLEAR_LINE}Average cycles for max8: {int(cycles/count)}")
    print(f"Average instructions for max8: {int(instructions/count)}")


def verifymax16(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "max16" not in only and "mathlib" not in only:
        return

    print("Verifying max16...")
    print("0% complete...")

    with open("lib/runtime/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/runtime/start.S", "r") as fp:
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
                "LOADI 123",
                "CALL max16",
                "HALT",
                *cmplines,
            ]))
            cpu = CPUCore(memory)
            rununtilhalt(cpu)
            answer = max(a, b)
            _assert(
                cpu.a == 123,
                f"max16 changed accumulator value from {123} to {cpu.a}!",
            )
            result = bintoint16((cpu.ram[cpu.pc] << 8) + cpu.ram[cpu.pc + 1])
            _assert(
                result == answer,
                f"Failed to max16({a}, {b}), "
                + f"got {answer} instead of {result}!",
            )
            cycles += cpu.cycles
            instructions += cpu.ticks
            count += 1

        print(f"{CLEAR_LINE}{int(((a + 32768) * 100) / 65536)}% complete...")
    print(f"{CLEAR_LINE}Average cycles for max16: {int(cycles/count)}")
    print(f"Average instructions for max16: {int(instructions/count)}")


def verifymax32(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "max32" not in only and "mathlib" not in only:
        return

    print("Verifying max32...")
    print("0% complete...")

    with open("lib/runtime/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/runtime/start.S", "r") as fp:
        initlines += fp.readlines()
    with open("lib/math/cmp.S", "r") as fp:
        cmplines = fp.readlines()

    def _verify_max32(a: int, b: int) -> CPUCore:
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
            "CALL max32",
            "HALT",
            *cmplines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)
        answer = max(a, b)
        result = bintoint32(
            (cpu.ram[cpu.pc] << 24) +
            (cpu.ram[cpu.pc + 1] << 16) +
            (cpu.ram[cpu.pc + 2] << 8) +
            cpu.ram[cpu.pc + 3]
        )
        _assert(
            cpu.a == 123,
            f"max32 changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            result == answer,
            f"Failed to max32({a}, {b}), "
            + f"got {result} instead of {answer}!",
        )
        return cpu

    cycles = 0
    instructions = 0
    count = 0
    for a in range(-(2**31), (2**31) - 1, 2**26 + 2**13 + 19):
        for b in range(
            -(2**31), (2**31) - 1, (2**26 + 2**13 + 7)
            if full
            else (2**28 + 2**13 + 11)
        ):
            cpu = _verify_max32(a, b)
            cycles += cpu.cycles
            instructions += cpu.ticks
            count += 1

        print(f"{CLEAR_LINE}{int(((a + 2**31) * 100) / (2**32))}% complete...")
    print(f"{CLEAR_LINE}Average cycles for max32: {int(cycles/count)}")
    print(f"Average instructions for max32: {int(instructions/count)}")


def verifyneg8(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "neg8" not in only and "mathlib" not in only:
        return

    print("Verifying neg8...")
    print("0% complete...")

    with open("lib/runtime/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/runtime/start.S", "r") as fp:
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
            "CALL neg8",
            "HALT",
            *neglines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)
        calculated = bintoint(cpu.a)
        real = -x
        _assert(
            real == calculated,
            f"Failed to neg8 {x}, "
            + f"got {calculated} instead of {real}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1
        print(f"{CLEAR_LINE}{int(((x + 127) * 100) / 256)}% complete...")

    print(f"{CLEAR_LINE}Average cycles for neg8: {int(cycles/count)}")
    print(f"Average instructions for neg8: {int(instructions/count)}")


def verifyneg16(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "neg16" not in only and "mathlib" not in only:
        return

    print("Verifying neg16...")
    print("0% complete...")

    with open("lib/runtime/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/runtime/start.S", "r") as fp:
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

    with open("lib/runtime/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/runtime/start.S", "r") as fp:
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

    with open("lib/runtime/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/runtime/start.S", "r") as fp:
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

    with open("lib/runtime/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/runtime/start.S", "r") as fp:
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
            "PUSHI 0x00",
            "PUSHI 0x20",
            "SWAP PC, SPC",
            "SETPC string",
            "SWAP PC, SPC",
            "PUSH SPC",
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
        stack_source = (cpu.ram[cpu.pc] << 8) + cpu.ram[cpu.pc + 1]
        stack_dest = (cpu.ram[cpu.pc + 2] << 8) + cpu.ram[cpu.pc + 3]
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


def verifystrncpy(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "strncpy" not in only and "stringlib" not in only:
        return

    print("Verifying strncpy...")

    with open("lib/runtime/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/runtime/start.S", "r") as fp:
        initlines += fp.readlines()
    with open("lib/string/strcpy.S", "r") as fp:
        liblines = fp.readlines()

    cycles = 0
    instructions = 0
    count = 0
    for amt in [0, 5, 10, 15]:
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
                "PUSHI 0x00",
                "PUSHI 0x20",
                "SWAP PC, SPC",
                "SETPC string",
                "SWAP PC, SPC",
                "PUSH SPC",
                f"PUSHI {amt}",
                "LOADI 123",
                "CALL strncpy",
                "HALT",
                *liblines,
            ]))
            cpu = CPUCore(memory)
            rununtilhalt(cpu)
            _assert(
                cpu.a == 123,
                f"strncpy changed A register from 123 to {cpu.a}!",
            )
            stack_amt = cpu.ram[cpu.pc]
            stack_source = (cpu.ram[cpu.pc + 1] << 8) + cpu.ram[cpu.pc + 2]
            stack_dest = (cpu.ram[cpu.pc + 3] << 8) + cpu.ram[cpu.pc + 4]
            _assert(
                stack_source == 0x1000,
                f"strncpy changed stack source from {0x1000} to {stack_source}!",
            )
            _assert(
                stack_dest == 0x2000,
                f"strncpy changed stack source from {0x2000} to {stack_dest}!",
            )
            _assert(
                stack_amt == amt,
                f"strncpy changed stack source from {0x2000} to {stack_dest}!",
            )
            expected = string[:amt]
            actual = getstring(cpu, 0x2000)
            _assert(
                actual == expected,
                f"Failed to strncpy(&{string!r}, 0x2000, {amt}), "
                + f"got {actual!r} instead of {expected!r}!",
            )
            cycles += cpu.cycles
            instructions += cpu.ticks
            count += 1

    print(f"Average cycles for strncpy: {int(cycles/count)}")
    print(f"Average instructions for strncpy: {int(instructions/count)}")


def verifystrcat(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "strcat" not in only and "stringlib" not in only:
        return

    print("Verifying strcat...")

    with open("lib/runtime/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/runtime/start.S", "r") as fp:
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
                "SETPC string",
                "SWAP PC, SPC",
                "PUSH SPC",
                "SWAP PC, SPC",
                "SETPC concatenation",
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
            stack_source = (cpu.ram[cpu.pc] << 8) + cpu.ram[cpu.pc + 1]
            stack_dest = (
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

    with open("lib/runtime/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/runtime/start.S", "r") as fp:
        initlines += fp.readlines()
    with open("lib/math/cmp.S", "r") as fp:
        cmplines = fp.readlines()
    with open("lib/string/strcmp.S", "r") as fp:
        liblines = fp.readlines()

    cycles = 0
    instructions = 0
    count = 0
    for first in [
        "a test",
        "the quick brown fox jumps over the lazy dog",
        "",
        "whatever this is",
    ]:
        for second in [
            "a test",
            "the quick brown fox jumps over the lazy dog",
            "",
            "whatever this is",
        ]:
            memory = getmemory(os.linesep.join([
                *initlines,
                ".org 0x1000",
                "first:",
                *[f".char {c!r}" for c in first],
                ".byte 0x00",
                ".org 0x2000",
                "second:",
                *[f".char {c!r}" for c in second],
                ".byte 0x00",
                ".org 0x3000",
                "main:",
                "SWAP PC, SPC",
                "SETPC first",
                "SWAP PC, SPC",
                "PUSH SPC",
                "SWAP PC, SPC",
                "SETPC second",
                "SWAP PC, SPC",
                "PUSH SPC",
                "CALL strcmp",
                "HALT",
                *liblines,
                *cmplines,
            ]))
            cpu = CPUCore(memory)
            rununtilhalt(cpu)

            if first < second:
                answer = -1
            elif first == second:
                answer = 0
            elif first > second:
                answer = 1
            stack_second = (cpu.ram[cpu.pc] << 8) + cpu.ram[cpu.pc + 1]
            stack_first = (
                (cpu.ram[cpu.pc + 2] << 8) + cpu.ram[cpu.pc + 3]
            )
            _assert(
                stack_first == 0x1000,
                f"strcmp changed stack source from {0x1000} "
                + f"to {stack_first}!",
            )
            _assert(
                stack_second == 0x2000,
                f"strcmp changed stack source from {0x2000} to {stack_second}!",
            )
            _assert(
                bintoint(cpu.a) == answer,
                f"Failed to strcmp(&{first!r}, &{second!r}), "
                + f"got {bintoint(cpu.a)} instead of {answer}!",
            )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    print(f"Average cycles for strcmp: {int(cycles/count)}")
    print(f"Average instructions for strcmp: {int(instructions/count)}")


def verifyutoa8(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "utoa8" not in only and "stringlib" not in only:
        return

    print("Verifying utoa8...")
    print("0% complete...")

    with open("lib/runtime/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/runtime/start.S", "r") as fp:
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
    for x in range(0, 256, 1 if full else 7):
        memory = getmemory(os.linesep.join([
            *initlines,
            "main:",
            "PUSHI 0x00",
            "PUSHI 0x10",
            f"LOADI {x}",
            "CALL utoa8",
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
            cpu.a == x,
            f"utoa8 changed A register from {x} to {cpu.a}!",
        )
        stack_input = (cpu.ram[cpu.pc] << 8) + cpu.ram[cpu.pc + 1]
        _assert(
            stack_input == 0x1000,
            f"utoa8 changed stack input from {0x1000} to {stack_input}!",
        )
        _assert(
            getstring(cpu, 0x1000) == str(x),
            f"Failed to utoa8({x}), "
            + f"got {getstring(cpu, 0x1000)} instead of {str(x)}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

        print(f"{CLEAR_LINE}{int((x * 100) / 256)}% complete...")
    print(f"{CLEAR_LINE}Average cycles for utoa8: {int(cycles/count)}")
    print(f"Average instructions for utoa8: {int(instructions/count)}")


def verifyutoa16(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "utoa16" not in only and "stringlib" not in only:
        return

    print("Verifying utoa16...")
    print("0% complete...")

    with open("lib/runtime/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/runtime/start.S", "r") as fp:
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
    for x in range(0, 65536, 123 if full else 2763):
        memory = getmemory(os.linesep.join([
            *initlines,
            "main:",
            f"PUSHI {x & 0xFF}",
            f"PUSHI {(x >> 8) & 0xFF}",
            "PUSHI 0x00",
            "PUSHI 0x10",
            "LOADI 123",
            "CALL utoa16",
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
            f"utoa16 changed accumulator value from {123} to {cpu.a}!",
        )
        stack_input = ((cpu.ram[cpu.pc] << 8) + cpu.ram[cpu.pc + 1])
        original_number = (
            (cpu.ram[cpu.pc + 2] << 8) + cpu.ram[cpu.pc + 3]
        )
        _assert(
            stack_input == 0x1000,
            f"utoa16 changed stack input from {0x1000} to {stack_input}!",
        )
        _assert(
            getstring(cpu, 0x1000) == str(x),
            f"Failed to utoa({x}), "
            + f"got {getstring(cpu, 0x1000)} instead of {str(x)}!",
        )
        _assert(
            original_number == x,
            f"utoa16 changed original number input from {x} to {original_number}!"
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

        print(f"{CLEAR_LINE}{int((x * 100) / 65536)}% complete...")

    print(f"{CLEAR_LINE}Average cycles for utoa16: {int(cycles/count)}")
    print(f"Average instructions for utoa16: {int(instructions/count)}")


def verifyutoa32(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "utoa32" not in only and "stringlib" not in only:
        return

    print("Verifying utoa32...")
    print("0% complete...")

    with open("lib/runtime/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/runtime/start.S", "r") as fp:
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
    for x in range(0, 4294967296, 8060929 if full else 381075969):
        memory = getmemory(os.linesep.join([
            *initlines,
            "main:",
            f"PUSHI {x & 0xFF}",
            f"PUSHI {(x >> 8) & 0xFF}",
            f"PUSHI {(x >> 16) & 0xFF}",
            f"PUSHI {(x >> 24) & 0xFF}",
            "PUSHI 0x00",
            "PUSHI 0x10",
            "LOADI 123",
            "CALL utoa32",
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
            f"utoa32 changed accumulator value from {123} to {cpu.a}!",
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
            f"utoa32 changed stack input from {0x1000} to {stack_input}!",
        )
        _assert(
            getstring(cpu, 0x1000) == str(x),
            f"Failed to utoa({x}), "
            + f"got {getstring(cpu, 0x1000)} instead of {str(x)}!",
        )
        _assert(
            original_number == x,
            f"utoa32 changed original number input from {x} to {original_number}!"
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

        print(f"{CLEAR_LINE}{int((x * 100) / 2**32)}% complete...")

    print(f"{CLEAR_LINE}Average cycles for utoa32: {int(cycles/count)}")
    print(f"Average instructions for utoa32: {int(instructions/count)}")


def verifyitoa8(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "itoa8" not in only and "stringlib" not in only:
        return

    print("Verifying itoa8...")
    print("0% complete...")

    with open("lib/runtime/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/runtime/start.S", "r") as fp:
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
            "CALL itoa8",
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
            f"itoa8 changed A register from {x} to {bintoint(cpu.a)}!",
        )
        stack_input = (cpu.ram[cpu.pc] << 8) + cpu.ram[cpu.pc + 1]
        _assert(
            stack_input == 0x1000,
            f"itoa8 changed stack input from {0x1000} to {stack_input}!",
        )
        _assert(
            getstring(cpu, 0x1000) == str(x),
            f"Failed to itoa8({x}), "
            + f"got {getstring(cpu, 0x1000)} instead of {str(x)}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

        print(f"{CLEAR_LINE}{int(((x + 128) * 100) / 256)}% complete...")
    print(f"{CLEAR_LINE}Average cycles for itoa8: {int(cycles/count)}")
    print(f"Average instructions for itoa8: {int(instructions/count)}")


def verifyitoa16(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "itoa16" not in only and "stringlib" not in only:
        return

    print("Verifying itoa16...")
    print("0% complete...")

    with open("lib/runtime/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/runtime/start.S", "r") as fp:
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

    with open("lib/runtime/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/runtime/start.S", "r") as fp:
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


def verifyatoi8(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "atoi8" not in only and "stringlib" not in only:
        return

    print("Verifying atoi8...")
    print("0% complete...")

    with open("lib/runtime/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/runtime/start.S", "r") as fp:
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
                    "CALL atoi8",
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
                    f"atoi8 expected stack {hex(0x1000 + len(numstr))} "
                    + f"but got {hex(stack_input)}!",
                )
                _assert(
                    bintoint(cpu.a) == x,
                    f"Failed to atoi8({numstr}), "
                    + f"got {bintoint(cpu.a)} instead of {x}!",
                )
                cycles += cpu.cycles
                instructions += cpu.ticks
                count += 1

        print(f"{CLEAR_LINE}{int(((x + 128) * 100) / 256)}% complete...")

    print(f"{CLEAR_LINE}Average cycles for atoi8: {int(cycles/count)}")
    print(f"Average instructions for atoi8: {int(instructions/count)}")


def verifyatoi16(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "atoi16" not in only and "stringlib" not in only:
        return

    print("Verifying atoi16...")
    print("0% complete...")

    with open("lib/runtime/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/runtime/start.S", "r") as fp:
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

    with open("lib/runtime/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/runtime/start.S", "r") as fp:
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


def verifyimports(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "imports" not in only and "compiler" not in only:
        return

    print("Verifying imports...")

    with open("lib/runtime/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/runtime/start.S", "r") as fp:
        initlines += fp.readlines()

    cycles = 0
    instructions = 0
    count = 0

    def loader(filename: str) -> Optional[str]:
        filename = os.path.basename(filename)

        if filename == "file1.py":
            return textwrap.dedent("""
                def math(a: int8, b: int8) -> int8:
                    return a + b
            """)
        elif filename == "file2.py":
            return textwrap.dedent("""
                def math(a: int8, b: int8) -> int8:
                    return a - b
            """)
        else:
            return None

    compiler = Compiler(settings, file_loader=loader)

    if True:
        memory = getmemory(os.linesep.join([
            *initlines,
            *compiler.parse_and_compile_module("imports.py", textwrap.dedent("""
                from file1 import math

                def func() -> int8:
                    return math(5, 10)
            """)).code,
            *parse_and_compile_module("file1.py", loader("file1.py") or "", settings).code,
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
            f"imports changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"imports changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"imports changed V value from {222} to {cpu.v}!",
        )
        result = bintoint(cpu.ram[cpu.pc + 0])
        expected = 5 + 10
        _assert(
            result == expected,
            "Failed to imports, "
            + f"got {result} instead of {expected}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    if True:
        memory = getmemory(os.linesep.join([
            *initlines,
            *compiler.parse_and_compile_module("imports.py", textwrap.dedent("""
                from file2 import math

                def func() -> int8:
                    return math(5, 10)
            """)).code,
            *parse_and_compile_module("file2.py", loader("file2.py") or "", settings).code,
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
            f"imports changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"imports changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"imports changed V value from {222} to {cpu.v}!",
        )
        result = bintoint(cpu.ram[cpu.pc + 0])
        expected = 5 - 10
        _assert(
            result == expected,
            "Failed to imports, "
            + f"got {result} instead of {expected}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    print(f"Average cycles for imports: {int(cycles/count)}")
    print(f"Average instructions for imports: {int(instructions/count)}")


def verifyextern(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "extern" not in only and "compiler" not in only:
        return

    print("Verifying extern...")

    with open("lib/runtime/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/runtime/start.S", "r") as fp:
        initlines += fp.readlines()

    cycles = 0
    instructions = 0
    count = 0

    def loader(filename: str) -> Optional[str]:
        filename = os.path.basename(filename)

        if filename == "file1.py":
            return textwrap.dedent("""
                global_var: extern[int8]

                def math(var: int8) -> extern[int8]: ...
            """)
        else:
            return None

    compiler = Compiler(settings, file_loader=loader)

    # First, test extern variables.
    if True:
        memory = getmemory(os.linesep.join([
            *initlines,
            *compiler.parse_and_compile_module("extern.py", textwrap.dedent("""
                global_var: extern[int8]

                def func() -> nopad[int8]:
                    return global_var
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
            "global_var:",
            ".byte 37",
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        _assert(
            cpu.a == 123,
            f"extern changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"extern changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"extern changed V value from {222} to {cpu.v}!",
        )
        result = bintoint(cpu.ram[cpu.pc + 0])
        expected = 37
        _assert(
            result == expected,
            "Failed to extern, "
            + f"got {result} instead of {expected}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    # Now, test extern functions.
    if True:
        memory = getmemory(os.linesep.join([
            *initlines,
            *compiler.parse_and_compile_module("extern.py", textwrap.dedent("""
                def math(var: int8) -> extern[int8]: ...

                def func() -> nopad[int8]:
                    return math(5)
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
            "math:",
            "ADDPCI 2",
            "LOAD A",
            "ADDI 17",
            "STORE A",
            "SUBPCI 2",
            "RET"
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        _assert(
            cpu.a == 123,
            f"extern changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"extern changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"extern changed V value from {222} to {cpu.v}!",
        )
        result = bintoint(cpu.ram[cpu.pc + 0])
        expected = 22
        _assert(
            result == expected,
            "Failed to extern, "
            + f"got {result} instead of {expected}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    # Now, test imported extern globals.
    if True:
        memory = getmemory(os.linesep.join([
            *initlines,
            *compiler.parse_and_compile_module("extern.py", textwrap.dedent("""
                from file1 import global_var

                def func() -> nopad[int8]:
                    return global_var
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
            "global_var:",
            ".byte 42",
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        _assert(
            cpu.a == 123,
            f"extern changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"extern changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"extern changed V value from {222} to {cpu.v}!",
        )
        result = bintoint(cpu.ram[cpu.pc + 0])
        expected = 42
        _assert(
            result == expected,
            "Failed to extern, "
            + f"got {result} instead of {expected}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    # Now, test imported extern functions.
    if True:
        memory = getmemory(os.linesep.join([
            *initlines,
            *compiler.parse_and_compile_module("extern.py", textwrap.dedent("""
                from file1 import math

                def func() -> nopad[int8]:
                    return math(5)
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
            "math:",
            "ADDPCI 2",
            "LOAD A",
            "ADDI 21",
            "STORE A",
            "SUBPCI 2",
            "RET"
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        _assert(
            cpu.a == 123,
            f"extern changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"extern changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"extern changed V value from {222} to {cpu.v}!",
        )
        result = bintoint(cpu.ram[cpu.pc + 0])
        expected = 26
        _assert(
            result == expected,
            "Failed to extern, "
            + f"got {result} instead of {expected}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    print(f"Average cycles for extern: {int(cycles/count)}")
    print(f"Average instructions for extern: {int(instructions/count)}")


def verifystaticreturn(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "staticreturn" not in only and "compiler" not in only:
        return

    print("Verifying staticreturn...")

    with open("lib/runtime/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/runtime/start.S", "r") as fp:
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
            """), settings).code,
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
            """), settings).code,
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

    with open("lib/runtime/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/runtime/start.S", "r") as fp:
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
            """), settings).code,
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
            """), settings).code,
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
            """), settings).code,
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

    with open("lib/runtime/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/runtime/start.S", "r") as fp:
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
            """), settings).code,
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
            """), settings).code,
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
            """), settings).code,
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

    with open("lib/runtime/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/runtime/start.S", "r") as fp:
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
            """), settings).code,
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
            """), settings).code,
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
            """), settings).code,
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

    with open("lib/runtime/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/runtime/start.S", "r") as fp:
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
            """), settings).code,
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
            """), settings).code,
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

    with open("lib/runtime/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/runtime/start.S", "r") as fp:
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
            """), settings).code,
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
            """), settings).code,
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
            """), settings).code,
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
            """), settings).code,
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
            """), settings).code,
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

    with open("lib/runtime/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/runtime/start.S", "r") as fp:
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
            """), settings).code,
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
            """), settings).code,
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
            """), settings).code,
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
            """), settings).code,
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
            """), settings).code,
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

    with open("lib/runtime/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/runtime/start.S", "r") as fp:
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
            """), settings).code,
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
            """), settings).code,
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
            """), settings).code,
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
            """), settings).code,
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
            """), settings).code,
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
            """), settings).code,
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

    with open("lib/runtime/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/runtime/start.S", "r") as fp:
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
            """), settings).code,
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
            """), settings).code,
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
            """), settings).code,
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
                """), settings).code,
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
                """), settings).code,
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
                """), settings).code,
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

    with open("lib/runtime/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/runtime/start.S", "r") as fp:
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
            """), settings).code,
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
            """), settings).code,
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
            """), settings).code,
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
                """), settings).code,
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
                """), settings).code,
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
                """), settings).code,
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


def verifyshiftandreturn(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "shiftandreturn" not in only and "compiler" not in only:
        return

    print("Verifying shiftandreturn...")

    with open("lib/runtime/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/runtime/start.S", "r") as fp:
        initlines += fp.readlines()
    with open("lib/math/shift.S", "r") as fp:
        shiftlines = fp.readlines()

    cycles = 0
    instructions = 0
    count = 0
    for x in range(0, 256, 29 if full else 51):
        for y in range(0, 8):
            for op in ["<<", ">>"]:
                memory = getmemory(os.linesep.join([
                    *initlines,
                    *shiftlines,
                    *parse_and_compile_module("shiftandreturn", textwrap.dedent(f"""
                        def shiftandreturn(param1: uint8, param2: uint8) -> uint8:
                            return param1 {op} param2
                    """), settings).code,
                    "main:",
                    f"PUSHI {x}",
                    f"PUSHI {y}",
                    "LOADI 111",
                    "MOV A, U",
                    "LOADI 222",
                    "MOV A, V",
                    "LOADI 123",
                    "CALL shiftandreturn",
                    "HALT",
                ]))
                cpu = CPUCore(memory)
                rununtilhalt(cpu)

                _assert(
                    cpu.a == 123,
                    f"shiftandreturn changed accumulator value from {123} to {cpu.a}!",
                )
                _assert(
                    cpu.u == 111,
                    f"shiftandreturn changed U value from {111} to {cpu.u}!",
                )
                _assert(
                    cpu.v == 222,
                    f"shiftandreturn changed V value from {222} to {cpu.v}!",
                )
                result = cpu.ram[cpu.pc + 0]
                expected = ((x << y) if op == "<<" else (x >> y)) & 0xFF
                _assert(
                    result == expected,
                    "Failed to shiftandreturn, "
                    + f"got {result} instead of {expected}!",
                )
                cycles += cpu.cycles
                instructions += cpu.ticks
                count += 1

    for x in range(0, 65536, 7281 if full else 13107):
        for y in range(0, 16):
            for op in ["<<", ">>"]:
                memory = getmemory(os.linesep.join([
                    *initlines,
                    *shiftlines,
                    *parse_and_compile_module("shiftandreturn", textwrap.dedent(f"""
                        def shiftandreturn(param1: uint16, param2: uint8) -> uint16:
                            return param1 {op} param2
                    """), settings).code,
                    "main:",
                    f"PUSHI {x & 0xFF}",
                    f"PUSHI {(x >> 8) & 0xFF}",
                    f"PUSHI {y}",
                    "LOADI 111",
                    "MOV A, U",
                    "LOADI 222",
                    "MOV A, V",
                    "LOADI 123",
                    "CALL shiftandreturn",
                    "HALT",
                ]))
                cpu = CPUCore(memory)
                rununtilhalt(cpu)

                _assert(
                    cpu.a == 123,
                    f"shiftandreturn changed accumulator value from {123} to {cpu.a}!",
                )
                _assert(
                    cpu.u == 111,
                    f"shiftandreturn changed U value from {111} to {cpu.u}!",
                )
                _assert(
                    cpu.v == 222,
                    f"shiftandreturn changed V value from {222} to {cpu.v}!",
                )
                result = (cpu.ram[cpu.pc + 0] << 8) + cpu.ram[cpu.pc + 1]
                expected = ((x << y) if op == "<<" else (x >> y)) & 0xFFFF
                _assert(
                    result == expected,
                    "Failed to shiftandreturn, "
                    + f"got {result} instead of {expected}!",
                )
                cycles += cpu.cycles
                instructions += cpu.ticks
                count += 1

    for x in range(0, 2**32, 477218589 if full else 858993459):
        for y in range(0, 16):
            for op in ["<<", ">>"]:
                memory = getmemory(os.linesep.join([
                    *initlines,
                    *shiftlines,
                    *parse_and_compile_module("shiftandreturn", textwrap.dedent(f"""
                        def shiftandreturn(param1: uint32, param2: uint8) -> uint32:
                            return param1 {op} param2
                    """), settings).code,
                    "main:",
                    f"PUSHI {x & 0xFF}",
                    f"PUSHI {(x >> 8) & 0xFF}",
                    f"PUSHI {(x >> 16) & 0xFF}",
                    f"PUSHI {(x >> 24) & 0xFF}",
                    f"PUSHI {y}",
                    "LOADI 111",
                    "MOV A, U",
                    "LOADI 222",
                    "MOV A, V",
                    "LOADI 123",
                    "CALL shiftandreturn",
                    "HALT",
                ]))
                cpu = CPUCore(memory)
                rununtilhalt(cpu)

                _assert(
                    cpu.a == 123,
                    f"shiftandreturn changed accumulator value from {123} to {cpu.a}!",
                )
                _assert(
                    cpu.u == 111,
                    f"shiftandreturn changed U value from {111} to {cpu.u}!",
                )
                _assert(
                    cpu.v == 222,
                    f"shiftandreturn changed V value from {222} to {cpu.v}!",
                )
                result = (
                    (cpu.ram[cpu.pc + 0] << 24) +
                    (cpu.ram[cpu.pc + 1] << 16) +
                    (cpu.ram[cpu.pc + 2] << 8) +
                    (cpu.ram[cpu.pc + 3] << 0)
                )
                expected = ((x << y) if op == "<<" else (x >> y)) & 0xFFFFFFFF
                _assert(
                    result == expected,
                    "Failed to shiftandreturn, "
                    + f"got {result} instead of {expected}!",
                )
                cycles += cpu.cycles
                instructions += cpu.ticks
                count += 1

    print(f"Average cycles for shiftandreturn: {int(cycles/count)}")
    print(f"Average instructions for shiftandreturn: {int(instructions/count)}")


def verifybitwiseand(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "bitwiseand" not in only and "compiler" not in only:
        return

    print("Verifying bitwiseand...")

    with open("lib/runtime/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/runtime/start.S", "r") as fp:
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
            """), settings).code,
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
            """), settings).code,
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
            """), settings).code,
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

    with open("lib/runtime/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/runtime/start.S", "r") as fp:
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
            """), settings).code,
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
            """), settings).code,
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
            """), settings).code,
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

    with open("lib/runtime/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/runtime/start.S", "r") as fp:
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
            """), settings).code,
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
            """), settings).code,
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
            """), settings).code,
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

    with open("lib/runtime/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/runtime/start.S", "r") as fp:
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
            """), settings).code,
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
            """), settings).code,
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
            """), settings).code,
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

    with open("lib/runtime/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/runtime/start.S", "r") as fp:
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
            """), settings).code,
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
            """), settings).code,
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
            """), settings).code,
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

    with open("lib/runtime/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/runtime/start.S", "r") as fp:
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
                    """), settings).code,
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

    with open("lib/runtime/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/runtime/start.S", "r") as fp:
        startlines = fp.readlines()
    with open("lib/runtime/data.S", "r") as fp:
        datalines = fp.readlines()
    with open("lib/runtime/heap.S", "r") as fp:
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
        """), settings)
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

    with open("lib/runtime/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/runtime/start.S", "r") as fp:
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
            """), settings).code,
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

    with open("lib/runtime/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/runtime/start.S", "r") as fp:
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
            """), settings).code,
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

    with open("lib/runtime/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/runtime/start.S", "r") as fp:
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
            """), settings).code,
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

    with open("lib/runtime/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/runtime/start.S", "r") as fp:
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
            """), settings).code,
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

    with open("lib/runtime/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/runtime/start.S", "r") as fp:
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
                """), settings).code,
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

    with open("lib/runtime/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/runtime/start.S", "r") as fp:
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
                """), settings).code,
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
            """), settings).code,
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

    with open("lib/runtime/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/runtime/start.S", "r") as fp:
        initlines += fp.readlines()

    cycles = 0
    instructions = 0
    count = 0

    # Shut mypy up so we don't have to choose different variable names for a test.
    val: Any

    # First, test normal ternary expressions.
    for a in [-5, 0, 5]:
        for b in [-7, 0, 7]:
            for val in [False, True]:
                memory = getmemory(os.linesep.join([
                    *initlines,
                    *parse_and_compile_module("ternaryexpressions", textwrap.dedent("""
                        def func(a: int8, b: int8, op: bool) -> int8:
                            return (a + 5) if op else (b - 7)
                    """), settings).code,
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

    # Now test constant narrowing.
    for vartype in ["uint8", "int8"]:
        for a in [-5, 0, 5] if vartype == "int8" else [1, 9]:
            for const in [-7, 0, 7] if vartype == "int8" else [3, 8]:
                for val in [False, True]:
                    memory = getmemory(os.linesep.join([
                        *initlines,
                        *parse_and_compile_module("ternaryexpressions", textwrap.dedent(f"""
                            def func(a: {vartype}, op: bool) -> int8:
                                return a if op else {const}
                        """), settings).code,
                        "main:",
                        f"PUSHI {a}",
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
                    expected = a if val else const
                    _assert(
                        result == expected,
                        "Failed to ternaryexpressions, "
                        + f"got {result} instead of {expected}!",
                    )
                    cycles += cpu.cycles
                    instructions += cpu.ticks
                    count += 1

    for vartype in ["uint8", "int8"]:
        for a in [-5, 0, 5] if vartype == "int8" else [1, 9]:
            for const in [-7, 0, 7] if vartype == "int8" else [3, 8]:
                for val in [False, True]:
                    memory = getmemory(os.linesep.join([
                        *initlines,
                        *parse_and_compile_module("ternaryexpressions", textwrap.dedent(f"""
                            def func(a: {vartype}, op: bool) -> int8:
                                return {const} if op else a
                        """), settings).code,
                        "main:",
                        f"PUSHI {a}",
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
                    expected = const if val else a
                    _assert(
                        result == expected,
                        "Failed to ternaryexpressions, "
                        + f"got {result} instead of {expected}!",
                    )
                    cycles += cpu.cycles
                    instructions += cpu.ticks
                    count += 1

    # Now test with coercing to a boolean type.
    for a in [-5, 0, 5]:
        for b in [-7, 0, 7]:
            for val in ["", "nonzero"]:
                memory = getmemory(os.linesep.join([
                    *initlines,
                    *parse_and_compile_module("ternaryexpressions", textwrap.dedent(f"""
                        def funcimpl(a: int8, b: int8, op: const[str]) -> int8:
                            return (a + 5) if op else (b - 7)

                        def func(a: int8, b: int8) -> int8:
                            return funcimpl(a, b, {val!r})
                    """), settings).code,
                    "main:",
                    f"PUSHI {a}",
                    f"PUSHI {b}",
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

    with open("lib/runtime/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/runtime/start.S", "r") as fp:
        initlines += fp.readlines()
    with open("lib/math/cmp.S", "r") as fp:
        cmplines = fp.readlines()
    with open("lib/string/strcmp.S", "r") as fp:
        strcmplines = fp.readlines()

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
                    """), settings).code,
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
                """), settings).code,
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
                """), settings).code,
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
                """), settings).code,
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
                """), settings).code,
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
                """), settings).code,
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

    for first in ['0', '7', 'a', 'd', 'A', 'Z']:
        for second in ['0', '7', 'a', 'd', 'A', 'Z']:
            memory = getmemory(os.linesep.join([
                *initlines,
                *parse_and_compile_module("equalityexpression", textwrap.dedent("""
                    def func(val1: char, val2: char) -> bool:
                        return val1 == val2
                """), settings).code,
                "main:",
                f"PUSHI {first!r}",
                f"PUSHI {second!r}",
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
            expected = first == second
            _assert(
                result == expected,
                "Failed to equalityexpression, "
                + f"got {result} instead of {expected}!",
            )
            cycles += cpu.cycles
            instructions += cpu.ticks
            count += 1

    for first in ['apples', 'bananas', 'carrots', 'dragons']:
        for second in ['apples', 'bananas', 'carrots', 'dragons']:
            memory = getmemory(os.linesep.join([
                *initlines,
                *cmplines,
                *strcmplines,
                *parse_and_compile_module("equalityexpression", textwrap.dedent("""
                    def func(val1: const[str], val2: const[str]) -> bool:
                        return val1 == val2
                """), settings).code,
                ".org 0x1000",
                "first:",
                *[f".char {c!r}" for c in first],
                ".byte 0x00",
                ".org 0x2000",
                "second:",
                *[f".char {c!r}" for c in second],
                ".byte 0x00",
                ".org 0x3000",
                "main:",
                "PUSHADDR first",
                "PUSHADDR second",
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
            expected = first == second
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

    with open("lib/runtime/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/runtime/start.S", "r") as fp:
        initlines += fp.readlines()
    with open("lib/math/cmp.S", "r") as fp:
        cmplines = fp.readlines()
    with open("lib/string/strcmp.S", "r") as fp:
        strcmplines = fp.readlines()

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
                """), settings).code,
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
                """), settings).code,
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
                """), settings).code,
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
                """), settings).code,
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
                """), settings).code,
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
                """), settings).code,
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

    for first in ['0', '7', 'a', 'd', 'A', 'Z']:
        for second in ['0', '7', 'a', 'd', 'A', 'Z']:
            memory = getmemory(os.linesep.join([
                *initlines,
                *parse_and_compile_module("equalityexpression", textwrap.dedent("""
                    def func(val1: char, val2: char) -> bool:
                        return val1 != val2
                """), settings).code,
                "main:",
                f"PUSHI {first!r}",
                f"PUSHI {second!r}",
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
            expected = first != second
            _assert(
                result == expected,
                "Failed to equalityexpression, "
                + f"got {result} instead of {expected}!",
            )
            cycles += cpu.cycles
            instructions += cpu.ticks
            count += 1

    for first in ['apples', 'bananas', 'carrots', 'dragons']:
        for second in ['apples', 'bananas', 'carrots', 'dragons']:
            memory = getmemory(os.linesep.join([
                *initlines,
                *cmplines,
                *strcmplines,
                *parse_and_compile_module("equalityexpression", textwrap.dedent("""
                    def func(val1: const[str], val2: const[str]) -> bool:
                        return val1 != val2
                """), settings).code,
                ".org 0x1000",
                "first:",
                *[f".char {c!r}" for c in first],
                ".byte 0x00",
                ".org 0x2000",
                "second:",
                *[f".char {c!r}" for c in second],
                ".byte 0x00",
                ".org 0x3000",
                "main:",
                "PUSHADDR first",
                "PUSHADDR second",
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
            expected = first != second
            _assert(
                result == expected,
                "Failed to equalityexpression, "
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

    with open("lib/runtime/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/runtime/start.S", "r") as fp:
        initlines += fp.readlines()
    with open("lib/math/cmp.S", "r") as fp:
        cmplines = fp.readlines()
    with open("lib/string/strcmp.S", "r") as fp:
        strcmplines = fp.readlines()

    cycles = 0
    instructions = 0
    count = 0
    for val1 in [0, 57, 123, 127, 255]:
        for val2 in [0, 57, 123, 127, 255]:
            for secondtype in ["uint8", "uint16", "uint32"]:
                for operator in ["<=", "<", ">=", ">="]:
                    memory = getmemory(os.linesep.join([
                        *initlines,
                        *parse_and_compile_module("alligatorexpression", textwrap.dedent(f"""
                            def func(val1: uint8, val2: {secondtype}) -> bool:
                                return val1 {operator} val2
                        """), settings).code,
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
                        """), settings).code,
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

    for first in ['0', '7', 'a', 'd', 'A', 'Z']:
        for second in ['0', '7', 'a', 'd', 'A', 'Z']:
            for operator in ["<=", "<", ">=", ">="]:
                memory = getmemory(os.linesep.join([
                    *initlines,
                    *parse_and_compile_module("alligatorexpression", textwrap.dedent(f"""
                        def func(val1: char, val2: char) -> bool:
                            return val1 {operator} val2
                    """), settings).code,
                    "main:",
                    f"PUSHI {first!r}",
                    f"PUSHI {second!r}",
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
                expected = eval(f"{first!r} {operator} {second!r}")
                _assert(
                    result == expected,
                    "Failed to alligatorexpression, "
                    + f"got {result} instead of {expected} for {val1} {operator} {val2}!",
                )
                cycles += cpu.cycles
                instructions += cpu.ticks
                count += 1

    for first in ['apples', 'bananas', 'carrots', 'dragons']:
        for second in ['apples', 'bananas', 'carrots', 'dragons']:
            for operator in ["<=", "<", ">=", ">="]:
                memory = getmemory(os.linesep.join([
                    *initlines,
                    *parse_and_compile_module("alligatorexpression", textwrap.dedent(f"""
                        def func(val1: const[str], val2: const[str]) -> bool:
                            return val1 {operator} val2
                    """), settings).code,
                    ".org 0x1000",
                    "first:",
                    *[f".char {c!r}" for c in first],
                    ".byte 0x00",
                    ".org 0x2000",
                    "second:",
                    *[f".char {c!r}" for c in second],
                    ".byte 0x00",
                    ".org 0x3000",
                    "main:",
                    "PUSHADDR first",
                    "PUSHADDR second",
                    "LOADI 111",
                    "MOV A, U",
                    "LOADI 222",
                    "MOV A, V",
                    "LOADI 123",
                    "CALL func",
                    "HALT",
                    *cmplines,
                    *strcmplines,
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
                expected = eval(f"{first!r} {operator} {second!r}")
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

    with open("lib/runtime/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/runtime/start.S", "r") as fp:
        startlines = fp.readlines()
    with open("lib/runtime/data.S", "r") as fp:
        datalines = fp.readlines()
    with open("lib/runtime/heap.S", "r") as fp:
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
        """), settings)
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
        """), settings)
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
                """), settings)
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
                """), settings)
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

    with open("lib/runtime/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/runtime/start.S", "r") as fp:
        startlines = fp.readlines()
    with open("lib/runtime/data.S", "r") as fp:
        datalines = fp.readlines()
    with open("lib/runtime/heap.S", "r") as fp:
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
            """), settings)
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
                result = bintoint(cpu.ram[0xC000])
            elif global_width == "int16":
                result = bintoint16(
                    (cpu.ram[0xC000] << 8) + cpu.ram[0xC001]
                )
            elif global_width == "int32":
                result = bintoint32(
                    (cpu.ram[0xC000] << 24) +
                    (cpu.ram[0xC001] << 16) +
                    (cpu.ram[0xC002] << 8) +
                    cpu.ram[0xC003]
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
            """), settings)
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
                result = (cpu.ram[0xC000])
            elif global_width == "uint16":
                result = (
                    (cpu.ram[0xC000] << 8) + cpu.ram[0xC001]
                )
            elif global_width == "uint32":
                result = (
                    (cpu.ram[0xC000] << 24) +
                    (cpu.ram[0xC001] << 16) +
                    (cpu.ram[0xC002] << 8) +
                    cpu.ram[0xC003]
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
    """), settings)
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
        (cpu.ram[0xC000] << 24) +
        (cpu.ram[0xC001] << 16) +
        (cpu.ram[0xC002] << 8) +
        cpu.ram[0xC003]
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

    with open("lib/runtime/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/runtime/start.S", "r") as fp:
        startlines = fp.readlines()
    with open("lib/runtime/data.S", "r") as fp:
        datalines = fp.readlines()
    with open("lib/runtime/heap.S", "r") as fp:
        heaplines = fp.readlines()
    with open("lib/math/cmp.S", "r") as fp:
        cmplines = fp.readlines()

    cycles = 0
    instructions = 0
    count = 0

    # Mypy throws a fit because variables in Python are scoped outside of their for loops, whatever.
    input_val: Any

    # First, test if statements with no else case, both when they return and when they
    # expect to naturally flow out past the indented block.
    for input_val, expected in [(True, 15), (False, -25)]:
        sections = parse_and_compile_module("ifstatements", textwrap.dedent("""
            def simpleif(condition: bool) -> int8:
                if condition:
                    return 15
                return -25
        """), settings)
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
        """), settings)
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
        """), settings)
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
        """), settings)
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
        """), settings)
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
        """), settings)
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
        """), settings)
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
        """), settings)
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
        """), settings)
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
        """), settings)
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

    # Now, test boolean coercing from other types.
    for input_val, expected in [(1, 15), (0, -25)]:
        sections = parse_and_compile_module("ifstatements", textwrap.dedent("""
            def simpleif(condition: uint8) -> int8:
                retval: int8 = -25
                if condition:
                    retval = 15
                return retval
        """), settings)
        memory = getmemory(os.linesep.join([
            *initlines,
            *sections.init,
            *startlines,
            *sections.code,
            "main:",
            f"PUSHI {input_val}",
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
            "Failed to ifstatements int coerced, "
            + f"got {result} instead of {expected}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    for input_val, expected in [("nonempty", 15), ("", -25)]:
        sections = parse_and_compile_module("ifstatements", textwrap.dedent(f"""
            def simpleifimpl(condition: const[str]) -> int8:
                retval: int8 = -25
                if condition:
                    retval = 15
                return retval

            def simpleif() -> int8:
                return simpleifimpl({input_val!r})
        """), settings)
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
            "Failed to ifstatements string coerced, "
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

    with open("lib/runtime/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/runtime/start.S", "r") as fp:
        startlines = fp.readlines()
    with open("lib/runtime/data.S", "r") as fp:
        datalines = fp.readlines()
    with open("lib/runtime/heap.S", "r") as fp:
        heaplines = fp.readlines()
    with open("lib/math/cmp.S", "r") as fp:
        cmplines = fp.readlines()
    with open("lib/string/strcpy.S", "r") as fp:
        strcpylines = fp.readlines()

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
        """), settings)
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
        """), settings)
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
        """), settings)
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
        """), settings)
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

    # Also, verify non-boolean expressions by implementing a terrible string length.
    for val, expected in [("", 0), ("abcde", 5)]:
        sections = parse_and_compile_module("whilestatements", textwrap.dedent(f"""
            def software_strlen(instr: const[str]) -> uint8:
                local: str[64] = instr
                actual_len: uint8 = 0

                while local:
                    actual_len += 1
                    local = local[1:]

                return actual_len

            def simple_while() -> uint8:
                return software_strlen({val!r})
        """), settings)
        memory = getmemory(os.linesep.join([
            *initlines,
            *sections.init,
            *startlines,
            *cmplines,
            *strcpylines,
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
        _assert(
            result == expected,
            "Failed to whilestatements strlen implementation, "
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

    with open("lib/runtime/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/runtime/start.S", "r") as fp:
        startlines = fp.readlines()
    with open("lib/runtime/data.S", "r") as fp:
        datalines = fp.readlines()
    with open("lib/runtime/heap.S", "r") as fp:
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
        """), settings)
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
        """), settings)
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
        """), settings)
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
        """), settings)
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
        """), settings)
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
        """), settings)
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
            """), settings)
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

    with open("lib/runtime/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/runtime/start.S", "r") as fp:
        startlines = fp.readlines()
    with open("lib/runtime/data.S", "r") as fp:
        datalines = fp.readlines()
    with open("lib/runtime/heap.S", "r") as fp:
        heaplines = fp.readlines()
    with open("lib/string/strcpy.S", "r") as fp:
        strcpylines = fp.readlines()

    cycles = 0
    instructions = 0
    count = 0

    # First, see if we can return a global constant string, and that we get the right value.
    if True:
        sections = parse_and_compile_module("stringreturn", textwrap.dedent("""
            STRING_CONST: const[str] = "This is a test."

            def return_string() -> const[str]:
                return STRING_CONST
        """), settings)
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

        assertmemory("stringreturn", memory, cpu.ram)
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
            + f"got {result!r} instead of {expected!r}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    # Now, see if we can return a global non-constant string, and that we get the right value.
    if True:
        sections = parse_and_compile_module("stringreturn", textwrap.dedent("""
            string_global: str[16] = "This is a test."

            def return_string() -> str:
                return string_global
        """), settings)
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

        assertmemory("stringreturn", memory, cpu.ram)
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
        result = bintostr(cpu, (cpu.ram[cpu.pc] << 8) + cpu.ram[cpu.pc + 1], 0xC000, 0x10000)
        expected = "This is a test."
        _assert(
            result == expected,
            "Failed to stringreturn simple, "
            + f"got {result!r} instead of {expected!r}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    # Now, see if we can return a local constant string, and that we get the right value.
    if True:
        sections = parse_and_compile_module("stringreturn", textwrap.dedent("""
            def return_string() -> const[str]:
                return "This is a test."
        """), settings)
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

        assertmemory("stringreturn", memory, cpu.ram)
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
            + f"got {result!r} instead of {expected!r}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    # Now, see if we can return a local non-constant string, and that we get the right value.
    for prefix in ["", "b", "r", "u"]:
        sections = parse_and_compile_module("stringreturn", textwrap.dedent(f"""
            def return_string() -> str:
                return {prefix}"This is a test."
        """), settings)
        memory = getmemory(os.linesep.join([
            *initlines,
            *sections.init,
            *startlines,
            *sections.code,
            *strcpylines,
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

        assertmemory("stringreturn", memory, cpu.ram)
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
        result = bintostr(cpu, (cpu.ram[cpu.pc] << 8) + cpu.ram[cpu.pc + 1], 0x0000, 0xC000)
        expected = "This is a test."
        _assert(
            result == expected,
            "Failed to stringreturn simple, "
            + f"got {result!r} instead of {expected!r}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    # Now make sure raw strings work fine.
    if True:
        sections = parse_and_compile_module("stringreturn", textwrap.dedent(r"""
            def return_string() -> str:
                return r"This is a test.\n"
        """), settings)
        memory = getmemory(os.linesep.join([
            *initlines,
            *sections.init,
            *startlines,
            *sections.code,
            *strcpylines,
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

        assertmemory("stringreturn", memory, cpu.ram)
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
        result = bintostr(cpu, (cpu.ram[cpu.pc] << 8) + cpu.ram[cpu.pc + 1], 0x0000, 0xC000)
        expected = r"This is a test.\n"
        _assert(
            result == expected,
            "Failed to stringreturn simple, "
            + f"got {result!r} instead of {expected!r}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    # Now, iterate a few times on assigning local variables from constants/non constants.
    if True:
        sections = parse_and_compile_module("stringreturn", textwrap.dedent("""
            STRING_CONST: const[str] = "This is a test."

            def return_string() -> const[str]:
                LOCAL_CONST: const[str] = STRING_CONST
                return LOCAL_CONST
        """), settings)
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

        assertmemory("stringreturn", memory, cpu.ram)
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
            + f"got {result!r} instead of {expected!r}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    if True:
        sections = parse_and_compile_module("stringreturn", textwrap.dedent("""
            STRING_CONST: const[str] = "This is a test."

            def return_string() -> str:
                local: str[32] = STRING_CONST
                return local
        """), settings)
        memory = getmemory(os.linesep.join([
            *initlines,
            *sections.init,
            *startlines,
            *sections.code,
            *strcpylines,
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

        assertmemory("stringreturn", memory, cpu.ram)
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
        result = bintostr(cpu, (cpu.ram[cpu.pc] << 8) + cpu.ram[cpu.pc + 1], 0xC000, 0x10000)
        expected = "This is a test."
        _assert(
            result == expected,
            "Failed to stringreturn simple, "
            + f"got {result!r} instead of {expected!r}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    for prefix in ["", "b", "r", "u"]:
        sections = parse_and_compile_module("stringreturn", textwrap.dedent(f"""
            def return_string() -> const[str]:
                LOCAL_CONST: const[str] = {prefix}"This is a test."
                return LOCAL_CONST
        """), settings)
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

        assertmemory("stringreturn", memory, cpu.ram)
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
            + f"got {result!r} instead of {expected!r}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    for prefix in ["", "b", "r", "u"]:
        sections = parse_and_compile_module("stringreturn", textwrap.dedent(f"""
            def return_string() -> str:
                local: str[32] = {prefix}"This is a test."
                return local
        """), settings)
        memory = getmemory(os.linesep.join([
            *initlines,
            *sections.init,
            *startlines,
            *sections.code,
            *strcpylines,
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

        assertmemory("stringreturn", memory, cpu.ram)
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
        result = bintostr(cpu, (cpu.ram[cpu.pc] << 8) + cpu.ram[cpu.pc + 1], 0xC000, 0x10000)
        expected = "This is a test."
        _assert(
            result == expected,
            "Failed to stringreturn simple, "
            + f"got {result!r} instead of {expected!r}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    if True:
        sections = parse_and_compile_module("stringreturn", textwrap.dedent("""
            def return_string() -> str:
                LOCAL_CONST: const[str] = "This is a test."
                local: str[32] = LOCAL_CONST
                return local
        """), settings)
        memory = getmemory(os.linesep.join([
            *initlines,
            *sections.init,
            *startlines,
            *sections.code,
            *strcpylines,
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

        assertmemory("stringreturn", memory, cpu.ram)
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
        result = bintostr(cpu, (cpu.ram[cpu.pc] << 8) + cpu.ram[cpu.pc + 1], 0xC000, 0x10000)
        expected = "This is a test."
        _assert(
            result == expected,
            "Failed to stringreturn simple, "
            + f"got {result!r} instead of {expected!r}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    # Test if statements with uninitialized variable.
    for var in [True, False]:
        sections = parse_and_compile_module("stringreturn", textwrap.dedent("""
            def return_string(var: bool) -> str:
                local: str[32]
                if var:
                    local = "Test 1."
                else:
                    local = "Test 2."
                return local
        """), settings)
        memory = getmemory(os.linesep.join([
            *initlines,
            *sections.init,
            *startlines,
            *sections.code,
            *strcpylines,
            "main:",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            f"PUSHI {'0xFF' if var else '0x00'}",
            "LOADI 123",
            "DECPC",
            "CALL return_string",
            "HALT",
            *datalines,
            *sections.data,
            *heaplines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        assertmemory("stringreturn", memory, cpu.ram)
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
        result = bintostr(cpu, (cpu.ram[cpu.pc] << 8) + cpu.ram[cpu.pc + 1], 0xC000, 0x10000)
        expected = "Test 1." if var else "Test 2."
        _assert(
            result == expected,
            "Failed to stringreturn simple, "
            + f"got {result!r} instead of {expected!r}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    # Test if statements with initialized variable.
    for var in [True, False]:
        sections = parse_and_compile_module("stringreturn", textwrap.dedent("""
            def return_string(var: bool) -> str:
                local: str[32] = ""
                if var:
                    local = "Test 1."
                else:
                    local = "Test 2."
                return local
        """), settings)
        memory = getmemory(os.linesep.join([
            *initlines,
            *sections.init,
            *startlines,
            *sections.code,
            *strcpylines,
            "main:",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            f"PUSHI {'0xFF' if var else '0x00'}",
            "LOADI 123",
            "DECPC",
            "CALL return_string",
            "HALT",
            *datalines,
            *sections.data,
            *heaplines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        assertmemory("stringreturn", memory, cpu.ram)
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
        result = bintostr(cpu, (cpu.ram[cpu.pc] << 8) + cpu.ram[cpu.pc + 1], 0xC000, 0x10000)
        expected = "Test 1." if var else "Test 2."
        _assert(
            result == expected,
            "Failed to stringreturn simple, "
            + f"got {result!r} instead of {expected!r}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    # Test if statements with string returns.
    for var in [True, False]:
        sections = parse_and_compile_module("stringreturn", textwrap.dedent("""
            def return_string(var: bool) -> str:
                if var:
                    return "Test 1."
                else:
                    return "Test 2."
        """), settings)
        memory = getmemory(os.linesep.join([
            *initlines,
            *sections.init,
            *startlines,
            *sections.code,
            *strcpylines,
            "main:",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            f"PUSHI {'0xFF' if var else '0x00'}",
            "LOADI 123",
            "DECPC",
            "CALL return_string",
            "HALT",
            *datalines,
            *sections.data,
            *heaplines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        assertmemory("stringreturn", memory, cpu.ram)
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
        result = bintostr(cpu, (cpu.ram[cpu.pc] << 8) + cpu.ram[cpu.pc + 1], 0x0000, 0xC000)
        expected = "Test 1." if var else "Test 2."
        _assert(
            result == expected,
            "Failed to stringreturn simple, "
            + f"got {result!r} instead of {expected!r}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    for var in [True, False]:
        sections = parse_and_compile_module("stringreturn", textwrap.dedent("""
            def return_string(var: bool) -> const[str]:
                if var:
                    return "Test 1."
                else:
                    return "Test 2."
        """), settings)
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
            f"PUSHI {'0xFF' if var else '0x00'}",
            "LOADI 123",
            "DECPC",
            "CALL return_string",
            "HALT",
            *datalines,
            *sections.data,
            *heaplines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        assertmemory("stringreturn", memory, cpu.ram)
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
        expected = "Test 1." if var else "Test 2."
        _assert(
            result == expected,
            "Failed to stringreturn simple, "
            + f"got {result!r} instead of {expected!r}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    print(f"Average cycles for stringreturn: {int(cycles/count)}")
    print(f"Average instructions for stringreturn: {int(instructions/count)}")


def verifystringlength(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "stringlength" not in only and "compiler" not in only:
        return

    print("Verifying stringlength...")

    with open("lib/runtime/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/runtime/start.S", "r") as fp:
        startlines = fp.readlines()
    with open("lib/runtime/data.S", "r") as fp:
        datalines = fp.readlines()
    with open("lib/runtime/heap.S", "r") as fp:
        heaplines = fp.readlines()
    with open("lib/string/strcpy.S", "r") as fp:
        strcpylines = fp.readlines()
    with open("lib/string/strlen.S", "r") as fp:
        strlenlines = fp.readlines()

    cycles = 0
    instructions = 0
    count = 0

    # Attempt to do string length on a constant string.
    for val in ["", "Testing 1, 2, 3!", "This song is just six words long."]:
        sections = parse_and_compile_module("stringlength", textwrap.dedent(f"""
            STRING_CONST: const[str] = "{val}"

            def string_length() -> uint8:
                return len(STRING_CONST)
        """), settings)
        memory = getmemory(os.linesep.join([
            *initlines,
            *sections.init,
            *startlines,
            *sections.code,
            *strlenlines,
            "main:",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            "LOADI 123",
            "DECPC",
            "CALL string_length",
            "HALT",
            *datalines,
            *sections.data,
            *heaplines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        assertmemory("stringlength", memory, cpu.ram)
        _assert(
            cpu.a == 123,
            f"stringlength changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"stringlength changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"stringlength changed V value from {222} to {cpu.v}!",
        )
        result = bintoint(cpu.ram[cpu.pc])
        expected = len(val)
        _assert(
            result == expected,
            "Failed to stringlength simple, "
            + f"got {result!r} instead of {expected!r}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    # Attempt to do string length on a global string.
    for val in ["", "Testing 1, 2, 3!", "This song is just six words long."]:
        sections = parse_and_compile_module("stringlength", textwrap.dedent(f"""
            global_string: str[40] = "{val}"

            def string_length() -> uint8:
                return len(global_string)
        """), settings)
        memory = getmemory(os.linesep.join([
            *initlines,
            *sections.init,
            *startlines,
            *sections.code,
            *strlenlines,
            "main:",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            "LOADI 123",
            "DECPC",
            "CALL string_length",
            "HALT",
            *datalines,
            *sections.data,
            *heaplines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        assertmemory("stringlength", memory, cpu.ram)
        _assert(
            cpu.a == 123,
            f"stringlength changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"stringlength changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"stringlength changed V value from {222} to {cpu.v}!",
        )
        result = bintoint(cpu.ram[cpu.pc])
        expected = len(val)
        _assert(
            result == expected,
            "Failed to stringlength simple, "
            + f"got {result!r} instead of {expected!r}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    # Attempt to do string length on a function parameter with an intermediate variable.
    for val in ["", "Testing 1, 2, 3!", "This song is just six words long."]:
        sections = parse_and_compile_module("stringlength", textwrap.dedent(f"""
            def string_length(which: const[str]) -> uint8:
                return len(which)

            def caller() -> uint8:
                val: const[str] = "{val}"
                return string_length(val)
        """), settings)
        memory = getmemory(os.linesep.join([
            *initlines,
            *sections.init,
            *startlines,
            *sections.code,
            *strlenlines,
            *strcpylines,
            "main:",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            "LOADI 123",
            "DECPC",
            "CALL caller",
            "HALT",
            *datalines,
            *sections.data,
            *heaplines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        assertmemory("stringlength", memory, cpu.ram)
        _assert(
            cpu.a == 123,
            f"stringlength changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"stringlength changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"stringlength changed V value from {222} to {cpu.v}!",
        )
        result = bintoint(cpu.ram[cpu.pc])
        expected = len(val)
        _assert(
            result == expected,
            "Failed to stringlength simple, "
            + f"got {result!r} instead of {expected!r}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    # Attempt to do the same thing again, but this time with a mutable local string variable.
    for val in ["", "Testing 1, 2, 3!", "This song is just six words long."]:
        sections = parse_and_compile_module("stringlength", textwrap.dedent(f"""
            def string_length(which: str[64]) -> uint8:
                return len(which)

            def caller() -> uint8:
                val: const[str] = "{val}"
                return string_length(val)
        """), settings)
        memory = getmemory(os.linesep.join([
            *initlines,
            *sections.init,
            *startlines,
            *sections.code,
            *strlenlines,
            *strcpylines,
            "main:",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            "LOADI 123",
            "DECPC",
            "CALL caller",
            "HALT",
            *datalines,
            *sections.data,
            *heaplines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        assertmemory("stringlength", memory, cpu.ram)
        _assert(
            cpu.a == 123,
            f"stringlength changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"stringlength changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"stringlength changed V value from {222} to {cpu.v}!",
        )
        result = bintoint(cpu.ram[cpu.pc])
        expected = len(val)
        _assert(
            result == expected,
            "Failed to stringlength simple, "
            + f"got {result!r} instead of {expected!r}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    # Attempt to do string length on a function parameter without an intermediate variable.
    for val in ["", "Testing 1, 2, 3!", "This song is just six words long."]:
        sections = parse_and_compile_module("stringlength", textwrap.dedent(f"""
            def string_length(which: const[str]) -> uint8:
                return len(which)

            def caller() -> uint8:
                return string_length("{val}")
        """), settings)
        memory = getmemory(os.linesep.join([
            *initlines,
            *sections.init,
            *startlines,
            *sections.code,
            *strlenlines,
            *strcpylines,
            "main:",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            "LOADI 123",
            "DECPC",
            "CALL caller",
            "HALT",
            *datalines,
            *sections.data,
            *heaplines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        assertmemory("stringlength", memory, cpu.ram)
        _assert(
            cpu.a == 123,
            f"stringlength changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"stringlength changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"stringlength changed V value from {222} to {cpu.v}!",
        )
        result = bintoint(cpu.ram[cpu.pc])
        expected = len(val)
        _assert(
            result == expected,
            "Failed to stringlength simple, "
            + f"got {result!r} instead of {expected!r}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    print(f"Average cycles for stringlength: {int(cycles/count)}")
    print(f"Average instructions for stringlength: {int(instructions/count)}")


def verifystringconcatenation(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "stringconcatenation" not in only and "compiler" not in only:
        return

    print("Verifying stringconcatenation...")

    with open("lib/runtime/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/runtime/start.S", "r") as fp:
        startlines = fp.readlines()
    with open("lib/runtime/data.S", "r") as fp:
        datalines = fp.readlines()
    with open("lib/runtime/heap.S", "r") as fp:
        heaplines = fp.readlines()
    with open("lib/math/cmp.S", "r") as fp:
        cmplines = fp.readlines()
    with open("lib/string/strcpy.S", "r") as fp:
        strcpylines = fp.readlines()
    with open("lib/string/strcat.S", "r") as fp:
        strcatlines = fp.readlines()
    with open("lib/string/strlen.S", "r") as fp:
        strlenlines = fp.readlines()

    cycles = 0
    instructions = 0
    count = 0

    # Concatenate string that is passed in via parameters.
    for val in ["jen", "dragon", "world"]:
        sections = parse_and_compile_module("stringconcatenation", textwrap.dedent(f"""
            def say_hello(thing: const[str]) -> str[64]:
                return "Hello, " + thing + "!"

            def caller() -> str:
                return say_hello("{val}")
        """), settings)
        memory = getmemory(os.linesep.join([
            *initlines,
            *sections.init,
            *startlines,
            *sections.code,
            *strcpylines,
            *strcatlines,
            "main:",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            "LOADI 123",
            "SUBPCI 2",
            "CALL caller",
            "HALT",
            *datalines,
            *sections.data,
            *heaplines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        assertmemory("stringconcatenation", memory, cpu.ram)
        _assert(
            cpu.a == 123,
            f"stringconcatenation changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"stringconcatenation changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"stringconcatenation changed V value from {222} to {cpu.v}!",
        )
        result = bintostr(cpu, (cpu.ram[cpu.pc] << 8) + cpu.ram[cpu.pc + 1], 0xC000, 0x10000)
        expected = f"Hello, {val}!"
        _assert(
            result == expected,
            "Failed to stringconcatenation simple, "
            + f"got {result!r} instead of {expected!r}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    # Concatenate local string and return that.
    for val in ["jen", "dragon", "world"]:
        sections = parse_and_compile_module("stringconcatenation", textwrap.dedent(f"""
            def caller() -> str:
                local_string: str[32] = "Hello, "
                local_string += {val!r}
                local_string += "!"
                return local_string
        """), settings)
        memory = getmemory(os.linesep.join([
            *initlines,
            *sections.init,
            *startlines,
            *sections.code,
            *strcpylines,
            *strcatlines,
            "main:",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            "LOADI 123",
            "SUBPCI 2",
            "CALL caller",
            "HALT",
            *datalines,
            *sections.data,
            *heaplines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        assertmemory("stringconcatenation", memory, cpu.ram)
        _assert(
            cpu.a == 123,
            f"stringconcatenation changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"stringconcatenation changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"stringconcatenation changed V value from {222} to {cpu.v}!",
        )
        result = bintostr(cpu, (cpu.ram[cpu.pc] << 8) + cpu.ram[cpu.pc + 1], 0xC000, 0x10000)
        expected = f"Hello, {val}!"
        _assert(
            result == expected,
            "Failed to stringconcatenation simple, "
            + f"got {result!r} instead of {expected!r}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    # Concatenate stress test.
    for val in ["jen", "dragon", "world"]:
        sections = parse_and_compile_module("stringconcatenation", textwrap.dedent(f"""
            def caller() -> str:
                local_string: str[32] = {val!r}
                local_string = local_string + "123"
                local_string = "456" + local_string
                local_string = f"abc{{local_string}}def"
                local_string = ">>" + local_string + "<<"
                return local_string
        """), settings)
        memory = getmemory(os.linesep.join([
            *initlines,
            *sections.init,
            *startlines,
            *sections.code,
            *strcpylines,
            *strcatlines,
            "main:",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            "LOADI 123",
            "SUBPCI 2",
            "CALL caller",
            "HALT",
            *datalines,
            *sections.data,
            *heaplines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        assertmemory("stringconcatenation", memory, cpu.ram)
        _assert(
            cpu.a == 123,
            f"stringconcatenation changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"stringconcatenation changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"stringconcatenation changed V value from {222} to {cpu.v}!",
        )
        result = bintostr(cpu, (cpu.ram[cpu.pc] << 8) + cpu.ram[cpu.pc + 1], 0xC000, 0x10000)
        expected = f">>abc456{val}123def<<"
        _assert(
            result == expected,
            "Failed to stringconcatenation simple, "
            + f"got {result!r} instead of {expected!r}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    # Concatenate global string and return that.
    for val in ["jen", "dragon", "world"]:
        sections = parse_and_compile_module("stringconcatenation", textwrap.dedent(f"""
            global_string: str[64]

            def caller() -> const[str]:
                global global_string

                global_string = "Hello, "
                global_string += {val!r}
                global_string += "!"
                return global_string
        """), settings)
        memory = getmemory(os.linesep.join([
            *initlines,
            *sections.init,
            *startlines,
            *sections.code,
            *strcpylines,
            *strcatlines,
            "main:",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            "LOADI 123",
            "SUBPCI 2",
            "CALL caller",
            "HALT",
            *datalines,
            *sections.data,
            *heaplines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        assertmemory("stringconcatenation", memory, cpu.ram)
        _assert(
            cpu.a == 123,
            f"stringconcatenation changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"stringconcatenation changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"stringconcatenation changed V value from {222} to {cpu.v}!",
        )
        result = bintostr(cpu, (cpu.ram[cpu.pc] << 8) + cpu.ram[cpu.pc + 1], 0xC000, 0x10000)
        expected = f"Hello, {val}!"
        _assert(
            result == expected,
            "Failed to stringconcatenation simple, "
            + f"got {result!r} instead of {expected!r}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    # Concatenate string that is returned from a function.
    for val in ["jen", "dragon", "world"]:
        sections = parse_and_compile_module("stringconcatenation", textwrap.dedent(f"""
            def who() -> const[str]:
                return "{val}"

            def say_hello() -> str[64]:
                return "Hello, " + who() + "!"
        """), settings)
        memory = getmemory(os.linesep.join([
            *initlines,
            *sections.init,
            *startlines,
            *sections.code,
            *strcpylines,
            *strcatlines,
            "main:",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            "LOADI 123",
            "SUBPCI 2",
            "CALL say_hello",
            "HALT",
            *datalines,
            *sections.data,
            *heaplines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        assertmemory("stringconcatenation", memory, cpu.ram)
        _assert(
            cpu.a == 123,
            f"stringconcatenation changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"stringconcatenation changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"stringconcatenation changed V value from {222} to {cpu.v}!",
        )
        result = bintostr(cpu, (cpu.ram[cpu.pc] << 8) + cpu.ram[cpu.pc + 1], 0xC000, 0x10000)
        expected = f"Hello, {val}!"
        _assert(
            result == expected,
            "Failed to stringconcatenation simple, "
            + f"got {result!r} instead of {expected!r}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    for val in ["jen", "dragon", "world"]:
        for ending in ["?", "!", "~"]:
            sections = parse_and_compile_module("stringconcatenation", textwrap.dedent(f"""
                def who() -> const[str]:
                    return "{val}"

                def say_hello() -> str[64]:
                    ending: char = {ending!r}
                    return "Hello, " + who() + ending
            """), settings)
            memory = getmemory(os.linesep.join([
                *initlines,
                *sections.init,
                *startlines,
                *sections.code,
                *strcpylines,
                *strcatlines,
                "main:",
                "LOADI 111",
                "MOV A, U",
                "LOADI 222",
                "MOV A, V",
                "LOADI 123",
                "SUBPCI 2",
                "CALL say_hello",
                "HALT",
                *datalines,
                *sections.data,
                *heaplines,
            ]))
            cpu = CPUCore(memory)
            rununtilhalt(cpu)

            assertmemory("stringconcatenation", memory, cpu.ram)
            _assert(
                cpu.a == 123,
                f"stringconcatenation changed accumulator value from {123} to {cpu.a}!",
            )
            _assert(
                cpu.u == 111,
                f"stringconcatenation changed U value from {111} to {cpu.u}!",
            )
            _assert(
                cpu.v == 222,
                f"stringconcatenation changed V value from {222} to {cpu.v}!",
            )
            result = bintostr(cpu, (cpu.ram[cpu.pc] << 8) + cpu.ram[cpu.pc + 1], 0xC000, 0x10000)
            expected = f"Hello, {val}{ending}"
            _assert(
                result == expected,
                "Failed to stringconcatenation simple, "
                + f"got {result!r} instead of {expected!r}!",
            )
            cycles += cpu.cycles
            instructions += cpu.ticks
            count += 1

    # Write out own terrible string clone function, for shiggles.
    for val in ["jen", "dragon", "world"]:
        sections = parse_and_compile_module("stringconcatenation", textwrap.dedent(f"""
            def clone(string: const[str]) -> str:
                retval: str[16] = ""

                i: uint8
                for i in range(len(string)):
                    retval += string[i]

                return retval

            def say_hello() -> str[64]:
                return "Hello, " + clone({val!r}) + "!"
        """), settings)
        memory = getmemory(os.linesep.join([
            *initlines,
            *sections.init,
            *startlines,
            *sections.code,
            *strcpylines,
            *strcatlines,
            *strlenlines,
            *cmplines,
            "main:",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            "LOADI 123",
            "SUBPCI 2",
            "CALL say_hello",
            "HALT",
            *datalines,
            *sections.data,
            *heaplines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        assertmemory("stringconcatenation", memory, cpu.ram)
        _assert(
            cpu.a == 123,
            f"stringconcatenation changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"stringconcatenation changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"stringconcatenation changed V value from {222} to {cpu.v}!",
        )
        result = bintostr(cpu, (cpu.ram[cpu.pc] << 8) + cpu.ram[cpu.pc + 1], 0xC000, 0x10000)
        expected = f"Hello, {val}!"
        _assert(
            result == expected,
            "Failed to stringconcatenation simple, "
            + f"got {result!r} instead of {expected!r}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    print(f"Average cycles for stringconcatenation: {int(cycles/count)}")
    print(f"Average instructions for stringconcatenation: {int(instructions/count)}")


def verifystringsubscript(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "stringsubscript" not in only and "compiler" not in only:
        return

    print("Verifying stringsubscript...")

    with open("lib/runtime/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/runtime/start.S", "r") as fp:
        startlines = fp.readlines()
    with open("lib/runtime/data.S", "r") as fp:
        datalines = fp.readlines()
    with open("lib/runtime/heap.S", "r") as fp:
        heaplines = fp.readlines()
    with open("lib/string/strcpy.S", "r") as fp:
        strcpylines = fp.readlines()

    cycles = 0
    instructions = 0
    count = 0

    # First, test constant evaluation in the compiler.
    for val in ["jen", "dragon", "world"]:
        sections = parse_and_compile_module("stringsubscript", textwrap.dedent(f"""
            def subscript() -> char:
                return "{val}"[2]
        """), settings)
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
            "CALL subscript",
            "HALT",
            *datalines,
            *sections.data,
            *heaplines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        assertmemory("stringsubscript", memory, cpu.ram)
        _assert(
            cpu.a == 123,
            f"stringsubscript changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"stringsubscript changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"stringsubscript changed V value from {222} to {cpu.v}!",
        )
        result = bintochar(cpu.ram[cpu.pc])
        expected = val[2]
        _assert(
            result == expected,
            "Failed to stringsubscript simple, "
            + f"got {result!r} instead of {expected!r}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    for val in ["jen", "dragon", "world"]:
        sections = parse_and_compile_module("stringsubscript", textwrap.dedent(f"""
            CONST_STR: const[str] = "{val}"

            def subscript() -> char:
                return CONST_STR[2]
        """), settings)
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
            "CALL subscript",
            "HALT",
            *datalines,
            *sections.data,
            *heaplines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        assertmemory("stringsubscript", memory, cpu.ram)
        _assert(
            cpu.a == 123,
            f"stringsubscript changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"stringsubscript changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"stringsubscript changed V value from {222} to {cpu.v}!",
        )
        result = bintochar(cpu.ram[cpu.pc])
        expected = val[2]
        _assert(
            result == expected,
            "Failed to stringsubscript simple, "
            + f"got {result!r} instead of {expected!r}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    # Now, verify non-constant global loads.
    for val in ["jen", "dragon", "world"]:
        sections = parse_and_compile_module("stringsubscript", textwrap.dedent(f"""
            global_str: str[16] = "{val}"

            def subscript() -> char:
                return global_str[2]
        """), settings)
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
            "CALL subscript",
            "HALT",
            *datalines,
            *sections.data,
            *heaplines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        assertmemory("stringsubscript", memory, cpu.ram)
        _assert(
            cpu.a == 123,
            f"stringsubscript changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"stringsubscript changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"stringsubscript changed V value from {222} to {cpu.v}!",
        )
        result = bintochar(cpu.ram[cpu.pc])
        expected = val[2]
        _assert(
            result == expected,
            "Failed to stringsubscript simple, "
            + f"got {result!r} instead of {expected!r}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    # Now, verify expression result evaluation subscript.
    for val in ["jen", "dragon", "world"]:
        sections = parse_and_compile_module("stringsubscript", textwrap.dedent(f"""
            def subscript() -> char:
                some_str: str[16]
                some_str = "{val}" + "!"
                return some_str[2]
        """), settings)
        memory = getmemory(os.linesep.join([
            *initlines,
            *sections.init,
            *startlines,
            *sections.code,
            *strcpylines,
            "main:",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            "LOADI 123",
            "DECPC",
            "CALL subscript",
            "HALT",
            *datalines,
            *sections.data,
            *heaplines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        assertmemory("stringsubscript", memory, cpu.ram)
        _assert(
            cpu.a == 123,
            f"stringsubscript changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"stringsubscript changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"stringsubscript changed V value from {222} to {cpu.v}!",
        )
        result = bintochar(cpu.ram[cpu.pc])
        expected = val[2]
        _assert(
            result == expected,
            "Failed to stringsubscript simple, "
            + f"got {result!r} instead of {expected!r}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    for val in ["jen", "dragon", "world"]:
        sections = parse_and_compile_module("stringsubscript", textwrap.dedent(f"""
            def getstr() -> const[str]:
                return "{val}"

            def subscript() -> char:
                return getstr()[2]
        """), settings)
        memory = getmemory(os.linesep.join([
            *initlines,
            *sections.init,
            *startlines,
            *sections.code,
            *strcpylines,
            "main:",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            "LOADI 123",
            "DECPC",
            "CALL subscript",
            "HALT",
            *datalines,
            *sections.data,
            *heaplines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        assertmemory("stringsubscript", memory, cpu.ram)
        _assert(
            cpu.a == 123,
            f"stringsubscript changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"stringsubscript changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"stringsubscript changed V value from {222} to {cpu.v}!",
        )
        result = bintochar(cpu.ram[cpu.pc])
        expected = val[2]
        _assert(
            result == expected,
            "Failed to stringsubscript simple, "
            + f"got {result!r} instead of {expected!r}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    # Now, test variable subscripts.
    for val in ["jen", "dragon", "world"]:
        for loc in [0, 1, 2]:
            sections = parse_and_compile_module("stringsubscript", textwrap.dedent(f"""
                def subscript(loc: uint8) -> char:
                    return "{val}"[loc]
            """), settings)
            memory = getmemory(os.linesep.join([
                *initlines,
                *sections.init,
                *startlines,
                *sections.code,
                "main:",
                f"PUSHI {loc}",
                "LOADI 111",
                "MOV A, U",
                "LOADI 222",
                "MOV A, V",
                "LOADI 123",
                "CALL subscript",
                "HALT",
                *datalines,
                *sections.data,
                *heaplines,
            ]))
            cpu = CPUCore(memory)
            rununtilhalt(cpu)

            assertmemory("stringsubscript", memory, cpu.ram)
            _assert(
                cpu.a == 123,
                f"stringsubscript changed accumulator value from {123} to {cpu.a}!",
            )
            _assert(
                cpu.u == 111,
                f"stringsubscript changed U value from {111} to {cpu.u}!",
            )
            _assert(
                cpu.v == 222,
                f"stringsubscript changed V value from {222} to {cpu.v}!",
            )
            result = bintochar(cpu.ram[cpu.pc])
            expected = val[loc]
            _assert(
                result == expected,
                "Failed to stringsubscript simple, "
                + f"got {result!r} instead of {expected!r}!",
            )
            cycles += cpu.cycles
            instructions += cpu.ticks
            count += 1

    for val in ["jen", "dragon", "world"]:
        for loc in [0, 1, 2]:
            sections = parse_and_compile_module("stringsubscript", textwrap.dedent(f"""
                def subscript_impl(str: const[str], loc: uint8) -> char:
                    return str[loc]

                def subscript(loc: uint8) -> char:
                    return subscript_impl("{val}", loc)
            """), settings)
            memory = getmemory(os.linesep.join([
                *initlines,
                *sections.init,
                *startlines,
                *sections.code,
                *strcpylines,
                "main:",
                f"PUSHI {loc}",
                "LOADI 111",
                "MOV A, U",
                "LOADI 222",
                "MOV A, V",
                "LOADI 123",
                "CALL subscript",
                "HALT",
                *datalines,
                *sections.data,
                *heaplines,
            ]))
            cpu = CPUCore(memory)
            rununtilhalt(cpu)

            assertmemory("stringsubscript", memory, cpu.ram)
            _assert(
                cpu.a == 123,
                f"stringsubscript changed accumulator value from {123} to {cpu.a}!",
            )
            _assert(
                cpu.u == 111,
                f"stringsubscript changed U value from {111} to {cpu.u}!",
            )
            _assert(
                cpu.v == 222,
                f"stringsubscript changed V value from {222} to {cpu.v}!",
            )
            result = bintochar(cpu.ram[cpu.pc])
            expected = val[loc]
            _assert(
                result == expected,
                "Failed to stringsubscript simple, "
                + f"got {result!r} instead of {expected!r}!",
            )
            cycles += cpu.cycles
            instructions += cpu.ticks
            count += 1

    print(f"Average cycles for stringsubscript: {int(cycles/count)}")
    print(f"Average instructions for stringsubscript: {int(instructions/count)}")


def verifystringslice(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "stringslice" not in only and "compiler" not in only:
        return

    print("Verifying stringslice...")

    with open("lib/runtime/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/runtime/start.S", "r") as fp:
        startlines = fp.readlines()
    with open("lib/runtime/data.S", "r") as fp:
        datalines = fp.readlines()
    with open("lib/runtime/heap.S", "r") as fp:
        heaplines = fp.readlines()
    with open("lib/string/strcpy.S", "r") as fp:
        strcpylines = fp.readlines()

    cycles = 0
    instructions = 0
    count = 0

    # First, test constant evaluation in the compiler.
    for sliceval in [":", ":8", "4:", "4:8"]:
        sliceable = "this is a test"
        sections = parse_and_compile_module("stringslice", textwrap.dedent(f"""
            def sliceme() -> str[32]:
                var: str[32] = {sliceable!r}
                return var[{sliceval}]
        """), settings)
        memory = getmemory(os.linesep.join([
            *initlines,
            *sections.init,
            *startlines,
            *sections.code,
            *strcpylines,
            "main:",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            "LOADI 123",
            "SUBPCI 2",
            "CALL sliceme",
            "HALT",
            *datalines,
            *sections.data,
            *heaplines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        assertmemory("stringslice", memory, cpu.ram)
        _assert(
            cpu.a == 123,
            f"stringslice changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"stringslice changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"stringslice changed V value from {222} to {cpu.v}!",
        )
        result = bintostr(cpu, (cpu.ram[cpu.pc] << 8) + cpu.ram[cpu.pc + 1], 0xC000, 0x10000)
        expected = eval(f'"{sliceable}"[{sliceval}]')
        _assert(
            result == expected,
            "Failed to stringslice simple, "
            + f"got {result!r} instead of {expected!r}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    # Now, test expression evaluation with constant slices.
    for sliceval in [":", ":8", "4:", "4:8"]:
        sliceable = "this is a test"
        sections = parse_and_compile_module("stringslice", textwrap.dedent(f"""
            def getstr() -> const[str]:
                return "{sliceable}"

            def sliceme() -> str[32]:
                return getstr()[{sliceval}]
        """), settings)
        memory = getmemory(os.linesep.join([
            *initlines,
            *sections.init,
            *startlines,
            *sections.code,
            *strcpylines,
            "main:",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            "LOADI 123",
            "SUBPCI 2",
            "CALL sliceme",
            "HALT",
            *datalines,
            *sections.data,
            *heaplines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        assertmemory("stringslice", memory, cpu.ram)
        _assert(
            cpu.a == 123,
            f"stringslice changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"stringslice changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"stringslice changed V value from {222} to {cpu.v}!",
        )
        result = bintostr(cpu, (cpu.ram[cpu.pc] << 8) + cpu.ram[cpu.pc + 1], 0xC000, 0x10000)
        expected = eval(f'"{sliceable}"[{sliceval}]')
        _assert(
            result == expected,
            "Failed to stringslice simple, "
            + f"got {result!r} instead of {expected!r}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    # Now test non-constant slice values
    for sliceint in [0, 2, 4, 8, 16]:
        sliceable = "this is a test"
        sections = parse_and_compile_module("stringslice", textwrap.dedent(f"""
            def getstr() -> const[str]:
                return "{sliceable}"

            def sliceme(loc: uint8) -> str[32]:
                return getstr()[:loc]
        """), settings)
        memory = getmemory(os.linesep.join([
            *initlines,
            *sections.init,
            *startlines,
            *sections.code,
            *strcpylines,
            "main:",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            f"PUSHI {sliceint}",
            "DECPC",
            "LOADI 123",
            "CALL sliceme",
            "HALT",
            *datalines,
            *sections.data,
            *heaplines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        assertmemory("stringslice", memory, cpu.ram)
        _assert(
            cpu.a == 123,
            f"stringslice changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"stringslice changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"stringslice changed V value from {222} to {cpu.v}!",
        )
        result = bintostr(cpu, (cpu.ram[cpu.pc] << 8) + cpu.ram[cpu.pc + 1], 0xC000, 0x10000)
        expected = sliceable[:sliceint]
        _assert(
            result == expected,
            "Failed to stringslice simple, "
            + f"got {result!r} instead of {expected!r}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    for sliceint in [0, 2, 4, 8, 16]:
        sliceable = "this is a test"
        sections = parse_and_compile_module("stringslice", textwrap.dedent(f"""
            def getstr() -> const[str]:
                return "{sliceable}"

            def sliceme(loc: uint8) -> str[32]:
                return getstr()[loc:]
        """), settings)
        memory = getmemory(os.linesep.join([
            *initlines,
            *sections.init,
            *startlines,
            *sections.code,
            *strcpylines,
            "main:",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            f"PUSHI {sliceint}",
            "DECPC",
            "LOADI 123",
            "CALL sliceme",
            "HALT",
            *datalines,
            *sections.data,
            *heaplines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        assertmemory("stringslice", memory, cpu.ram)
        _assert(
            cpu.a == 123,
            f"stringslice changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"stringslice changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"stringslice changed V value from {222} to {cpu.v}!",
        )
        result = bintostr(cpu, (cpu.ram[cpu.pc] << 8) + cpu.ram[cpu.pc + 1], 0xC000, 0x10000)
        expected = sliceable[sliceint:]
        _assert(
            result == expected,
            "Failed to stringslice simple, "
            + f"got {result!r} instead of {expected!r}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    # Now, test slices with both a start and an end.
    for sliceint in [0, 2, 4, 8, 16]:
        for extendval in [0, 1, 3, 7, 11]:
            sliceable = "this is a test"
            sections = parse_and_compile_module("stringslice", textwrap.dedent(f"""
                def getstr() -> const[str]:
                    return "{sliceable}"

                def sliceme(loc1: uint8, loc2: uint8) -> str[32]:
                    return getstr()[loc1:loc2]
            """), settings)
            memory = getmemory(os.linesep.join([
                *initlines,
                *sections.init,
                *startlines,
                *sections.code,
                *strcpylines,
                "main:",
                "LOADI 111",
                "MOV A, U",
                "LOADI 222",
                "MOV A, V",
                f"PUSHI {sliceint}",
                f"PUSHI {sliceint + extendval}",
                "LOADI 123",
                "CALL sliceme",
                "HALT",
                *datalines,
                *sections.data,
                *heaplines,
            ]))
            cpu = CPUCore(memory)
            rununtilhalt(cpu)

            assertmemory("stringslice", memory, cpu.ram)
            _assert(
                cpu.a == 123,
                f"stringslice changed accumulator value from {123} to {cpu.a}!",
            )
            _assert(
                cpu.u == 111,
                f"stringslice changed U value from {111} to {cpu.u}!",
            )
            _assert(
                cpu.v == 222,
                f"stringslice changed V value from {222} to {cpu.v}!",
            )
            result = bintostr(cpu, (cpu.ram[cpu.pc] << 8) + cpu.ram[cpu.pc + 1], 0xC000, 0x10000)
            expected = sliceable[sliceint:(sliceint + extendval)]
            _assert(
                result == expected,
                "Failed to stringslice simple, "
                + f"got {result!r} instead of {expected!r}!",
            )
            cycles += cpu.cycles
            instructions += cpu.ticks
            count += 1

    print(f"Average cycles for stringslice: {int(cycles/count)}")
    print(f"Average instructions for stringslice: {int(instructions/count)}")


def verifystringassignment(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "stringassignment" not in only and "compiler" not in only:
        return

    print("Verifying stringassignment...")

    with open("lib/runtime/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/runtime/start.S", "r") as fp:
        startlines = fp.readlines()
    with open("lib/runtime/data.S", "r") as fp:
        datalines = fp.readlines()
    with open("lib/runtime/heap.S", "r") as fp:
        heaplines = fp.readlines()
    with open("lib/string/strcpy.S", "r") as fp:
        strcpylines = fp.readlines()

    cycles = 0
    instructions = 0
    count = 0

    # Verify local assignment updates.
    for offset in [0, 2, 4, 8]:
        for updated in ['~', '!', '*']:
            sliceable = "this is a test"
            sections = parse_and_compile_module("stringassignment", textwrap.dedent(f"""
                def set_char(string: str[32], offset: uint8, val: char) -> str:
                    string[offset] = val
                    return string

                def updateme() -> str:
                    sliceable: str[32] = {sliceable!r}
                    return set_char(sliceable, {offset}, {updated!r})
            """), settings)
            memory = getmemory(os.linesep.join([
                *initlines,
                *sections.init,
                *startlines,
                *sections.code,
                *strcpylines,
                "main:",
                "LOADI 111",
                "MOV A, U",
                "LOADI 222",
                "MOV A, V",
                "LOADI 123",
                "SUBPCI 2",
                "CALL updateme",
                "HALT",
                *datalines,
                *sections.data,
                *heaplines,
            ]))
            cpu = CPUCore(memory)
            rununtilhalt(cpu)

            assertmemory("stringassignment", memory, cpu.ram)
            _assert(
                cpu.a == 123,
                f"stringassignment changed accumulator value from {123} to {cpu.a}!",
            )
            _assert(
                cpu.u == 111,
                f"stringassignment changed U value from {111} to {cpu.u}!",
            )
            _assert(
                cpu.v == 222,
                f"stringassignment changed V value from {222} to {cpu.v}!",
            )
            result = bintostr(cpu, (cpu.ram[cpu.pc] << 8) + cpu.ram[cpu.pc + 1], 0xC000, 0x10000)
            expected = sliceable[:offset] + updated + sliceable[(offset + 1):]
            _assert(
                result == expected,
                "Failed to stringassignment simple, "
                + f"got {result!r} instead of {expected!r}!",
            )
            cycles += cpu.cycles
            instructions += cpu.ticks
            count += 1

    # Verify global variable character setting.
    for offset in [0, 2, 4, 8]:
        for updated in ['~', '!', '*']:
            sliceable = "this is a test"
            sections = parse_and_compile_module("stringassignment", textwrap.dedent(f"""
                global_var: str[32] = {sliceable!r}

                def set_char(offset: uint8, val: char) -> const[str]:
                    global_var[offset] = val
                    return global_var

                def updateme() -> const[str]:
                    return set_char({offset}, {updated!r})
            """), settings)
            memory = getmemory(os.linesep.join([
                *initlines,
                *sections.init,
                *startlines,
                *sections.code,
                *strcpylines,
                "main:",
                "LOADI 111",
                "MOV A, U",
                "LOADI 222",
                "MOV A, V",
                "LOADI 123",
                "SUBPCI 2",
                "CALL updateme",
                "HALT",
                *datalines,
                *sections.data,
                *heaplines,
            ]))
            cpu = CPUCore(memory)
            rununtilhalt(cpu)

            assertmemory("stringassignment", memory, cpu.ram)
            _assert(
                cpu.a == 123,
                f"stringassignment changed accumulator value from {123} to {cpu.a}!",
            )
            _assert(
                cpu.u == 111,
                f"stringassignment changed U value from {111} to {cpu.u}!",
            )
            _assert(
                cpu.v == 222,
                f"stringassignment changed V value from {222} to {cpu.v}!",
            )
            result = bintostr(cpu, (cpu.ram[cpu.pc] << 8) + cpu.ram[cpu.pc + 1], 0xC000, 0x10000)
            expected = sliceable[:offset] + updated + sliceable[(offset + 1):]
            _assert(
                result == expected,
                "Failed to stringassignment simple, "
                + f"got {result!r} instead of {expected!r}!",
            )
            cycles += cpu.cycles
            instructions += cpu.ticks
            count += 1

    # Now, verify that when we assign a global variable, we strcpy as we should under the hood.
    for setval in [True, False]:
        sections = parse_and_compile_module("stringassignment", textwrap.dedent("""
            global_string: str[16] = ""

            def set_global(bval: bool) -> void:
                global global_string

                if bval:
                    global_string = "Hello"
                else:
                    global_string = "Goodbye"

            def verifyset(bval: bool) -> str:
                set_global(bval)

                return global_string

        """), settings)
        memory = getmemory(os.linesep.join([
            *initlines,
            *sections.init,
            *startlines,
            *sections.code,
            *strcpylines,
            "main:",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            f"PUSHI {"0xFF" if setval else "0x00"}",
            "SUBPCI 1",
            "LOADI 123",
            "CALL verifyset",
            "HALT",
            *datalines,
            *sections.data,
            *heaplines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        assertmemory("stringassignment", memory, cpu.ram)
        _assert(
            cpu.a == 123,
            f"stringassignment changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"stringassignment changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"stringassignment changed V value from {222} to {cpu.v}!",
        )
        result = bintostr(cpu, (cpu.ram[cpu.pc] << 8) + cpu.ram[cpu.pc + 1], 0xC000, 0x10000)
        expected = "Hello" if setval else "Goodbye"
        _assert(
            result == expected,
            "Failed to stringassignment simple, "
            + f"got {result!r} instead of {expected!r}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    print(f"Average cycles for stringassignment: {int(cycles/count)}")
    print(f"Average instructions for stringassignment: {int(instructions/count)}")


def verifystringcast(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "stringcast" not in only and "compiler" not in only:
        return

    print("Verifying stringcast...")

    with open("lib/runtime/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/runtime/start.S", "r") as fp:
        startlines = fp.readlines()
    with open("lib/runtime/data.S", "r") as fp:
        datalines = fp.readlines()
    with open("lib/runtime/heap.S", "r") as fp:
        heaplines = fp.readlines()
    with open("lib/string/strcpy.S", "r") as fp:
        strcpylines = fp.readlines()
    with open("lib/conversion/itoa.S", "r") as fp:
        itoalines = fp.readlines()
    with open("lib/math/divide.S", "r") as fp:
        dividelines = fp.readlines()
    with open("lib/math/add.S", "r") as fp:
        addlines = fp.readlines()
    with open("lib/math/neg.S", "r") as fp:
        neglines = fp.readlines()
    with open("lib/math/cmp.S", "r") as fp:
        cmplines = fp.readlines()

    cycles = 0
    instructions = 0
    count = 0

    # Verify casting from characters.
    for char in ['a', 'b', 'c', 'd']:
        sections = parse_and_compile_module("stringcast", textwrap.dedent("""
            def castme(c: char) -> str:
                lvar: str[16] = str(c)
                return lvar
        """), settings)
        memory = getmemory(os.linesep.join([
            *initlines,
            *sections.init,
            *startlines,
            *sections.code,
            *strcpylines,
            "main:",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            f"PUSHI {char!r}",
            "SUBPCI 1",
            "LOADI 123",
            "CALL castme",
            "HALT",
            *datalines,
            *sections.data,
            *heaplines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        assertmemory("stringcast", memory, cpu.ram)
        _assert(
            cpu.a == 123,
            f"stringcast changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"stringcast changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"stringcast changed V value from {222} to {cpu.v}!",
        )
        result = bintostr(cpu, (cpu.ram[cpu.pc] << 8) + cpu.ram[cpu.pc + 1], 0xC000, 0x10000)
        expected = str(char)
        _assert(
            result == expected,
            "Failed to stringcast character, "
            + f"got {result!r} instead of {expected!r}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    # Verify casting from booleans.
    for boolean in [True, False]:
        sections = parse_and_compile_module("stringcast", textwrap.dedent("""
            def castme(b: bool) -> str:
                lvar: str[16] = str(b)
                return lvar
        """), settings)
        memory = getmemory(os.linesep.join([
            *initlines,
            *sections.init,
            *startlines,
            *sections.code,
            *strcpylines,
            "main:",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            f"PUSHI {"0xFF" if boolean else "0x00"}",
            "SUBPCI 1",
            "LOADI 123",
            "CALL castme",
            "HALT",
            *datalines,
            *sections.data,
            *heaplines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        assertmemory("stringcast", memory, cpu.ram)
        _assert(
            cpu.a == 123,
            f"stringcast changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"stringcast changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"stringcast changed V value from {222} to {cpu.v}!",
        )
        result = bintostr(cpu, (cpu.ram[cpu.pc] << 8) + cpu.ram[cpu.pc + 1], 0xC000, 0x10000)
        expected = str(boolean)
        _assert(
            result == expected,
            "Failed to stringcast boolean, "
            + f"got {result!r} instead of {expected!r}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    # Verify casting from strings.
    for string in ["testing", "derg derg derg"]:
        sections = parse_and_compile_module("stringcast", textwrap.dedent(f"""
            def castme_impl(s: const[str]) -> str:
                lvar: str[16] = str(s)
                return lvar

            def castme() -> str:
                lvar: const[str] = {string!r}
                return castme_impl(lvar)
        """), settings)
        memory = getmemory(os.linesep.join([
            *initlines,
            *sections.init,
            *startlines,
            *sections.code,
            *strcpylines,
            "main:",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            "SUBPCI 2",
            "LOADI 123",
            "CALL castme",
            "HALT",
            *datalines,
            *sections.data,
            *heaplines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        assertmemory("stringcast", memory, cpu.ram)
        _assert(
            cpu.a == 123,
            f"stringcast changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"stringcast changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"stringcast changed V value from {222} to {cpu.v}!",
        )
        result = bintostr(cpu, (cpu.ram[cpu.pc] << 8) + cpu.ram[cpu.pc + 1], 0xC000, 0x10000)
        expected = str(string)
        _assert(
            result == expected,
            "Failed to stringcast string, "
            + f"got {result!r} instead of {expected!r}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    # Verify casting from integers.
    for integer, itype in [
        (0, "uint8"),
        (0, "int8"),
        (37, "uint8"),
        (37, "int8"),
        (127, "uint8"),
        (127, "int8"),
        (200, "uint8"),
        (-37, "int8"),
        (255, "uint8"),
        (-128, "int8"),
    ]:
        sections = parse_and_compile_module("stringcast", textwrap.dedent(f"""
            def castme(i: {itype}) -> str:
                lvar: str[16] = str(i)
                return lvar
        """), settings)
        memory = getmemory(os.linesep.join([
            *initlines,
            *sections.init,
            *startlines,
            *sections.code,
            *strcpylines,
            *itoalines,
            *dividelines,
            *neglines,
            *addlines,
            *cmplines,
            "main:",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            f"PUSHI {integer}",
            "SUBPCI 1",
            "LOADI 123",
            "CALL castme",
            "HALT",
            *datalines,
            *sections.data,
            *heaplines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        assertmemory("stringcast", memory, cpu.ram)
        _assert(
            cpu.a == 123,
            f"stringcast changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"stringcast changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"stringcast changed V value from {222} to {cpu.v}!",
        )
        result = bintostr(cpu, (cpu.ram[cpu.pc] << 8) + cpu.ram[cpu.pc + 1], 0xC000, 0x10000)
        expected = str(integer)
        _assert(
            result == expected,
            "Failed to stringcast 8 bit integer, "
            + f"got {result!r} instead of {expected!r}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    for integer, itype in [
        (0, "uint16"),
        (0, "int16"),
        (37, "uint16"),
        (37, "int16"),
        (12345, "uint16"),
        (12345, "int16"),
        (45678, "uint16"),
        (-12345, "int16"),
        (65535, "uint16"),
        (-32768, "int16"),
    ]:
        sections = parse_and_compile_module("stringcast", textwrap.dedent(f"""
            def castme(i: {itype}) -> str:
                lvar: str[16] = str(i)
                return lvar
        """), settings)
        memory = getmemory(os.linesep.join([
            *initlines,
            *sections.init,
            *startlines,
            *sections.code,
            *strcpylines,
            *itoalines,
            *dividelines,
            *neglines,
            *addlines,
            *cmplines,
            "main:",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            f"PUSHI {integer & 0xFF}",
            f"PUSHI {(integer >> 8) & 0xFF}",
            "LOADI 123",
            "CALL castme",
            "HALT",
            *datalines,
            *sections.data,
            *heaplines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        assertmemory("stringcast", memory, cpu.ram)
        _assert(
            cpu.a == 123,
            f"stringcast changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"stringcast changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"stringcast changed V value from {222} to {cpu.v}!",
        )
        result = bintostr(cpu, (cpu.ram[cpu.pc] << 8) + cpu.ram[cpu.pc + 1], 0xC000, 0x10000)
        expected = str(integer)
        _assert(
            result == expected,
            "Failed to stringcast 16 bit integer, "
            + f"got {result!r} instead of {expected!r}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    for integer, itype in [
        (0, "uint32"),
        (0, "int32"),
        (37, "uint32"),
        (37, "int32"),
        (12345, "uint32"),
        (12345, "int32"),
        (45678, "uint32"),
        (-12345, "int32"),
        (65535, "uint32"),
        (-32768, "int32"),
        (2**32 - 1, "uint32"),
        (-2**31, "int32"),
    ]:
        sections = parse_and_compile_module("stringcast", textwrap.dedent(f"""
            def castme(i: {itype}) -> str:
                lvar: str[16] = str(i)
                return lvar
        """), settings)
        memory = getmemory(os.linesep.join([
            *initlines,
            *sections.init,
            *startlines,
            *sections.code,
            *strcpylines,
            *itoalines,
            *dividelines,
            *neglines,
            *addlines,
            *cmplines,
            "main:",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            f"PUSHI {integer & 0xFF}",
            f"PUSHI {(integer >> 8) & 0xFF}",
            f"PUSHI {(integer >> 16) & 0xFF}",
            f"PUSHI {(integer >> 24) & 0xFF}",
            "LOADI 123",
            "CALL castme",
            "HALT",
            *datalines,
            *sections.data,
            *heaplines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        assertmemory("stringcast", memory, cpu.ram)
        _assert(
            cpu.a == 123,
            f"stringcast changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"stringcast changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"stringcast changed V value from {222} to {cpu.v}!",
        )
        result = bintostr(cpu, (cpu.ram[cpu.pc] << 8) + cpu.ram[cpu.pc + 1], 0xC000, 0x10000)
        expected = str(integer)
        _assert(
            result == expected,
            "Failed to stringcast 32 bit integer, "
            + f"got {result!r} instead of {expected!r}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    print(f"Average cycles for stringcast: {int(cycles/count)}")
    print(f"Average instructions for stringcast: {int(instructions/count)}")


def verifystringformat(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "stringformat" not in only and "compiler" not in only:
        return

    print("Verifying stringformat...")

    with open("lib/runtime/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/runtime/start.S", "r") as fp:
        startlines = fp.readlines()
    with open("lib/runtime/data.S", "r") as fp:
        datalines = fp.readlines()
    with open("lib/runtime/heap.S", "r") as fp:
        heaplines = fp.readlines()
    with open("lib/string/strcpy.S", "r") as fp:
        strcpylines = fp.readlines()
    with open("lib/string/strcat.S", "r") as fp:
        strcatlines = fp.readlines()
    with open("lib/conversion/itoa.S", "r") as fp:
        itoalines = fp.readlines()
    with open("lib/math/divide.S", "r") as fp:
        dividelines = fp.readlines()
    with open("lib/math/add.S", "r") as fp:
        addlines = fp.readlines()
    with open("lib/math/neg.S", "r") as fp:
        neglines = fp.readlines()
    with open("lib/math/cmp.S", "r") as fp:
        cmplines = fp.readlines()

    cycles = 0
    instructions = 0
    count = 0

    # Verify f-strings with other strings.
    for string in ["dragon", "jen", "test"]:
        sections = parse_and_compile_module("stringformat", textwrap.dedent(f"""
            def formatme(string: const[str]) -> str[100]:
                return f"A string: {{string}}"

            def call() -> str:
                return formatme({string!r})
        """), settings)
        memory = getmemory(os.linesep.join([
            *initlines,
            *sections.init,
            *startlines,
            *sections.code,
            *strcpylines,
            *strcatlines,
            "main:",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            "LOADI 123",
            "SUBPCI 2",
            "CALL call",
            "HALT",
            *datalines,
            *sections.data,
            *heaplines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        assertmemory("stringformat", memory, cpu.ram)
        _assert(
            cpu.a == 123,
            f"stringformat changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"stringformat changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"stringformat changed V value from {222} to {cpu.v}!",
        )
        result = bintostr(cpu, (cpu.ram[cpu.pc] << 8) + cpu.ram[cpu.pc + 1], 0xC000, 0x10000)
        expected = f"A string: {string}"
        _assert(
            result == expected,
            "Failed to stringformat string, "
            + f"got {result!r} instead of {expected!r}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    # Verify f-strings with characters.
    for char in ["a", "b", "d", "z"]:
        sections = parse_and_compile_module("stringformat", textwrap.dedent("""
            def formatme(ch: char) -> str[100]:
                return f"A character: {ch}"
        """), settings)
        memory = getmemory(os.linesep.join([
            *initlines,
            *sections.init,
            *startlines,
            *sections.code,
            *strcpylines,
            *strcatlines,
            "main:",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            f"PUSHI {char!r}",
            "SUBPCI 1",
            "LOADI 123",
            "CALL formatme",
            "HALT",
            *datalines,
            *sections.data,
            *heaplines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        assertmemory("stringformat", memory, cpu.ram)
        _assert(
            cpu.a == 123,
            f"stringformat changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"stringformat changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"stringformat changed V value from {222} to {cpu.v}!",
        )
        result = bintostr(cpu, (cpu.ram[cpu.pc] << 8) + cpu.ram[cpu.pc + 1], 0xC000, 0x10000)
        expected = f"A character: {char}"
        _assert(
            result == expected,
            "Failed to stringformat character, "
            + f"got {result!r} instead of {expected!r}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    # Verify f-strings with booleans.
    for boolean in [True, False]:
        sections = parse_and_compile_module("stringformat", textwrap.dedent("""
            def formatme(b: bool) -> str[100]:
                return f"A boolean: {b}"
        """), settings)
        memory = getmemory(os.linesep.join([
            *initlines,
            *sections.init,
            *startlines,
            *sections.code,
            *strcpylines,
            *strcatlines,
            "main:",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            f"PUSHI {'0xFF' if boolean else '0x00'}",
            "SUBPCI 1",
            "LOADI 123",
            "CALL formatme",
            "HALT",
            *datalines,
            *sections.data,
            *heaplines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        assertmemory("stringformat", memory, cpu.ram)
        _assert(
            cpu.a == 123,
            f"stringformat changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"stringformat changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"stringformat changed V value from {222} to {cpu.v}!",
        )
        result = bintostr(cpu, (cpu.ram[cpu.pc] << 8) + cpu.ram[cpu.pc + 1], 0xC000, 0x10000)
        expected = f"A boolean: {boolean}"
        _assert(
            result == expected,
            "Failed to stringformat boolean, "
            + f"got {result!r} instead of {expected!r}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    # Verify f-strings with integers.
    for integer in [0, 37, -37, 69, 100, -100]:
        sections = parse_and_compile_module("stringformat", textwrap.dedent("""
            def formatme(i: int8) -> str[100]:
                return f"An integer: {i}"
        """), settings)
        memory = getmemory(os.linesep.join([
            *initlines,
            *sections.init,
            *startlines,
            *sections.code,
            *strcpylines,
            *strcatlines,
            *itoalines,
            *dividelines,
            *neglines,
            *addlines,
            *cmplines,
            "main:",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            f"PUSHI {integer}",
            "SUBPCI 1",
            "LOADI 123",
            "CALL formatme",
            "HALT",
            *datalines,
            *sections.data,
            *heaplines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        assertmemory("stringformat", memory, cpu.ram)
        _assert(
            cpu.a == 123,
            f"stringformat changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"stringformat changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"stringformat changed V value from {222} to {cpu.v}!",
        )
        result = bintostr(cpu, (cpu.ram[cpu.pc] << 8) + cpu.ram[cpu.pc + 1], 0xC000, 0x10000)
        expected = f"An integer: {integer}"
        _assert(
            result == expected,
            "Failed to stringformat integer, "
            + f"got {result!r} instead of {expected!r}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    # Finally, let's do something interesting.
    for x in [0, 37, -37, 69, 100, -100]:
        for y in [0, 5, -5, 7, -7]:
            sections = parse_and_compile_module("stringformat", textwrap.dedent("""
                def formatme(x: int8, y: int8) -> str[100]:
                    return f"The sum of {x} and {y} is {x + y}"
            """), settings)
            memory = getmemory(os.linesep.join([
                *initlines,
                *sections.init,
                *startlines,
                *sections.code,
                *strcpylines,
                *strcatlines,
                *itoalines,
                *dividelines,
                *neglines,
                *addlines,
                *cmplines,
                "main:",
                "LOADI 111",
                "MOV A, U",
                "LOADI 222",
                "MOV A, V",
                f"PUSHI {x}",
                f"PUSHI {y}",
                "LOADI 123",
                "CALL formatme",
                "HALT",
                *datalines,
                *sections.data,
                *heaplines,
            ]))
            cpu = CPUCore(memory)
            rununtilhalt(cpu)

            assertmemory("stringformat", memory, cpu.ram)
            _assert(
                cpu.a == 123,
                f"stringformat changed accumulator value from {123} to {cpu.a}!",
            )
            _assert(
                cpu.u == 111,
                f"stringformat changed U value from {111} to {cpu.u}!",
            )
            _assert(
                cpu.v == 222,
                f"stringformat changed V value from {222} to {cpu.v}!",
            )
            result = bintostr(cpu, (cpu.ram[cpu.pc] << 8) + cpu.ram[cpu.pc + 1], 0xC000, 0x10000)
            expected = f"The sum of {x} and {y} is {x + y}"
            _assert(
                result == expected,
                "Failed to stringformat integer, "
                + f"got {result!r} instead of {expected!r}!",
            )
            cycles += cpu.cycles
            instructions += cpu.ticks
            count += 1

    print(f"Average cycles for stringformat: {int(cycles/count)}")
    print(f"Average instructions for stringformat: {int(instructions/count)}")


def verifystringcombination(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "stringcombination" not in only and "compiler" not in only:
        return

    print("Verifying stringcombination...")

    with open("lib/runtime/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/runtime/start.S", "r") as fp:
        startlines = fp.readlines()
    with open("lib/runtime/data.S", "r") as fp:
        datalines = fp.readlines()
    with open("lib/runtime/heap.S", "r") as fp:
        heaplines = fp.readlines()
    with open("lib/string/strcpy.S", "r") as fp:
        strcpylines = fp.readlines()
    with open("lib/string/strcat.S", "r") as fp:
        strcatlines = fp.readlines()

    cycles = 0
    instructions = 0
    count = 0

    # Test a combination of concatenations and slices in a complex expression.
    if True:
        sections = parse_and_compile_module("stringcombination", textwrap.dedent("""
            def inner(first: const[str], second: const[str], third: char) -> str[64]:
                return (first[:5] + third)[1:] + " " + second[1:4]

            def func() -> str:
                return inner("things", "thats", "e")
        """), settings)
        memory = getmemory(os.linesep.join([
            *initlines,
            *sections.init,
            *startlines,
            *sections.code,
            *strcpylines,
            *strcatlines,
            "main:",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            "LOADI 123",
            "SUBPCI 2",
            "CALL func",
            "HALT",
            *datalines,
            *sections.data,
            *heaplines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        assertmemory("stringcombination", memory, cpu.ram)
        _assert(
            cpu.a == 123,
            f"stringcombination changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"stringcombination changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"stringcombination changed V value from {222} to {cpu.v}!",
        )
        result = bintostr(cpu, (cpu.ram[cpu.pc] << 8) + cpu.ram[cpu.pc + 1], 0xC000, 0x10000)
        expected = "hinge hat"
        _assert(
            result == expected,
            "Failed to stringcombination, "
            + f"got {result!r} instead of {expected!r}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    print(f"Average cycles for stringslice: {int(cycles/count)}")
    print(f"Average instructions for stringslice: {int(instructions/count)}")


def verifystringloop(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "stringloop" not in only and "compiler" not in only:
        return

    print("Verifying stringloop...")

    with open("lib/runtime/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/runtime/start.S", "r") as fp:
        startlines = fp.readlines()
    with open("lib/runtime/data.S", "r") as fp:
        datalines = fp.readlines()
    with open("lib/runtime/heap.S", "r") as fp:
        heaplines = fp.readlines()
    with open("lib/string/strcpy.S", "r") as fp:
        strcpylines = fp.readlines()
    with open("lib/string/strcat.S", "r") as fp:
        strcatlines = fp.readlines()

    cycles = 0
    instructions = 0
    count = 0

    # First, run the simplest for loop with a static string.
    if True:
        sections = parse_and_compile_module("stringloop", textwrap.dedent("""
            def simple_for() -> int8:
                retval: int8 = 0

                c: char
                for c in "Hello, world!":
                    if c == ",":
                        break
                    retval += 1

                return retval
        """), settings)
        memory = getmemory(os.linesep.join([
            *initlines,
            *sections.init,
            *startlines,
            *strcpylines,
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
            f"stringloop changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"stringloop changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"stringloop changed V value from {222} to {cpu.v}!",
        )
        result = bintoint(cpu.ram[cpu.pc])
        expected = 5
        _assert(
            result == expected,
            "Failed to stringloop simple, "
            + f"got {result} instead of {expected}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    # Now, run the simplest for loop with a string variable.
    if True:
        sections = parse_and_compile_module("stringloop", textwrap.dedent("""
            def simple_for() -> int8:
                someStr: str[16] = "Hello, world!"
                retval: int8 = 0

                c: char
                for c in someStr:
                    if c == ",":
                        break
                    retval += 1

                return retval
        """), settings)
        memory = getmemory(os.linesep.join([
            *initlines,
            *sections.init,
            *startlines,
            *strcpylines,
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
            f"stringloop changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"stringloop changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"stringloop changed V value from {222} to {cpu.v}!",
        )
        result = bintoint(cpu.ram[cpu.pc])
        expected = 5
        _assert(
            result == expected,
            "Failed to stringloop simple, "
            + f"got {result} instead of {expected}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    # Now, run the for loop with a string expression
    if True:
        sections = parse_and_compile_module("stringloop", textwrap.dedent("""
            def simple_for() -> int8:
                someStr: str[16] = "Hello, world!"
                retval: int8 = 0

                c: char
                for c in "GGGG" + someStr[2:]:
                    if c == ",":
                        break
                    retval += 1

                return retval
        """), settings)
        memory = getmemory(os.linesep.join([
            *initlines,
            *sections.init,
            *startlines,
            *strcpylines,
            *strcatlines,
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
            f"stringloop changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"stringloop changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"stringloop changed V value from {222} to {cpu.v}!",
        )
        result = bintoint(cpu.ram[cpu.pc])
        expected = 7
        _assert(
            result == expected,
            "Failed to stringloop simple, "
            + f"got {result} instead of {expected}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    print(f"Average cycles for stringloop: {int(cycles/count)}")
    print(f"Average instructions for stringloop: {int(instructions/count)}")


def verifypeek(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "peek" not in only and "compiler" not in only:
        return

    print("Verifying peek...")

    with open("lib/runtime/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/runtime/start.S", "r") as fp:
        startlines = fp.readlines()
    with open("lib/runtime/data.S", "r") as fp:
        datalines = fp.readlines()
    with open("lib/runtime/heap.S", "r") as fp:
        heaplines = fp.readlines()
    with open("lib/string/strcpy.S", "r") as fp:
        strcpylines = fp.readlines()

    cycles = 0
    instructions = 0
    count = 0

    # Mypy throws a fit because variables in Python are scoped outside of their for loops, whatever.
    val: Any
    result: Any
    expected: Any

    # Test signed integers.
    for width in ["int8", "int16", "int32"]:
        for val in [0, 37, -37] + ([12345, -12345] if width in {"int16", "int32"} else []) + ([123456789, -123456789] if width == "int32" else []):
            sections = parse_and_compile_module("peek", textwrap.dedent(f"""
                def callable() -> {width}:
                    return peek(0x1337)
            """), settings)
            memory = getmemory(os.linesep.join([
                *initlines,
                *sections.init,
                *startlines,
                *sections.code,
                ".org 0x1337",
                *([f".byte {(val >> 24) & 0xFF}", f".byte {(val >> 16 & 0xFF)}"] if width == "int32" else []),
                *([f".byte {(val >> 8) & 0xFF}"] if width in {"int16", "int32"} else []),
                f".byte {(val >> 0) & 0xFF}",
                "main:",
                "LOADI 111",
                "MOV A, U",
                "LOADI 222",
                "MOV A, V",
                "LOADI 123",
                f"SUBPCI {4 if width == 'int32' else (2 if width == 'int16' else 1)}",
                "CALL callable",
                "HALT",
                *datalines,
                *sections.data,
                *heaplines,
            ]))
            cpu = CPUCore(memory)
            rununtilhalt(cpu)

            _assert(
                cpu.a == 123,
                f"peek changed accumulator value from {123} to {cpu.a}!",
            )
            _assert(
                cpu.u == 111,
                f"peek changed U value from {111} to {cpu.u}!",
            )
            _assert(
                cpu.v == 222,
                f"peek changed V value from {222} to {cpu.v}!",
            )
            if width == "int8":
                result = bintoint(cpu.ram[cpu.pc])
            elif width == "int16":
                result = bintoint16(
                    (cpu.ram[cpu.pc + 0] << 8) + cpu.ram[cpu.pc + 1]
                )
            elif width == "int32":
                result = bintoint32(
                    (cpu.ram[cpu.pc + 0] << 24) +
                    (cpu.ram[cpu.pc + 1] << 16) +
                    (cpu.ram[cpu.pc + 2] << 8) +
                    cpu.ram[cpu.pc + 3]
                )
            else:
                result = 0xDEADBEEF
            expected = val
            _assert(
                result == expected,
                f"Failed to peek at {width}, "
                + f"got {result} instead of {expected}!",
            )
            cycles += cpu.cycles
            instructions += cpu.ticks
            count += 1

    # Test unsigned integers.
    for width in ["uint8", "uint16", "uint32"]:
        for val in [0, 37, 69, 200] + ([12345, 65432] if width in {"uint16", "uint32"} else []) + ([123456789, 987654321] if width == "uint32" else []):
            sections = parse_and_compile_module("peek", textwrap.dedent(f"""
                def callable() -> {width}:
                    return peek(0x1337)
            """), settings)
            memory = getmemory(os.linesep.join([
                *initlines,
                *sections.init,
                *startlines,
                *sections.code,
                ".org 0x1337",
                *([f".byte {(val >> 24) & 0xFF}", f".byte {(val >> 16 & 0xFF)}"] if width == "uint32" else []),
                *([f".byte {(val >> 8) & 0xFF}"] if width in {"uint16", "uint32"} else []),
                f".byte {(val >> 0) & 0xFF}",
                "main:",
                "LOADI 111",
                "MOV A, U",
                "LOADI 222",
                "MOV A, V",
                "LOADI 123",
                f"SUBPCI {4 if width == 'uint32' else (2 if width == 'uint16' else 1)}",
                "CALL callable",
                "HALT",
                *datalines,
                *sections.data,
                *heaplines,
            ]))
            cpu = CPUCore(memory)
            rununtilhalt(cpu)

            _assert(
                cpu.a == 123,
                f"peek changed accumulator value from {123} to {cpu.a}!",
            )
            _assert(
                cpu.u == 111,
                f"peek changed U value from {111} to {cpu.u}!",
            )
            _assert(
                cpu.v == 222,
                f"peek changed V value from {222} to {cpu.v}!",
            )
            if width == "uint8":
                result = cpu.ram[cpu.pc]
            elif width == "uint16":
                result = (
                    (cpu.ram[cpu.pc + 0] << 8) + cpu.ram[cpu.pc + 1]
                )
            elif width == "uint32":
                result = (
                    (cpu.ram[cpu.pc + 0] << 24) +
                    (cpu.ram[cpu.pc + 1] << 16) +
                    (cpu.ram[cpu.pc + 2] << 8) +
                    cpu.ram[cpu.pc + 3]
                )
            else:
                result = 0xDEADBEEF
            expected = val
            _assert(
                result == expected,
                f"Failed to peek at {width}, "
                + f"got {result} instead of {expected}!",
            )
            cycles += cpu.cycles
            instructions += cpu.ticks
            count += 1

    # Test characters
    for val in ['a', 'b', 'y', 'z']:
        sections = parse_and_compile_module("peek", textwrap.dedent("""
            def callable() -> char:
                return peek(0x1337)
        """), settings)
        memory = getmemory(os.linesep.join([
            *initlines,
            *sections.init,
            *startlines,
            *sections.code,
            ".org 0x1337",
            f".char {val!r}",
            "main:",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            "LOADI 123",
            "SUBPCI 1",
            "CALL callable",
            "HALT",
            *datalines,
            *sections.data,
            *heaplines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        _assert(
            cpu.a == 123,
            f"peek changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"peek changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"peek changed V value from {222} to {cpu.v}!",
        )
        result = chr(cpu.ram[cpu.pc])
        expected = val
        _assert(
            result == expected,
            "Failed to peek at char, "
            + f"got {result} instead of {expected}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    # Test booleans
    for val, expected in [(0, False), (1, True), (69, True), (255, True)]:
        sections = parse_and_compile_module("peek", textwrap.dedent("""
            def callable() -> bool:
                return peek(0x1337)
        """), settings)
        memory = getmemory(os.linesep.join([
            *initlines,
            *sections.init,
            *startlines,
            *sections.code,
            ".org 0x1337",
            f".byte {val}",
            "main:",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            "LOADI 123",
            "SUBPCI 1",
            "CALL callable",
            "HALT",
            *datalines,
            *sections.data,
            *heaplines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        _assert(
            cpu.a == 123,
            f"peek changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"peek changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"peek changed V value from {222} to {cpu.v}!",
        )
        result = bool(cpu.ram[cpu.pc])
        _assert(
            result == expected,
            "Failed to peek at bool, "
            + f"got {result} instead of {expected}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    # Test strings
    for val in ["This is a test.", "The quick brown fox jumps over the lazy dog.", ""]:
        sections = parse_and_compile_module("peek", textwrap.dedent("""
            def callable() -> str[40]:
                return peek(0x1337)
        """), settings)
        memory = getmemory(os.linesep.join([
            *initlines,
            *sections.init,
            *startlines,
            *strcpylines,
            *sections.code,
            ".org 0x1337",
            f".str {val!r}",
            ".byte 0x00",
            "main:",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            "LOADI 123",
            "SUBPCI 2",
            "CALL callable",
            "HALT",
            *datalines,
            *sections.data,
            *heaplines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        _assert(
            cpu.a == 123,
            f"peek changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"peek changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"peek changed V value from {222} to {cpu.v}!",
        )
        result = bintostr(cpu, (cpu.ram[cpu.pc] << 8) + cpu.ram[cpu.pc + 1], 0xC000, 0x10000)
        expected = val
        _assert(
            result == expected,
            "Failed to peek at str, "
            + f"got {result} instead of {expected}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    # Test strings with a maximum copy length.
    for val in ["This is a test.", "The quick brown fox jumps over the lazy dog.", ""]:
        sections = parse_and_compile_module("peek", textwrap.dedent("""
            def callable() -> str[40]:
                return peek(0x1337, 20)
        """), settings)
        memory = getmemory(os.linesep.join([
            *initlines,
            *sections.init,
            *startlines,
            *strcpylines,
            *sections.code,
            ".org 0x1337",
            f".str {val!r}",
            ".byte 0x00",
            "main:",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            "LOADI 123",
            "SUBPCI 2",
            "CALL callable",
            "HALT",
            *datalines,
            *sections.data,
            *heaplines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        _assert(
            cpu.a == 123,
            f"peek changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"peek changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"peek changed V value from {222} to {cpu.v}!",
        )
        result = bintostr(cpu, (cpu.ram[cpu.pc] << 8) + cpu.ram[cpu.pc + 1], 0xC000, 0x10000)
        expected = val[:20]
        _assert(
            result == expected,
            "Failed to peek at str, "
            + f"got {result} instead of {expected}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    print(f"Average cycles for peek: {int(cycles/count)}")
    print(f"Average instructions for peek: {int(instructions/count)}")


def verifycast(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "cast" not in only and "compiler" not in only:
        return

    print("Verifying cast...")

    with open("lib/runtime/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/runtime/start.S", "r") as fp:
        startlines = fp.readlines()
    with open("lib/runtime/data.S", "r") as fp:
        datalines = fp.readlines()
    with open("lib/runtime/heap.S", "r") as fp:
        heaplines = fp.readlines()
    with open("lib/math/add.S", "r") as fp:
        addlines = fp.readlines()
    with open("lib/string/strcpy.S", "r") as fp:
        strcpylines = fp.readlines()

    cycles = 0
    instructions = 0
    count = 0

    # Test strings cast to integeres and back.
    for val in ["This is a test.", "The quick brown fox jumps over the lazy dog."]:
        sections = parse_and_compile_module("cast", textwrap.dedent(f"""
            def callable() -> str:
                someString: const[str] = {val!r}
                someInt: uint16 = cast(uint16, someString)
                someInt += 5
                return cast(str, someInt)
        """), settings)
        memory = getmemory(os.linesep.join([
            *initlines,
            *sections.init,
            *startlines,
            *addlines,
            *strcpylines,
            *sections.code,
            "main:",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            "LOADI 123",
            "SUBPCI 2",
            "CALL callable",
            "HALT",
            *datalines,
            *sections.data,
            *heaplines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        _assert(
            cpu.a == 123,
            f"cast changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"cast changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"cast changed V value from {222} to {cpu.v}!",
        )
        result = bintostr(cpu, (cpu.ram[cpu.pc] << 8) + cpu.ram[cpu.pc + 1], 0x0000, 0xC000)
        expected = val[5:]
        _assert(
            result == expected,
            "Failed to cast at str, "
            + f"got {result} instead of {expected}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    print(f"Average cycles for cast: {int(cycles/count)}")
    print(f"Average instructions for cast: {int(instructions/count)}")


def verifypoke(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "poke" not in only and "compiler" not in only:
        return

    print("Verifying poke...")

    with open("lib/runtime/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/runtime/start.S", "r") as fp:
        startlines = fp.readlines()
    with open("lib/runtime/data.S", "r") as fp:
        datalines = fp.readlines()
    with open("lib/runtime/heap.S", "r") as fp:
        heaplines = fp.readlines()
    with open("lib/string/strcpy.S", "r") as fp:
        strcpylines = fp.readlines()

    cycles = 0
    instructions = 0
    count = 0

    # Mypy throws a fit because variables in Python are scoped outside of their for loops, whatever.
    val: Any
    result: Any
    expected: Any

    # Test signed integers.
    for width in ["int8", "int16", "int32"]:
        for val in [0, 37, -37] + ([12345, -12345] if width in {"int16", "int32"} else []) + ([123456789, -123456789] if width == "int32" else []):
            sections = parse_and_compile_module("poke", textwrap.dedent(f"""
                def callable(input: {width}) -> void:
                    poke(0x9000, input)
            """), settings)
            memory = getmemory(os.linesep.join([
                *initlines,
                *sections.init,
                *startlines,
                *sections.code,
                "main:",
                f"PUSHI {(val >> 0) & 0xFF}",
                *([f"PUSHI {(val >> 8) & 0xFF}"] if width in {"int16", "int32"} else []),
                *([f"PUSHI {(val >> 16) & 0xFF}", f"PUSHI {(val >> 24 & 0xFF)}"] if width == "int32" else []),
                "LOADI 111",
                "MOV A, U",
                "LOADI 222",
                "MOV A, V",
                "LOADI 123",
                "CALL callable",
                "HALT",
                *datalines,
                *sections.data,
                *heaplines,
                ".org 0x9000",
            ]))
            cpu = CPUCore(memory)
            rununtilhalt(cpu)

            _assert(
                cpu.a == 123,
                f"poke changed accumulator value from {123} to {cpu.a}!",
            )
            _assert(
                cpu.u == 111,
                f"poke changed U value from {111} to {cpu.u}!",
            )
            _assert(
                cpu.v == 222,
                f"poke changed V value from {222} to {cpu.v}!",
            )
            if width == "int8":
                result = bintoint(cpu.ram[0x9000])
            elif width == "int16":
                result = bintoint16(
                    (cpu.ram[0x9000 + 0] << 8) + cpu.ram[0x9000 + 1]
                )
            elif width == "int32":
                result = bintoint32(
                    (cpu.ram[0x9000 + 0] << 24) +
                    (cpu.ram[0x9000 + 1] << 16) +
                    (cpu.ram[0x9000 + 2] << 8) +
                    cpu.ram[0x9000 + 3]
                )
            else:
                result = 0xDEADBEEF
            expected = val
            _assert(
                result == expected,
                f"Failed to poke at {width}, "
                + f"got {result} instead of {expected}!",
            )
            cycles += cpu.cycles
            instructions += cpu.ticks
            count += 1

    # Test unsigned integers.
    for width in ["uint8", "uint16", "uint32"]:
        for val in [0, 37, 69, 200] + ([12345, 65432] if width in {"uint16", "uint32"} else []) + ([123456789, 987654321] if width == "uint32" else []):
            sections = parse_and_compile_module("poke", textwrap.dedent(f"""
                def callable(input: {width}) -> void:
                    poke(0x9000, input)
            """), settings)
            memory = getmemory(os.linesep.join([
                *initlines,
                *sections.init,
                *startlines,
                *sections.code,
                "main:",
                f"PUSHI {(val >> 0) & 0xFF}",
                *([f"PUSHI {(val >> 8) & 0xFF}"] if width in {"uint16", "uint32"} else []),
                *([f"PUSHI {(val >> 16) & 0xFF}", f"PUSHI {(val >> 24 & 0xFF)}"] if width == "uint32" else []),
                "LOADI 111",
                "MOV A, U",
                "LOADI 222",
                "MOV A, V",
                "LOADI 123",
                "CALL callable",
                "HALT",
                *datalines,
                *sections.data,
                *heaplines,
                ".org 0x9000",
            ]))
            cpu = CPUCore(memory)
            rununtilhalt(cpu)

            _assert(
                cpu.a == 123,
                f"poke changed accumulator value from {123} to {cpu.a}!",
            )
            _assert(
                cpu.u == 111,
                f"poke changed U value from {111} to {cpu.u}!",
            )
            _assert(
                cpu.v == 222,
                f"poke changed V value from {222} to {cpu.v}!",
            )
            if width == "uint8":
                result = cpu.ram[0x9000]
            elif width == "uint16":
                result = (
                    (cpu.ram[0x9000 + 0] << 8) + cpu.ram[0x9000 + 1]
                )
            elif width == "uint32":
                result = (
                    (cpu.ram[0x9000 + 0] << 24) +
                    (cpu.ram[0x9000 + 1] << 16) +
                    (cpu.ram[0x9000 + 2] << 8) +
                    cpu.ram[0x9000 + 3]
                )
            else:
                result = 0xDEADBEEF
            expected = val
            _assert(
                result == expected,
                f"Failed to poke at {width}, "
                + f"got {result} instead of {expected}!",
            )
            cycles += cpu.cycles
            instructions += cpu.ticks
            count += 1

    # Test characters
    for val in ['a', 'b', 'y', 'z']:
        sections = parse_and_compile_module("poke", textwrap.dedent("""
            def callable(input: char) -> void:
                poke(0x9000, input)
        """), settings)
        memory = getmemory(os.linesep.join([
            *initlines,
            *sections.init,
            *startlines,
            *sections.code,
            "main:",
            f"PUSHI {val!r}",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            "LOADI 123",
            "CALL callable",
            "HALT",
            *datalines,
            *sections.data,
            *heaplines,
            ".org 0x9000",
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        _assert(
            cpu.a == 123,
            f"poke changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"poke changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"poke changed V value from {222} to {cpu.v}!",
        )
        result = chr(cpu.ram[0x9000])
        expected = val
        _assert(
            result == expected,
            "Failed to poke at char, "
            + f"got {result} instead of {expected}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    # Test booleans
    for val, expected in [(False, 0x00), (True, 0xFF)]:
        sections = parse_and_compile_module("poke", textwrap.dedent("""
            def callable(input: bool) -> void:
                poke(0x9000, input)
        """), settings)
        memory = getmemory(os.linesep.join([
            *initlines,
            *sections.init,
            *startlines,
            *sections.code,
            "main:",
            f"PUSHI {'0xFF' if val else '0x00'}",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            "LOADI 123",
            "CALL callable",
            "HALT",
            *datalines,
            *sections.data,
            *heaplines,
            ".org 0x9000",
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        _assert(
            cpu.a == 123,
            f"poke changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"poke changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"poke changed V value from {222} to {cpu.v}!",
        )
        result = cpu.ram[0x9000]
        _assert(
            result == expected,
            "Failed to poke at bool, "
            + f"got {result} instead of {expected}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    # Test constants
    for val in [0, 37, 69, 123, 234, 255]:
        sections = parse_and_compile_module("poke", textwrap.dedent(f"""
            def callable() -> void:
                poke(0x9000, {val})
        """), settings)
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
            "CALL callable",
            "HALT",
            *datalines,
            *sections.data,
            *heaplines,
            ".org 0x9000",
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        _assert(
            cpu.a == 123,
            f"poke changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"poke changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"poke changed V value from {222} to {cpu.v}!",
        )
        result = cpu.ram[0x9000]
        expected = val
        _assert(
            result == expected,
            "Failed to poke at bool, "
            + f"got {result} instead of {expected}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    # Test strings
    for val in ["This is a test.", "The quick brown fox jumps over the lazy dog.", ""]:
        sections = parse_and_compile_module("poke", textwrap.dedent(f"""
            def callable() -> void:
                string: str[40] = {val!r}
                poke(0x9000, string)
        """), settings)
        memory = getmemory(os.linesep.join([
            *initlines,
            *sections.init,
            *startlines,
            *strcpylines,
            *sections.code,
            "main:",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            "LOADI 123",
            "CALL callable",
            "HALT",
            *datalines,
            *sections.data,
            *heaplines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        _assert(
            cpu.a == 123,
            f"poke changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"poke changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"poke changed V value from {222} to {cpu.v}!",
        )
        result = getstring(cpu, 0x9000)
        expected = val
        _assert(
            result == expected,
            "Failed to poke at str, "
            + f"got {result} instead of {expected}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    print(f"Average cycles for poke: {int(cycles/count)}")
    print(f"Average instructions for poke: {int(instructions/count)}")


def verifyabs(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "abs" not in only and "compiler" not in only:
        return

    print("Verifying abs...")

    with open("lib/runtime/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/runtime/start.S", "r") as fp:
        startlines = fp.readlines()
    with open("lib/runtime/data.S", "r") as fp:
        datalines = fp.readlines()
    with open("lib/runtime/heap.S", "r") as fp:
        heaplines = fp.readlines()
    with open("lib/math/abs.S", "r") as fp:
        abslines = fp.readlines()
    with open("lib/math/neg.S", "r") as fp:
        neglines = fp.readlines()

    cycles = 0
    instructions = 0
    count = 0

    # Mypy throws a fit because variables in Python are scoped outside of their for loops, whatever.
    val: Any
    result: Any
    expected: Any

    # Test signed integers.
    for width in ["int8", "int16", "int32"]:
        for val in [0, 37, -37] + ([12345, -12345] if width in {"int16", "int32"} else []) + ([123456789, -123456789] if width == "int32" else []):
            sections = parse_and_compile_module("abs", textwrap.dedent(f"""
                def callable(input: {width}) -> {width}:
                    return abs(input)
            """), settings)
            memory = getmemory(os.linesep.join([
                *initlines,
                *sections.init,
                *startlines,
                *abslines,
                *neglines,
                *sections.code,
                "main:",
                f"PUSHI {(val >> 0) & 0xFF}",
                *([f"PUSHI {(val >> 8) & 0xFF}"] if width in {"int16", "int32"} else []),
                *([f"PUSHI {(val >> 16) & 0xFF}", f"PUSHI {(val >> 24 & 0xFF)}"] if width == "int32" else []),
                "LOADI 111",
                "MOV A, U",
                "LOADI 222",
                "MOV A, V",
                "LOADI 123",
                "CALL callable",
                "HALT",
                *datalines,
                *sections.data,
                *heaplines,
            ]))
            cpu = CPUCore(memory)
            rununtilhalt(cpu)

            _assert(
                cpu.a == 123,
                f"abs changed accumulator value from {123} to {cpu.a}!",
            )
            _assert(
                cpu.u == 111,
                f"abs changed U value from {111} to {cpu.u}!",
            )
            _assert(
                cpu.v == 222,
                f"abs changed V value from {222} to {cpu.v}!",
            )
            if width == "int8":
                result = bintoint(cpu.ram[cpu.pc + 0])
            elif width == "int16":
                result = bintoint16(
                    (cpu.ram[cpu.pc + 0] << 8) + cpu.ram[cpu.pc + 1]
                )
            elif width == "int32":
                result = bintoint32(
                    (cpu.ram[cpu.pc + 0] << 24) +
                    (cpu.ram[cpu.pc + 1] << 16) +
                    (cpu.ram[cpu.pc + 2] << 8) +
                    cpu.ram[cpu.pc + 3]
                )
            else:
                result = 0xDEADBEEF
            expected = abs(val)
            _assert(
                result == expected,
                f"Failed to abs at {width}, "
                + f"got {result} instead of {expected}!",
            )
            cycles += cpu.cycles
            instructions += cpu.ticks
            count += 1

    # Test unsigned integers.
    for width in ["uint8", "uint16", "uint32"]:
        for val in [0, 37, 69, 200] + ([12345, 65432] if width in {"uint16", "uint32"} else []) + ([123456789, 987654321] if width == "uint32" else []):
            sections = parse_and_compile_module("abs", textwrap.dedent(f"""
                def callable(input: {width}) -> {width}:
                    return abs(input)
            """), settings)
            memory = getmemory(os.linesep.join([
                *initlines,
                *sections.init,
                *startlines,
                *abslines,
                *neglines,
                *sections.code,
                "main:",
                f"PUSHI {(val >> 0) & 0xFF}",
                *([f"PUSHI {(val >> 8) & 0xFF}"] if width in {"uint16", "uint32"} else []),
                *([f"PUSHI {(val >> 16) & 0xFF}", f"PUSHI {(val >> 24 & 0xFF)}"] if width == "uint32" else []),
                "LOADI 111",
                "MOV A, U",
                "LOADI 222",
                "MOV A, V",
                "LOADI 123",
                "CALL callable",
                "HALT",
                *datalines,
                *sections.data,
                *heaplines,
            ]))
            cpu = CPUCore(memory)
            rununtilhalt(cpu)

            _assert(
                cpu.a == 123,
                f"abs changed accumulator value from {123} to {cpu.a}!",
            )
            _assert(
                cpu.u == 111,
                f"abs changed U value from {111} to {cpu.u}!",
            )
            _assert(
                cpu.v == 222,
                f"abs changed V value from {222} to {cpu.v}!",
            )
            if width == "uint8":
                result = cpu.ram[cpu.pc]
            elif width == "uint16":
                result = (
                    (cpu.ram[cpu.pc + 0] << 8) + cpu.ram[cpu.pc + 1]
                )
            elif width == "uint32":
                result = (
                    (cpu.ram[cpu.pc + 0] << 24) +
                    (cpu.ram[cpu.pc + 1] << 16) +
                    (cpu.ram[cpu.pc + 2] << 8) +
                    cpu.ram[cpu.pc + 3]
                )
            else:
                result = 0xDEADBEEF
            expected = abs(val)
            _assert(
                result == expected,
                f"Failed to abs at {width}, "
                + f"got {result} instead of {expected}!",
            )
            cycles += cpu.cycles
            instructions += cpu.ticks
            count += 1

    print(f"Average cycles for abs: {int(cycles/count)}")
    print(f"Average instructions for abs: {int(instructions/count)}")


def verifybool(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "bool" not in only and "compiler" not in only:
        return

    print("Verifying bool...")

    with open("lib/runtime/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/runtime/start.S", "r") as fp:
        startlines = fp.readlines()
    with open("lib/runtime/data.S", "r") as fp:
        datalines = fp.readlines()
    with open("lib/runtime/heap.S", "r") as fp:
        heaplines = fp.readlines()

    cycles = 0
    instructions = 0
    count = 0

    # Mypy throws a fit because variables in Python are scoped outside of their for loops, whatever.
    val: Any
    result: Any
    expected: Any

    # Test integers.
    for width in ["uint8", "uint16", "uint32"]:
        for val in (
            [0x00, 0xA5, 0x5A, 0xFF] +
            ([0xFF00, 0x00FF, 0xA5A5] if width == "uint16" else []) +
            ([0x000000FF, 0x0000FF00, 0x00FF0000, 0xFF000000, 0xA5A5A5A5] if width == "uint32" else [])
        ):
            sections = parse_and_compile_module("bool", textwrap.dedent(f"""
                def callable(input: {width}) -> bool:
                    return bool(input)
            """), settings)
            memory = getmemory(os.linesep.join([
                *initlines,
                *sections.init,
                *startlines,
                *sections.code,
                "main:",
                f"PUSHI {(val >> 0) & 0xFF}",
                *([f"PUSHI {(val >> 8) & 0xFF}"] if width in {"uint16", "uint32"} else []),
                *([f"PUSHI {(val >> 16) & 0xFF}", f"PUSHI {(val >> 24 & 0xFF)}"] if width == "uint32" else []),
                "LOADI 111",
                "MOV A, U",
                "LOADI 222",
                "MOV A, V",
                "LOADI 123",
                "CALL callable",
                "HALT",
                *datalines,
                *sections.data,
                *heaplines,
            ]))
            cpu = CPUCore(memory)
            rununtilhalt(cpu)

            _assert(
                cpu.a == 123,
                f"bool changed accumulator value from {123} to {cpu.a}!",
            )
            _assert(
                cpu.u == 111,
                f"bool changed U value from {111} to {cpu.u}!",
            )
            _assert(
                cpu.v == 222,
                f"bool changed V value from {222} to {cpu.v}!",
            )
            result = bool(cpu.ram[cpu.pc + 0])
            expected = bool(val)
            _assert(
                result == expected,
                f"Failed to bool at {width}, "
                + f"got {result} instead of {expected}!",
            )
            cycles += cpu.cycles
            instructions += cpu.ticks
            count += 1

    # Test characters.
    for val in ['\0', 'a', 'b', 'c']:
        sections = parse_and_compile_module("bool", textwrap.dedent("""
            def callable(input: char) -> bool:
                return bool(input)
        """), settings)
        memory = getmemory(os.linesep.join([
            *initlines,
            *sections.init,
            *startlines,
            *sections.code,
            "main:",
            f"PUSHI {val!r}",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            "LOADI 123",
            "CALL callable",
            "HALT",
            *datalines,
            *sections.data,
            *heaplines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        _assert(
            cpu.a == 123,
            f"bool changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"bool changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"bool changed V value from {222} to {cpu.v}!",
        )
        result = bool(cpu.ram[cpu.pc + 0])
        expected = False if val == "\0" else True
        _assert(
            result == expected,
            "Failed to bool at char, "
            + f"got {result} instead of {expected}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    # Test booleans.
    for val in [True, False]:
        sections = parse_and_compile_module("bool", textwrap.dedent("""
            def callable(input: bool) -> bool:
                return bool(input)
        """), settings)
        memory = getmemory(os.linesep.join([
            *initlines,
            *sections.init,
            *startlines,
            *sections.code,
            "main:",
            f"PUSHI {'0xff' if val else '0x00'}",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            "LOADI 123",
            "CALL callable",
            "HALT",
            *datalines,
            *sections.data,
            *heaplines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        _assert(
            cpu.a == 123,
            f"bool changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"bool changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"bool changed V value from {222} to {cpu.v}!",
        )
        result = bool(cpu.ram[cpu.pc + 0])
        expected = val
        _assert(
            result == expected,
            "Failed to bool at char, "
            + f"got {result} instead of {expected}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    # Test strings.
    for val in ["", "nonzero"]:
        sections = parse_and_compile_module("bool", textwrap.dedent(f"""
            def inner(input: const[str]) -> bool:
                return bool(input)

            def callable() -> bool:
                return inner({val!r})
        """), settings)
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
            "CALL callable",
            "HALT",
            *datalines,
            *sections.data,
            *heaplines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        _assert(
            cpu.a == 123,
            f"bool changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"bool changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"bool changed V value from {222} to {cpu.v}!",
        )
        result = bool(cpu.ram[cpu.pc + 0])
        expected = bool(val)
        _assert(
            result == expected,
            "Failed to bool at char, "
            + f"got {result} instead of {expected}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    print(f"Average cycles for bool: {int(cycles/count)}")
    print(f"Average instructions for bool: {int(instructions/count)}")


def verifychr(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "chr" not in only and "compiler" not in only:
        return

    print("Verifying chr...")

    with open("lib/runtime/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/runtime/start.S", "r") as fp:
        startlines = fp.readlines()
    with open("lib/runtime/data.S", "r") as fp:
        datalines = fp.readlines()
    with open("lib/runtime/heap.S", "r") as fp:
        heaplines = fp.readlines()
    with open("lib/math/cmp.S", "r") as fp:
        cmplines = fp.readlines()
    with open("lib/string/strcpy.S", "r") as fp:
        strcpylines = fp.readlines()

    cycles = 0
    instructions = 0
    count = 0

    # Test integers.
    for width in ["uint8", "uint16", "uint32"]:
        for val in [0x00, 0x20, 0x65, 0x21]:
            sections = parse_and_compile_module("chr", textwrap.dedent(f"""
                def callable(input: {width}) -> char:
                    return chr(input)
            """), settings)
            memory = getmemory(os.linesep.join([
                *initlines,
                *sections.init,
                *startlines,
                *sections.code,
                "main:",
                f"PUSHI {(val >> 0) & 0xFF}",
                *([f"PUSHI {(val >> 8) & 0xFF}"] if width in {"uint16", "uint32"} else []),
                *([f"PUSHI {(val >> 16) & 0xFF}", f"PUSHI {(val >> 24 & 0xFF)}"] if width == "uint32" else []),
                "LOADI 111",
                "MOV A, U",
                "LOADI 222",
                "MOV A, V",
                "LOADI 123",
                "CALL callable",
                "HALT",
                *datalines,
                *sections.data,
                *heaplines,
            ]))
            cpu = CPUCore(memory)
            rununtilhalt(cpu)

            _assert(
                cpu.a == 123,
                f"chr changed accumulator value from {123} to {cpu.a}!",
            )
            _assert(
                cpu.u == 111,
                f"chr changed U value from {111} to {cpu.u}!",
            )
            _assert(
                cpu.v == 222,
                f"chr changed V value from {222} to {cpu.v}!",
            )
            result = cpu.ram[cpu.pc + 0]
            expected = val & 0xFF
            _assert(
                result == expected,
                f"Failed to chr at {width}, "
                + f"got {result} instead of {expected}!",
            )
            cycles += cpu.cycles
            instructions += cpu.ticks
            count += 1

    # Test silly program.
    if True:
        sections = parse_and_compile_module("chr", textwrap.dedent("""
            def callable() -> str:
                out: str[8] = ""
                ascval: int8

                for ascval in range(65, 70):
                    out += chr(ascval)

                return out
        """), settings)
        memory = getmemory(os.linesep.join([
            *initlines,
            *sections.init,
            *startlines,
            *strcpylines,
            *cmplines,
            *sections.code,
            "main:",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            "LOADI 123",
            "SUBPCI 2",
            "CALL callable",
            "HALT",
            *datalines,
            *sections.data,
            *heaplines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        _assert(
            cpu.a == 123,
            f"chr changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"chr changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"chr changed V value from {222} to {cpu.v}!",
        )
        resultstr = bintostr(cpu, (cpu.ram[cpu.pc] << 8) + cpu.ram[cpu.pc + 1], 0xC000, 0x10000)
        expectedstr = "ABCDE"
        _assert(
            resultstr == expectedstr,
            "Failed to chr in string concatenation, "
            + f"got {resultstr} instead of {expectedstr}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    print(f"Average cycles for chr: {int(cycles/count)}")
    print(f"Average instructions for chr: {int(instructions/count)}")


def verifyord(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "ord" not in only and "compiler" not in only:
        return

    print("Verifying ord...")

    with open("lib/runtime/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/runtime/start.S", "r") as fp:
        startlines = fp.readlines()
    with open("lib/runtime/data.S", "r") as fp:
        datalines = fp.readlines()
    with open("lib/runtime/heap.S", "r") as fp:
        heaplines = fp.readlines()
    with open("lib/math/cmp.S", "r") as fp:
        cmplines = fp.readlines()
    with open("lib/string/strlen.S", "r") as fp:
        strlenlines = fp.readlines()

    cycles = 0
    instructions = 0
    count = 0

    # Test integers.
    for val in [' ', 'A', '!']:
        for outsize in ['uint8', 'int8', 'uint16', 'int16', 'uint32', 'int32']:
            sections = parse_and_compile_module("ord", textwrap.dedent(f"""
                def callable(input: char) -> nopad[{outsize}]:
                    return ord(input)
            """), settings)
            memory = getmemory(os.linesep.join([
                *initlines,
                *sections.init,
                *startlines,
                *sections.code,
                "main:",
                f"PUSHI {val!r}",
                "LOADI 111",
                "MOV A, U",
                "LOADI 222",
                "MOV A, V",
                "LOADI 123",
                "CALL callable",
                "HALT",
                *datalines,
                *sections.data,
                *heaplines,
            ]))
            cpu = CPUCore(memory)
            rununtilhalt(cpu)

            _assert(
                cpu.a == 123,
                f"ord changed accumulator value from {123} to {cpu.a}!",
            )
            _assert(
                cpu.u == 111,
                f"ord changed U value from {111} to {cpu.u}!",
            )
            _assert(
                cpu.v == 222,
                f"ord changed V value from {222} to {cpu.v}!",
            )
            if outsize in {"uint8", "int8"}:
                result = cpu.ram[cpu.pc + 0]
            elif outsize in {"uint16", "int16"}:
                result = bintoint16(
                    (cpu.ram[cpu.pc] << 8) + cpu.ram[cpu.pc + 1]
                )
            else:
                result = bintoint32(
                    (cpu.ram[cpu.pc] << 24) +
                    (cpu.ram[cpu.pc + 1] << 16) +
                    (cpu.ram[cpu.pc + 2] << 8) +
                    cpu.ram[cpu.pc + 3]
                )
            expected = ord(val)
            _assert(
                result == expected,
                "Failed to ord standard, "
                + f"got {result} instead of {expected}!",
            )
            cycles += cpu.cycles
            instructions += cpu.ticks
            count += 1

    # Test silly program.
    if True:
        sections = parse_and_compile_module("ord", textwrap.dedent("""
            def callable() -> uint8:
                instr: const[str] = "ABCDE"
                chksum: uint8 = 0
                pos: uint8

                for pos in range(len(instr)):
                    chksum += ord(instr[pos])

                return chksum
        """), settings)
        memory = getmemory(os.linesep.join([
            *initlines,
            *sections.init,
            *startlines,
            *sections.code,
            *cmplines,
            *strlenlines,
            "main:",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            "LOADI 123",
            "SUBPCI 1",
            "CALL callable",
            "HALT",
            *datalines,
            *sections.data,
            *heaplines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        _assert(
            cpu.a == 123,
            f"chr changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"chr changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"chr changed V value from {222} to {cpu.v}!",
        )
        result = cpu.ram[cpu.pc]
        expected = sum(ord(x) for x in "ABCDE") & 0xFF
        _assert(
            result == expected,
            "Failed to ord in string loop, "
            + f"got {result} instead of {expected}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    print(f"Average cycles for ord: {int(cycles/count)}")
    print(f"Average instructions for ord: {int(instructions/count)}")


def verifyint(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "int" not in only and "compiler" not in only:
        return

    print("Verifying int...")

    with open("lib/runtime/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/runtime/start.S", "r") as fp:
        startlines = fp.readlines()
    with open("lib/runtime/data.S", "r") as fp:
        datalines = fp.readlines()
    with open("lib/runtime/heap.S", "r") as fp:
        heaplines = fp.readlines()
    with open("lib/math/multiply.S", "r") as fp:
        multiplylines = fp.readlines()
    with open("lib/math/divide.S", "r") as fp:
        dividelines = fp.readlines()
    with open("lib/math/add.S", "r") as fp:
        addlines = fp.readlines()
    with open("lib/math/neg.S", "r") as fp:
        neglines = fp.readlines()
    with open("lib/math/cmp.S", "r") as fp:
        cmplines = fp.readlines()
    with open("lib/conversion/atoi.S", "r") as fp:
        atoilines = fp.readlines()
    with open("lib/conversion/itoa.S", "r") as fp:
        itoalines = fp.readlines()
    with open("lib/string/strcpy.S", "r") as fp:
        strcpylines = fp.readlines()
    with open("lib/string/strcat.S", "r") as fp:
        strcatlines = fp.readlines()

    cycles = 0
    instructions = 0
    count = 0

    # Mypy throws a fit because variables in Python are scoped outside of their for loops, whatever.
    val: Any
    result: Any
    expected: Any

    # Test integers.
    for width in ["uint8", "int8", "uint16", "int16", "uint32", "int32"]:
        for val in (
            [0x00, 0xA5, 0x5A, 0xFF] +
            ([0xFF00, 0x00FF, 0xA5A5] if width in {"uint16", "int16"} else []) +
            ([0x000000FF, 0x0000FF00, 0x00FF0000, 0xFF000000, 0xA5A5A5A5] if width in {"uint32", "int32"} else [])
        ):
            sections = parse_and_compile_module("int", textwrap.dedent(f"""
                def callable(input: {width}) -> {width}:
                    return int(input)
            """), settings)
            memory = getmemory(os.linesep.join([
                *initlines,
                *sections.init,
                *startlines,
                *sections.code,
                "main:",
                f"PUSHI {(val >> 0) & 0xFF}",
                *([f"PUSHI {(val >> 8) & 0xFF}"] if width in {"uint16", "int16", "uint32", "int32"} else []),
                *([f"PUSHI {(val >> 16) & 0xFF}", f"PUSHI {(val >> 24 & 0xFF)}"] if width in {"uint32", "int32"} else []),
                "LOADI 111",
                "MOV A, U",
                "LOADI 222",
                "MOV A, V",
                "LOADI 123",
                "CALL callable",
                "HALT",
                *datalines,
                *sections.data,
                *heaplines,
            ]))
            cpu = CPUCore(memory)
            rununtilhalt(cpu)

            _assert(
                cpu.a == 123,
                f"int changed accumulator value from {123} to {cpu.a}!",
            )
            _assert(
                cpu.u == 111,
                f"int changed U value from {111} to {cpu.u}!",
            )
            _assert(
                cpu.v == 222,
                f"int changed V value from {222} to {cpu.v}!",
            )
            if width in {"uint8", "int8"}:
                result = cpu.ram[cpu.pc + 0]
            elif width in {"uint16", "int16"}:
                result = (
                    (cpu.ram[cpu.pc] << 8) + cpu.ram[cpu.pc + 1]
                )
            else:
                result = (
                    (cpu.ram[cpu.pc] << 24) +
                    (cpu.ram[cpu.pc + 1] << 16) +
                    (cpu.ram[cpu.pc + 2] << 8) +
                    cpu.ram[cpu.pc + 3]
                )
            expected = val
            _assert(
                result == expected,
                f"Failed to int at {width}, "
                + f"got {result} instead of {expected}!",
            )
            cycles += cpu.cycles
            instructions += cpu.ticks
            count += 1

    # Test booleans.
    for val in [True, False]:
        sections = parse_and_compile_module("int", textwrap.dedent("""
            def callable(input: bool) -> int8:
                return int(input)
        """), settings)
        memory = getmemory(os.linesep.join([
            *initlines,
            *sections.init,
            *startlines,
            *sections.code,
            "main:",
            f"PUSHI {'0xff' if val else '0x00'}",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            "LOADI 123",
            "CALL callable",
            "HALT",
            *datalines,
            *sections.data,
            *heaplines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        _assert(
            cpu.a == 123,
            f"int changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"int changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"int changed V value from {222} to {cpu.v}!",
        )
        result = int(cpu.ram[cpu.pc + 0])
        expected = int(val)
        _assert(
            result == expected,
            "Failed to int at bool, "
            + f"got {result} instead of {expected}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    # Test strings.
    for val, expected in [("", 0), ("0", 0), ("123", 123), ("123, 456", 123)]:
        for size in ["uint8", "uint16", "uint32"]:
            sections = parse_and_compile_module("int", textwrap.dedent(f"""
                def inner(input: const[str]) -> {size}:
                    return int(input)

                def callable() -> {size}:
                    return inner({val!r})
            """), settings)
            memory = getmemory(os.linesep.join([
                *initlines,
                *sections.init,
                *startlines,
                *atoilines,
                *multiplylines,
                *addlines,
                *neglines,
                *sections.code,
                "main:",
                "LOADI 111",
                "MOV A, U",
                "LOADI 222",
                "MOV A, V",
                "LOADI 123",
                "SUBPCI 1" if size == "uint8" else ("SUBPCI 2" if size == "uint16" else "SUBPCI 4"),
                "CALL callable",
                "HALT",
                *datalines,
                *sections.data,
                *heaplines,
            ]))
            cpu = CPUCore(memory)
            rununtilhalt(cpu)

            _assert(
                cpu.a == 123,
                f"int changed accumulator value from {123} to {cpu.a}!",
            )
            _assert(
                cpu.u == 111,
                f"int changed U value from {111} to {cpu.u}!",
            )
            _assert(
                cpu.v == 222,
                f"int changed V value from {222} to {cpu.v}!",
            )
            if size == "uint8":
                result = cpu.ram[cpu.pc + 0]
            elif size == "uint16":
                result = (
                    (cpu.ram[cpu.pc] << 8) + cpu.ram[cpu.pc + 1]
                )
            else:
                result = (
                    (cpu.ram[cpu.pc] << 24) +
                    (cpu.ram[cpu.pc + 1] << 16) +
                    (cpu.ram[cpu.pc + 2] << 8) +
                    cpu.ram[cpu.pc + 3]
                )
            _assert(
                result == expected,
                "Failed to int at string, "
                + f"got {result} instead of {expected} for {val!r}!",
            )
            cycles += cpu.cycles
            instructions += cpu.ticks
            count += 1

    # Test string pointer advancement.
    for val, expectedstr in [("", ":0"), ("0", ":0"), ("123", ":123"), ("123, 456", ", 456:123"), ("123 456", " 456:123")]:
        for size in ["uint8", "uint16", "uint32"]:
            sections = parse_and_compile_module("int", textwrap.dedent(f"""
                def callable() -> str[32]:
                    strval: str[16] = {val!r}
                    intval: {size} = int(strval)
                    return strval + ":" + str(intval)
            """), settings)
            memory = getmemory(os.linesep.join([
                *initlines,
                *sections.init,
                *startlines,
                *atoilines,
                *itoalines,
                *dividelines,
                *multiplylines,
                *addlines,
                *neglines,
                *cmplines,
                *strcpylines,
                *strcatlines,
                *sections.code,
                "main:",
                "LOADI 111",
                "MOV A, U",
                "LOADI 222",
                "MOV A, V",
                "LOADI 123",
                "SUBPCI 2",
                "CALL callable",
                "HALT",
                *datalines,
                *sections.data,
                *heaplines,
            ]))
            cpu = CPUCore(memory)
            rununtilhalt(cpu)

            _assert(
                cpu.a == 123,
                f"int changed accumulator value from {123} to {cpu.a}!",
            )
            _assert(
                cpu.u == 111,
                f"int changed U value from {111} to {cpu.u}!",
            )
            _assert(
                cpu.v == 222,
                f"int changed V value from {222} to {cpu.v}!",
            )
            resultstr = bintostr(cpu, (cpu.ram[cpu.pc] << 8) + cpu.ram[cpu.pc + 1], 0xC000, 0x10000)
            _assert(
                resultstr == expectedstr,
                "Failed to int at string, "
                + f"got {resultstr} instead of {expectedstr} for {val!r}!",
            )
            cycles += cpu.cycles
            instructions += cpu.ticks
            count += 1

    # Test string pointer non-advancement for const.
    for val, expectedstr in [("", ":0"), ("0", "0:0"), ("123", "123:123"), ("123, 456", "123, 456:123"), ("123 456", "123 456:123")]:
        for size in ["uint8", "uint16", "uint32"]:
            sections = parse_and_compile_module("int", textwrap.dedent(f"""
                def callable() -> str[32]:
                    strval: const[str] = {val!r}
                    intval: {size} = int(strval)
                    return strval + ":" + str(intval)
            """), settings)
            memory = getmemory(os.linesep.join([
                *initlines,
                *sections.init,
                *startlines,
                *atoilines,
                *itoalines,
                *dividelines,
                *multiplylines,
                *addlines,
                *neglines,
                *cmplines,
                *strcpylines,
                *strcatlines,
                *sections.code,
                "main:",
                "LOADI 111",
                "MOV A, U",
                "LOADI 222",
                "MOV A, V",
                "LOADI 123",
                "SUBPCI 2",
                "CALL callable",
                "HALT",
                *datalines,
                *sections.data,
                *heaplines,
            ]))
            cpu = CPUCore(memory)
            rununtilhalt(cpu)

            _assert(
                cpu.a == 123,
                f"int changed accumulator value from {123} to {cpu.a}!",
            )
            _assert(
                cpu.u == 111,
                f"int changed U value from {111} to {cpu.u}!",
            )
            _assert(
                cpu.v == 222,
                f"int changed V value from {222} to {cpu.v}!",
            )
            resultstr = bintostr(cpu, (cpu.ram[cpu.pc] << 8) + cpu.ram[cpu.pc + 1], 0xC000, 0x10000)
            _assert(
                resultstr == expectedstr,
                "Failed to int at string, "
                + f"got {resultstr} instead of {expectedstr} for {val!r}!",
            )
            cycles += cpu.cycles
            instructions += cpu.ticks
            count += 1

    print(f"Average cycles for int: {int(cycles/count)}")
    print(f"Average instructions for int: {int(instructions/count)}")


def verifyhex(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "hex" not in only and "compiler" not in only:
        return

    print("Verifying hex...")

    with open("lib/runtime/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/runtime/start.S", "r") as fp:
        startlines = fp.readlines()
    with open("lib/runtime/data.S", "r") as fp:
        datalines = fp.readlines()
    with open("lib/runtime/heap.S", "r") as fp:
        heaplines = fp.readlines()
    with open("lib/conversion/hex.S", "r") as fp:
        hexlines = fp.readlines()

    cycles = 0
    instructions = 0
    count = 0

    def realhex(val: int, width: str) -> str:
        actual = {
            "uint8": 2,
            "int8": 2,
            "uint16": 4,
            "int16": 4,
            "uint32": 8,
            "int32": 8,
        }[width]

        strval = hex(val)[2:]
        while len(strval) < actual:
            strval = "0" + strval
        return "0x" + strval.upper()

    for width in ["uint8", "int8", "uint16", "int16", "uint32", "int32"]:
        for val in (
            [0x00, 0xA5, 0x5A, 0xFF, 0x12, 0x34, 0xCD, 0xEF] +
            ([0xFF00, 0x00FF, 0xA5A5, 0xABCD, 0x1337] if width in {"uint16", "int16"} else []) +
            ([0x000000FF, 0x0000FF00, 0x00FF0000, 0xFF000000, 0xA5A5A5A5, 0xDEADBEEF, 0xCAFEBABE, 0xC0FEBABE] if width in {"uint32", "int32"} else [])
        ):
            sections = parse_and_compile_module("hex", textwrap.dedent(f"""
                def callable(input: {width}) -> nopad[str[16]]:
                    return hex(input)
            """), settings)
            memory = getmemory(os.linesep.join([
                *initlines,
                *sections.init,
                *startlines,
                *sections.code,
                *hexlines,
                "main:",
                f"PUSHI {(val >> 0) & 0xFF}",
                *([f"PUSHI {(val >> 8) & 0xFF}"] if width in {"uint16", "int16", "uint32", "int32"} else []),
                *([f"PUSHI {(val >> 16) & 0xFF}", f"PUSHI {(val >> 24 & 0xFF)}"] if width in {"uint32", "int32"} else []),
                "LOADI 111",
                "MOV A, U",
                "LOADI 222",
                "MOV A, V",
                "LOADI 123",
                "CALL callable",
                "HALT",
                *datalines,
                *sections.data,
                *heaplines,
            ]))
            cpu = CPUCore(memory)
            rununtilhalt(cpu)

            _assert(
                cpu.a == 123,
                f"hex changed accumulator value from {123} to {cpu.a}!",
            )
            _assert(
                cpu.u == 111,
                f"hex changed U value from {111} to {cpu.u}!",
            )
            _assert(
                cpu.v == 222,
                f"hex changed V value from {222} to {cpu.v}!",
            )
            result = bintostr(cpu, (cpu.ram[cpu.pc] << 8) + cpu.ram[cpu.pc + 1], 0xC000, 0x10000)
            expected = realhex(val, width)
            _assert(
                result == expected,
                "Failed to hex, "
                + f"got {result} instead of {expected} for {val!r}!",
            )
            cycles += cpu.cycles
            instructions += cpu.ticks
            count += 1

    print(f"Average cycles for hex: {int(cycles/count)}")
    print(f"Average instructions for hex: {int(instructions/count)}")


def verifymin(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "min" not in only and "compiler" not in only:
        return

    print("Verifying min...")

    with open("lib/runtime/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/runtime/start.S", "r") as fp:
        startlines = fp.readlines()
    with open("lib/runtime/data.S", "r") as fp:
        datalines = fp.readlines()
    with open("lib/runtime/heap.S", "r") as fp:
        heaplines = fp.readlines()
    with open("lib/math/cmp.S", "r") as fp:
        cmplines = fp.readlines()

    cycles = 0
    instructions = 0
    count = 0

    def realmin(val1: int, val2: int, width: str) -> int:
        if width == "int8":
            val1 = bintoint(val1)
            val2 = bintoint(val2)
        if width == "int16":
            val1 = bintoint16(val1)
            val2 = bintoint16(val2)
        if width == "int32":
            val1 = bintoint32(val1)
            val2 = bintoint32(val2)
        return min(val1, val2)

    for width in ["uint8", "int8", "uint16", "int16", "uint32", "int32"]:
        for val1 in (
            [0x00, 0xA5, 0x5A, 0xFF, 0x12, 0x34, 0xCD, 0xEF] +
            ([0xFF00, 0x00FF, 0xA5A5, 0xABCD, 0x1337] if width in {"uint16", "int16"} else []) +
            ([0x000000FF, 0x0000FF00, 0x00FF0000, 0xFF000000, 0xA5A5A5A5, 0xDEADBEEF, 0xCAFEBABE, 0xC0FEBABE] if width in {"uint32", "int32"} else [])
        ):
            for val2 in (
                [0x00, 0xA5, 0x5A, 0xFF, 0x12, 0x34, 0xCD, 0xEF] +
                ([0xFF00, 0x00FF, 0xA5A5, 0xABCD, 0x1337] if width in {"uint16", "int16"} else []) +
                ([0x000000FF, 0x0000FF00, 0x00FF0000, 0xFF000000, 0xA5A5A5A5, 0xDEADBEEF, 0xCAFEBABE, 0xC0FEBABE] if width in {"uint32", "int32"} else [])
            ):
                sections = parse_and_compile_module("min", textwrap.dedent(f"""
                    def callable(val1: {width}, val2: {width}) -> nopad[{width}]:
                        return min(val1, val2)
                """), settings)
                memory = getmemory(os.linesep.join([
                    *initlines,
                    *sections.init,
                    *startlines,
                    *sections.code,
                    *cmplines,
                    "main:",
                    f"PUSHI {(val1 >> 0) & 0xFF}",
                    *([f"PUSHI {(val1 >> 8) & 0xFF}"] if width in {"uint16", "int16", "uint32", "int32"} else []),
                    *([f"PUSHI {(val1 >> 16) & 0xFF}", f"PUSHI {(val1 >> 24 & 0xFF)}"] if width in {"uint32", "int32"} else []),
                    f"PUSHI {(val2 >> 0) & 0xFF}",
                    *([f"PUSHI {(val2 >> 8) & 0xFF}"] if width in {"uint16", "int16", "uint32", "int32"} else []),
                    *([f"PUSHI {(val2 >> 16) & 0xFF}", f"PUSHI {(val2 >> 24 & 0xFF)}"] if width in {"uint32", "int32"} else []),
                    "LOADI 111",
                    "MOV A, U",
                    "LOADI 222",
                    "MOV A, V",
                    "LOADI 123",
                    "CALL callable",
                    "HALT",
                    *datalines,
                    *sections.data,
                    *heaplines,
                ]))
                cpu = CPUCore(memory)
                rununtilhalt(cpu)

                _assert(
                    cpu.a == 123,
                    f"min changed accumulator value from {123} to {cpu.a}!",
                )
                _assert(
                    cpu.u == 111,
                    f"min changed U value from {111} to {cpu.u}!",
                )
                _assert(
                    cpu.v == 222,
                    f"min changed V value from {222} to {cpu.v}!",
                )
                if width == "uint8":
                    result = cpu.ram[cpu.pc + 0]
                elif width == "int8":
                    result = bintoint(cpu.ram[cpu.pc + 0])
                elif width == "uint16":
                    result = (
                        (cpu.ram[cpu.pc] << 8) + cpu.ram[cpu.pc + 1]
                    )
                elif width == "int16":
                    result = bintoint16(
                        (cpu.ram[cpu.pc] << 8) + cpu.ram[cpu.pc + 1]
                    )
                elif width == "uint32":
                    result = (
                        (cpu.ram[cpu.pc] << 24) +
                        (cpu.ram[cpu.pc + 1] << 16) +
                        (cpu.ram[cpu.pc + 2] << 8) +
                        cpu.ram[cpu.pc + 3]
                    )
                else:
                    result = bintoint32(
                        (cpu.ram[cpu.pc] << 24) +
                        (cpu.ram[cpu.pc + 1] << 16) +
                        (cpu.ram[cpu.pc + 2] << 8) +
                        cpu.ram[cpu.pc + 3]
                    )
                expected = realmin(val1, val2, width)
                _assert(
                    result == expected,
                    "Failed to min({val1}, {val2}), "
                    + f"got {result} instead of {expected}!",
                )
                cycles += cpu.cycles
                instructions += cpu.ticks
                count += 1

    print(f"Average cycles for min: {int(cycles/count)}")
    print(f"Average instructions for min: {int(instructions/count)}")


def verifymax(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "max" not in only and "compiler" not in only:
        return

    print("Verifying max...")

    with open("lib/runtime/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/runtime/start.S", "r") as fp:
        startlines = fp.readlines()
    with open("lib/runtime/data.S", "r") as fp:
        datalines = fp.readlines()
    with open("lib/runtime/heap.S", "r") as fp:
        heaplines = fp.readlines()
    with open("lib/math/cmp.S", "r") as fp:
        cmplines = fp.readlines()

    cycles = 0
    instructions = 0
    count = 0

    def realmax(val1: int, val2: int, width: str) -> int:
        if width == "int8":
            val1 = bintoint(val1)
            val2 = bintoint(val2)
        if width == "int16":
            val1 = bintoint16(val1)
            val2 = bintoint16(val2)
        if width == "int32":
            val1 = bintoint32(val1)
            val2 = bintoint32(val2)
        return max(val1, val2)

    for width in ["uint8", "int8", "uint16", "int16", "uint32", "int32"]:
        for val1 in (
            [0x00, 0xA5, 0x5A, 0xFF, 0x12, 0x34, 0xCD, 0xEF] +
            ([0xFF00, 0x00FF, 0xA5A5, 0xABCD, 0x1337] if width in {"uint16", "int16"} else []) +
            ([0x000000FF, 0x0000FF00, 0x00FF0000, 0xFF000000, 0xA5A5A5A5, 0xDEADBEEF, 0xCAFEBABE, 0xC0FEBABE] if width in {"uint32", "int32"} else [])
        ):
            for val2 in (
                [0x00, 0xA5, 0x5A, 0xFF, 0x12, 0x34, 0xCD, 0xEF] +
                ([0xFF00, 0x00FF, 0xA5A5, 0xABCD, 0x1337] if width in {"uint16", "int16"} else []) +
                ([0x000000FF, 0x0000FF00, 0x00FF0000, 0xFF000000, 0xA5A5A5A5, 0xDEADBEEF, 0xCAFEBABE, 0xC0FEBABE] if width in {"uint32", "int32"} else [])
            ):
                sections = parse_and_compile_module("max", textwrap.dedent(f"""
                    def callable(val1: {width}, val2: {width}) -> nopad[{width}]:
                        return max(val1, val2)
                """), settings)
                memory = getmemory(os.linesep.join([
                    *initlines,
                    *sections.init,
                    *startlines,
                    *sections.code,
                    *cmplines,
                    "main:",
                    f"PUSHI {(val1 >> 0) & 0xFF}",
                    *([f"PUSHI {(val1 >> 8) & 0xFF}"] if width in {"uint16", "int16", "uint32", "int32"} else []),
                    *([f"PUSHI {(val1 >> 16) & 0xFF}", f"PUSHI {(val1 >> 24 & 0xFF)}"] if width in {"uint32", "int32"} else []),
                    f"PUSHI {(val2 >> 0) & 0xFF}",
                    *([f"PUSHI {(val2 >> 8) & 0xFF}"] if width in {"uint16", "int16", "uint32", "int32"} else []),
                    *([f"PUSHI {(val2 >> 16) & 0xFF}", f"PUSHI {(val2 >> 24 & 0xFF)}"] if width in {"uint32", "int32"} else []),
                    "LOADI 111",
                    "MOV A, U",
                    "LOADI 222",
                    "MOV A, V",
                    "LOADI 123",
                    "CALL callable",
                    "HALT",
                    *datalines,
                    *sections.data,
                    *heaplines,
                ]))
                cpu = CPUCore(memory)
                rununtilhalt(cpu)

                _assert(
                    cpu.a == 123,
                    f"max changed accumulator value from {123} to {cpu.a}!",
                )
                _assert(
                    cpu.u == 111,
                    f"max changed U value from {111} to {cpu.u}!",
                )
                _assert(
                    cpu.v == 222,
                    f"max changed V value from {222} to {cpu.v}!",
                )
                if width == "uint8":
                    result = cpu.ram[cpu.pc + 0]
                elif width == "int8":
                    result = bintoint(cpu.ram[cpu.pc + 0])
                elif width == "uint16":
                    result = (
                        (cpu.ram[cpu.pc] << 8) + cpu.ram[cpu.pc + 1]
                    )
                elif width == "int16":
                    result = bintoint16(
                        (cpu.ram[cpu.pc] << 8) + cpu.ram[cpu.pc + 1]
                    )
                elif width == "uint32":
                    result = (
                        (cpu.ram[cpu.pc] << 24) +
                        (cpu.ram[cpu.pc + 1] << 16) +
                        (cpu.ram[cpu.pc + 2] << 8) +
                        cpu.ram[cpu.pc + 3]
                    )
                else:
                    result = bintoint32(
                        (cpu.ram[cpu.pc] << 24) +
                        (cpu.ram[cpu.pc + 1] << 16) +
                        (cpu.ram[cpu.pc + 2] << 8) +
                        cpu.ram[cpu.pc + 3]
                    )
                expected = realmax(val1, val2, width)
                _assert(
                    result == expected,
                    "Failed to max({val1}, {val2}), "
                    + f"got {result} instead of {expected}!",
                )
                cycles += cpu.cycles
                instructions += cpu.ticks
                count += 1

    print(f"Average cycles for max: {int(cycles/count)}")
    print(f"Average instructions for max: {int(instructions/count)}")


def verifyoptimizations(only: Optional[Container[str]], full: bool) -> None:
    if only is not None and "optimizations" not in only and "compiler" not in only:
        return

    print("Verifying optimizations...")

    with open("lib/runtime/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/runtime/start.S", "r") as fp:
        startlines = fp.readlines()
    with open("lib/runtime/data.S", "r") as fp:
        datalines = fp.readlines()
    with open("lib/runtime/heap.S", "r") as fp:
        heaplines = fp.readlines()
    with open("lib/math/cmp.S", "r") as fp:
        cmplines = fp.readlines()
    with open("lib/string/strcmp.S", "r") as fp:
        strcmplines = fp.readlines()
    with open("lib/string/strcpy.S", "r") as fp:
        strcpylines = fp.readlines()

    cycles = 0
    instructions = 0
    count = 0

    left: Any
    right: Any

    # First, equality of various types.
    for vtype, left, right in [
        ("uint8", 5, 5),
        ("uint8", 5, 10),
        ("int8", 5, 5),
        ("int8", 5, 10),
        ("uint16", 5, 5),
        ("uint16", 5, 10),
        ("int16", 5, 5),
        ("int16", 5, 10),
        ("uint32", 5, 5),
        ("uint32", 5, 10),
        ("int32", 5, 5),
        ("int32", 5, 10),
    ]:
        sections = parse_and_compile_module("optimizations", textwrap.dedent(f"""
            def callable(val1: {vtype}, val2: {vtype}) -> nopad[bool]:
                if val1 == val2:
                    return True
                else:
                    return False
        """), settings)
        memory = getmemory(os.linesep.join([
            *initlines,
            *sections.init,
            *startlines,
            *sections.code,
            *cmplines,
            *strcmplines,
            "main:",
            f"PUSHI {(left >> 0) & 0xFF}",
            *([f"PUSHI {(left >> 8) & 0xFF}"] if vtype in {"uint16", "int16", "uint32", "int32"} else []),
            *([f"PUSHI {(left >> 16) & 0xFF}", f"PUSHI {(left >> 24 & 0xFF)}"] if vtype in {"uint32", "int32"} else []),
            f"PUSHI {(right >> 0) & 0xFF}",
            *([f"PUSHI {(right >> 8) & 0xFF}"] if vtype in {"uint16", "int16", "uint32", "int32"} else []),
            *([f"PUSHI {(right >> 16) & 0xFF}", f"PUSHI {(right >> 24 & 0xFF)}"] if vtype in {"uint32", "int32"} else []),
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            "LOADI 123",
            "CALL callable",
            "HALT",
            *datalines,
            *sections.data,
            *heaplines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        _assert(
            cpu.a == 123,
            f"optimizations changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"optimizations changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"optimizations changed V value from {222} to {cpu.v}!",
        )
        result = bool(cpu.ram[cpu.pc + 0])
        expected = left == right
        _assert(
            result == expected,
            "Failed to optimizations equality with {val1} and {val2}, "
            + f"got {result} instead of {expected}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    for left, right in [('a', 'a'), ('a', 'c')]:
        sections = parse_and_compile_module("optimizations", textwrap.dedent("""
            def callable(val1: char, val2: char) -> nopad[bool]:
                if val1 == val2:
                    return True
                else:
                    return False
        """), settings)
        memory = getmemory(os.linesep.join([
            *initlines,
            *sections.init,
            *startlines,
            *sections.code,
            *cmplines,
            *strcmplines,
            "main:",
            f"PUSHI {left!r}",
            f"PUSHI {right!r}",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            "LOADI 123",
            "CALL callable",
            "HALT",
            *datalines,
            *sections.data,
            *heaplines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        _assert(
            cpu.a == 123,
            f"optimizations changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"optimizations changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"optimizations changed V value from {222} to {cpu.v}!",
        )
        result = bool(cpu.ram[cpu.pc + 0])
        expected = left == right
        _assert(
            result == expected,
            "Failed to optimizations equality with {val1} and {val2}, "
            + f"got {result} instead of {expected}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    for left, right in [("abc", "abc"), ("abc", "def")]:
        sections = parse_and_compile_module("optimizations", textwrap.dedent(f"""
            def inner(val1: const[str], val2: const[str]) -> nopad[bool]:
                if val1 == val2:
                    return True
                else:
                    return False

            def callable() -> nopad[bool]:
                left: const[str] = {left!r}
                right: const[str] = {right!r}
                return inner(left, right)
        """), settings)
        memory = getmemory(os.linesep.join([
            *initlines,
            *sections.init,
            *startlines,
            *sections.code,
            *cmplines,
            *strcmplines,
            "main:",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            "LOADI 123",
            "CALL callable",
            "HALT",
            *datalines,
            *sections.data,
            *heaplines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        _assert(
            cpu.a == 123,
            f"optimizations changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"optimizations changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"optimizations changed V value from {222} to {cpu.v}!",
        )
        result = bool(cpu.ram[cpu.pc + 0])
        expected = left == right
        _assert(
            result == expected,
            "Failed to optimizations equality with {val1} and {val2}, "
            + f"got {result} instead of {expected}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    # Second, inequality of various types.
    for vtype, left, right in [
        ("uint8", 5, 5),
        ("uint8", 5, 10),
        ("int8", 5, 5),
        ("int8", 5, 10),
        ("uint16", 5, 5),
        ("uint16", 5, 10),
        ("int16", 5, 5),
        ("int16", 5, 10),
        ("uint32", 5, 5),
        ("uint32", 5, 10),
        ("int32", 5, 5),
        ("int32", 5, 10),
    ]:
        sections = parse_and_compile_module("optimizations", textwrap.dedent(f"""
            def callable(val1: {vtype}, val2: {vtype}) -> nopad[bool]:
                if val1 != val2:
                    return True
                else:
                    return False
        """), settings)
        memory = getmemory(os.linesep.join([
            *initlines,
            *sections.init,
            *startlines,
            *sections.code,
            *cmplines,
            *strcmplines,
            "main:",
            f"PUSHI {(left >> 0) & 0xFF}",
            *([f"PUSHI {(left >> 8) & 0xFF}"] if vtype in {"uint16", "int16", "uint32", "int32"} else []),
            *([f"PUSHI {(left >> 16) & 0xFF}", f"PUSHI {(left >> 24 & 0xFF)}"] if vtype in {"uint32", "int32"} else []),
            f"PUSHI {(right >> 0) & 0xFF}",
            *([f"PUSHI {(right >> 8) & 0xFF}"] if vtype in {"uint16", "int16", "uint32", "int32"} else []),
            *([f"PUSHI {(right >> 16) & 0xFF}", f"PUSHI {(right >> 24 & 0xFF)}"] if vtype in {"uint32", "int32"} else []),
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            "LOADI 123",
            "CALL callable",
            "HALT",
            *datalines,
            *sections.data,
            *heaplines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        _assert(
            cpu.a == 123,
            f"optimizations changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"optimizations changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"optimizations changed V value from {222} to {cpu.v}!",
        )
        result = bool(cpu.ram[cpu.pc + 0])
        expected = left != right
        _assert(
            result == expected,
            "Failed to optimizations inequality with {val1} and {val2}, "
            + f"got {result} instead of {expected}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    for left, right in [('a', 'a'), ('a', 'c')]:
        sections = parse_and_compile_module("optimizations", textwrap.dedent("""
            def callable(val1: char, val2: char) -> nopad[bool]:
                if val1 != val2:
                    return True
                else:
                    return False
        """), settings)
        memory = getmemory(os.linesep.join([
            *initlines,
            *sections.init,
            *startlines,
            *sections.code,
            *cmplines,
            *strcmplines,
            "main:",
            f"PUSHI {left!r}",
            f"PUSHI {right!r}",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            "LOADI 123",
            "CALL callable",
            "HALT",
            *datalines,
            *sections.data,
            *heaplines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        _assert(
            cpu.a == 123,
            f"optimizations changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"optimizations changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"optimizations changed V value from {222} to {cpu.v}!",
        )
        result = bool(cpu.ram[cpu.pc + 0])
        expected = left != right
        _assert(
            result == expected,
            "Failed to optimizations inequality with {val1} and {val2}, "
            + f"got {result} instead of {expected}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    for left, right in [("abc", "abc"), ("abc", "def")]:
        sections = parse_and_compile_module("optimizations", textwrap.dedent(f"""
            def inner(val1: const[str], val2: const[str]) -> nopad[bool]:
                if val1 != val2:
                    return True
                else:
                    return False

            def callable() -> nopad[bool]:
                left: const[str] = {left!r}
                right: const[str] = {right!r}
                return inner(left, right)
        """), settings)
        memory = getmemory(os.linesep.join([
            *initlines,
            *sections.init,
            *startlines,
            *sections.code,
            *cmplines,
            *strcmplines,
            "main:",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            "LOADI 123",
            "CALL callable",
            "HALT",
            *datalines,
            *sections.data,
            *heaplines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        _assert(
            cpu.a == 123,
            f"optimizations changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"optimizations changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"optimizations changed V value from {222} to {cpu.v}!",
        )
        result = bool(cpu.ram[cpu.pc + 0])
        expected = left != right
        _assert(
            result == expected,
            "Failed to optimizations inequality with {val1} and {val2}, "
            + f"got {result} instead of {expected}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    # Third, alligator expressions of various types.
    for check in ["<", "<=", ">", ">="]:
        for vtype, left, right in [
            ("uint8", 5, 0),
            ("uint8", 5, 5),
            ("uint8", 5, 10),
            ("int8", 5, 0),
            ("int8", 5, 5),
            ("int8", 5, 10),
            ("uint16", 5, 0),
            ("uint16", 5, 5),
            ("uint16", 5, 10),
            ("int16", 5, 0),
            ("int16", 5, 5),
            ("int16", 5, 10),
            ("uint32", 5, 0),
            ("uint32", 5, 5),
            ("uint32", 5, 10),
            ("int32", 5, 0),
            ("int32", 5, 5),
            ("int32", 5, 10),
        ]:
            sections = parse_and_compile_module("optimizations", textwrap.dedent(f"""
                def callable(val1: {vtype}, val2: {vtype}) -> nopad[bool]:
                    if val1 {check} val2:
                        return True
                    else:
                        return False
            """), settings)
            memory = getmemory(os.linesep.join([
                *initlines,
                *sections.init,
                *startlines,
                *sections.code,
                *cmplines,
                *strcmplines,
                "main:",
                f"PUSHI {(left >> 0) & 0xFF}",
                *([f"PUSHI {(left >> 8) & 0xFF}"] if vtype in {"uint16", "int16", "uint32", "int32"} else []),
                *([f"PUSHI {(left >> 16) & 0xFF}", f"PUSHI {(left >> 24 & 0xFF)}"] if vtype in {"uint32", "int32"} else []),
                f"PUSHI {(right >> 0) & 0xFF}",
                *([f"PUSHI {(right >> 8) & 0xFF}"] if vtype in {"uint16", "int16", "uint32", "int32"} else []),
                *([f"PUSHI {(right >> 16) & 0xFF}", f"PUSHI {(right >> 24 & 0xFF)}"] if vtype in {"uint32", "int32"} else []),
                "LOADI 111",
                "MOV A, U",
                "LOADI 222",
                "MOV A, V",
                "LOADI 123",
                "CALL callable",
                "HALT",
                *datalines,
                *sections.data,
                *heaplines,
            ]))
            cpu = CPUCore(memory)
            rununtilhalt(cpu)

            _assert(
                cpu.a == 123,
                f"optimizations changed accumulator value from {123} to {cpu.a}!",
            )
            _assert(
                cpu.u == 111,
                f"optimizations changed U value from {111} to {cpu.u}!",
            )
            _assert(
                cpu.v == 222,
                f"optimizations changed V value from {222} to {cpu.v}!",
            )
            result = bool(cpu.ram[cpu.pc + 0])
            expected = eval(f"{left} {check} {right}")
            _assert(
                result == expected,
                "Failed to optimizations {check} with {val1} and {val2}, "
                + f"got {result} instead of {expected}!",
            )
            cycles += cpu.cycles
            instructions += cpu.ticks
            count += 1

    # Verify truncation of self.
    if True:
        sections = parse_and_compile_module("stringtruncation", textwrap.dedent("""
            def func() -> str:
                string: str[32] = "Hello!"
                string = string[:5]
                return string
        """), settings)
        memory = getmemory(os.linesep.join([
            *initlines,
            *sections.init,
            *startlines,
            *sections.code,
            *strcpylines,
            "main:",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            "LOADI 123",
            "SUBPCI 2",
            "CALL func",
            "HALT",
            *datalines,
            *sections.data,
            *heaplines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        assertmemory("stringtruncation", memory, cpu.ram)
        _assert(
            cpu.a == 123,
            f"stringtruncation changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"stringtruncation changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"stringtruncation changed V value from {222} to {cpu.v}!",
        )
        resultstr = bintostr(cpu, (cpu.ram[cpu.pc] << 8) + cpu.ram[cpu.pc + 1], 0xC000, 0x10000)
        expectedstr = "Hello"
        _assert(
            resultstr == expectedstr,
            "Failed to stringtruncation, "
            + f"got {resultstr!r} instead of {expectedstr!r}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    # Verify while loop optimization.
    if True:
        sections = parse_and_compile_module("whileoptimization", textwrap.dedent("""
            def func() -> str:
                string: str[32] = "Hello!"
                idx: uint8 = 0

                while string[idx] != "!":
                    idx += 1

                string = string[:idx]
                return string
        """), settings)
        memory = getmemory(os.linesep.join([
            *initlines,
            *sections.init,
            *startlines,
            *sections.code,
            *strcpylines,
            "main:",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            "LOADI 123",
            "SUBPCI 2",
            "CALL func",
            "HALT",
            *datalines,
            *sections.data,
            *heaplines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        assertmemory("stringtruncation", memory, cpu.ram)
        _assert(
            cpu.a == 123,
            f"stringtruncation changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"stringtruncation changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"stringtruncation changed V value from {222} to {cpu.v}!",
        )
        resultstr = bintostr(cpu, (cpu.ram[cpu.pc] << 8) + cpu.ram[cpu.pc + 1], 0xC000, 0x10000)
        expectedstr = "Hello"
        _assert(
            resultstr == expectedstr,
            "Failed to stringtruncation, "
            + f"got {resultstr!r} instead of {expectedstr!r}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    # Verify while loop optimization.
    if True:
        sections = parse_and_compile_module("whileoptimization", textwrap.dedent("""
            def func() -> str:
                string: str[32] = "+++!!"
                idx: uint8 = 0

                while string[idx] == "+":
                    idx += 1

                string = string[:idx]
                return string
        """), settings)
        memory = getmemory(os.linesep.join([
            *initlines,
            *sections.init,
            *startlines,
            *sections.code,
            *strcpylines,
            "main:",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            "LOADI 123",
            "SUBPCI 2",
            "CALL func",
            "HALT",
            *datalines,
            *sections.data,
            *heaplines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        assertmemory("stringtruncation", memory, cpu.ram)
        _assert(
            cpu.a == 123,
            f"stringtruncation changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"stringtruncation changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"stringtruncation changed V value from {222} to {cpu.v}!",
        )
        resultstr = bintostr(cpu, (cpu.ram[cpu.pc] << 8) + cpu.ram[cpu.pc + 1], 0xC000, 0x10000)
        expectedstr = "+++"
        _assert(
            resultstr == expectedstr,
            "Failed to stringtruncation, "
            + f"got {resultstr!r} instead of {expectedstr!r}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    # Verify while loop optimization.
    if True:
        sections = parse_and_compile_module("whileoptimization", textwrap.dedent("""
            def func() -> str:
                string: str[32] = "Hello!"
                idx: uint8 = 0

                while string[idx]:
                    idx += 1

                string = string[:idx]
                return string
        """), settings)
        memory = getmemory(os.linesep.join([
            *initlines,
            *sections.init,
            *startlines,
            *sections.code,
            *strcpylines,
            "main:",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            "LOADI 123",
            "SUBPCI 2",
            "CALL func",
            "HALT",
            *datalines,
            *sections.data,
            *heaplines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        assertmemory("stringtruncation", memory, cpu.ram)
        _assert(
            cpu.a == 123,
            f"stringtruncation changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"stringtruncation changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"stringtruncation changed V value from {222} to {cpu.v}!",
        )
        resultstr = bintostr(cpu, (cpu.ram[cpu.pc] << 8) + cpu.ram[cpu.pc + 1], 0xC000, 0x10000)
        expectedstr = "Hello!"
        _assert(
            resultstr == expectedstr,
            "Failed to stringtruncation, "
            + f"got {resultstr!r} instead of {expectedstr!r}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    # Verify while loop optimization.
    if True:
        sections = parse_and_compile_module("whileoptimization", textwrap.dedent("""
            def func() -> str:
                string: str[32] = "Hello!"
                idx: uint8 = 0

                while idx < 3:
                    idx += 1

                string = string[:idx]
                return string
        """), settings)
        memory = getmemory(os.linesep.join([
            *initlines,
            *sections.init,
            *startlines,
            *sections.code,
            *strcpylines,
            *cmplines,
            "main:",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            "LOADI 123",
            "SUBPCI 2",
            "CALL func",
            "HALT",
            *datalines,
            *sections.data,
            *heaplines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        assertmemory("stringtruncation", memory, cpu.ram)
        _assert(
            cpu.a == 123,
            f"stringtruncation changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"stringtruncation changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"stringtruncation changed V value from {222} to {cpu.v}!",
        )
        resultstr = bintostr(cpu, (cpu.ram[cpu.pc] << 8) + cpu.ram[cpu.pc + 1], 0xC000, 0x10000)
        expectedstr = "Hel"
        _assert(
            resultstr == expectedstr,
            "Failed to stringtruncation, "
            + f"got {resultstr!r} instead of {expectedstr!r}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    # Verify while loop optimization.
    if True:
        sections = parse_and_compile_module("whileoptimization", textwrap.dedent("""
            def func() -> str:
                string: str[32] = "Hello!"
                idx: uint8 = 0

                while idx <= 3:
                    idx += 1

                string = string[:idx]
                return string
        """), settings)
        memory = getmemory(os.linesep.join([
            *initlines,
            *sections.init,
            *startlines,
            *sections.code,
            *strcpylines,
            *cmplines,
            "main:",
            "LOADI 111",
            "MOV A, U",
            "LOADI 222",
            "MOV A, V",
            "LOADI 123",
            "SUBPCI 2",
            "CALL func",
            "HALT",
            *datalines,
            *sections.data,
            *heaplines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)

        assertmemory("stringtruncation", memory, cpu.ram)
        _assert(
            cpu.a == 123,
            f"stringtruncation changed accumulator value from {123} to {cpu.a}!",
        )
        _assert(
            cpu.u == 111,
            f"stringtruncation changed U value from {111} to {cpu.u}!",
        )
        _assert(
            cpu.v == 222,
            f"stringtruncation changed V value from {222} to {cpu.v}!",
        )
        resultstr = bintostr(cpu, (cpu.ram[cpu.pc] << 8) + cpu.ram[cpu.pc + 1], 0xC000, 0x10000)
        expectedstr = "Hell"
        _assert(
            resultstr == expectedstr,
            "Failed to stringtruncation, "
            + f"got {resultstr!r} instead of {expectedstr!r}!",
        )
        cycles += cpu.cycles
        instructions += cpu.ticks
        count += 1

    print(f"Average cycles for optimizations: {int(cycles/count)}")
    print(f"Average instructions for optimizations: {int(instructions/count)}")


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
        "-c",
        "--highlight-changes",
        help="Highlight changes between instructions in red.",
        action="store_true",
    )
    parser.add_argument(
        "-p",
        "--print-code",
        help="Print code before sending it to the assembler.",
        action="store_true",
    )
    parser.add_argument(
        "-o",
        "--only",
        help="Only run this test (comma separated values allowed).",
        type=str,
        default=None,
    )
    parser.add_argument(
        "-d",
        "--disable-optimizations",
        help="Disable compiler optimizations",
        action="store_true",
    )
    args = parser.parse_args()
    only = {
        x.strip() for x in args.only.lower().split(',')
    } if args.only else None

    # Make sure we can debug.
    verbose = args.verbose
    highlight_changes = args.highlight_changes
    print_code = args.print_code
    settings = CompilerSettings(optimize=not args.disable_optimizations)

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
    verifylshift8(only, args.full)
    verifylshift16(only, args.full)
    verifylshift32(only, args.full)
    verifyrshift8(only, args.full)
    verifyrshift16(only, args.full)
    verifyrshift32(only, args.full)
    verifyadd8(only, args.full)
    verifyadd16(only, args.full)
    verifyadd32(only, args.full)
    verifymult8(only, args.full)
    verifymult16(only, args.full)
    verifymult32(only, args.full)
    verifyudiv8(only, args.full)
    verifyudiv16(only, args.full)
    verifyudiv32(only, args.full)
    verifyabs8(only, args.full)
    verifyabs16(only, args.full)
    verifyabs32(only, args.full)
    verifyucmp8(only, args.full)
    verifyucmp16(only, args.full)
    verifyucmp32(only, args.full)
    verifycmp8(only, args.full)
    verifycmp16(only, args.full)
    verifycmp32(only, args.full)
    verifyumin8(only, args.full)
    verifyumin16(only, args.full)
    verifyumin32(only, args.full)
    verifyumax8(only, args.full)
    verifyumax16(only, args.full)
    verifyumax32(only, args.full)
    verifymin8(only, args.full)
    verifymin16(only, args.full)
    verifymin32(only, args.full)
    verifymax8(only, args.full)
    verifymax16(only, args.full)
    verifymax32(only, args.full)
    verifyneg8(only, args.full)
    verifyneg16(only, args.full)
    verifyneg32(only, args.full)

    # String library verification
    verifystrlen(only, args.full)
    verifystrcpy(only, args.full)
    verifystrncpy(only, args.full)
    verifystrcat(only, args.full)
    verifystrcmp(only, args.full)

    # Conversion library verification
    verifyitoa8(only, args.full)
    verifyitoa16(only, args.full)
    verifyitoa32(only, args.full)
    verifyutoa8(only, args.full)
    verifyutoa16(only, args.full)
    verifyutoa32(only, args.full)
    verifyatoi8(only, args.full)
    verifyatoi16(only, args.full)
    verifyatoi32(only, args.full)

    # Compiler verifications
    verifyimports(only, args.full)
    verifyextern(only, args.full)
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
    verifyshiftandreturn(only, args.full)
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
    verifystringlength(only, args.full)
    verifystringconcatenation(only, args.full)
    verifystringsubscript(only, args.full)
    verifystringslice(only, args.full)
    verifystringassignment(only, args.full)
    verifystringcast(only, args.full)
    verifystringformat(only, args.full)
    verifystringcombination(only, args.full)
    verifystringloop(only, args.full)
    verifypeek(only, args.full)
    verifypoke(only, args.full)
    verifycast(only, args.full)
    verifyabs(only, args.full)
    verifybool(only, args.full)
    verifychr(only, args.full)
    verifyord(only, args.full)
    verifyint(only, args.full)
    verifyhex(only, args.full)
    verifymin(only, args.full)
    verifymax(only, args.full)
    verifyoptimizations(only, args.full)
