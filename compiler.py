import argparse
import os
import sys
from typing import List, Union

from core import CompilerError, FunctionPrototype, GlobalVariable, Sections, builtin_forward_refs, parse_forward_refs, compile_module


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Simple Python to MiniDragon Assembly compiler."
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        help="The output file, defaults to out.S",
        default="out.S",
    )
    parser.add_argument(
        "-d",
        "--data",
        type=str,
        help="The data file, defaults to data.S",
        default="data.S",
    )
    parser.add_argument(
        "-i",
        "--init",
        type=str,
        help="The init file, defaults to init.S",
        default="init.S",
    )
    parser.add_argument(
        "file",
        metavar="FILE",
        nargs="+",
        type=str,
        help="File to compile",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose error output",
    )
    args = parser.parse_args()

    try:
        refs: List[Union[FunctionPrototype, GlobalVariable]] = builtin_forward_refs()
        for fname in args.file:
            with open(fname, "r") as fp:
                refs += parse_forward_refs(fname, fp.read())

        compiled = Sections()
        for fname in args.file:
            with open(fname, "r") as fp:
                compiled += compile_module(fname, fp.read(), refs)

        with open(args.output, "w") as fp:
            for line in compiled.code:
                fp.write(line + os.linesep)

        if compiled.data:
            with open(args.data, "w") as fp:
                for line in compiled.data:
                    fp.write(line + os.linesep)

        if compiled.init:
            with open(args.init, "w") as fp:
                for line in compiled.init:
                    fp.write(line + os.linesep)

        sys.exit(0)

    except CompilerError as e:
        if args.verbose:
            raise
        else:
            print(str(e), file=sys.stderr)
            sys.exit(1)
