#! /usr/bin/python3
import copy
import struct
from ast import literal_eval
from abc import ABC, abstractmethod
from typing import Callable, Dict, List, Optional, Set, Tuple


def sign_extend(val: int, msb: int) -> int:
    """
    Given a binary represented as an integer, sign extend it to the
    MSB. The MSB is given inclusively, so if you set the MSB to 0,
    that means the 0'th bit will be sign extended. So, if want to
    sign extend an 8-bit number, you would give a MSB of 7.

    NOTE: This assumes a 16-bit number.
    """

    high_bit = 0b1 << msb
    bit_mask = (0b1 << (msb + 1)) - 1
    rest_mask = (~bit_mask) & 0xFFFF

    val = val & bit_mask

    if (val & high_bit) != 0:
        val = val | rest_mask
    return val


def hexstr(num: int, digits: int) -> str:
    val = hex(num)[2:]
    while len(val) < digits:
        val = "0" + val
    return val


def binstr(num: int, digits: int) -> str:
    val = bin(num)[2:]
    while len(val) < digits:
        val = "0" + val
    return val


def bintoint(binary: int) -> int:
    return struct.unpack("b", struct.pack("B", binary))[0]


class BaseInstruction(ABC):
    # Whether this class handles opcodes represented by instruction.
    @abstractmethod
    def handles(self, instruction: int) -> bool:
        ...

    # The mnemonic for this instruction.
    @abstractmethod
    def mnemonic(self, instruction: int) -> str:
        ...

    # The control signals for a CPU implementing this instruction.
    @abstractmethod
    def signals(self, instruction: int) -> List["ControlSignals"]:
        ...

    # Whether this class handles mnemonics represented by mnemonic.
    @abstractmethod
    def assembles(self, mnemonic: str) -> bool:
        ...

    # The instruction for this mnemonic and parameter.
    @abstractmethod
    def vals(
        self,
        mnemonic: str,
        parameter: str,
        origin: int,
        labels: Dict[str, int],
    ) -> List[int]:
        ...


def instruction(obj: Callable) -> Callable:
    instructions.append(obj())
    return obj


instructions: List[BaseInstruction] = []


def disassemble(instruction: int) -> str:
    global instructions

    for inst in instructions:
        if inst.handles(instruction):
            return inst.mnemonic(instruction)
    return f".byte {hexstr(instruction, 2)}"


def decode(instruction: int) -> List["ControlSignals"]:
    global instructions

    for inst in instructions:
        if inst.handles(instruction):
            signals = inst.signals(instruction)
            if len(signals) > 15:
                raise Exception("Instruction contains too many microcodes")
            return signals
    else:
        raise Exception("Instruction not implemented")


def _getint(val: str) -> int:
    if val.strip()[:2] in {"0x", "0X"}:
        try:
            return int(val.strip(), 16)
        except ValueError:
            pass

    if val.strip()[:2] in {"0b", "0B"}:
        try:
            return int(val.strip(), 2)
        except ValueError:
            pass

    try:
        return int(val.strip())
    except ValueError:
        pass

    raise Exception(f"Invalid integer {val}")


def getint(val: str, bits: int) -> int:
    intval = _getint(val)

    # Bounds check the integer.
    if intval > ((2 ** bits) - 1):
        raise Exception(f"Out of range integer {val}")

    if intval < 0 and abs(intval) > (2 ** (bits - 1)):
        raise Exception(f"Out of range integer {val}")

    if intval < 0:
        # Get unsigned representation.
        intval = struct.unpack("H", struct.pack("h", intval))[0]

    # Return it masked.
    return intval & ((2 ** bits) - 1)


def assemble(
    mnemonics: List[str],
    labels: Dict[str, int] = {},
) -> List[Tuple[int, int]]:
    global instructions

    org = 0
    labels = copy.deepcopy(labels)
    data: Dict[int, int] = {}
    seen: Set[int] = set()

    # First pass, render out instructions that aren't labels, and
    # calculate label locations.
    for mnemonic in mnemonics:
        # Verify that it isn't full already.
        if org in seen:
            raise Exception(
                f"Cannot place code/data into section " +
                f"{hexstr(org, 4)}, already occupied!"
            )

        # Preprocessor directives.
        if mnemonic.startswith(".org "):
            # Origin directive
            org = getint(mnemonic[5:], 16)
            if org in seen:
                raise Exception(
                    f"Cannot place code into section {hexstr(org, 4)}, " +
                    f"already occupied!"
                )
        elif mnemonic.startswith(".byte "):
            # Data directive
            val = getint(mnemonic[6:], 8)
            data[org] = val
            org += 1
        elif mnemonic.startswith(".char "):
            # Data directive
            val = getint(str(ord(literal_eval(mnemonic[6:]))), 8)
            data[org] = val
            org += 1

        # Labels.
        elif mnemonic.endswith(":"):
            # A label of some sort.
            labels[mnemonic[:-1].lower()] = org

        # Regular opcodes.
        else:
            # We must assemble this.
            if " " in mnemonic:
                mnemonic, param = mnemonic.split(" ", 1)
                if " " in param:
                    raise Exception(
                        f"Cannot have more than one parameter for {mnemonic}!"
                    )
            else:
                param = ""

            mnemonic = mnemonic.upper()
            param = param.lower()

            for inst in instructions:
                if inst.assembles(mnemonic):
                    # Assemble without labels, telling the instruction to
                    # substitute whatever.
                    for val in inst.vals(mnemonic, param, org, labels):
                        data[org] = val
                        org += 1
                    break
            else:
                raise Exception(f"Unrecognized instruction {mnemonic}!")

    # Now, do the whole thing again, ignoring seen state and non-instructions
    # and let the instructions re-generate themselves with correct labels.
    org = 0
    for mnemonic in mnemonics:
        # Preprocessor directives.
        if mnemonic.startswith(".org "):
            org = getint(mnemonic[5:], 16)
        elif mnemonic.startswith(".byte "):
            org += 1
        elif mnemonic.startswith(".char "):
            org += 1
        # Labels.
        elif mnemonic.endswith(":"):
            pass
        # Regular opcodes.
        else:
            # We must assemble this.
            if " " in mnemonic:
                mnemonic, param = mnemonic.split(" ", 1)
                if " " in param:
                    raise Exception(
                        f"Cannot have more than one parameter for {mnemonic}!"
                    )
            else:
                param = ""

            mnemonic = mnemonic.upper()
            param = param.lower()

            for inst in instructions:
                if inst.assembles(mnemonic):
                    # Assemble without labels, telling the instruction to
                    # substitute whatever.
                    for val in inst.vals(mnemonic, param, org, labels):
                        data[org] = val
                        org += 1
                    break
            else:
                raise Exception(f"Unrecognized instruction {mnemonic}!")

    # Finally, reformat as a list of tuples of memory address, memory value.
    return list(data.items())


@instruction
class JRI(BaseInstruction):
    # Jump relative to immediate sign extended (also NOP if IR == 0b00000000).

    def handles(self, instruction: int) -> bool:
        return instruction & 0b11000000 == 0b00000000

    def mnemonic(self, instruction: int) -> str:
        jumppoint = bintoint(sign_extend(instruction & 0x3F, 5) & 0xFF)
        if jumppoint == 0:
            return "NOP"
        elif jumppoint == -1:
            return "HALT"
        else:
            return f"JRI {jumppoint}"

    def signals(self, instruction: int) -> List["ControlSignals"]:
        return [
            ControlSignals(
                imm_output=True,
                b_input=True,
            ),
            ControlSignals(
                alu_src=ControlSignals.ALU_SRC_IP,
                alu_op=ALU.OPERATION_ADD,
                carry=ControlSignals.CARRY_SET,
                alu_output=True,
                ip_input=True,
            ),
        ]

    def assembles(self, mnemonic: str) -> bool:
        return mnemonic in {"NOP", "HALT", "JRI"}

    def vals(
        self,
        mnemonic: str,
        parameter: str,
        origin: int,
        labels: Dict[str, int],
    ) -> List[int]:
        if mnemonic == "NOP":
            if parameter != "":
                raise Exception(f"Invalid parameter {parameter} for NOP!")
            return [0b00000000]
        if mnemonic == "HALT":
            if parameter != "":
                raise Exception(f"Invalid parameter {parameter} for HALT!")
            return [0b00111111]

        # A jump, relative to instruction. We need to handle labels.
        # First, try to get this as an integer.
        try:
            location = getint(parameter, 6)
        except Exception:
            # Now, try as a label.
            if parameter in labels:
                parameter = str(labels[parameter] - origin - 1)
                location = getint(parameter, 6)
            else:
                # We don't care about this value right now, fill it in as
                # whatever.
                location = 0b00111111

        return [0b00000000 | location]


@instruction
class LOADI(BaseInstruction):
    # Load immediate sign extended to A.

    def handles(self, instruction: int) -> bool:
        return instruction & 0b11000000 == 0b01000000

    def mnemonic(self, instruction: int) -> str:
        integer = bintoint(sign_extend(instruction & 0x3F, 5) & 0xFF)
        if integer == 0:
            return f"ZERO"
        else:
            return f"LOADI {integer}"

    def signals(self, instruction: int) -> List["ControlSignals"]:
        return [
            ControlSignals(
                imm_output=True,
                a_input=True,
            ),
            ControlSignals(
                z_output=True,
                b_input=True,
            ),
            ControlSignals(
                alu_src=ControlSignals.ALU_SRC_IP,
                alu_op=ALU.OPERATION_ADD,
                carry=ControlSignals.CARRY_SET,
                alu_output=True,
                ip_input=True,
            ),
        ]

    def assembles(self, mnemonic: str) -> bool:
        return mnemonic in {"LOADI", "ZERO"}

    def vals(
        self,
        mnemonic: str,
        parameter: str,
        origin: int,
        labels: Dict[str, int],
    ) -> List[int]:
        if mnemonic == "ZERO":
            if parameter != "":
                raise Exception(f"Invalid parameter {parameter} for ZERO!")
            loadval = 0
        else:
            loadval = getint(parameter, 6)
        return [0b01000000 | loadval]


