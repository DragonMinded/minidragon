#! /usr/bin/python3
import argparse
import os
from typing import List
from core import CPUCore, assemble, bintoint

CLEAR_LINE = "\033[F\033[K"
BACK_AND_CLEAR_LINE = "\033[F\033[K\033[F"


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


def verifyloadi(full: bool) -> None:
    print("Verifying LOADI...")
    for i in range(-32, 32):
        memory = getmemory(f"""
            LOADI {i}
            HALT
        """)
        cpu = CPUCore(memory)
        rununtilhalt(cpu)
        assert bintoint(cpu.a) == i, f"Failed to load {i} into A register!"


def verifyaddi(full: bool) -> None:
    print("Verifying ADDI...")
    for i in range(-32, 32):
        memory = getmemory(f"""
            LOADI 5
            ADDI {i}
            HALT
        """)
        cpu = CPUCore(memory)
        rununtilhalt(cpu)
        assert bintoint(cpu.a) == (i + 5), f"Failed to add {i} to A register!"


def verifyseta(full: bool) -> None:
    print("Verifying SETA...")
    for i in range(0, 256):
        memory = getmemory(f"""
            SETA {i}
            HALT
        """)
        cpu = CPUCore(memory)
        rununtilhalt(cpu)
        assert cpu.a == i, f"Failed to set A to {i}!"

    for i in range(-128, 128):
        memory = getmemory(f"""
            SETA {i}
            HALT
        """)
        cpu = CPUCore(memory)
        rununtilhalt(cpu)
        assert bintoint(cpu.a) == i, f"Failed to set A to {i}!"


def verifysetpc(full: bool) -> None:
    print("Verifying SETPC...")
    print("0% complete...")
    for i in range(0, 0xFFFF, 1 if full else 29):
        memory = getmemory(f"""
            SETPC {i}
            HALT
        """)
        cpu = CPUCore(memory)
        rununtilhalt(cpu)
        assert cpu.p[0] == (i >> 8) & 0xFF, f"Failed to set PC to {i}!"
        assert cpu.c[0] == i & 0xFF, f"Failed to set PC to {i}!"

        if i & 0xFF == 0:
            print(f"{CLEAR_LINE}{int((i * 100) / 0xFFFF)}% complete...")
    print(BACK_AND_CLEAR_LINE)


def verifyneg(full: bool) -> None:
    print("Verifying NEG...")
    for i in range(-127, 128):
        memory = getmemory(f"""
            SETA {i}
            NEG
            HALT
        """)
        cpu = CPUCore(memory)
        rununtilhalt(cpu)
        assert bintoint(cpu.a) == -i, f"Failed to negate A!"


def verifyaddpc(full: bool) -> None:
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
        assert cpu.p[0] == ((0x01FA + i) >> 8) & 0xFF, f"Failed to ADDPC {i}!"
        assert cpu.c[0] == (0x01FA + i) & 0xFF, f"Failed to ADDPC {i}!"
    print(BACK_AND_CLEAR_LINE)


def verifysubpc(full: bool) -> None:
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
        assert cpu.p[0] == ((0x0204 - i) >> 8) & 0xFF, f"Failed to SUBPC {i}!"
        assert cpu.c[0] == (0x0204 - i) & 0xFF, f"Failed to SUBPC {i}!"
    print(BACK_AND_CLEAR_LINE)


def verifymultiply(full: bool) -> None:
    print("Verifying multiply...")
    print("0% complete...")

    with open("lib/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/multiply.S", "r") as fp:
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
            assert cpu.a == x * y, f"Failed to multiply {x} by {y}, got {cpu.a} instead of {x * y}!"
            cycles += cpu.cycles
            instructions += cpu.ticks
            count += 1

        print(f"{CLEAR_LINE}{int((x * 100) / 16)}% complete...")
    print(f"{CLEAR_LINE}Average cycles for multiply: {int(cycles/count)}")
    print(f"Average instructions for multiply: {int(instructions/count)}")


def verifyadd16(full: bool) -> None:
    print("Verifying add16...")
    print("0% complete...")

    with open("lib/init.S", "r") as fp:
        initlines = fp.readlines()
    with open("lib/add16.S", "r") as fp:
        addlines = fp.readlines()

    cycles = 0
    instructions = 0
    count = 0
    for x in range(0, 65536, 1 if full else 100):
        for y in range(0, 65536, 1 if full else 95):
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
            cpu.dump()
            answer = (cpu.ram[cpu.pc[0]] << 8) + cpu.ram[cpu.pc[0] + 1]
            assert answer == x + y, f"Failed to add16 {x} and {y}, got {answer} instead of {x + y}!"
            cycles += cpu.cycles
            instructions += cpu.ticks
            count += 1

        print(f"{CLEAR_LINE}{int((x * 100) / 16)}% complete...")
    print(f"{CLEAR_LINE}Average cycles for add16: {int(cycles/count)}")
    print(f"Average instructions for add16: {int(instructions/count)}")


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
    args = parser.parse_args()

    # Raw instruction verification
    verifyloadi(args.full)
    verifyaddi(args.full)
    verifyseta(args.full)
    verifysetpc(args.full)
    verifyneg(args.full)
    verifyaddpc(args.full)
    verifysubpc(args.full)

    # Function library verification
    verifymultiply(args.full)
    #verifyadd16(args.full)
