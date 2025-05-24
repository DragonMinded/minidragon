import argparse
import os
import sys
from typing import List, Union

from compiler.core import CompilerError, FunctionPrototype, GlobalVariable, builtin_forward_refs, parse_forward_refs, compile_module


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

    try:
        refs: List[Union[FunctionPrototype, GlobalVariable]] = builtin_forward_refs()
        compiled: List[str] = []
        for fname in args.file:
            with open(fname, "r") as fp:
                refs += parse_forward_refs(fname, fp.read())

        compiled: List[str] = []
        for fname in args.file:
            with open(fname, "r") as fp:
                compiled += compile_module(fname, fp.read(), refs)

        with open(args.destination, "w") as fp:
            for line in compiled:
                fp.write(line + os.linesep)

        sys.exit(0)

    except CompilerError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)