@instruction
class ADDI(BaseInstruction):
    # Add immediate sign extended to A.

    def handles(self, instruction: int) -> bool:
        return instruction & 0b11000000 == 0b10000000

    def mnemonic(self, instruction: int) -> str:
        integer = bintoint(sign_extend(instruction & 0x3F, 5) & 0xFF)
        if integer == 1:
            return "INC"
        elif integer == -1:
            return "DEC"
        else:
            return f"ADDI {integer}"

    def signals(self, instruction: int) -> List["ControlSignals"]:
        return [
            ControlSignals(
                imm_output=True,
                b_input=True,
            ),
            ControlSignals(
                alu_src=ControlSignals.ALU_SRC_A,
                alu_op=ALU.OPERATION_ADD,
                carry=ControlSignals.CARRY_CLEAR,
                alu_output=True,
                a_input=True,
                flags_input=True,
            ),
            ControlSignals(
                z_output=True,
                b_input=True,
            ),
            ControlSignals(
                alu_src=ControlSignals.ALU_SRC_IP,
                alu_op=ALU.OPERATION_ADD,
                carry=ControlSignals.CARRY_SET,
                alu_output=True,
                ip_input=True,
            ),
        ]

    def assembles(self, mnemonic: str) -> bool:
        return mnemonic in {"ADDI", "INC", "DEC"}

    def vals(
        self,
        mnemonic: str,
        parameter: str,
        origin: int,
        labels: Dict[str, int],
    ) -> List[int]:
        if mnemonic == "INC":
            if parameter != "":
                raise Exception("No parameter required for INC mnemonic")
            addval = 1
        elif mnemonic == "DEC":
            if parameter != "":
                raise Exception("No parameter required for DEC mnemonic")
            addval = 0b00111111
        else:
            addval = getint(parameter, 6)
        return [0b10000000 | addval]


@instruction
class PUSHIP(BaseInstruction):
    # Decrement PC by 2, take the current IP, add an immediate zero-extended
    # value to it, and store that at PC.

    def handles(self, instruction: int) -> bool:
        return instruction & 0b11111000 == 0b11000000

    def mnemonic(self, instruction: int) -> str:
        integer = bintoint(sign_extend(instruction & 0x3F, 5) & 0xFF)
        return f"PUSHIP {integer}"

    def signals(self, instruction: int) -> List["ControlSignals"]:
        return [
            # First, preload the B register with negative 1 so we can decrement
            # the PC register.
            ControlSignals(
                b_input=True,
            ),
            # Decrement PC register to get to the previous byte.
            ControlSignals(
                alu_src=ControlSignals.ALU_SRC_PC,
                alu_op=ALU.OPERATION_ADD,
                carry=ControlSignals.CARRY_CLEAR,
                alu_output=True,
                p_input=True,
                c_input=True,
            ),
            # Store the immediate value zero-extended into B.
            ControlSignals(
                imm_output=True,
                b_input=True,
            ),
            # Add the immediate value to the current IP, store
            # the low byte in SRAM.
            ControlSignals(
                alu_src=ControlSignals.ALU_SRC_IP,
                alu_op=ALU.OPERATION_ADD,
                carry=ControlSignals.CARRY_CLEAR,
                alu_output=True,
                address_src=ControlSignals.ADDRESS_SRC_PC,
                sram_input=True,
            ),
            # Now, preload the B register with negative 1 so we can decrement
            # the PC register a second time.
            ControlSignals(
                b_input=True,
            ),
            # Decrement PC register to get to the previous byte.
            ControlSignals(
                alu_src=ControlSignals.ALU_SRC_PC,
                alu_op=ALU.OPERATION_ADD,
                carry=ControlSignals.CARRY_CLEAR,
                alu_output=True,
                p_input=True,
                c_input=True,
            ),
            # Store the immediate value zero-extended into B.
            ControlSignals(
                imm_output=True,
                b_input=True,
            ),
            # Add the immediate value to the current IP, store
            # the high byte in SRAM.
            ControlSignals(
                alu_src=ControlSignals.ALU_SRC_IP,
                alu_op=ALU.OPERATION_ADD,
                carry=ControlSignals.CARRY_CLEAR,
                alu_low_output=True,
                address_src=ControlSignals.ADDRESS_SRC_PC,
                sram_input=True,
            ),
            # Finally, go to the next instruction.
            ControlSignals(
                z_output=True,
                b_input=True,
            ),
            ControlSignals(
                alu_src=ControlSignals.ALU_SRC_IP,
                alu_op=ALU.OPERATION_ADD,
                carry=ControlSignals.CARRY_SET,
                alu_output=True,
                ip_input=True,
            ),
        ]

    def assembles(self, mnemonic: str) -> bool:
        return mnemonic == "PUSHIP"

    def vals(
        self,
        mnemonic: str,
        parameter: str,
        origin: int,
        labels: Dict[str, int],
    ) -> List[int]:
        try:
            # Try to grab the offset as a raw integer.
            location = getint(parameter, 5)
        except Exception:
            # Now, try as a label.
            if parameter in labels:
                parameter = str(labels[parameter] - origin)
                location = getint(parameter, 5)
            else:
                # We don't care about this value right now, fill it in as
                # whatever. We'll get to it on the second pass.
                location = 0

        if location < 0:
            raise Exception("Can only have a positive offset for PUSHIP")
        if location > 7:
            raise Exception("Can only store an offset up to 7 for PUSHIP")

        return [0b11000000 + location]


@instruction
class ADDPCI(BaseInstruction):
    # Add immediate to the P+C virtual register.

    def handles(self, instruction: int) -> bool:
        return instruction & 0b11111000 == 0b11001000

    def mnemonic(self, instruction: int) -> str:
        integer = (instruction & 0b111) + 1
        if integer == 1:
            return "INCPC"
        else:
            return f"ADDPCI {integer}"

    def signals(self, instruction: int) -> List["ControlSignals"]:
        signals = [
            ControlSignals(
                z_output=True,
                b_input=True,
            ),
        ]

        for _ in range((instruction & 0b111) + 1):
            signals.append(
                ControlSignals(
                    alu_src=ControlSignals.ALU_SRC_PC,
                    alu_op=ALU.OPERATION_ADD,
                    carry=ControlSignals.CARRY_SET,
                    alu_output=True,
                    p_input=True,
                    c_input=True,
                )
            )

        signals.append(
            ControlSignals(
                alu_src=ControlSignals.ALU_SRC_IP,
                alu_op=ALU.OPERATION_ADD,
                carry=ControlSignals.CARRY_SET,
                alu_output=True,
                ip_input=True,
            )
        )
        return signals

    def assembles(self, mnemonic: str) -> bool:
        return mnemonic in {"INCPC", "ADDPCI"}

    def vals(
        self,
        mnemonic: str,
        parameter: str,
        origin: int,
        labels: Dict[str, int],
    ) -> List[int]:
        if mnemonic == "INCPC":
            if parameter != "":
                raise Exception("INCPC takes no parameters!")
            return [0b11001000]

        location = getint(parameter, 4) - 1
        if location > 7:
            raise Exception("Parameter out of range for INCPC!")
        return [0b11001000 + location]


@instruction
class SUBPCI(BaseInstruction):
    # Add immediate to the P+C virtual register.

    def handles(self, instruction: int) -> bool:
        return instruction & 0b11111000 == 0b11010000

    def mnemonic(self, instruction: int) -> str:
        integer = (instruction & 0b111) + 1
        if integer == 1:
            return "DECPC"
        else:
            return f"SUBPCI {integer}"

    def signals(self, instruction: int) -> List["ControlSignals"]:
        signals = [
            ControlSignals(
                b_input=True,
            ),
        ]

        for _ in range((instruction & 0b111) + 1):
            signals.append(
                ControlSignals(
                    alu_src=ControlSignals.ALU_SRC_PC,
                    alu_op=ALU.OPERATION_ADD,
                    carry=ControlSignals.CARRY_CLEAR,
                    alu_output=True,
                    p_input=True,
                    c_input=True,
                )
            )

        signals.extend([
            ControlSignals(
                z_output=True,
                b_input=True,
            ),
            ControlSignals(
                alu_src=ControlSignals.ALU_SRC_IP,
                alu_op=ALU.OPERATION_ADD,
                carry=ControlSignals.CARRY_SET,
                alu_output=True,
                ip_input=True,
            )
        ])
        return signals

    def assembles(self, mnemonic: str) -> bool:
        return mnemonic in {"DECPC", "SUBPCI"}

    def vals(
        self,
        mnemonic: str,
        parameter: str,
        origin: int,
        labels: Dict[str, int],
    ) -> List[int]:
        if mnemonic == "DECPC":
            if parameter != "":
                raise Exception("DECPC takes no parameters!")
            return [0b11010000]

        location = getint(parameter, 4) - 1
        if location > 7:
            raise Exception("Parameter out of range for DECPC!")
        return [0b11010000 + location]


class BaseALUInstruction(BaseInstruction, ABC):
    opcode: int

    def handles(self, instruction: int) -> bool:
        if instruction & 0b11111000 != 0b11100000:
            return False
        return instruction & 0b111 == self.opcode

    def mnemonic(self, instruction: int) -> str:
        # ALU operations don't take any parameters.
        return self.__class__.__name__

    def assembles(self, mnemonic: str) -> bool:
        return self.__class__.__name__ == mnemonic

    def vals(
        self,
        mnemonic: str,
        parameter: str,
        origin: int,
        labels: Dict[str, int],
    ) -> List[int]:
        if parameter != "":
            raise Exception(
                f"{self.__class__.__name__} does not take any parameters!"
            )
        return [0b11100000 | self.opcode]


