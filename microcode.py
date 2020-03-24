#! /usr/bin/python3
import argparse
import os
from typing import List
from core import instructions


def count_jumpers(line: str) -> int:
    count: int = 0
    for char in line:
        if char == "X":
            count += 1
    return count


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generates microcode programming lines."
    )
    parser.add_argument(
        "-f",
        "--file",
        type=str,
        help="Output to a file instead of stdout.",
    )
    args = parser.parse_args()
    microcodes: List[str] = []
    jumpers: int = 0
    holes: int = 0

    for instruction in instructions:
        try:
            signals = instruction.signals()
        except Exception:
            # Skip over macro instructions, we don't need to opcode those.
            continue

        microcodes.append(instruction.__class__.__name__)
        for num, step in enumerate(signals):
            # The hard part is mapping the individual control lines to the
            # microcode boards. We do this based on the instruction decoder
            # schematic. The instruction decoder logic works as an
            # open-collector memory system, so we represent a "1" with a ".",
            # or lack of jumper, and a "0" with a "X", or request for a
            # jumper in that spot.
            microcode: str = ""

            # Calculate immediate register control signals.
            immsrc: int = 3
            if step.imm_4_output:
                immsrc = 0
            elif step.imm_6_output:
                immsrc = 1
            elif step.z_output:
                immsrc = 2

            # Bit 0
            microcode += "." if step.ip_input else "X"
            microcode += "." if step.ir_input else "X"
            microcode += "." if step.a_input else "X"
            microcode += "." if step.b_input else "X"

            # Bit 4
            microcode += "." if step.c_input else "X"
            microcode += "." if step.d_input else "X"
            microcode += "." if step.p_input else "X"
            microcode += "." if step.sram_input else "X"

            # Bit 8
            microcode += "." if step.flags_input else "X"
            microcode += "." if step.alu_output else "X"
            microcode += "." if step.alu_low_output else "X"
            microcode += "." if step.a_output else "X"

            # Bit 12
            microcode += "." if step.a_high_output else "X"
            microcode += "." if step.d_output else "X"
            microcode += "." if step.d_high_output else "X"
            microcode += "." if step.sram_output else "X"

            # Bit 16
            microcode += "." if step.flags_output else "X"
            microcode += "." if step.pc_swap else "X"
            microcode += "." if (step.alu_src & 0x2) != 0 else "X"
            microcode += "." if (step.alu_src & 0x1) != 0 else "X"

            # Bit 20
            microcode += "." if (step.carry & 0x2) != 0 else "X"
            microcode += "." if (step.carry & 0x1) != 0 else "X"
            microcode += "." if (step.alu_op & 0x4) != 0 else "X"
            microcode += "." if (step.alu_op & 0x2) != 0 else "X"

            # Bit 24
            microcode += "." if (step.alu_op & 0x1) != 0 else "X"
            microcode += "." if (immsrc & 0x2) != 0 else "X"
            microcode += "." if (immsrc & 0x1) != 0 else "X"
            microcode += "." if (step.alu_src & 0x1) != 0 else "X"

            # Bit 28
            microcode += "."
            microcode += "."
            microcode += "."
            # This isn't the last instruction, so don't reset the
            # microcode counter.
            microcode += "X"

            # Keep track of how many jumpers we will need
            jumpers += count_jumpers(microcode)
            holes += (32 - count_jumpers(microcode))
            microcodes.append(microcode)

        # Append an "early terminate" signal to the microcode counter if we
        # haven't run out of room.
        if num < 15:
            # We can cheat, we don't care about the rest of the signals since
            # we're going to reset the microcode counter asynchronously,
            # looking up the next instruction in the process.
            microcodes.append("................................")
        microcodes.append("")

    microcodes.append(f"Total jumpers: {jumpers}")
    microcodes.append(f"Total holes: {holes}")

    if args.file:
        with open(args.file, "w") as fp:
            fp.write(os.linesep.join(microcodes))
    else:
        print(os.linesep.join(microcodes))