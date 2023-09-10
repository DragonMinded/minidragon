#! /usr/bin/python3
import argparse
import os
from typing import List
from core import CPUCore, assemble, getint


def getlines(instr: str) -> List[str]:
    lines: List[str] = []

    for line in instr.split(os.linesep):
        line, *_ = line.split(';')
        line = line.strip()
        if line:
            lines.append(line)
    return lines


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="A simulator for MiniDragon.")
    parser.add_argument(
        "file",
        metavar="FILE",
        help="The assembly file to simulate.",
    )
    parser.add_argument(
        "-b",
        "--binary",
        action="store_true",
        help="Treat input file as a binary instead of assembly file.",
    )
    parser.add_argument(
        "-o",
        "--origin",
        type=str,
        help=(
            "The origin to place the binary file at when specifying a binary."
        ),
        default="0",
    )
    args = parser.parse_args()
    origin = getint(args.origin, 16)

    memory = [0] * 0x8000
    if args.binary:
        with open(args.file, "rb") as bfp:
            data = bfp.read()
        for i, byte in enumerate(data):
            memory[i + origin] = byte
    else:
        with open(args.file, "r") as fp:
            assembled = assemble(getlines(fp.read()))
        for loc, intval in assembled:
            memory[loc] = intval

    cpu = CPUCore(memory)
    cpu.print()

    while True:
        operation = input("> ")
        if operation in ["", "c"]:
            cpu.tick()
            cpu.print()
        elif operation in ["r"]:
            # Advance past the current RET, if we're on one.
            cpu.tick()
            cpu.print()
            while cpu.mnemonic != "POPIP":
                cpu.tick()
                cpu.print()
        elif operation in ["s"]:
            # Somewhat complicated, we want to recursively skip
            # this current function.
            depth = 0
            while True:
                insn, *_ = cpu.mnemonic.split(" ", 1)
                cpu.tick()
                cpu.print()

                if insn == "PUSHIP":
                    depth += 1
                elif insn == "POPIP":
                    depth -= 1

                # If we hit the end of our run, exit.
                if depth == 0:
                    break
        elif operation in ["h"]:
            while True:
                if cpu.mnemonic == "HALT":
                    break
                cpu.tick()
                cpu.print()
        elif operation in ["p"]:
            cpu.print()
        elif operation in ["m"]:
            cpu.dump()
        elif operation in ["d"]:
            cpu.disassemble()
        elif operation in ["q"]:
            break
        elif operation[:2] == "j ":
            ip = int(operation[2:], 16)
            cpu.ip = ip
            cpu.print()
        elif operation[:2] == "a ":
            ip = int(operation[2:], 16)
            while True:
                if cpu.ip == ip:
                    break
                cpu.tick()
                cpu.print()

        elif operation in ["?"]:
            print("c - Continue")
            print("s - Step over")
            print("r - Run until RET")
            print("h - Run until HALT")
            print("a - Run until ADDRESS")
            print("p - Print")
            print("m - Memory contents")
            print("d - Disassemble memory")
            print("j - Jump to hex address")
            print("q - Quit")
        else:
            print("Unrecognized command.")
