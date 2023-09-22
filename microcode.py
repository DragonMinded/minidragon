#! /usr/bin/python3
import argparse
import os
from typing import List
from core import InstructionLoadControlSignals, ControlSignals, instructions


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
    boards: int = 0
    miniboards: int = 0

    def append_microcode(step: ControlSignals) -> None:
        global jumpers
        global holes

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

        # Calculate the data bus high control signals.
        dbus: int = 3
        if step.a_high_output:
            dbus = 0
        elif step.d_high_output:
            dbus = 1
        elif step.alu_output:
            dbus = 2

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
        microcode += "." if (dbus & 0x2) != 0 else "X"
        microcode += "." if (dbus & 0x1) != 0 else "X"
        microcode += "." if step.alu_low_output else "X"

        # Bit 12
        microcode += "." if step.a_output else "X"
        microcode += "." if step.d_output else "X"
        microcode += "." if step.u_output else "X"
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
        microcode += "." if (step.address_src & 0x1) != 0 else "X"

        # Bit 28
        microcode += "." if step.v_output else "X"
        microcode += "." if step.u_input else "X"
        microcode += "." if step.v_input else "X"
        # This isn't the last instruction, so don't reset the
        # microcode counter.
        microcode += "."

        # Keep track of how many jumpers we will need
        jumpers += count_jumpers(microcode)
        holes += (32 - count_jumpers(microcode))
        microcodes.append(microcode)

    microcodes.append("Instruction Load")
    append_microcode(InstructionLoadControlSignals())
    microcodes.append("ROM boards: 0")
    microcodes.append("MiniROM boards: 1")
    miniboards += 1
    microcodes.append("")

    for instruction in instructions:
        try:
            signals = instruction.signals()
        except Exception:
            # Skip over macro instructions, we don't need to opcode those.
            continue

        microcodes.append(instruction.__class__.__name__)
        for num, step in enumerate(signals):
            append_microcode(step)

        # One-indexed instead of zero-indexed, and add one for the early
        # terminate.
        actual = num + 2
        if (actual % 4) == 1:
            # We can do a regular board followed by a mini-board.
            addboards = actual // 4
            addminiboards = 1
        else:
            # Round up, so two or more of the microcodes go onto the
            # last board.
            addboards = (actual + 3) // 4
            addminiboards = 0

        boards += addboards
        miniboards += addminiboards

        # Append an "early terminate" signal to the microcode counter if we
        # haven't run out of room.
        if num < 15:
            # We can cheat, we don't care about the rest of the signals since
            # we're going to reset the microcode counter asynchronously,
            # looking up the next instruction in the process.
            microcodes.append("...............................X")
            jumpers += 1
            holes += 31
        else:
            raise Exception(
                "Cannot generate microcode reset signal, this instruction "
                "will infinite loop!"
            )
        microcodes.append(f"ROM boards: {addboards}")
        microcodes.append(f"MiniROM boards: {addminiboards}")
        microcodes.append("")

    microcodes.append(f"Total jumpers: {jumpers}")
    microcodes.append(f"Total holes: {holes}")
    microcodes.append(f"Total ROM boards: {boards}")
    microcodes.append(f"Total MiniROM boards: {miniboards}")

    if args.file:
        with open(args.file, "w") as fp:
            fp.write(os.linesep.join(microcodes))
    else:
        print(os.linesep.join(microcodes))