@instruction
class INV(BaseALUInstruction):
    # Invert contents of A.

    opcode = 0b000

    def signals(self, instruction: int) -> List["ControlSignals"]:
        return [
            ControlSignals(
                alu_src=ControlSignals.ALU_SRC_A,
                alu_op=ALU.OPERATION_INV,
                alu_output=True,
                a_input=True,
                flags_input=True,
            ),
            ControlSignals(
                z_output=True,
                b_input=True,
            ),
            ControlSignals(
                alu_src=ControlSignals.ALU_SRC_IP,
                alu_op=ALU.OPERATION_ADD,
                carry=ControlSignals.CARRY_SET,
                alu_output=True,
                ip_input=True,
            ),
        ]


@instruction
class ADD(BaseALUInstruction):
    # Add contents of memory at P+C to A register.

    opcode = 0b001

    def signals(self, instruction: int) -> List["ControlSignals"]:
        return [
            ControlSignals(
                address_src=ControlSignals.ADDRESS_SRC_PC,
                sram_output=True,
                b_input=True,
            ),
            ControlSignals(
                alu_src=ControlSignals.ALU_SRC_A,
                alu_op=ALU.OPERATION_ADD,
                carry=ControlSignals.CARRY_CLEAR,
                alu_output=True,
                a_input=True,
                flags_input=True,
            ),
            ControlSignals(
                z_output=True,
                b_input=True,
            ),
            ControlSignals(
                alu_src=ControlSignals.ALU_SRC_IP,
                alu_op=ALU.OPERATION_ADD,
                carry=ControlSignals.CARRY_SET,
                alu_output=True,
                ip_input=True,
            ),
        ]


@instruction
class ADC(BaseALUInstruction):
    # Add contents of memory at P+C to A register with carry in.

    opcode = 0b010

    def signals(self, instruction: int) -> List["ControlSignals"]:
        return [
            ControlSignals(
                address_src=ControlSignals.ADDRESS_SRC_PC,
                sram_output=True,
                b_input=True,
            ),
            ControlSignals(
                alu_src=ControlSignals.ALU_SRC_A,
                alu_op=ALU.OPERATION_ADD,
                carry=ControlSignals.CARRY_FROM_FLAGS,
                alu_output=True,
                a_input=True,
                flags_input=True,
            ),
            ControlSignals(
                z_output=True,
                b_input=True,
            ),
            ControlSignals(
                alu_src=ControlSignals.ALU_SRC_IP,
                alu_op=ALU.OPERATION_ADD,
                carry=ControlSignals.CARRY_SET,
                alu_output=True,
                ip_input=True,
            ),
        ]


@instruction
class AND(BaseALUInstruction):
    # Add contents of memory at P+C with A register.

    opcode = 0b011

    def signals(self, instruction: int) -> List["ControlSignals"]:
        return [
            ControlSignals(
                address_src=ControlSignals.ADDRESS_SRC_PC,
                sram_output=True,
                b_input=True,
            ),
            ControlSignals(
                alu_src=ControlSignals.ALU_SRC_A,
                alu_op=ALU.OPERATION_AND,
                carry=ControlSignals.CARRY_CLEAR,
                alu_output=True,
                a_input=True,
                flags_input=True,
            ),
            ControlSignals(
                z_output=True,
                b_input=True,
            ),
            ControlSignals(
                alu_src=ControlSignals.ALU_SRC_IP,
                alu_op=ALU.OPERATION_ADD,
                carry=ControlSignals.CARRY_SET,
                alu_output=True,
                ip_input=True,
            ),
        ]


@instruction
class OR(BaseALUInstruction):
    # Or contents of memory at P+C with A register.

    opcode = 0b100

    def signals(self, instruction: int) -> List["ControlSignals"]:
        return [
            ControlSignals(
                address_src=ControlSignals.ADDRESS_SRC_PC,
                sram_output=True,
                b_input=True,
            ),
            ControlSignals(
                alu_src=ControlSignals.ALU_SRC_A,
                alu_op=ALU.OPERATION_OR,
                carry=ControlSignals.CARRY_CLEAR,
                alu_output=True,
                a_input=True,
                flags_input=True,
            ),
            ControlSignals(
                z_output=True,
                b_input=True,
            ),
            ControlSignals(
                alu_src=ControlSignals.ALU_SRC_IP,
                alu_op=ALU.OPERATION_ADD,
                carry=ControlSignals.CARRY_SET,
                alu_output=True,
                ip_input=True,
            ),
        ]


@instruction
class XOR(BaseALUInstruction):
    # Exclusive or contents of memory at P+C with A register.

    opcode = 0b101

    def signals(self, instruction: int) -> List["ControlSignals"]:
        return [
            ControlSignals(
                address_src=ControlSignals.ADDRESS_SRC_PC,
                sram_output=True,
                b_input=True,
            ),
            ControlSignals(
                alu_src=ControlSignals.ALU_SRC_A,
                alu_op=ALU.OPERATION_XOR,
                carry=ControlSignals.CARRY_CLEAR,
                alu_output=True,
                a_input=True,
                flags_input=True,
            ),
            ControlSignals(
                z_output=True,
                b_input=True,
            ),
            ControlSignals(
                alu_src=ControlSignals.ALU_SRC_IP,
                alu_op=ALU.OPERATION_ADD,
                carry=ControlSignals.CARRY_SET,
                alu_output=True,
                ip_input=True,
            ),
        ]


@instruction
class SHL(BaseALUInstruction):
    # Shift contents of A left.

    opcode = 0b110

    def signals(self, instruction: int) -> List["ControlSignals"]:
        return [
            ControlSignals(
                alu_src=ControlSignals.ALU_SRC_A,
                alu_op=ALU.OPERATION_SHL,
                alu_output=True,
                a_input=True,
                flags_input=True,
            ),
            ControlSignals(
                z_output=True,
                b_input=True,
            ),
            ControlSignals(
                alu_src=ControlSignals.ALU_SRC_IP,
                alu_op=ALU.OPERATION_ADD,
                carry=ControlSignals.CARRY_SET,
                alu_output=True,
                ip_input=True,
            ),
        ]


@instruction
class SHR(BaseALUInstruction):
    # Shift contents of A right.

    opcode = 0b111

    def signals(self, instruction: int) -> List["ControlSignals"]:
        return [
            ControlSignals(
                alu_src=ControlSignals.ALU_SRC_A,
                alu_op=ALU.OPERATION_SHR,
                alu_output=True,
                a_input=True,
                flags_input=True,
            ),
            ControlSignals(
                z_output=True,
                b_input=True,
            ),
            ControlSignals(
                alu_src=ControlSignals.ALU_SRC_IP,
                alu_op=ALU.OPERATION_ADD,
                carry=ControlSignals.CARRY_SET,
                alu_output=True,
                ip_input=True,
            ),
        ]


class BaseMemoryInstruction(BaseInstruction, ABC):
    opcode: int

    def handles(self, instruction: int) -> bool:
        if instruction & 0b11111000 != 0b11101000:
            return False
        return instruction & 0b111 == self.opcode

    def mnemonic(self, instruction: int) -> str:
        # Memory operations don't take any parameters.
        return self.__class__.__name__

    def assembles(self, mnemonic: str) -> bool:
        return self.__class__.__name__ == mnemonic

    def vals(
        self,
        mnemonic: str,
        parameter: str,
        origin: int,
        labels: Dict[str, int],
    ) -> List[int]:
        if parameter != "":
            raise Exception(
                f"{self.__class__.__name__} does not take any parameters!"
            )
        return [0b11101000 | self.opcode]


@instruction
class ATOP(BaseMemoryInstruction):
    # Move contents of A register to P register.

    opcode = 0b000

    def signals(self, instruction: int) -> List["ControlSignals"]:
        return [
            # We can cheat here to save on microcodes, since both p and
            # b input on different halves of the bus, and both a_high and
            # z output on different halves of the bus.
            ControlSignals(
                p_input=True,
                b_input=True,
                a_high_output=True,
                z_output=True,
            ),
            ControlSignals(
                alu_src=ControlSignals.ALU_SRC_IP,
                alu_op=ALU.OPERATION_ADD,
                carry=ControlSignals.CARRY_SET,
                alu_output=True,
                ip_input=True,
            ),
        ]


@instruction
class ATOC(BaseMemoryInstruction):
    # Move contents of A register to C register.

    opcode = 0b001

    def signals(self, instruction: int) -> List["ControlSignals"]:
        return [
            ControlSignals(
                c_input=True,
                a_output=True,
            ),
            ControlSignals(
                z_output=True,
                b_input=True,
            ),
            ControlSignals(
                alu_src=ControlSignals.ALU_SRC_IP,
                alu_op=ALU.OPERATION_ADD,
                carry=ControlSignals.CARRY_SET,
                alu_output=True,
                ip_input=True,
            ),
        ]


@instruction
class PTOA(BaseMemoryInstruction):
    # Move contents of P register to A register.

    opcode = 0b010

    def signals(self, instruction: int) -> List["ControlSignals"]:
        return [
            # To save on control signals, we are routing through the ALU.
            # We do this by adding zero to the PC and taking that output.
            ControlSignals(
                z_output=True,
                b_input=True,
            ),
            ControlSignals(
                alu_src=ControlSignals.ALU_SRC_PC,
                alu_op=ALU.OPERATION_ADD,
                carry=ControlSignals.CARRY_CLEAR,
                alu_low_output=True,
                a_input=True,
            ),
            ControlSignals(
                alu_src=ControlSignals.ALU_SRC_IP,
                alu_op=ALU.OPERATION_ADD,
                carry=ControlSignals.CARRY_SET,
                alu_output=True,
                ip_input=True,
            ),
        ]


