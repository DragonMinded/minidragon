import argparse
import os
from typing import List

from compiler.core import FunctionPrototype, builtin_prototypes, parse_prototypes, parse_and_compile


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Simple Python to MiniDragon Assembly compiler."
    )
    parser.add_argument(
        "-d",
        "--destination",
        type=str,
        help="The destination file, defaults to out.S",
        default="out.S",
    )
    parser.add_argument(
        "file",
        metavar="FILE",
        nargs="+",
        type=str,
        help="File to compile",
    )
    args = parser.parse_args()

    refs: List[FunctionPrototype] = builtin_prototypes()
    compiled: List[str] = []
    for fname in args.file:
        with open(fname, "r") as fp:
            compiled += parse_prototypes(fname, fp.read())

    compiled: List[str] = []
    for fname in args.file:
        with open(fname, "r") as fp:
            compiled += parse_and_compile(fname, fp.read(), refs)

    with open(args.destination, "w") as fp:
        for line in compiled:
            fp.write(line + os.linesep)
