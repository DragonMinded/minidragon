import argparse
import os
from typing import List
from ..core import InstructionLoadControlSignals, ControlSignals, instructions


def count_jumpers(line: str) -> int:
    count: int = 0
    for char in line:
        if char == "X":
            count += 1
    return count


def format_line(microcode: str) -> str:
    if len(microcode) != 32:
        raise Exception("Logic error, unexpected number of microcodes!")

    return f"{microcode[0:8]} {microcode[8:16]} {microcode[16:24]} {microcode[24:32]}"


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
        # open-collector memory system, but the bus termination circuit
        # does an invert for us, so we represent a "0" with a ".",
        # or lack of jumper, and a "1" with a "X", or request for a
        # jumper in that spot.
        microcode: str = ""

        # Calculate immediate register control signals.
        immsrc: int = 0
        if step.z_output:
            immsrc = 1
        elif step.imm_6_output:
            immsrc = 2
        elif step.imm_4_output:
            immsrc = 3

        # Calculate the data bus high control signals.
        dbus: int = 0
        if step.alu_output:
            dbus = 1
        elif step.d_high_output:
            dbus = 2
        elif step.a_high_output:
            dbus = 3

        # Bit 0
        microcode += "X" if step.ip_input else "."
        microcode += "X" if step.ir_input else "."
        microcode += "X" if step.a_input else "."
        microcode += "X" if step.b_input else "."

        # Bit 4
        microcode += "X" if step.c_input else "."
        microcode += "X" if step.d_input else "."
        microcode += "X" if step.p_input else "."
        microcode += "X" if step.sram_input else "."

        # Bit 8
        microcode += "X" if step.flags_input else "."
        microcode += "X" if (dbus & 0x2) != 0 else "."
        microcode += "X" if (dbus & 0x1) != 0 else "."
        microcode += "X" if step.alu_low_output else "."

        # Bit 12
        microcode += "X" if step.a_output else "."
        microcode += "X" if step.d_output else "."
        microcode += "X" if step.u_output else "."
        microcode += "X" if step.sram_output else "."

        # Bit 16
        microcode += "X" if step.flags_output else "."
        microcode += "X" if step.pc_swap else "."
        microcode += "X" if (step.alu_src & 0x2) != 0 else "."
        microcode += "X" if (step.alu_src & 0x1) != 0 else "."

        # Bit 20
        microcode += "X" if (step.carry & 0x2) != 0 else "."
        microcode += "X" if (step.carry & 0x1) != 0 else "."
        microcode += "X" if (step.alu_op & 0x4) != 0 else "."
        microcode += "X" if (step.alu_op & 0x2) != 0 else "."

        # Bit 24
        microcode += "X" if (step.alu_op & 0x1) != 0 else "."
        microcode += "X" if (immsrc & 0x2) != 0 else "."
        microcode += "X" if (immsrc & 0x1) != 0 else "."
        microcode += "X" if (step.address_src & 0x1) != 0 else "."

        # Bit 28
        microcode += "X" if step.v_output else "."
        microcode += "X" if step.u_input else "."
        microcode += "X" if step.v_input else "."
        # This isn't the last instruction, so don't reset the
        # microcode counter.
        microcode += "."

        # Keep track of how many jumpers we will need
        jumpers += count_jumpers(microcode)
        holes += (32 - count_jumpers(microcode))
        microcodes.append(format_line(microcode))

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
            if num % 4 == 3:
                microcodes.append("")

        # One-indexed instead of zero-indexed, and add one for the early
        # terminate. One-indexed because the first ROM board for every
        # instruction is the instruction load control signals which is
        # handled using special hardware when detecting the 0'th position
        # in the microcode counter circuit.
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
            microcodes.append(format_line("...............................X"))
            jumpers += 1
            holes += 31
        else:
            raise Exception(
                "Cannot generate microcode reset signal, this instruction "
                "will infinite loop!"
            )

        while actual % 4 in {2, 3}:
            microcodes.append(format_line("................................"))
            actual += 1

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
