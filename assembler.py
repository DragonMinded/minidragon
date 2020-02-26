#! /usr/bin/python3
import argparse
import os
from typing import Dict, List
from core import assemble, getint


def getlines(instr: str) -> List[str]:
    lines: List[str] = []

    for line in instr.split(os.linesep):
        line, *_ = line.split(';')
        line = line.strip()
        if line:
            lines.append(line)
    return lines


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="An assembler for MiniDragon."
    )
    parser.add_argument(
        "-o",
        "--origin",
        type=str,
        help="The origin to place the assembled binary at.",
        required=True,
    )
    parser.add_argument(
        "-s",
        "--size",
        type=str,
        help="The size of the assembled binary.",
        required=True,
    )
    parser.add_argument(
        "-d",
        "--destination",
        type=str,
        help="The destination file, defaults to out.bin",
        default="out.bin",
    )
    parser.add_argument(
        "-g",
        "--generate-symbols",
        action="store_true",
        help="Generate a symbol table file.",
    ),
    parser.add_argument(
        "-y",
        "--symbol-file",
        type=str,
        help="The symbol file, defaults to out.sym",
        default="out.sym",
    ),
    parser.add_argument(
        "-u",
        "--use-symbol-file",
        type=str,
        help=(
            "A symbol file that was previously generated which should be " +
            "used during assembly."
        ),
        default=None,
    )
    parser.add_argument(
        "file",
        metavar="FILE",
        nargs="+",
        type=str,
        help="File to assemble",
    )
    args = parser.parse_args()
    start = getint(args.origin, 16)
    size = getint(args.size, 16)
    lines: List[str] = []

    for fname in args.file:
        with open(fname, "r") as fp:
            lines.extend(getlines(fp.read()))

    labels: Dict[str, int] = {}

    if args.use_symbol_file:
        with open(args.use_symbol_file, "r") as fp:
            symbols = fp.readlines()
            for symbol in symbols:
                label, addr = symbol.split(":", 1)
                label = label.strip()
                address = getint(addr.strip(), 16)
                labels[label] = address

    assembled = assemble(lines, labels)

    memory = [0] * size
    for loc, data in assembled:
        if loc < start or loc >= (start + size):
            raise Exception(
                f"Assembled output tried to place at memory address {loc}!"
            )
        memory[loc - start] = data

    with open(args.destination, "wb") as bfp:
        bfp.write(bytes(memory))

    if args.generate_symbols:
        with open(args.symbol_file, "w") as fp:
            for label, address in labels.items():
                if label.startswith("_"):
                    continue
                fp.write(f"{label}: {hex(address)}{os.linesep}")
