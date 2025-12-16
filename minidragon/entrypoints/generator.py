import argparse
import os
import sys
from typing import List


def main() -> None:
    parser = argparse.ArgumentParser(
        description="A utility to convert binary data to MiniDragon Assembly."
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        help="The code file we will produce, defaults to out.S",
        default="out.S",
    )
    parser.add_argument(
        "file",
        metavar="FILE",
        type=str,
        help="File to convert",
    )
    parser.add_argument(
        "label",
        metavar="GLOBAL",
        type=str,
        help="Name of the global constant for the converted data",
    )
    args = parser.parse_args()

    for ch in args.label:
        if ch not in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_":
            print(f"Global constant name contains illegal character {ch!r}", file=sys.stderr)
            sys.exit(1)

    with open(args.file, "rb") as bfp:
        data = bfp.read()

    lines: List[str] = [f"{args.label}:"]
    for b in data:
        lines.append(f"  .byte {hex(b)}")

    with open(args.output, "w") as fp:
        fp.write(os.linesep.join(lines) + os.linesep)

    sys.exit(0)


if __name__ == "__main__":
    main()