@instruction
class CTOA(BaseMemoryInstruction):
    # Move contents of C register to A register.

    opcode = 0b011

    def signals(self, instruction: int) -> List["ControlSignals"]:
        return [
            # To save on control signals, we are routing through the ALU.
            # We do this by adding zero to the PC and taking that output.
            ControlSignals(
                z_output=True,
                b_input=True,
            ),
            ControlSignals(
                alu_src=ControlSignals.ALU_SRC_PC,
                alu_op=ALU.OPERATION_ADD,
                carry=ControlSignals.CARRY_CLEAR,
                alu_output=True,
                a_input=True,
            ),
            ControlSignals(
                alu_src=ControlSignals.ALU_SRC_IP,
                alu_op=ALU.OPERATION_ADD,
                carry=ControlSignals.CARRY_SET,
                alu_output=True,
                ip_input=True,
            ),
        ]


@instruction
class LOAD(BaseMemoryInstruction):
    # Load the contents of memory at P+C to A register.

    opcode = 0b100

    def signals(self, instruction: int) -> List["ControlSignals"]:
        return [
            ControlSignals(
                address_src=ControlSignals.ADDRESS_SRC_PC,
                sram_output=True,
                a_input=True,
            ),
            ControlSignals(
                z_output=True,
                b_input=True,
            ),
            ControlSignals(
                alu_src=ControlSignals.ALU_SRC_IP,
                alu_op=ALU.OPERATION_ADD,
                carry=ControlSignals.CARRY_SET,
                alu_output=True,
                ip_input=True,
            ),
        ]


@instruction
class STORE(BaseMemoryInstruction):
    # Store the contents of the A register to memory at P+C.

    opcode = 0b101

    def signals(self, instruction: int) -> List["ControlSignals"]:
        return [
            ControlSignals(
                address_src=ControlSignals.ADDRESS_SRC_PC,
                sram_input=True,
                a_output=True,
            ),
            ControlSignals(
                z_output=True,
                b_input=True,
            ),
            ControlSignals(
                alu_src=ControlSignals.ALU_SRC_IP,
                alu_op=ALU.OPERATION_ADD,
                carry=ControlSignals.CARRY_SET,
                alu_output=True,
                ip_input=True,
            ),
        ]


@instruction
class SKIPIF(BaseInstruction):
    # Skip the next instruction if immediate condition true.

    def handles(self, instruction: int) -> bool:
        if instruction & 0b11111000 != 0b11110000:
            return False
        return instruction & 0b111 in {0b010, 0b011, 0b100, 0b101}

    def mnemonic(self, instruction: int) -> str:
        condition = instruction & 0b100
        negate = instruction & 0b001
        if condition == 0b100:
            flag = "ZF"
        elif condition == 0b000:
            flag = "CF"
        else:
            raise Exception("Unimplemented skipif condition")
        if negate != 0:
            flag = "!" + flag

        return f"SKIPIF {flag}"

    def signals(self, instruction: int) -> List["ControlSignals"]:
        # Skip next instruction if:
        # - 0b010 = CF set
        # - 0b011 = CF clear
        # - 0b100 = ZF set
        # - 0b101 = ZF clear
        return [
            ControlSignals(
                flags_output=True,
                b_input=True,
            ),
            ControlSignals(
                alu_src=ControlSignals.ALU_SRC_IP,
                alu_op=ALU.OPERATION_ADD,
                carry=ControlSignals.CARRY_SET,
                alu_output=True,
                ip_input=True,
            ),
        ]

    def assembles(self, mnemonic: str) -> bool:
        return mnemonic == "SKIPIF"

    def vals(
        self,
        mnemonic: str,
        parameter: str,
        origin: int,
        labels: Dict[str, int],
    ) -> List[int]:
        base = 0b11110000

        if parameter.startswith("!"):
            flag = parameter[1:]
            base |= 0b1
        else:
            flag = parameter

        if flag == "cf":
            base |= 0b010
        elif flag == "zf":
            base |= 0b100
        else:
            raise Exception(
                f"Invalid parameter {parameter} for SKIPIF!",
            )
        return [base]


class BaseStackInstruction(BaseInstruction, ABC):
    opcode: int

    def handles(self, instruction: int) -> bool:
        if instruction & 0b11111000 != 0b11111000:
            return False
        return instruction & 0b111 == self.opcode

    def mnemonic(self, instruction: int) -> str:
        # ALU operations don't take any parameters.
        return self.__class__.__name__

    def assembles(self, mnemonic: str) -> bool:
        return self.__class__.__name__ == mnemonic

    def vals(
        self,
        mnemonic: str,
        parameter: str,
        origin: int,
        labels: Dict[str, int],
    ) -> List[int]:
        if parameter != "":
            raise Exception(
                f"{self.__class__.__name__} does not take any parameters!"
            )
        return [0b11111000 | self.opcode]


@instruction
class LNGJUMP(BaseStackInstruction):
    # Jump to 16-bit immediate value stored directly after instruction.
    opcode = 0b000

    def signals(self, instruction: int) -> List["ControlSignals"]:
        return [
            # First, increment the IP so we can get the address of
            # the upper byte.
            ControlSignals(
                z_output=True,
                b_input=True,
            ),
            ControlSignals(
                alu_src=ControlSignals.ALU_SRC_IP,
                alu_op=ALU.OPERATION_ADD,
                carry=ControlSignals.CARRY_SET,
                alu_output=True,
                ip_input=True,
            ),
            # Store it in D register
            ControlSignals(
                address_src=ControlSignals.ADDRESS_SRC_IP,
                sram_output=True,
                d_input=True,
            ),
            # Now, increment the IP again so we can get the address
            # of the lower byte.
            ControlSignals(
                alu_src=ControlSignals.ALU_SRC_IP,
                alu_op=ALU.OPERATION_ADD,
                carry=ControlSignals.CARRY_SET,
                alu_output=True,
                ip_input=True,
            ),
            # Now, output the SRAM as well as D register, inputting
            # to the IP to jump to that address.
            ControlSignals(
                address_src=ControlSignals.ADDRESS_SRC_IP,
                d_high_output=True,
                sram_output=True,
                ip_input=True,
            ),

        ]

    def vals(
        self,
        mnemonic: str,
        parameter: str,
        origin: int,
        labels: Dict[str, int],
    ) -> List[int]:
        # We override the base because we technically take an immediate for
        # this opcode, its just stored in memory after the opcode itself.

        if not parameter:
            # We could assume that the next two bytes are the value, but that
            # seems to be in poor form.
            raise Exception("Must give an immediate value for LNGJUMP")

        # Assume the user wanted to jump to an immediate or a label.
        try:
            location = getint(parameter, 16)
        except Exception:
            # Now, try as a label.
            if parameter in labels:
                parameter = str(labels[parameter])
                location = getint(parameter, 16)
            else:
                # We don't care about this value right now, fill it in as
                # whatever.
                location = 0

        return [0b11111000, (location >> 8) & 0xFF, location & 0xFF]


@instruction
class SWAP(BaseStackInstruction):
    # Swap PC and SPC registers.
    opcode = 0b001

    def signals(self, instruction: int) -> List["ControlSignals"]:
        return [
            ControlSignals(
                z_output=True,
                b_input=True,
                pc_swap=True,
            ),
            ControlSignals(
                alu_src=ControlSignals.ALU_SRC_IP,
                alu_op=ALU.OPERATION_ADD,
                carry=ControlSignals.CARRY_SET,
                alu_output=True,
                ip_input=True,
            ),
        ]


@instruction
class ADDPC(BaseStackInstruction):
    # Add contents of A register sign extended to 16 bits to the P+C
    # virtual register.
    opcode = 0b010

    def signals(self, instruction: int) -> List["ControlSignals"]:
        return [
            ControlSignals(
                a_output=True,
                b_input=True,
            ),
            ControlSignals(
                alu_src=ControlSignals.ALU_SRC_PC,
                alu_op=ALU.OPERATION_ADD,
                carry=ControlSignals.CARRY_CLEAR,
                alu_output=True,
                p_input=True,
                c_input=True,
            ),
            ControlSignals(
                z_output=True,
                b_input=True,
            ),
            ControlSignals(
                alu_src=ControlSignals.ALU_SRC_IP,
                alu_op=ALU.OPERATION_ADD,
                carry=ControlSignals.CARRY_SET,
                alu_output=True,
                ip_input=True,
            )
        ]


@instruction
class POPIP(BaseStackInstruction):
    # Take a 16-bit value stored at PC and PC + 1 (big-endian), and store it
    # to IP.
    opcode = 0b011

    def signals(self, instruction: int) -> List["ControlSignals"]:
        return [
            # First, preload the B register with zero so we can increment.
            # the PC register.
            ControlSignals(
                z_output=True,
                b_input=True,
            ),
            # Store PC in D register.
            ControlSignals(
                address_src=ControlSignals.ADDRESS_SRC_PC,
                sram_output=True,
                d_input=True,
            ),
            # Increment PC register to get to the next byte.
            ControlSignals(
                alu_src=ControlSignals.ALU_SRC_PC,
                alu_op=ALU.OPERATION_ADD,
                carry=ControlSignals.CARRY_SET,
                alu_output=True,
                p_input=True,
                c_input=True,
            ),
            # Store D + sram into IP register.
            ControlSignals(
                address_src=ControlSignals.ADDRESS_SRC_PC,
                sram_output=True,
                d_high_output=True,
                ip_input=True,
            ),
            # Increment PC register to get to the next byte in the stack.
            ControlSignals(
                alu_src=ControlSignals.ALU_SRC_PC,
                alu_op=ALU.OPERATION_ADD,
                carry=ControlSignals.CARRY_SET,
                alu_output=True,
                p_input=True,
                c_input=True,
            ),
        ]

    def assembles(self, mnemonic: str) -> bool:
        # We override this to provide a convenience mnemonic so that subroutine
        # code looks nicer.
        return mnemonic in {"POPIP", "RET"}


