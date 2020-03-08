#! /usr/bin/python3
import argparse
import os
from typing import List, Optional
from core import CPUCore, assemble, bintoint

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


def verifyaddpc(only: Optional[str], full: bool) -> None:
    if only is not None and only != "addpc":
        return

    print("Verifying ADDPC...")
    print("0% complete...")
    for i in range(1, 9):
        memory = getmemory(f"""
            SETPC 0x01FA
            ADDPC {i}
            HALT
        """)
        cpu = CPUCore(memory)
        rununtilhalt(cpu)
        _assert(
            cpu.p[0] == ((0x01FA + i) >> 8) & 0xFF,
            f"Failed to ADDPC {i}!",
        )
        _assert(cpu.c[0] == (0x01FA + i) & 0xFF, f"Failed to ADDPC {i}!")
    print(BACK_AND_CLEAR_LINE)


def verifysubpc(only: Optional[str], full: bool) -> None:
    if only is not None and only != "subpc":
        return

    print("Verifying SUBPC...")
    print("0% complete...")
    for i in range(1, 9):
        memory = getmemory(f"""
            SETPC 0x0204
            SUBPC {i}
            HALT
        """)
        cpu = CPUCore(memory)
        rununtilhalt(cpu)
        _assert(
            cpu.p[0] == ((0x0204 - i) >> 8) & 0xFF,
            f"Failed to SUBPC {i}!",
        )
        _assert(cpu.c[0] == (0x0204 - i) & 0xFF, f"Failed to SUBPC {i}!")
    print(BACK_AND_CLEAR_LINE)


def verifymultiply(only: Optional[str], full: bool) -> None:
    if only is not None and only != "multiply":
        return

    print("Verifying multiply...")
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
                f"CALL multiply",
                f"HALT",
                *multiplylines,
            ]))
            cpu = CPUCore(memory)
            rununtilhalt(cpu)
            _assert(
                cpu.a == x * y,
                f"Failed to multiply {x} by {y}, "
                + "got {cpu.a} instead of {x * y}!",
            )
            cycles += cpu.cycles
            instructions += cpu.ticks
            count += 1

        print(f"{CLEAR_LINE}{int((x * 100) / 16)}% complete...")
    print(f"{CLEAR_LINE}Average cycles for multiply: {int(cycles/count)}")
    print(f"Average instructions for multiply: {int(instructions/count)}")


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
                f"CALL add16",
                f"HALT",
                *addlines,
            ]))
            cpu = CPUCore(memory)
            rununtilhalt(cpu)
            calculated = (cpu.ram[cpu.pc[0]] << 8) + cpu.ram[cpu.pc[0] + 1]
            real = (x + y) & 0xFFFF
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
    with open("lib/math/abs.S", "r") as fp:
        addlines = fp.readlines()

    cycles = 0
    instructions = 0
    count = 0
    for x in range(-127, 128):
        memory = getmemory(os.linesep.join([
            *initlines,
            f"SETA {x}",
            f"CALL abs",
            f"HALT",
            *addlines,
        ]))
        cpu = CPUCore(memory)
        rununtilhalt(cpu)
        _assert(
            cpu.a == abs(x),
            f"Failed to abs({x}), got {cpu.a} instead of {x}!",
        )


def verifystrlen(only: Optional[str], full: bool) -> None:
    if only is not None and only != "strlen":
        return

    print("Verifying strlen...")

    with open("lib/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/string/strlen.S", "r") as fp:
        liblines = fp.readlines()

    for string in [
        "a test",
        "the quick brown fox jumps over the lazy dog",
        "",
        "whatever this is",
    ]:
        memory = getmemory(os.linesep.join([
            *initlines,
            "LNGJUMP code",
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
        _assert(
            cpu.a == len(string),
            f"Failed to strlen({string!r}), "
            + f"got {cpu.a} instead of {len(string)}",
        )


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

    # Raw instruction verification
    verifyloadi(only, args.full)
    verifyaddi(only, args.full)
    verifyseta(only, args.full)
    verifysetpc(only, args.full)
    verifyneg(only, args.full)
    verifyaddpc(only, args.full)
    verifysubpc(only, args.full)

    # Function library verification
    verifymultiply(only, args.full)
    verifyadd16(only, args.full)
    verifyadd32(only, args.full)
    verifyabs(only, args.full)

    verifystrlen(only, args.full)
