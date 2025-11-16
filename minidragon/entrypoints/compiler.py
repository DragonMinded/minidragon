import argparse
import os
import sys
from typing import List, Union

from ..compiler import (
    CompilerError,
    CompilerSettings,
    FunctionPrototype,
    GlobalVariable,
    Sections,
    Compiler,
    builtin_forward_refs,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="A MiniPy Python to MiniDragon Assembly compiler."
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        help="The code file we will produce, defaults to out.S",
        default="out.S",
    )
    parser.add_argument(
        "-d",
        "--data",
        type=str,
        help="The data file we will produce, defaults to data.S",
        default="data.S",
    )
    parser.add_argument(
        "-i",
        "--init",
        type=str,
        help="The init file we will produce, defaults to init.S",
        default="init.S",
    )
    parser.add_argument(
        "-z",
        "--optimize",
        action="store_true",
        help="Optimize compiled code, defaults to unoptimized code",
        default=False,
    )
    parser.add_argument(
        "-l",
        "--lib",
        action="append",
        help="Look for libraries in this directory",
        default=[],
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
    settings = CompilerSettings(optimize=args.optimize)
    compiler = Compiler(settings)

    for lib in args.lib:
        compiler.add_library_directory(os.path.abspath(lib))

    try:
        refs: List[Union[FunctionPrototype, GlobalVariable]] = builtin_forward_refs()
        for fname in args.file:
            with open(fname, "r") as fp:
                fname = os.path.abspath(fname)
                compiler.set_working_directory(os.path.dirname(fname))

                refs += compiler.parse_forward_refs(fname, fp.read())

        compiled = Sections()
        for fname in args.file:
            with open(fname, "r") as fp:
                fname = os.path.abspath(fname)
                compiler.set_working_directory(os.path.dirname(fname))

                compiled += compiler.compile_module(fname, fp.read(), refs)

        with open(args.output, "w") as fp:
            for line in compiled.code:
                fp.write(line + os.linesep)

        if compiled.data:
            with open(args.data, "w") as fp:
                for line in compiled.data:
                    fp.write(line + os.linesep)
        else:
            with open(args.data, "w") as fp:
                fp.write("")

        if compiled.init:
            with open(args.init, "w") as fp:
                for line in compiled.init:
                    fp.write(line + os.linesep)
        else:
            with open(args.init, "w") as fp:
                fp.write("")

        sys.exit(0)

    except CompilerError as e:
        if args.verbose:
            raise
        else:
            print(str(e), file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
