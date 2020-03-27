#! /usr/bin/python3
import ast
import argparse
from typing import Dict, Optional


class Color:
    RED = '\033[91m'
    YELLOW = '\033[93m'
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'

    GRAY = '\033[100m'

    END = '\033[0m'


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="A stack visualizer for MiniDragon code.",
    )
    parser.add_argument(
        "file",
        metavar="FILE",
        help="The source file to visualize.",
    )
    parser.add_argument(
        "--adjust",
        "-a",
        type=int,
        default=0,
        metavar="ADJUSTMENT",
        help="An adjustment to the starting PC offset.",
    )
    parser.add_argument(
        "--shadow-adjust",
        "-s",
        type=int,
        default=0,
        metavar="ADJUSTMENT",
        help="An adjustment to the starting SPC offset.",
    )
    args = parser.parse_args()
    with open(args.file, "r") as fp:
        lines = fp.readlines()

    def _isswap(insn: str) -> bool:
        return insn.upper() == "SWAP"

    def _islabel(param: str) -> bool:
        if not param:
            return False
        try:
            ast.literal_eval(param)
            return False
        except (ValueError, SyntaxError):
            return True

    swapped_labels: Dict[str, bool] = {}
    swapped: bool = False
    stackpos: Dict[bool, Optional[int]] = {
        False: args.adjust,
        True: args.shadow_adjust,
    }

    def _insncolor(insn: str) -> str:
        if _isswap(insn):
            return Color.GRAY
        elif swapped:
            return Color.PURPLE
        else:
            return ""

    def _paramcolor(param: str) -> str:
        if _islabel(param):
            return Color.GREEN
        else:
            return Color.RED

    def _stackpos(insn: str) -> str:
        if _isswap(insn):
            return "      "

        pos = stackpos[swapped]
        newpos = _adjust_pos(pos, insn, param)
        if newpos != pos:
            strval = (
                f"{pos if pos is not None else '?'}" +
                f"->" +
                f"{newpos if newpos is not None else '?'}"
            )
        else:
            strval = str(pos) if pos is not None else "?"
        return f"{Color.YELLOW}{strval.ljust(6)}{Color.END}"

    def _adjust_pos(
        curpos: Optional[int], insn: str, param: str,
    ) -> Optional[int]:
        if curpos is None:
            return None
        insn = insn.upper()
        if insn in {"PUSHSPC", "PUSHIP"}:
            return curpos - 2
        elif insn in {"POPSPC", "POPIP"}:
            return curpos + 2
        elif insn in {"PUSH", "PUSHI", "DECPC"}:
            return curpos - 1
        elif insn in {
            "POP", "INCPC", "POPADD", "POPADC", "POPAND", "POPOR", "POPXOR"
        }:
            return curpos + 1
        elif insn == "ADDPCI":
            return curpos + int(param)
        elif insn == "SUBPCI":
            return curpos - int(param)
        elif insn == "ADDPC":
            # Can't track dynamic stuff.
            return None
        else:
            return curpos

    for line in lines:
        stripline = line.strip()
        if stripline.startswith(';'):
            # Full line comment
            print(f"      {Color.BLUE}{line}{Color.END}", end="")
        elif stripline.endswith(':'):
            # Label
            print(f"      {Color.GREEN}{line}{Color.END}", end="")

            # See if we need to set swap
            label = stripline.split(':')[0].strip()
            if label in swapped_labels:
                swapped = swapped_labels[label]
        else:
            # Need to split by comment
            line, *rest = line.split(';', 1)

            # Split the line to its parts (indentation, instruction, trailer)
            insn = line.strip()
            if insn:
                before, after = line.split(insn, 1)
            else:
                before = ""
                after = ""

            # If this is an empty line, just spit it out.
            if not rest and not insn and not before and not after:
                print(line, end="")
                continue

            insn, *params = insn.split(" ", 1)
            if params:
                param = params[0]
                space = " "
                if _islabel(param):
                    swapped_labels[param] = swapped
            else:
                param = ""
                space = ""

            # First, print the line
            print(
                f"{_stackpos(insn)}" +
                f"{before}" +
                f"{_insncolor(insn)}{insn}{Color.END}" +
                f"{space}" +
                f"{_paramcolor(param)}{param}{Color.END}" +
                f"{after}",
                end="",
            )

            # Now, figure out if we need to swap
            if _isswap(insn):
                swapped = not swapped
            else:
                stackpos[swapped] = _adjust_pos(stackpos[swapped], insn, param)

            # Now, print the comment if it exists
            if rest:
                print(f"{Color.BLUE}{rest[0]}{Color.END}", end="")