@instruction
class PUSHSPC(BaseStackInstruction):
    # Take the current register SPC and store it to memory pointed at
    # PC - 1 and PC - 2.

    opcode = 0b100

    def signals(self, instruction: int) -> List["ControlSignals"]:
        return [
            # First, preload the B register with negative one so we
            # can decrement the PC register.
            ControlSignals(
                b_input=True,
            ),
            # Decrement PC register to get to the previous byte.
            ControlSignals(
                alu_src=ControlSignals.ALU_SRC_PC,
                alu_op=ALU.OPERATION_ADD,
                carry=ControlSignals.CARRY_CLEAR,
                alu_output=True,
                p_input=True,
                c_input=True,
            ),
            # Swap to SPC so we can grab the SC register, preload
            # b register with zero to do this trick.
            ControlSignals(
                pc_swap=True,
                z_output=True,
                b_input=True,
            ),
            # Store value of SC in D register, routed through ALU.
            ControlSignals(
                alu_src=ControlSignals.ALU_SRC_PC,
                alu_op=ALU.OPERATION_ADD,
                carry=ControlSignals.CARRY_CLEAR,
                alu_output=True,
                d_input=True,
            ),
            # Swap back to PC so we can store the next byte, preload
            # b register with negative one again so we can decrement
            # the PC register.
            ControlSignals(
                pc_swap=True,
                b_input=True,
            ),
            # Store the contents of the D register in SRAM.
            ControlSignals(
                address_src=ControlSignals.ADDRESS_SRC_PC,
                d_output=True,
                sram_input=True,
            ),
            # Decrement PC register to get to the previous byte.
            ControlSignals(
                alu_src=ControlSignals.ALU_SRC_PC,
                alu_op=ALU.OPERATION_ADD,
                carry=ControlSignals.CARRY_CLEAR,
                alu_output=True,
                p_input=True,
                c_input=True,
            ),
            # Swap to SPC so we can grab the SC register, preload
            # b register with zero to do this trick.
            ControlSignals(
                pc_swap=True,
                z_output=True,
                b_input=True,
            ),
            # Store value of SP in D register, routed through ALU.
            ControlSignals(
                alu_src=ControlSignals.ALU_SRC_PC,
                alu_op=ALU.OPERATION_ADD,
                carry=ControlSignals.CARRY_CLEAR,
                alu_low_output=True,
                d_input=True,
            ),
            # Swap back to PC so we can store the next byte.
            ControlSignals(
                pc_swap=True,
            ),
            # Store the contents of the D register in SRAM.
            ControlSignals(
                address_src=ControlSignals.ADDRESS_SRC_PC,
                d_output=True,
                sram_input=True,
            ),
            # Finally, increment the IP register to go to the next insn.
            ControlSignals(
                alu_src=ControlSignals.ALU_SRC_IP,
                alu_op=ALU.OPERATION_ADD,
                carry=ControlSignals.CARRY_SET,
                alu_output=True,
                ip_input=True,
            ),
        ]


@instruction
class POPSPC(BaseStackInstruction):
    # Take a 16-bit value stored at PC and PC + 1 (big-endian), and store it
    # to SPC.
    opcode = 0b101

    def signals(self, instruction: int) -> List["ControlSignals"]:
        return [
            # First, preload the B register with zero so we can increment.
            # the PC register.
            ControlSignals(
                z_output=True,
                b_input=True,
            ),
            # Store contents of PC in D register, swap to SPC.
            ControlSignals(
                address_src=ControlSignals.ADDRESS_SRC_PC,
                sram_output=True,
                d_input=True,
                pc_swap=True,
            ),
            # Store the contents of the D register in the SP register.
            ControlSignals(
                d_high_output=True,
                p_input=True,
            ),
            # Swap back to PC so we can grab the next byte.
            ControlSignals(
                pc_swap=True,
            ),
            # Increment PC register to get to the next byte.
            ControlSignals(
                alu_src=ControlSignals.ALU_SRC_PC,
                alu_op=ALU.OPERATION_ADD,
                carry=ControlSignals.CARRY_SET,
                alu_output=True,
                p_input=True,
                c_input=True,
            ),
            # Store contents of PC in D register, swap to SPC.
            ControlSignals(
                address_src=ControlSignals.ADDRESS_SRC_PC,
                sram_output=True,
                d_input=True,
                pc_swap=True,
            ),
            # Store the contents of the D register in the SC register.
            ControlSignals(
                d_output=True,
                c_input=True,
            ),
            # Swap back so we can increment to the next stack position.
            ControlSignals(
                pc_swap=True,
            ),
            # Increment PC register to get to the next byte in the stack.
            ControlSignals(
                alu_src=ControlSignals.ALU_SRC_PC,
                alu_op=ALU.OPERATION_ADD,
                carry=ControlSignals.CARRY_SET,
                alu_output=True,
                p_input=True,
                c_input=True,
            ),
            # Finally, increment the IP register to go to the next insn.
            ControlSignals(
                alu_src=ControlSignals.ALU_SRC_IP,
                alu_op=ALU.OPERATION_ADD,
                carry=ControlSignals.CARRY_SET,
                alu_output=True,
                ip_input=True,
            ),
        ]


class BaseMacro(BaseInstruction):
    def handles(self, instruction: int) -> bool:
        # We never handle disassembly, macros generate assembly blocks
        return False

    def mnemonic(self, instruction: int) -> str:
        raise Exception(
            "We don't handle any opcodes so we should never be asked for "
            "a mnemonic!"
        )

    def signals(self, instruction: int) -> List["ControlSignals"]:
        raise Exception(
            "We don't handle any opcodes so we should never be asked for "
            "signals!"
        )

    def compile(self, org: int, instructions: List[str]) -> List[int]:
        loc_and_assembly = assemble([f".org {org}", *instructions])
        opcodes: List[int] = []
        for loc, val in loc_and_assembly:
            if loc != org:
                raise Exception(
                    "Assembly error, non-contiguous macro compilation!"
                )
            org += 1
            opcodes.append(val)
        return opcodes


@instruction
class SETA(BaseMacro):
    def assembles(self, mnemonic: str) -> bool:
        return mnemonic == "SETA"

    def vals(
        self,
        mnemonic: str,
        parameter: str,
        origin: int,
        labels: Dict[str, int],
    ) -> List[int]:
        # Load immediate 8-bit value into A.
        aval = getint(parameter, 8)

        # Now, assemble the load and return that value
        return self.compile(origin, self._immtoa(aval))

    def _immtoa(self, val: int) -> List[str]:
        instructions: List[str] = []
        if val < 0b00100000:
            # This is safe to load as an immediate directly, without
            # risking sign extension.
            instructions.append(f"LOADI {val}")
        elif val < 0b01000000:
            # We will need to shift in the value and perhaps add to it
            instructions.append(f"LOADI {val >> 1}")
            instructions.append("SHL")
            if val & 0b00000001 != 0:
                instructions.append(f"ADDI 1")
        else:
            # We will need to shift in the value and perhaps add to it.
            # Its safe to do this in all cases since we know that either
            # the top bit is clear so shifting right by two will mean
            # that it doesn't get extended, or the top bit is set, in
            # which case it will, but we'll override that by shifting
            # left twice anyway.
            instructions.append(f"LOADI {val >> 2}")
            instructions.append("SHL")
            instructions.append("SHL")
            if val & 0b00000011 != 0:
                instructions.append(f"ADDI {val & 0b00000011}")
        return instructions


@instruction
class SETPC(BaseMacro):
    def assembles(self, mnemonic: str) -> bool:
        return mnemonic == "SETPC"

    def vals(
        self,
        mnemonic: str,
        parameter: str,
        origin: int,
        labels: Dict[str, int],
    ) -> List[int]:
        # Load immediate value into PC.
        # First, try to get this as an integer.
        try:
            location = getint(parameter, 16)
        except Exception:
            # Now, try as a label.
            if parameter in labels:
                location = getint(str(labels[parameter]), 16)
            else:
                # Unfortunately this macro takes a variable number of
                # instructions, due to us needing to potentially shift
                # values into upper bits of the A register, so we must
                # have already seen a label to use it.
                raise Exception(
                    "Cannot SETPC to a label not yet seen!"
                )

        # Now, split the location into two halves.
        pval = (location >> 8) & 0xFF
        cval = location & 0xFF

        # Now, get the instructions themselves
        instructions = [
            f"SETA {pval}",
            "ATOP",
            f"SETA {cval}",
            "ATOC",
        ]

        # Now, assemble them and return that value
        return self.compile(origin, instructions)


@instruction
class JRIZ(BaseMacro):
    # Jump reliative to immediate if zero set.

    def assembles(self, mnemonic: str) -> bool:
        return mnemonic == "JRIZ"

    def vals(
        self,
        mnemonic: str,
        parameter: str,
        origin: int,
        labels: Dict[str, int],
    ) -> List[int]:
        try:
            # First, try as an integer.
            location = getint(parameter, 6)
            # We subtract one because the virtual position of this instruction
            # is one memory address earlier than where the actual jump
            # instruction will go.
            if location & 0b00100000:
                location -= 1
        except Exception:
            # Now, try as a label.
            if parameter in labels:
                absolute_location = labels[parameter]
                # Adjust backwards 2 so we can skip past our skip
                # instruction.
                relative_location = absolute_location - origin - 2
                location = getint(str(relative_location), 6)
            else:
                # Assume nothing for now, will be filled in later
                location = 0

        # If we want to jump on zero flag set, we need to skip the
        # jump if zero flag cleared.
        return self.compile(origin, ["SKIPIF !ZF", f"JRI {location}"])


@instruction
class JRINZ(BaseMacro):
    # Jump reliative to immediate if zero not set.

    def assembles(self, mnemonic: str) -> bool:
        return mnemonic == "JRINZ"

    def vals(
        self,
        mnemonic: str,
        parameter: str,
        origin: int,
        labels: Dict[str, int],
    ) -> List[int]:
        try:
            # First, try as an integer.
            location = getint(parameter, 6)
            # We subtract one because the virtual position of this instruction
            # is one memory address earlier than where the actual jump
            # instruction will go.
            if location & 0b00100000:
                location -= 1
        except Exception:
            # Now, try as a label.
            if parameter in labels:
                absolute_location = labels[parameter]
                # Adjust backwards 2 so we can skip past our skip
                # instruction.
                relative_location = absolute_location - origin - 2
                location = getint(str(relative_location), 6)
            else:
                # Assume nothing for now, will be filled in later
                location = 0

        # If we want to jump on zero flag cleared, we need to skip the
        # jump if zero flag set.
        return self.compile(origin, ["SKIPIF ZF", f"JRI {location}"])


@instruction
class JRIC(BaseMacro):
    # Jump reliative to immediate if carry set.

    def assembles(self, mnemonic: str) -> bool:
        return mnemonic == "JRIC"

    def vals(
        self,
        mnemonic: str,
        parameter: str,
        origin: int,
        labels: Dict[str, int],
    ) -> List[int]:
        try:
            # First, try as an integer.
            location = getint(parameter, 6)
            # We subtract one because the virtual position of this instruction
            # is one memory address earlier than where the actual jump
            # instruction will go.
            if location & 0b00100000:
                location -= 1
        except Exception:
            # Now, try as a label.
            if parameter in labels:
                absolute_location = labels[parameter]
                # Adjust backwards 2 so we can skip past our skip
                # instruction.
                relative_location = absolute_location - origin - 2
                location = getint(str(relative_location), 6)
            else:
                # Assume nothing for now, will be filled in later
                location = 0

        # If we want to jump on carry flag set, we need to skip the
        # jump if carry flag cleared.
        return self.compile(origin, ["SKIPIF !CF", f"JRI {location}"])


@instruction
class JRINC(BaseMacro):
    # Jump reliative to immediate if carry not set.

    def assembles(self, mnemonic: str) -> bool:
        return mnemonic == "JRINC"

    def vals(
        self,
        mnemonic: str,
        parameter: str,
        origin: int,
        labels: Dict[str, int],
    ) -> List[int]:
        try:
            # First, try as an integer.
            location = getint(parameter, 6)
            # We subtract one because the virtual position of this instruction
            # is one memory address earlier than where the actual jump
            # instruction will go.
            if location & 0b00100000:
                location -= 1
        except Exception:
            # Now, try as a label.
            if parameter in labels:
                absolute_location = labels[parameter]
                # Adjust backwards 2 so we can skip past our skip
                # instruction.
                relative_location = absolute_location - origin - 2
                location = getint(str(relative_location), 6)
            else:
                # Assume nothing for now, will be filled in later
                location = 0

        # If we want to jump on carry flag cleared, we need to skip the
        # jump if carry flag set.
        return self.compile(origin, ["SKIPIF CF", f"JRI {location}"])


@instruction
class LNGJUMPZ(BaseMacro):
    # Jump to immediate if zero flag set.

    def assembles(self, mnemonic: str) -> bool:
        return mnemonic == "LNGJUMPZ"

    def vals(
        self,
        mnemonic: str,
        parameter: str,
        origin: int,
        labels: Dict[str, int],
    ) -> List[int]:
        try:
            # First, try as an integer.
            location = getint(parameter, 16)
        except Exception:
            # Now, try as a label.
            if parameter in labels:
                parameter = str(labels[parameter])
                location = getint(parameter, 16)
            else:
                # Assume nothing for now, will be filled in later
                location = 0

        return self.compile(
            origin, [
                "SKIPIF ZF",
                "JRI skip_longjump",
                f"LNGJUMP {location}",
                "skip_longjump:",
            ]
        )


@instruction
class LNGJUMPNZ(BaseMacro):
    # Jump to immediate if zero flag not set.

    def assembles(self, mnemonic: str) -> bool:
        return mnemonic == "LNGJUMPNZ"

    def vals(
        self,
        mnemonic: str,
        parameter: str,
        origin: int,
        labels: Dict[str, int],
    ) -> List[int]:
        try:
            # First, try as an integer.
            location = getint(parameter, 16)
        except Exception:
            # Now, try as a label.
            if parameter in labels:
                parameter = str(labels[parameter])
                location = getint(parameter, 16)
            else:
                # Assume nothing for now, will be filled in later
                location = 0

        return self.compile(
            origin, [
                "SKIPIF !ZF",
                "JRI skip_longjump",
                f"LNGJUMP {location}",
                "skip_longjump:",
            ]
        )


@instruction
class LNGJUMPC(BaseMacro):
    # Jump to immediate if carry flag set.

    def assembles(self, mnemonic: str) -> bool:
        return mnemonic == "LNGJUMPC"

    def vals(
        self,
        mnemonic: str,
        parameter: str,
        origin: int,
        labels: Dict[str, int],
    ) -> List[int]:
        try:
            # First, try as an integer.
            location = getint(parameter, 16)
        except Exception:
            # Now, try as a label.
            if parameter in labels:
                parameter = str(labels[parameter])
                location = getint(parameter, 16)
            else:
                # Assume nothing for now, will be filled in later
                location = 0

        return self.compile(
            origin, [
                "SKIPIF CF",
                "JRI skip_longjump",
                f"LNGJUMP {location}",
                "skip_longjump:",
            ]
        )


@instruction
class LNGJUMPNC(BaseMacro):
    # Jump to immediate if carry flag not set.

    def assembles(self, mnemonic: str) -> bool:
        return mnemonic == "LNGJUMPNC"

    def vals(
        self,
        mnemonic: str,
        parameter: str,
        origin: int,
        labels: Dict[str, int],
    ) -> List[int]:
        try:
            # First, try as an integer.
            location = getint(parameter, 16)
        except Exception:
            # Now, try as a label.
            if parameter in labels:
                parameter = str(labels[parameter])
                location = getint(parameter, 16)
            else:
                # Assume nothing for now, will be filled in later
                location = 0

        return self.compile(
            origin, [
                "SKIPIF !CF",
                "JRI skip_longjump",
                f"LNGJUMP {location}",
                "skip_longjump:",
            ]
        )


@instruction
class NEG(BaseMacro):
    # Twos compliment negate the A register.

    def assembles(self, mnemonic: str) -> bool:
        return mnemonic == "NEG"

    def vals(
        self,
        mnemonic: str,
        parameter: str,
        origin: int,
        labels: Dict[str, int],
    ) -> List[int]:
        if parameter != "":
            raise Exception(f"Invalid parameter {parameter} for NEG!")
        # Super simple, but convenient to use.
        return self.compile(origin, ["INV", "ADDI 1"])


@instruction
class CALL(BaseMacro):
    # Call subroutine.

    def assembles(self, mnemonic: str) -> bool:
        return mnemonic == "CALL"

    def vals(
        self,
        mnemonic: str,
        parameter: str,
        origin: int,
        labels: Dict[str, int],
    ) -> List[int]:
        # Load immediate value into PC.
        # First, try to get this as an integer.
        try:
            location = getint(parameter, 16)
        except Exception:
            # Now, try as a label.
            if parameter in labels:
                location = getint(str(labels[parameter]), 16)
            else:
                # We will fill this in later.
                location = 0

        # Create a springboard.
        instructions = [
            "PUSHIP retloc",
            f"LNGJUMP {location}",
            "retloc:"
        ]

        # Now, assemble the springboard and return that value
        return self.compile(origin, instructions)


@instruction
class CALLRI(BaseMacro):
    # Call relative subroutine.

    def assembles(self, mnemonic: str) -> bool:
        return mnemonic == "CALLRI"

    def vals(
        self,
        mnemonic: str,
        parameter: str,
        origin: int,
        labels: Dict[str, int],
    ) -> List[int]:
        try:
            # First, try as an integer.
            location = getint(parameter, 6)
            # We subtract one because the virtual position of this instruction
            # is one memory address earlier than where the actual jump
            # instruction will go.
            if location & 0b00100000:
                location -= 1
        except Exception:
            # Now, try as a label.
            if parameter in labels:
                absolute_location = labels[parameter]
                # Adjust backwards 2 so we can skip past our skip
                # instruction.
                relative_location = absolute_location - origin - 2
                location = getint(str(relative_location), 6)
            else:
                # Assume nothing for now, will be filled in later
                location = 0

        # Create a springboard.
        instructions = [
            "PUSHIP retloc",
            f"JRI {location}",
            "retloc:"
        ]

        # Now, assemble the springboard and return that value
        return self.compile(origin, instructions)


@instruction
class PUSH(BaseMacro):
    # Decrement PC, store A to PC.

    def assembles(self, mnemonic: str) -> bool:
        return mnemonic == "PUSH"

    def vals(
        self,
        mnemonic: str,
        parameter: str,
        origin: int,
        labels: Dict[str, int],
    ) -> List[int]:
        # Super simple, but convenient to use.
        if parameter != "":
            raise Exception(f"Invalid parameter {parameter} for PUSH!")
        return self.compile(origin, ["DECPC", "STORE"])


@instruction
class STOREI(BaseMacro):
    # Store immediate to PC, clobber A.

    def assembles(self, mnemonic: str) -> bool:
        return mnemonic == "STOREI"

    def vals(
        self,
        mnemonic: str,
        parameter: str,
        origin: int,
        labels: Dict[str, int],
    ) -> List[int]:
        # Super simple, but convenient to use.
        return self.compile(origin, [f"SETA {parameter}", "STORE"])


@instruction
class PUSHI(BaseMacro):
    # Decrement PC, store immediate to PC, clobber A.

    def assembles(self, mnemonic: str) -> bool:
        return mnemonic == "PUSHI"

    def vals(
        self,
        mnemonic: str,
        parameter: str,
        origin: int,
        labels: Dict[str, int],
    ) -> List[int]:
        # Super simple, but convenient to use.
        return self.compile(origin, ["DECPC", f"SETA {parameter}", "STORE"])


@instruction
class POP(BaseMacro):
    # Load PC to A, increment PC.

    def assembles(self, mnemonic: str) -> bool:
        return mnemonic == "POP"

    def vals(
        self,
        mnemonic: str,
        parameter: str,
        origin: int,
        labels: Dict[str, int],
    ) -> List[int]:
        # Super simple, but convenient to use.
        if parameter != "":
            raise Exception(f"Invalid parameter {parameter} for POP!")
        return self.compile(origin, ["LOAD", "INCPC"])


@instruction
class POPADD(BaseMacro):
    # Add PC to A, increment PC.

    def assembles(self, mnemonic: str) -> bool:
        return mnemonic == "POPADD"

    def vals(
        self,
        mnemonic: str,
        parameter: str,
        origin: int,
        labels: Dict[str, int],
    ) -> List[int]:
        # Super simple, but convenient to use.
        if parameter != "":
            raise Exception(f"Invalid parameter {parameter} for POPADD!")
        return self.compile(origin, ["ADD", "INCPC"])


@instruction
class POPADC(BaseMacro):
    # Add PC to A with carry from flags, increment PC.

    def assembles(self, mnemonic: str) -> bool:
        return mnemonic == "POPADC"

    def vals(
        self,
        mnemonic: str,
        parameter: str,
        origin: int,
        labels: Dict[str, int],
    ) -> List[int]:
        # Super simple, but convenient to use.
        if parameter != "":
            raise Exception(f"Invalid parameter {parameter} for POPADC!")
        return self.compile(origin, ["ADC", "INCPC"])


@instruction
class POPAND(BaseMacro):
    # And PC to A, increment PC.

    def assembles(self, mnemonic: str) -> bool:
        return mnemonic == "POPAND"

    def vals(
        self,
        mnemonic: str,
        parameter: str,
        origin: int,
        labels: Dict[str, int],
    ) -> List[int]:
        # Super simple, but convenient to use.
        if parameter != "":
            raise Exception(f"Invalid parameter {parameter} for POPAND!")
        return self.compile(origin, ["AND", "INCPC"])


@instruction
class POPOR(BaseMacro):
    # Or PC to A, increment PC.

    def assembles(self, mnemonic: str) -> bool:
        return mnemonic == "POPOR"

    def vals(
        self,
        mnemonic: str,
        parameter: str,
        origin: int,
        labels: Dict[str, int],
    ) -> List[int]:
        # Super simple, but convenient to use.
        if parameter != "":
            raise Exception(f"Invalid parameter {parameter} for POPOR!")
        return self.compile(origin, ["OR", "INCPC"])


@instruction
class POPXOR(BaseMacro):
    # Xor PC to A, increment PC.

    def assembles(self, mnemonic: str) -> bool:
        return mnemonic == "POPXOR"

    def vals(
        self,
        mnemonic: str,
        parameter: str,
        origin: int,
        labels: Dict[str, int],
    ) -> List[int]:
        # Super simple, but convenient to use.
        if parameter != "":
            raise Exception(f"Invalid parameter {parameter} for POPXOR!")
        return self.compile(origin, ["XOR", "INCPC"])


class ControlSignals:

    ALU_SRC_A = 0
    ALU_SRC_IP = 2
    ALU_SRC_PC = 3

    CARRY_CLEAR = 0
    CARRY_SET = 1
    CARRY_FROM_FLAGS = 2

    ADDRESS_SRC_IP = 0
    ADDRESS_SRC_PC = 1

    def __init__(
        self,
        *,

        # ALU signals

        alu_src: Optional[int] = None,
        carry: Optional[int] = None,
        alu_op: Optional[int] = None,

        # Data bus assertion signals

        # 16 bits, occupies the whole bus
        alu_output: Optional[bool] = None,
        # 8 bits, output on low 8 bits of the bus, from high 8 bits of ALU
        alu_low_output: Optional[bool] = None,
        # 6 bits sign-extended to 8, output on low 8 bits of the bus
        imm_output: Optional[bool] = None,
        # 8 bits, output on low 8 bits of the bus
        a_output: Optional[bool] = None,
        # 8 bits, output on top 8 bits of the bus
        a_high_output: Optional[bool] = None,
        # 8 bits, output on low 8 bits of the bus
        d_output: Optional[bool] = None,
        # 8 bits, output on top 8 bits of the bus
        d_high_output: Optional[bool] = None,
        # 8 bits, output on low 8 bits of the bus
        z_output: Optional[bool] = None,
        # 8 bits, output on low 8 bits of the bus
        sram_output: Optional[bool] = None,
        # 1 bit, zero extended, output on low 8 bits of the bus
        flags_output: Optional[bool] = None,

        # Write enable signals

        ip_input: Optional[bool] = None,
        ir_input: Optional[bool] = None,
        a_input: Optional[bool] = None,
        b_input: Optional[bool] = None,
        c_input: Optional[bool] = None,
        d_input: Optional[bool] = None,
        p_input: Optional[bool] = None,
        sram_input: Optional[bool] = None,
        flags_input: Optional[bool] = None,

        # Address bus assertion signals

        address_src: Optional[int] = None,

        # Flags control signals

        pc_swap: Optional[bool] = None,
    ) -> None:
        self.alu_src = alu_src or self.ALU_SRC_A
        self.carry = carry or self.CARRY_CLEAR
        self.alu_op = alu_op or ALU.OPERATION_ADD
        self.address_src = address_src or self.ADDRESS_SRC_IP
        self.ip_input = ip_input or False
        self.alu_output = alu_output or False
        self.alu_low_output = alu_low_output or False
        self.imm_output = imm_output or False
        self.z_output = z_output or False
        self.a_input = a_input or False
        self.a_output = a_output or False
        self.a_high_output = a_high_output or False
        self.b_input = b_input or False
        self.sram_input = sram_input or False
        self.sram_output = sram_output or False
        self.ir_input = ir_input or False
        self.flags_input = flags_input or False
        self.flags_output = flags_output or False
        self.pc_swap = pc_swap or False
        self.p_input = p_input or False
        self.c_input = c_input or False
        self.d_input = d_input or False
        self.d_output = d_output or False
        self.d_high_output = d_high_output or False


class ALU:

    # Add 16-bit value from "A" source to 8-bit value from "B" source,
    # returning a 16-bit result. Zero set if result is zero, carry set
    # if result would not fit in 8 bits.
    OPERATION_ADD = 0
    # Shift an 8-bit value from "A" source. Carry set if bit 7 was 1
    # and shifted out. Zero set if result is zero.
    OPERATION_SHL = 1
    # Shift an 8-bit value from "A" source. Carry set if bit 0 was 1
    # and shifted out. Zero set if result is zero.
    OPERATION_SHR = 2
    # Invert an 8-bit value in "A" source. Carry never set. Zero set if
    # result is zero.
    OPERATION_INV = 3
    # And an 8-bit value in "A" against an 8-bit value in "B". Carry never
    # set. Zero set if result is zero.
    OPERATION_AND = 4
    # Or an 8-bit value in "A" against an 8-bit value in "B". Carry never
    # set. Zero set if result is zero.
    OPERATION_OR = 5
    # Exclusive or an 8-bit value in "A" against an 8-bit value in "B".
    # Carry never set. Zero set if result is zero.
    OPERATION_XOR = 6

    def __init__(self, op: int, a: int, b: int, carry: bool) -> None:
        self.op = op
        self.a = a
        self.b = b
        self.carryin = carry

    @property
    def result(self) -> int:
        if self.op == self.OPERATION_ADD:
            return (self.a + self.b + (1 if self.carryin else 0)) & 0xFFFF
        if self.op == self.OPERATION_SHL:
            return (self.a << 1) & 0xFF
        if self.op == self.OPERATION_SHR:
            return (self.a >> 1) & 0xFF
        if self.op == self.OPERATION_INV:
            return (~self.a) & 0xFF
        if self.op == self.OPERATION_AND:
            return (self.a & self.b) & 0xFF
        if self.op == self.OPERATION_OR:
            return (self.a | self.b) & 0xFF
        if self.op == self.OPERATION_XOR:
            return (self.a ^ self.b) & 0xFF
        raise Exception("Not implemented!")

    @property
    def carryout(self) -> bool:
        # While the ALU itself is 16-bit, flags are relative to 8-bit
        # operations.
        if self.op == self.OPERATION_ADD:
            return (
                (self.a & 0xFF) + (self.b & 0xFF) + (1 if self.carryin else 0)
            ) & 0x100 != 0
        if self.op == self.OPERATION_SHL:
            return (self.a << 1) & 0x100 != 0
        if self.op == self.OPERATION_SHR:
            return (self.a & 0b1) != 0
        if self.op in [
            self.OPERATION_INV,
            self.OPERATION_AND,
            self.OPERATION_OR,
            self.OPERATION_XOR
        ]:
            return False
        raise Exception("Not implemented!")

    @property
    def zero(self) -> bool:
        # While the ALU itself is 16-bit, flags are relative to 8-bit
        # operations.
        if self.op == self.OPERATION_ADD:
            return (
                self.a + self.b + (1 if self.carryin else 0)
            ) & 0xFF == 0
        if self.op == self.OPERATION_SHL:
            return (self.a << 1) & 0xFF == 0
        if self.op == self.OPERATION_SHR:
            return (self.a >> 1) & 0xFF == 0
        if self.op == self.OPERATION_INV:
            return False
        if self.op == self.OPERATION_AND:
            return ((self.a & self.b) & 0xFF) == 0
        if self.op == self.OPERATION_OR:
            return ((self.a | self.b) & 0xFF) == 0
        if self.op == self.OPERATION_XOR:
            return ((self.a ^ self.b) & 0xFF) == 0
        raise Exception("Not implemented!")


class CPUCore:

    FLAGS_CF = 0x01
    FLAGS_ZF = 0x02
    FLAGS_PC = 0x04

    def __init__(self, ram: List[int]) -> None:
        # General purpose registers. A is read/write, while
        # P+C are write and update only.
        self.a = 0
        self.p = [0, 0]
        self.c = [0, 0]

        # Processor statistics.
        self.cycles = 0
        self.ticks = 0

        # Temporary registers, write only.
        self.b = 0

        # Flags bits, flags register, write only, read through skip
        # instruction.
        self.flags = 0

        # Internal registers, cannot be read from or written to by
        # program code.
        self.ip = 0
        self.ir = 0
        self.d = 0

        # CPU RAM, fully read/write.
        self.ram = ram
        while len(self.ram) < 0x8000:
            self.ram.append(0)

        # ALU
        self.alu = ALU(ALU.OPERATION_ADD, 0, 0, False)

        # Busses
        self.data = 0b1111111111111111
        self.address = 0b1111111111111111

        # Control signals
        self.last_instruction = ControlSignals()

    @property
    def pc(self) -> List[int]:
        return [(self.p[0] << 8) + self.c[0], (self.p[1] << 8) + self.c[1]]

    def print(self) -> None:
        # Look up the current bus values if we're about to store on this
        # instruction.
        ip = self.data if self.last_instruction.ip_input else self.ip

        flags = (
            self.current_flags()
            if self.last_instruction.flags_input
            else self.flags
        )
        cf = flags & self.FLAGS_CF != 0
        zf = flags & self.FLAGS_ZF != 0
        pc = self.flags & self.FLAGS_PC != 0

        if self.last_instruction.pc_swap:
            pc = not pc
        p = (
            self.data >> 8
            if self.last_instruction.p_input
            else self.p[1 if pc else 0]
        )
        p = (p << 8) & 0xFF00
        c = (
            self.data
            if self.last_instruction.c_input
            else self.c[1 if pc else 0]
        )
        c = c & 0xFF
        pandc = p + c

        sp = self.p[0 if pc else 1]
        sp = (sp << 8) & 0xFF00
        sc = self.c[0 if pc else 1]
        sc = sc & 0xFF
        spandsc = sp + sc

        a = self.data if self.last_instruction.a_input else self.a
        a_dec = bintoint(a & 0xFF)

        print("\n".join([
            f"IP:    {hexstr(ip, 4)}",
            f"PC:    {hexstr(pandc, 4)}",
            f"SPC:   {hexstr(spandsc, 4)}",
            f"A:     {hexstr(a, 2)} (unsigned: {a}, signed: {a_dec})",
            f"Flags: {hexstr(flags, 3)} (cf: {cf}, zf: {zf}, pc: {pc})",
            f"NextI: {disassemble(self.ram[ip])} ({binstr(self.ram[ip], 8)})",
        ]))

    def dump(self) -> None:
        # Print the contents of RAM
        def asc(val: int) -> str:
            if val >= 0x20 and val <= 0x7F:
                return chr(val)
            return "."

        starred = False
        for start in range(0, len(self.ram), 16):
            chunk = self.ram[start:(start+16)]
            if any(x for x in chunk):
                starred = False
                print(
                    f"{hexstr(start, 4)}: " +
                    f"{' '.join(hexstr(x, 2) for x in chunk)} "
                    f"{''.join(asc(x) for x in chunk)}"
                )
            else:
                if not starred:
                    print("*")
                    starred = True

    def disassemble(self) -> None:
        # Disassemble the contents of RAM
        starred = False
        for start in range(0, len(self.ram), 16):
            chunk = self.ram[start:(start+16)]
            if any(x for x in chunk):
                starred = False
                for offset, x in enumerate(chunk):
                    print(
                        f"{hexstr(start + offset, 4)}: " +
                        f"{hexstr(x, 2)} {disassemble(x)}"
                    )
            else:
                if not starred:
                    print("*")
                    starred = True

    def current_flags(self) -> int:
        cf = self.alu.carryout
        zf = self.alu.zero
        pc = self.flags & self.FLAGS_PC

        return (
            (self.FLAGS_CF if cf else 0) +
            (self.FLAGS_ZF if zf else 0) +
            (self.FLAGS_PC if pc else 0)
        )

    def tick(self) -> None:
        # Fetch instruction from RAM microcode.
        instructions = [
            ControlSignals(
                address_src=ControlSignals.ADDRESS_SRC_IP,
                sram_output=True,
                ir_input=True,
            ),
            # Dummy signals, since we know we will always
            # move to the next microcode on real HW.
            ControlSignals(),
        ]

        # Run microcode.
        while len(instructions) > 0:
            # Keep track of cycles
            self.cycles += 1

            # Store flags if we need to (its on its own bus)
            if self.last_instruction.flags_input:
                self.flags = self.current_flags()
            # Swap the PC flag if we need to (its implemented as a T flip-flop)
            if self.last_instruction.pc_swap:
                self.flags = self.flags ^ self.FLAGS_PC

            # Shortcut our PC calculation.
            which_pc = 1 if self.flags & self.FLAGS_PC else 0

            # Load from the bus if we're told to.
            if self.last_instruction.ip_input:
                self.ip = self.data
            if self.last_instruction.a_input:
                self.a = self.data & 0xFF
            if self.last_instruction.b_input:
                self.b = self.data & 0xFF
            if self.last_instruction.d_input:
                self.d = self.data & 0xFF
            if self.last_instruction.p_input:
                self.p[which_pc] = (self.data >> 8) & 0xFF
            if self.last_instruction.c_input:
                self.c[which_pc] = self.data & 0xFF
            if self.last_instruction.sram_input:
                if self.address >= len(self.ram) or self.address < 0:
                    raise Exception(
                        f"Address {self.address} outside of bounds of "
                        + "given memory!"
                    )
                self.ram = (
                    self.ram[:self.address] +
                    [self.data & 0xFF] +
                    self.ram[(self.address + 1):]
                )
            if self.last_instruction.ir_input:
                self.ir = self.data & 0xFF
                instructions = self.instruction_decode()

            # Fetch
            instruction = instructions[0]
            instructions = instructions[1:]

            # Now, set up the ALU.
            self.alu.op = instruction.alu_op
            self.alu.b = sign_extend(self.b, 7)
            if instruction.alu_src == ControlSignals.ALU_SRC_A:
                self.alu.a = self.a
            elif instruction.alu_src == ControlSignals.ALU_SRC_IP:
                self.alu.a = self.ip
            elif instruction.alu_src == ControlSignals.ALU_SRC_PC:
                self.alu.a = (
                    ((self.p[which_pc] << 8) & 0xFF00) +
                    (self.c[which_pc] & 0xFF)
                )
            else:
                raise Exception("Not implemented")
            if instruction.carry == ControlSignals.CARRY_CLEAR:
                self.alu.carryin = False
            elif instruction.carry == ControlSignals.CARRY_SET:
                self.alu.carryin = True
            elif instruction.carry == ControlSignals.CARRY_FROM_FLAGS:
                self.alu.carryin = (self.flags & self.FLAGS_CF) != 0
            else:
                raise Exception("Not implemented")

            # Update the address bus
            addr_bus = instruction.address_src
            if addr_bus == ControlSignals.ADDRESS_SRC_IP:
                self.address = self.ip
            elif addr_bus == ControlSignals.ADDRESS_SRC_PC:
                self.address = (
                    ((self.p[which_pc] << 8) & 0xFF00) +
                    (self.c[which_pc] & 0xFF)
                )
            else:
                raise Exception("Not implemented")

            # Now, write to the data bus if we're told to.
            self.data = 0b1111111111111111

            # The following write to all 16 bits of the bus.
            if instruction.alu_output:
                self.data = self.alu.result

            # The following write to only 8 bits of the bus.
            if instruction.sram_output:
                if self.address >= len(self.ram) or self.address < 0:
                    raise Exception(
                        f"Address {self.address} outside of bounds of "
                        + "given memory!"
                    )
                self.data = (
                    (self.data & 0xFF00) +
                    (self.ram[self.address] & 0xFF)
                )
            if instruction.a_output:
                self.data = (self.data & 0xFF00) + (self.a & 0xFF)
            if instruction.a_high_output:
                self.data = ((self.a << 8) & 0xFF00) + (self.data & 0x00FF)
            if instruction.d_output:
                self.data = (self.data & 0xFF00) + (self.d & 0xFF)
            if instruction.d_high_output:
                self.data = ((self.d << 8) & 0xFF00) + (self.data & 0x00FF)
            if instruction.alu_low_output:
                self.data = (
                    (self.data & 0xFF00) +
                    ((self.alu.result >> 8) & 0xFF)
                )
            if instruction.imm_output:
                self.data = (
                    (self.data & 0xFF00) +
                    (sign_extend(self.ir, 5) & 0xFF)
                )
            if instruction.z_output:
                self.data = (self.data & 0xFF00)
            if instruction.flags_output:
                # Combinatorial logic for doing skip instructions.
                bits = (self.ir & 0b110) >> 1
                param = self.ir & 0b001

                # The instructions are set up for easiest combinatorial
                # logic. bits 1 and 2 will always be 0b01 or 0b10, so
                # we just need to grab the flag bit that corresponds,
                # and or the two bits together to see if we are adding
                # or not.
                setbit = (bits & self.flags)
                bus_in = 1 if setbit != 0 else 0

                # Now, we just need to xor it with the param, so that
                # we can flip the bit if its supposed to be negated.
                bus_in = (bus_in ^ param) & 0b1

                # Finally, present it to the bus as the value we computed.
                self.data = (self.data & 0xFF00) + (bus_in & 0xFF)

            # Cap off the bus, since it is 16-bits in real HW.
            self.data = self.data & 0xFFFF

            # Remember last instruction since it is what is telling the
            # registers to store on the next tick.
            self.last_instruction = instruction

        # Keep track of ticks
        self.ticks += 1

    def instruction_decode(self) -> List[ControlSignals]:
        return decode(self.ir)
