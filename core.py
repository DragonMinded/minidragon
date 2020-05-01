#! /usr/bin/python3
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


def _splitparams(blob: str) -> Tuple[str, ...]:
    params: List[str] = []
    curparam: str = ""
    quote: Optional[str] = None

    for char in blob:
        if char == quote:
            # End quote, close it
            curparam += char
            quote = None
        elif quote is None and char in {"'", '"'}:
            # Start quote, open it
            curparam += char
            quote = quote
        elif quote is None and char == ",":
            # We aren't quoted, so this is a parameter separator
            params.append(curparam.strip())
            curparam = ""
        else:
            # Nothing but a regular ol' param piece here.
            curparam += char
    # Cap off with any possible accumulated last parameter
    if curparam:
        params.append(curparam.strip())
    return tuple(params)


def _paramrep(parameters: Tuple[str, ...]) -> str:
    if len(parameters) > 0:
        return ", ".join(parameters)
    else:
        return ""


def _insnrep(mnemonic: str, parameters: Tuple[str, ...]) -> str:
    if len(parameters) > 0:
        return f"{mnemonic} {_paramrep(parameters)}"
    else:
        return mnemonic


def _checkempty(mnemonic: str, parameters: Tuple[str, ...]) -> None:
    if len(parameters) > 0:
        raise ParameterOutOfRangeException(
            f"Invalid parameter {_paramrep(parameters)} for instruction "
            + _insnrep(mnemonic, parameters)
        ) from None


def _checkoneparam(mnemonic: str, parameters: Tuple[str, ...]) -> None:
    if len(parameters) == 0:
        raise ParameterOutOfRangeException(
            f"Expected parameter for instruction "
            + _insnrep(mnemonic, parameters)
        ) from None
    if len(parameters) > 1:
        raise ParameterOutOfRangeException(
            f"Too many parameters for instruction "
            + _insnrep(mnemonic, parameters)
        ) from None


def _checktwoparams(mnemonic: str, parameters: Tuple[str, ...]) -> None:
    if len(parameters) == 0:
        raise ParameterOutOfRangeException(
            f"Expected parameters for instruction "
            + _insnrep(mnemonic, parameters)
        ) from None
    if len(parameters) == 1:
        raise ParameterOutOfRangeException(
            f"Too few parameters for instruction "
            + _insnrep(mnemonic, parameters)
        ) from None
    if len(parameters) > 2:
        raise ParameterOutOfRangeException(
            f"Too many parameters for instruction "
            + _insnrep(mnemonic, parameters)
        ) from None


def _checklabel(
    mnemonic: str,
    parameters: Tuple[str, ...],
    loose: bool,
) -> None:
    if not loose:
        raise ParameterOutOfRangeException(
            f"Undefined label {_paramrep(parameters)} for instruction "
            + _insnrep(mnemonic, parameters)
        ) from None


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
    def signals(self) -> List["ControlSignals"]:
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
        parameters: Tuple[str, ...],
        origin: int,
        labels: Dict[str, int],
        loose: bool,
    ) -> List[int]:
        ...


def instruction(obj: Callable) -> Callable:
    instructions.append(obj())
    return obj


instructions: List[BaseInstruction] = []


class InvalidInstructionException(Exception):
    pass


class ParameterOutOfRangeException(Exception):
    pass


class CodeOutOfRangeException(Exception):
    pass


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
            signals = inst.signals()
            if len(signals) > 15:
                raise InvalidInstructionException(
                    "Instruction contains too many microcodes"
                )
            return signals
    else:
        raise InvalidInstructionException("Instruction not implemented")


def _getint(
    val: str,
    allow_unsigned: bool = False,
    hint: Optional[str] = None,
) -> int:
    val = val.strip()

    if (
        (val[0] == '"' and val[-1] == '"') or
        (val[0] == "'" and val[-1] == "'")
    ):
        # ascii character
        try:
            return ord(literal_eval(val))
        except ValueError:
            pass

    if val[:2] in {"0x", "0X"}:
        try:
            return int(val, 16)
        except ValueError:
            pass

    if val[:2] in {"0b", "0B"}:
        try:
            return int(val, 2)
        except ValueError:
            pass

    try:
        return int(val)
    except ValueError:
        pass

    raise InvalidInstructionException(
        f"Invalid integer {val}"
        + f"{'' if hint is None else ' on instruction ' + hint}"
    )


def getint(
    val: str,
    bits: int,
    allow_unsigned: bool = False,
    hint: Optional[str] = None,
) -> int:
    intval = _getint(val, hint=hint)

    # Bounds check the integer.
    if intval > ((2 ** (bits - (1 if not allow_unsigned else 0))) - 1):
        raise ParameterOutOfRangeException(
            f"Out of range integer {val}"
            + f"{'' if hint is None else ' on instruction ' + hint}"
        )

    if intval < 0 and abs(intval) > (2 ** (bits - 1)):
        raise ParameterOutOfRangeException(
            f"Out of range integer {val}"
            + f"{'' if hint is None else ' on instruction ' + hint}"
        )

    if intval < 0:
        # Get unsigned representation.
        intval = struct.unpack("H", struct.pack("h", intval))[0]

    # Return it masked.
    return intval & ((2 ** bits) - 1)


def assemble(
    mnemonics: List[str],
    existing_labels: Optional[Dict[str, int]] = None,
) -> List[Tuple[int, int]]:
    global instructions

    org = 0
    labels: Dict[str, int] = (
        existing_labels if existing_labels is not None else {}
    )
    data: Dict[int, int] = {}
    seen: Set[int] = set()

    # First pass, render out instructions that aren't labels, and
    # calculate label locations.
    for mnemonic in mnemonics:
        # Verify that it isn't full already.
        if org in seen:
            raise CodeOutOfRangeException(
                f"Cannot place code/data {mnemonic} into section " +
                f"0x{hexstr(org, 4)}, already occupied"
            )

        # Preprocessor directives.
        if mnemonic.startswith(".org "):
            # Origin directive
            org = getint(mnemonic[5:], 16, allow_unsigned=True)
        elif mnemonic.startswith(".byte "):
            # Data directive
            val = getint(mnemonic[6:], 8, allow_unsigned=True)
            data[org] = val
            seen.add(org)
            org += 1
        elif mnemonic.startswith(".char "):
            # Data directive
            val = getint(
                str(ord(literal_eval(mnemonic[6:]))),
                8,
                allow_unsigned=True,
            )
            data[org] = val
            seen.add(org)
            org += 1
        elif mnemonic.startswith(".str "):
            # Data directive
            for char in literal_eval(mnemonic[5:]):
                val = getint(
                    str(ord(char)),
                    8,
                    allow_unsigned=True,
                )
                data[org] = val
                seen.add(org)
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
                params = _splitparams(param)
            else:
                param = ""
                params = ()

            mnemonic = mnemonic.upper()
            for inst in instructions:
                if inst.assembles(mnemonic):
                    # Assemble without labels, telling the instruction to
                    # substitute whatever.
                    for val in inst.vals(
                        mnemonic, params, org, labels, loose=True
                    ):
                        data[org] = val
                        seen.add(org)
                        org += 1
                    break
            else:
                raise InvalidInstructionException(
                    f"Unrecognized instruction {mnemonic} {param}"
                )

    # Now, do the whole thing again, ignoring seen state and non-instructions
    # and let the instructions re-generate themselves with correct labels.
    org = 0
    for mnemonic in mnemonics:
        # Preprocessor directives.
        if mnemonic.startswith(".org "):
            org = getint(mnemonic[5:], 16, allow_unsigned=True)
        elif mnemonic.startswith(".byte "):
            org += 1
        elif mnemonic.startswith(".char "):
            org += 1
        elif mnemonic.startswith(".str "):
            for char in literal_eval(mnemonic[5:]):
                org += 1
        # Labels.
        elif mnemonic.endswith(":"):
            pass
        # Regular opcodes.
        else:
            # We must assemble this.
            if " " in mnemonic:
                mnemonic, param = mnemonic.split(" ", 1)
                params = _splitparams(param)
            else:
                param = ""
                params = ()

            mnemonic = mnemonic.upper()
            for inst in instructions:
                if inst.assembles(mnemonic):
                    # Assemble without labels, telling the instruction to
                    # substitute whatever.
                    for val in inst.vals(
                        mnemonic, params, org, labels, loose=False
                    ):
                        data[org] = val
                        org += 1
                    break
            else:
                raise InvalidInstructionException(
                    f"Unrecognized instruction {mnemonic} {param}"
                )

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

    def signals(self) -> List["ControlSignals"]:
        return [
            ControlSignals(
                imm_6_output=True,
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
        parameters: Tuple[str, ...],
        origin: int,
        labels: Dict[str, int],
        loose: bool,
    ) -> List[int]:
        if mnemonic == "NOP":
            _checkempty(mnemonic, parameters)
            return [0b00000000]
        if mnemonic == "HALT":
            _checkempty(mnemonic, parameters)
            return [0b00111111]

        # A jump, relative to instruction. We need to handle labels.
        # First, try to get this as an integer.
        _checkoneparam(mnemonic, parameters)
        parameter = parameters[0]
        try:
            location = getint(
                parameter,
                6,
                hint=_insnrep(mnemonic, parameters),
            )
        except InvalidInstructionException:
            # Now, try as a label.
            if parameter in labels:
                offset = str(labels[parameter] - origin - 1)
                location = getint(
                    offset,
                    6,
                    hint=_insnrep(mnemonic, parameters),
                )
            else:
                # Verify that we do or don't need labels.
                _checklabel(mnemonic, parameters, loose)

                # We don't care about this value right now, fill it in as
                # whatever.
                location = 0b00111111

        return [0b00000000 | location]


@instruction
class ADDI(BaseInstruction):
    # Add immediate sign extended to A.

    def handles(self, instruction: int) -> bool:
        return instruction & 0b11000000 == 0b01000000

    def mnemonic(self, instruction: int) -> str:
        integer = bintoint(sign_extend(instruction & 0x3F, 5) & 0xFF)
        if integer == 1:
            return "INC"
        elif integer == -1:
            return "DEC"
        else:
            return f"ADDI {integer}"

    def signals(self) -> List["ControlSignals"]:
        return [
            ControlSignals(
                imm_6_output=True,
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
        parameters: Tuple[str, ...],
        origin: int,
        labels: Dict[str, int],
        loose: bool,
    ) -> List[int]:
        if mnemonic == "INC":
            _checkempty(mnemonic, parameters)
            addval = 1
        elif mnemonic == "DEC":
            _checkempty(mnemonic, parameters)
            addval = 0b00111111
        else:
            _checkoneparam(mnemonic, parameters)
            parameter = parameters[0]
            addval = getint(parameter, 6, hint=_insnrep(mnemonic, parameters))
        return [0b01000000 | addval]


@instruction
class PUSHIP(BaseInstruction):
    # Decrement PC by 2, take the current IP, add an immediate zero-extended
    # value to it, and store that at PC.

    def handles(self, instruction: int) -> bool:
        return instruction & 0b11111000 == 0b10000000

    def mnemonic(self, instruction: int) -> str:
        # Cleverly, we ensured that the sign-extend portion of the instruction
        # is zeros by choosing where in our number space to place it. This
        # means we can only have a positive offset, but we don't need new
        # hardware to handle just this instruction.
        integer = bintoint(sign_extend(instruction & 0x0F, 3) & 0xFF)
        return f"PUSHIP {integer}"

    def signals(self) -> List["ControlSignals"]:
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
                imm_4_output=True,
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
                imm_4_output=True,
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
        parameters: Tuple[str, ...],
        origin: int,
        labels: Dict[str, int],
        loose: bool,
    ) -> List[int]:
        _checkoneparam(mnemonic, parameters)
        parameter = parameters[0]

        try:
            # Try to grab the offset as a raw integer.
            location = getint(
                parameter,
                3,
                allow_unsigned=True,
                hint=_insnrep(mnemonic, parameters),
            )
        except InvalidInstructionException:
            # Now, try as a label.
            if parameter in labels:
                offset = str(labels[parameter] - origin)
                location = getint(
                    offset,
                    3,
                    allow_unsigned=True,
                    hint=_insnrep(mnemonic, parameters),
                )
            else:
                # We don't care about this value right now, fill it in as
                # whatever. We'll get to it on the second pass.
                _checklabel(mnemonic, parameters, loose)
                location = 0

        if location < 0:
            raise ParameterOutOfRangeException(
                f"Can only have a positive offset "
                + f"for instruction {_insnrep(mnemonic, parameters)}"
            )
        if location > 7:
            raise ParameterOutOfRangeException(
                f"Can only store an offset up to 7 "
                + f"for instruction {_insnrep(mnemonic, parameters)}"
            )

        return [0b10000000 + location]


class BaseALUUInstruction(BaseInstruction, ABC):
    opcode: int

    def handles(self, instruction: int) -> bool:
        if instruction & 0b11100000 != 0b10000000:
            # This is not our range.
            return False
        if instruction & 0b00011000 != 0b00001000:
            # This is not our register selection.
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
        parameters: Tuple[str, ...],
        origin: int,
        labels: Dict[str, int],
        loose: bool,
    ) -> List[int]:
        _checkempty(mnemonic, parameters)
        return [0b10001000 | self.opcode]


@instruction
class ADDU(BaseALUUInstruction):
    # Add contents of memory at P+C to A register.

    opcode = 0b001

    def signals(self) -> List["ControlSignals"]:
        return [
            ControlSignals(
                address_src=ControlSignals.ADDRESS_SRC_PC,
                u_output=True,
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
class ADCU(BaseALUUInstruction):
    # Add contents of memory at P+C to A register with carry in.

    opcode = 0b010

    def signals(self) -> List["ControlSignals"]:
        return [
            ControlSignals(
                address_src=ControlSignals.ADDRESS_SRC_PC,
                u_output=True,
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
class ANDU(BaseALUUInstruction):
    # Add contents of memory at P+C with A register.

    opcode = 0b011

    def signals(self) -> List["ControlSignals"]:
        return [
            ControlSignals(
                address_src=ControlSignals.ADDRESS_SRC_PC,
                u_output=True,
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
class ORU(BaseALUUInstruction):
    # Or contents of memory at P+C with A register.

    opcode = 0b100

    def signals(self) -> List["ControlSignals"]:
        return [
            ControlSignals(
                address_src=ControlSignals.ADDRESS_SRC_PC,
                u_output=True,
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
class XORU(BaseALUUInstruction):
    # Exclusive or contents of memory at P+C with A register.

    opcode = 0b101

    def signals(self) -> List["ControlSignals"]:
        return [
            ControlSignals(
                address_src=ControlSignals.ADDRESS_SRC_PC,
                u_output=True,
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


class BaseALUVInstruction(BaseInstruction, ABC):
    opcode: int

    def handles(self, instruction: int) -> bool:
        if instruction & 0b11100000 != 0b10000000:
            # This is not our range.
            return False
        if instruction & 0b00011000 != 0b00010000:
            # This is not our register selection.
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
        parameters: Tuple[str, ...],
        origin: int,
        labels: Dict[str, int],
        loose: bool,
    ) -> List[int]:
        _checkempty(mnemonic, parameters)
        return [0b10010000 | self.opcode]


@instruction
class ADDV(BaseALUVInstruction):
    # Add contents of memory at P+C to A register.

    opcode = 0b001

    def signals(self) -> List["ControlSignals"]:
        return [
            ControlSignals(
                address_src=ControlSignals.ADDRESS_SRC_PC,
                v_output=True,
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
class ADCV(BaseALUVInstruction):
    # Add contents of memory at P+C to A register with carry in.

    opcode = 0b010

    def signals(self) -> List["ControlSignals"]:
        return [
            ControlSignals(
                address_src=ControlSignals.ADDRESS_SRC_PC,
                v_output=True,
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
class ANDV(BaseALUVInstruction):
    # Add contents of memory at P+C with A register.

    opcode = 0b011

    def signals(self) -> List["ControlSignals"]:
        return [
            ControlSignals(
                address_src=ControlSignals.ADDRESS_SRC_PC,
                v_output=True,
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
class ORV(BaseALUVInstruction):
    # Or contents of memory at P+C with A register.

    opcode = 0b100

    def signals(self) -> List["ControlSignals"]:
        return [
            ControlSignals(
                address_src=ControlSignals.ADDRESS_SRC_PC,
                v_output=True,
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
class XORV(BaseALUVInstruction):
    # Exclusive or contents of memory at P+C with A register.

    opcode = 0b101

    def signals(self) -> List["ControlSignals"]:
        return [
            ControlSignals(
                address_src=ControlSignals.ADDRESS_SRC_PC,
                v_output=True,
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
class RCL(BaseALUVInstruction):
    # Shift contents of A left and shift in carry flag.

    opcode = 0b110

    def signals(self) -> List["ControlSignals"]:
        return [
            ControlSignals(
                alu_src=ControlSignals.ALU_SRC_A,
                alu_op=ALU.OPERATION_SHL,
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
class RCR(BaseALUVInstruction):
    # Shift contents of A right.

    opcode = 0b111

    def signals(self) -> List["ControlSignals"]:
        return [
            ControlSignals(
                alu_src=ControlSignals.ALU_SRC_A,
                alu_op=ALU.OPERATION_SHR,
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


class BaseALUSRAMInstruction(BaseInstruction, ABC):
    opcode: int

    def handles(self, instruction: int) -> bool:
        if instruction & 0b11100000 != 0b10000000:
            # This is not our range.
            return False
        if instruction & 0b00011000 != 0b00011000:
            # This is not our register selection.
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
        parameters: Tuple[str, ...],
        origin: int,
        labels: Dict[str, int],
        loose: bool,
    ) -> List[int]:
        _checkempty(mnemonic, parameters)
        return [0b10011000 | self.opcode]


@instruction
class INV(BaseALUSRAMInstruction):
    # Invert contents of A.

    opcode = 0b000

    def signals(self) -> List["ControlSignals"]:
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
class ADD(BaseALUSRAMInstruction):
    # Add contents of memory at P+C to A register.

    opcode = 0b001

    def signals(self) -> List["ControlSignals"]:
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
class ADC(BaseALUSRAMInstruction):
    # Add contents of memory at P+C to A register with carry in.

    opcode = 0b010

    def signals(self) -> List["ControlSignals"]:
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
class AND(BaseALUSRAMInstruction):
    # Add contents of memory at P+C with A register.

    opcode = 0b011

    def signals(self) -> List["ControlSignals"]:
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
class OR(BaseALUSRAMInstruction):
    # Or contents of memory at P+C with A register.

    opcode = 0b100

    def signals(self) -> List["ControlSignals"]:
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
class XOR(BaseALUSRAMInstruction):
    # Exclusive or contents of memory at P+C with A register.

    opcode = 0b101

    def signals(self) -> List["ControlSignals"]:
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
class SHL(BaseALUSRAMInstruction):
    # Shift contents of A left.

    opcode = 0b110

    def signals(self) -> List["ControlSignals"]:
        return [
            ControlSignals(
                alu_src=ControlSignals.ALU_SRC_A,
                alu_op=ALU.OPERATION_SHL,
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
class SHR(BaseALUSRAMInstruction):
    # Shift contents of A right.

    opcode = 0b111

    def signals(self) -> List["ControlSignals"]:
        return [
            ControlSignals(
                alu_src=ControlSignals.ALU_SRC_A,
                alu_op=ALU.OPERATION_SHR,
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
class ADDPCI(BaseInstruction):
    # Add immediate to the P+C virtual register.

    def handles(self, instruction: int) -> bool:
        return instruction & 0b11100000 == 0b11000000

    def mnemonic(self, instruction: int) -> str:
        # Technically, we look at the bottom 6 bits, and this instruction
        # is specifically placed to have a zero in the 6th bit position.
        integer = bintoint(sign_extend(instruction & 0x3F, 5) & 0xFF) + 1
        if integer == 1:
            return "INCPC"
        else:
            return f"ADDPCI {integer}"

    def signals(self) -> List["ControlSignals"]:
        signals = [
            ControlSignals(
                imm_6_output=True,
                b_input=True,
            ),
            ControlSignals(
                alu_src=ControlSignals.ALU_SRC_PC,
                alu_op=ALU.OPERATION_ADD,
                carry=ControlSignals.CARRY_SET,
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
            ),
        ]
        return signals

    def assembles(self, mnemonic: str) -> bool:
        return mnemonic in {"INCPC", "ADDPCI"}

    def vals(
        self,
        mnemonic: str,
        parameters: Tuple[str, ...],
        origin: int,
        labels: Dict[str, int],
        loose: bool,
    ) -> List[int]:
        if mnemonic == "INCPC":
            _checkempty(mnemonic, parameters)
            return [0b11000000]

        _checkoneparam(mnemonic, parameters)
        parameter = parameters[0]
        location = getint(
            parameter,
            6,
            allow_unsigned=True,
            hint=_insnrep(mnemonic, parameters)
        ) - 1
        if location > 31 or location < 0:
            raise ParameterOutOfRangeException(
                f"Parameter out of range for "
                + f"instruction {_insnrep(mnemonic, parameters)}"
            )
        return [0b11000000 | (location & 0b11111)]


@instruction
class SUBPCI(BaseInstruction):
    # Add immediate to the P+C virtual register.

    def handles(self, instruction: int) -> bool:
        return instruction & 0b11100000 == 0b10100000

    def mnemonic(self, instruction: int) -> str:
        integer = -bintoint(sign_extend(instruction & 0x3F, 5) & 0xFF)
        if integer == 1:
            return "DECPC"
        else:
            return f"SUBPCI {integer}"

    def signals(self) -> List["ControlSignals"]:
        signals = [
            ControlSignals(
                imm_6_output=True,
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
            ),
        ]
        return signals

    def assembles(self, mnemonic: str) -> bool:
        return mnemonic in {"DECPC", "SUBPCI"}

    def vals(
        self,
        mnemonic: str,
        parameters: Tuple[str, ...],
        origin: int,
        labels: Dict[str, int],
        loose: bool,
    ) -> List[int]:
        if mnemonic == "DECPC":
            _checkempty(mnemonic, parameters)
            return [0b10111111]

        _checkoneparam(mnemonic, parameters)
        parameter = parameters[0]
        location = getint(
            parameter,
            6,
            allow_unsigned=True,
            hint=_insnrep(mnemonic, parameters)
        )
        if location > 32 or location < 1:
            raise ParameterOutOfRangeException(
                f"Parameter out of range for "
                + f"instruction {_insnrep(mnemonic, parameters)}"
            )
        return [0b10100000 | ((-location) & 0b11111)]


class BaseRegisterInstruction(BaseInstruction, ABC):
    opcode: int

    def handles(self, instruction: int) -> bool:
        if instruction & 0b11111000 != 0b11100000:
            return False
        return instruction & 0b111 == self.opcode

    def mnemonic(self, instruction: int) -> str:
        # Register operations don't take any parameters.
        return self.__class__.__name__

    def assembles(self, mnemonic: str) -> bool:
        return self.__class__.__name__ == mnemonic

    def vals(
        self,
        mnemonic: str,
        parameters: Tuple[str, ...],
        origin: int,
        labels: Dict[str, int],
        loose: bool,
    ) -> List[int]:
        _checkempty(mnemonic, parameters)
        return [0b11100000 | self.opcode]


@instruction
class LOADU(BaseRegisterInstruction):
    # Load the contents of memory at P+C to U register.

    opcode = 0b000

    def signals(self) -> List["ControlSignals"]:
        return [
            ControlSignals(
                address_src=ControlSignals.ADDRESS_SRC_PC,
                sram_output=True,
                u_input=True,
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
class STOREU(BaseRegisterInstruction):
    # Store the contents of the U register to memory at P+C.

    opcode = 0b001

    def signals(self) -> List["ControlSignals"]:
        return [
            ControlSignals(
                address_src=ControlSignals.ADDRESS_SRC_PC,
                sram_input=True,
                u_output=True,
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
class LOADV(BaseRegisterInstruction):
    # Load the contents of memory at P+C to V register.

    opcode = 0b010

    def signals(self) -> List["ControlSignals"]:
        return [
            ControlSignals(
                address_src=ControlSignals.ADDRESS_SRC_PC,
                sram_output=True,
                v_input=True,
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
class STOREV(BaseRegisterInstruction):
    # Store the contents of the V register to memory at P+C.

    opcode = 0b011

    def signals(self) -> List["ControlSignals"]:
        return [
            ControlSignals(
                address_src=ControlSignals.ADDRESS_SRC_PC,
                sram_input=True,
                v_output=True,
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
class SWAPAU(BaseRegisterInstruction):
    # Swap the contents of the A and U registers.

    opcode = 0b100

    def signals(self) -> List["ControlSignals"]:
        return [
            ControlSignals(
                a_output=True,
                d_input=True,
            ),
            ControlSignals(
                u_output=True,
                a_input=True,
            ),
            ControlSignals(
                d_output=True,
                u_input=True,
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
class SWAPAV(BaseRegisterInstruction):
    # Swap the contents of the A and V registers.

    opcode = 0b101

    def signals(self) -> List["ControlSignals"]:
        return [
            ControlSignals(
                a_output=True,
                d_input=True,
            ),
            ControlSignals(
                v_output=True,
                a_input=True,
            ),
            ControlSignals(
                d_output=True,
                v_input=True,
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
class SWAPUV(BaseRegisterInstruction):
    # Swap the contents of the U and V registers.

    opcode = 0b110

    def signals(self) -> List["ControlSignals"]:
        return [
            ControlSignals(
                u_output=True,
                d_input=True,
            ),
            ControlSignals(
                v_output=True,
                u_input=True,
            ),
            ControlSignals(
                d_output=True,
                v_input=True,
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
class SWAPPC(BaseRegisterInstruction):
    # Swap PC and SPC registers.
    opcode = 0b111

    def signals(self) -> List["ControlSignals"]:
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


class BaseMoveInstruction(BaseInstruction, ABC):
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
        parameters: Tuple[str, ...],
        origin: int,
        labels: Dict[str, int],
        loose: bool,
    ) -> List[int]:
        _checkempty(mnemonic, parameters)
        return [0b11101000 | self.opcode]


@instruction
class ATOP(BaseMoveInstruction):
    # Move contents of A register to P register.

    opcode = 0b000

    def signals(self) -> List["ControlSignals"]:
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
class ATOC(BaseMoveInstruction):
    # Move contents of A register to C register.

    opcode = 0b001

    def signals(self) -> List["ControlSignals"]:
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
class PTOA(BaseMoveInstruction):
    # Move contents of P register to A register.

    opcode = 0b010

    def signals(self) -> List["ControlSignals"]:
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
class CTOA(BaseMoveInstruction):
    # Move contents of C register to A register.

    opcode = 0b011

    def signals(self) -> List["ControlSignals"]:
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
class ATOU(BaseMoveInstruction):
    # Move contents of A register to U register.

    opcode = 0b100

    def signals(self) -> List["ControlSignals"]:
        return [
            ControlSignals(
                u_input=True,
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
class ATOV(BaseMoveInstruction):
    # Move contents of A register to V register.

    opcode = 0b101

    def signals(self) -> List["ControlSignals"]:
        return [
            ControlSignals(
                v_input=True,
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
class UTOA(BaseMoveInstruction):
    # Move contents of U register to A register.

    opcode = 0b110

    def signals(self) -> List["ControlSignals"]:
        return [
            ControlSignals(
                a_input=True,
                u_output=True,
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
class VTOA(BaseMoveInstruction):
    # Move contents of V register to A register.

    opcode = 0b111

    def signals(self) -> List["ControlSignals"]:
        return [
            ControlSignals(
                a_input=True,
                v_output=True,
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

    def signals(self) -> List["ControlSignals"]:
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
        parameters: Tuple[str, ...],
        origin: int,
        labels: Dict[str, int],
        loose: bool,
    ) -> List[int]:
        _checkoneparam(mnemonic, parameters)
        parameter = parameters[0]
        base = 0b11110000

        if parameter.startswith("!"):
            flag = parameter[1:].lower()
            base |= 0b1
        else:
            flag = parameter.lower()

        if flag == "cf":
            base |= 0b010
        elif flag == "zf":
            base |= 0b100
        else:
            raise ParameterOutOfRangeException(
                f"Invalid condition {_paramrep(parameters)} for "
                + f"instruction {_insnrep(mnemonic, parameters)}",
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
        parameters: Tuple[str, ...],
        origin: int,
        labels: Dict[str, int],
        loose: bool,
    ) -> List[int]:
        _checkempty(mnemonic, parameters)
        return [0b11111000 | self.opcode]


@instruction
class LNGJUMP(BaseStackInstruction):
    # Jump to 16-bit immediate value stored directly after instruction.
    opcode = 0b000

    def signals(self) -> List["ControlSignals"]:
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
        parameters: Tuple[str, ...],
        origin: int,
        labels: Dict[str, int],
        loose: bool,
    ) -> List[int]:
        # We override the base because we technically take an immediate for
        # this opcode, its just stored in memory after the opcode itself.
        _checkoneparam(mnemonic, parameters)
        parameter = parameters[0]

        # Assume the user wanted to jump to an immediate or a label.
        try:
            location = getint(
                parameter,
                16,
                allow_unsigned=True,
                hint=_insnrep(mnemonic, parameters),
            )
        except InvalidInstructionException:
            # Now, try as a label.
            if parameter in labels:
                offset = str(labels[parameter])
                location = getint(
                    offset,
                    16,
                    allow_unsigned=True,
                    hint=_insnrep(mnemonic, parameters),
                )
            else:
                # We don't care about this value right now, fill it in as
                # whatever.
                _checklabel(mnemonic, parameters, loose)
                location = 0

        return [0b11111000, (location >> 8) & 0xFF, location & 0xFF]


@instruction
class LOADI(BaseStackInstruction):
    # Load immediate stored after instruction to A.
    opcode = 0b001

    def signals(self) -> List["ControlSignals"]:
        return [
            # First, increment the IP so we can grab the value.
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
            # Store it in A register
            ControlSignals(
                address_src=ControlSignals.ADDRESS_SRC_IP,
                sram_output=True,
                a_input=True,
            ),
            # Now, increment once more to go to next intstruction.
            ControlSignals(
                alu_src=ControlSignals.ALU_SRC_IP,
                alu_op=ALU.OPERATION_ADD,
                carry=ControlSignals.CARRY_SET,
                alu_output=True,
                ip_input=True,
            ),
        ]

    def vals(
        self,
        mnemonic: str,
        parameters: Tuple[str, ...],
        origin: int,
        labels: Dict[str, int],
        loose: bool,
    ) -> List[int]:
        # We override the base because we technically take an immediate for
        # this opcode, its just stored in memory after the opcode itself.
        _checkoneparam(mnemonic, parameters)
        parameter = parameters[0]
        loadval = getint(
            parameter,
            8,
            allow_unsigned=True,
            hint=_insnrep(mnemonic, parameters),
        )
        return [0b11111001, loadval & 0xFF]


@instruction
class ADDPC(BaseStackInstruction):
    # Add contents of A register sign extended to 16 bits to the P+C
    # virtual register.
    opcode = 0b010

    def signals(self) -> List["ControlSignals"]:
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

    def signals(self) -> List["ControlSignals"]:
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

    def signals(self) -> List["ControlSignals"]:
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

    def signals(self) -> List["ControlSignals"]:
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


@instruction
class LOADA(BaseStackInstruction):
    # Load the contents of memory at P+C to A register.

    opcode = 0b110

    def signals(self) -> List["ControlSignals"]:
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
class STOREA(BaseStackInstruction):
    # Store the contents of the A register to memory at P+C.

    opcode = 0b111

    def signals(self) -> List["ControlSignals"]:
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


class BaseMacro(BaseInstruction):
    def handles(self, instruction: int) -> bool:
        # We never handle disassembly, macros generate assembly blocks
        return False

    def mnemonic(self, instruction: int) -> str:
        raise Exception(
            "We don't handle any opcodes so we should never be asked for "
            "a mnemonic!"
        )

    def signals(self) -> List["ControlSignals"]:
        raise Exception(
            "We don't handle any opcodes so we should never be asked for "
            "signals!"
        )

    def compile(
        self,
        org: int,
        instructions: List[str],
        hint: Optional[str] = None,
    ) -> List[int]:
        if hint:
            try:
                loc_and_assembly = assemble([f".org {org}", *instructions])
            except ParameterOutOfRangeException:
                raise InvalidInstructionException(
                    f"Couldn't compile macro {hint}",
                )
        else:
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
class SETPC(BaseMacro):
    def assembles(self, mnemonic: str) -> bool:
        return mnemonic == "SETPC"

    def vals(
        self,
        mnemonic: str,
        parameters: Tuple[str, ...],
        origin: int,
        labels: Dict[str, int],
        loose: bool,
    ) -> List[int]:
        _checkoneparam(mnemonic, parameters)
        parameter = parameters[0]

        # Load immediate value into PC.
        # First, try to get this as an integer.
        try:
            location = getint(
                parameter,
                16,
                allow_unsigned=True,
                hint=_insnrep(mnemonic, parameters),
            )
        except InvalidInstructionException:
            # Now, try as a label.
            if parameter in labels:
                location = getint(
                    str(labels[parameter]),
                    16,
                    allow_unsigned=True,
                    hint=_insnrep(mnemonic, parameters),
                )
            else:
                # Unfortunately this macro takes a variable number of
                # instructions, due to us needing to potentially shift
                # values into upper bits of the A register, so we must
                # have already seen a label to use it.
                raise ParameterOutOfRangeException(
                    f"Cannot SETPC to a label not yet seen for "
                    + f"instruction {_insnrep(mnemonic, parameters)}"
                )

        # Now, split the location into two halves.
        pval = (location >> 8) & 0xFF
        cval = location & 0xFF

        # Now, get the instructions themselves
        instructions = [
            f"LOADI {pval}",
            "ATOP",
            f"LOADI {cval}",
            "ATOC",
        ]

        # Now, assemble them and return that value
        return self.compile(
            origin,
            instructions,
            hint=_insnrep(mnemonic, parameters),
        )


@instruction
class JRIZ(BaseMacro):
    # Jump reliative to immediate if zero set.

    def assembles(self, mnemonic: str) -> bool:
        return mnemonic == "JRIZ"

    def vals(
        self,
        mnemonic: str,
        parameters: Tuple[str, ...],
        origin: int,
        labels: Dict[str, int],
        loose: bool,
    ) -> List[int]:
        _checkoneparam(mnemonic, parameters)
        parameter = parameters[0]

        try:
            # First, try as an integer.
            location = getint(
                parameter,
                6,
                hint=_insnrep(mnemonic, parameters),
            )
            # We subtract one because the virtual position of this instruction
            # is one memory address earlier than where the actual jump
            # instruction will go.
            if location & 0b00100000:
                location -= 1
        except InvalidInstructionException:
            # Now, try as a label.
            if parameter in labels:
                absolute_location = labels[parameter]
                # Adjust backwards 2 so we can skip past our skip
                # instruction.
                location = absolute_location - origin - 2
            else:
                # Assume nothing for now, will be filled in later
                _checklabel(mnemonic, parameters, loose)
                location = 0

        # If we want to jump on zero flag set, we need to skip the
        # jump if zero flag cleared.
        return self.compile(
            origin,
            ["SKIPIF !ZF", f"JRI {location}"],
            hint=_insnrep(mnemonic, parameters),
        )


@instruction
class JRINZ(BaseMacro):
    # Jump reliative to immediate if zero not set.

    def assembles(self, mnemonic: str) -> bool:
        return mnemonic == "JRINZ"

    def vals(
        self,
        mnemonic: str,
        parameters: Tuple[str, ...],
        origin: int,
        labels: Dict[str, int],
        loose: bool,
    ) -> List[int]:
        _checkoneparam(mnemonic, parameters)
        parameter = parameters[0]

        try:
            # First, try as an integer.
            location = getint(
                parameter,
                6,
                hint=_insnrep(mnemonic, parameters),
            )
            # We subtract one because the virtual position of this instruction
            # is one memory address earlier than where the actual jump
            # instruction will go.
            if location & 0b00100000:
                location -= 1
        except InvalidInstructionException:
            # Now, try as a label.
            if parameter in labels:
                absolute_location = labels[parameter]
                # Adjust backwards 2 so we can skip past our skip
                # instruction.
                location = absolute_location - origin - 2
            else:
                # Assume nothing for now, will be filled in later
                _checklabel(mnemonic, parameters, loose)
                location = 0

        # If we want to jump on zero flag cleared, we need to skip the
        # jump if zero flag set.
        return self.compile(
            origin,
            ["SKIPIF ZF", f"JRI {location}"],
            hint=_insnrep(mnemonic, parameters),
        )


@instruction
class JRIC(BaseMacro):
    # Jump reliative to immediate if carry set.

    def assembles(self, mnemonic: str) -> bool:
        return mnemonic == "JRIC"

    def vals(
        self,
        mnemonic: str,
        parameters: Tuple[str, ...],
        origin: int,
        labels: Dict[str, int],
        loose: bool,
    ) -> List[int]:
        _checkoneparam(mnemonic, parameters)
        parameter = parameters[0]

        try:
            # First, try as an integer.
            location = getint(
                parameter,
                6,
                hint=_insnrep(mnemonic, parameters),
            )
            # We subtract one because the virtual position of this instruction
            # is one memory address earlier than where the actual jump
            # instruction will go.
            if location & 0b00100000:
                location -= 1
        except InvalidInstructionException:
            # Now, try as a label.
            if parameter in labels:
                absolute_location = labels[parameter]
                # Adjust backwards 2 so we can skip past our skip
                # instruction.
                location = absolute_location - origin - 2
            else:
                # Assume nothing for now, will be filled in later
                _checklabel(mnemonic, parameters, loose)
                location = 0

        # If we want to jump on carry flag set, we need to skip the
        # jump if carry flag cleared.
        return self.compile(
            origin,
            ["SKIPIF !CF", f"JRI {location}"],
            hint=_insnrep(mnemonic, parameters),
        )


@instruction
class JRINC(BaseMacro):
    # Jump reliative to immediate if carry not set.

    def assembles(self, mnemonic: str) -> bool:
        return mnemonic == "JRINC"

    def vals(
        self,
        mnemonic: str,
        parameters: Tuple[str, ...],
        origin: int,
        labels: Dict[str, int],
        loose: bool,
    ) -> List[int]:
        _checkoneparam(mnemonic, parameters)
        parameter = parameters[0]

        try:
            # First, try as an integer.
            location = getint(
                parameter,
                6,
                hint=_insnrep(mnemonic, parameters),
            )
            # We subtract one because the virtual position of this instruction
            # is one memory address earlier than where the actual jump
            # instruction will go.
            if location & 0b00100000:
                location -= 1
        except InvalidInstructionException:
            # Now, try as a label.
            if parameter in labels:
                absolute_location = labels[parameter]
                # Adjust backwards 2 so we can skip past our skip
                # instruction.
                location = absolute_location - origin - 2
            else:
                # Assume nothing for now, will be filled in later
                _checklabel(mnemonic, parameters, loose)
                location = 0

        # If we want to jump on carry flag cleared, we need to skip the
        # jump if carry flag set.
        return self.compile(
            origin,
            ["SKIPIF CF", f"JRI {location}"],
            hint=_insnrep(mnemonic, parameters),
        )


@instruction
class LNGJUMPZ(BaseMacro):
    # Jump to immediate if zero flag set.

    def assembles(self, mnemonic: str) -> bool:
        return mnemonic == "LNGJUMPZ"

    def vals(
        self,
        mnemonic: str,
        parameters: Tuple[str, ...],
        origin: int,
        labels: Dict[str, int],
        loose: bool,
    ) -> List[int]:
        _checkoneparam(mnemonic, parameters)
        parameter = parameters[0]

        try:
            # First, try as an integer.
            location = getint(
                parameter,
                16,
                allow_unsigned=True,
                hint=_insnrep(mnemonic, parameters),
            )
        except InvalidInstructionException:
            # Now, try as a label.
            if parameter in labels:
                offset = str(labels[parameter])
                location = getint(
                    offset,
                    16,
                    allow_unsigned=True,
                    hint=_insnrep(mnemonic, parameters),
                )
            else:
                # Assume nothing for now, will be filled in later
                _checklabel(mnemonic, parameters, loose)
                location = 0

        return self.compile(
            origin,
            [
                "SKIPIF ZF",
                "JRI skip_longjump",
                f"LNGJUMP {location}",
                "skip_longjump:",
            ],
            hint=_insnrep(mnemonic, parameters),
        )


@instruction
class LNGJUMPNZ(BaseMacro):
    # Jump to immediate if zero flag not set.

    def assembles(self, mnemonic: str) -> bool:
        return mnemonic == "LNGJUMPNZ"

    def vals(
        self,
        mnemonic: str,
        parameters: Tuple[str, ...],
        origin: int,
        labels: Dict[str, int],
        loose: bool,
    ) -> List[int]:
        _checkoneparam(mnemonic, parameters)
        parameter = parameters[0]

        try:
            # First, try as an integer.
            location = getint(
                parameter,
                16,
                allow_unsigned=True,
                hint=_insnrep(mnemonic, parameters),
            )
        except InvalidInstructionException:
            # Now, try as a label.
            if parameter in labels:
                offset = str(labels[parameter])
                location = getint(
                    offset,
                    16,
                    allow_unsigned=True,
                    hint=_insnrep(mnemonic, parameters),
                )
            else:
                # Assume nothing for now, will be filled in later
                _checklabel(mnemonic, parameters, loose)
                location = 0

        return self.compile(
            origin,
            [
                "SKIPIF !ZF",
                "JRI skip_longjump",
                f"LNGJUMP {location}",
                "skip_longjump:",
            ],
            hint=_insnrep(mnemonic, parameters),
        )


@instruction
class LNGJUMPC(BaseMacro):
    # Jump to immediate if carry flag set.

    def assembles(self, mnemonic: str) -> bool:
        return mnemonic == "LNGJUMPC"

    def vals(
        self,
        mnemonic: str,
        parameters: Tuple[str, ...],
        origin: int,
        labels: Dict[str, int],
        loose: bool,
    ) -> List[int]:
        _checkoneparam(mnemonic, parameters)
        parameter = parameters[0]

        try:
            # First, try as an integer.
            location = getint(
                parameter,
                16,
                allow_unsigned=True,
                hint=_insnrep(mnemonic, parameters),
            )
        except InvalidInstructionException:
            # Now, try as a label.
            if parameter in labels:
                offset = str(labels[parameter])
                location = getint(
                    offset,
                    16,
                    allow_unsigned=True,
                    hint=_insnrep(mnemonic, parameters),
                )
            else:
                # Assume nothing for now, will be filled in later
                _checklabel(mnemonic, parameters, loose)
                location = 0

        return self.compile(
            origin,
            [
                "SKIPIF CF",
                "JRI skip_longjump",
                f"LNGJUMP {location}",
                "skip_longjump:",
            ],
            hint=_insnrep(mnemonic, parameters),
        )


@instruction
class LNGJUMPNC(BaseMacro):
    # Jump to immediate if carry flag not set.

    def assembles(self, mnemonic: str) -> bool:
        return mnemonic == "LNGJUMPNC"

    def vals(
        self,
        mnemonic: str,
        parameters: Tuple[str, ...],
        origin: int,
        labels: Dict[str, int],
        loose: bool,
    ) -> List[int]:
        _checkoneparam(mnemonic, parameters)
        parameter = parameters[0]

        try:
            # First, try as an integer.
            location = getint(
                parameter,
                16,
                allow_unsigned=True,
                hint=_insnrep(mnemonic, parameters),
            )
        except InvalidInstructionException:
            # Now, try as a label.
            if parameter in labels:
                offset = str(labels[parameter])
                location = getint(
                    offset,
                    16,
                    allow_unsigned=True,
                    hint=_insnrep(mnemonic, parameters),
                )
            else:
                # Assume nothing for now, will be filled in later
                _checklabel(mnemonic, parameters, loose)
                location = 0

        return self.compile(
            origin,
            [
                "SKIPIF !CF",
                "JRI skip_longjump",
                f"LNGJUMP {location}",
                "skip_longjump:",
            ],
            hint=_insnrep(mnemonic, parameters),
        )


@instruction
class NEG(BaseMacro):
    # Twos compliment negate the A register.

    def assembles(self, mnemonic: str) -> bool:
        return mnemonic == "NEG"

    def vals(
        self,
        mnemonic: str,
        parameters: Tuple[str, ...],
        origin: int,
        labels: Dict[str, int],
        loose: bool,
    ) -> List[int]:
        # Super simple, but convenient to use.
        _checkempty(mnemonic, parameters)
        return self.compile(
            origin,
            ["INV", "ADDI 1"],
            hint=_insnrep(mnemonic, parameters),
        )


@instruction
class CALL(BaseMacro):
    # Call subroutine.

    def assembles(self, mnemonic: str) -> bool:
        return mnemonic == "CALL"

    def vals(
        self,
        mnemonic: str,
        parameters: Tuple[str, ...],
        origin: int,
        labels: Dict[str, int],
        loose: bool,
    ) -> List[int]:
        _checkoneparam(mnemonic, parameters)
        parameter = parameters[0]

        # Load immediate value into PC.
        # First, try to get this as an integer.
        try:
            location = getint(
                parameter,
                16,
                allow_unsigned=True,
                hint=_insnrep(mnemonic, parameters),
            )
        except InvalidInstructionException:
            # Now, try as a label.
            if parameter in labels:
                location = getint(
                    str(labels[parameter]),
                    16,
                    allow_unsigned=True,
                    hint=_insnrep(mnemonic, parameters),
                )
            else:
                # We will fill this in later.
                _checklabel(mnemonic, parameters, loose)
                location = 0

        # Create a springboard.
        instructions = [
            "PUSHIP retloc",
            f"LNGJUMP {location}",
            "retloc:"
        ]

        # Now, assemble the springboard and return that value
        return self.compile(
            origin,
            instructions,
            hint=_insnrep(mnemonic, parameters),
        )


@instruction
class CALLRI(BaseMacro):
    # Call relative subroutine.

    def assembles(self, mnemonic: str) -> bool:
        return mnemonic == "CALLRI"

    def vals(
        self,
        mnemonic: str,
        parameters: Tuple[str, ...],
        origin: int,
        labels: Dict[str, int],
        loose: bool,
    ) -> List[int]:
        _checkoneparam(mnemonic, parameters)
        parameter = parameters[0]

        try:
            # First, try as an integer.
            location = getint(
                parameter,
                6,
                hint=_insnrep(mnemonic, parameters),
            )
            # We subtract one because the virtual position of this instruction
            # is one memory address earlier than where the actual jump
            # instruction will go.
            if location & 0b00100000:
                location -= 1
        except InvalidInstructionException:
            # Now, try as a label.
            if parameter in labels:
                absolute_location = labels[parameter]
                # Adjust backwards 2 so we can skip past our skip
                # instruction.
                relative_location = absolute_location - origin - 2
                location = getint(
                    str(relative_location),
                    6,
                    hint=_insnrep(mnemonic, parameters),
                )
            else:
                # Assume nothing for now, will be filled in later
                _checklabel(mnemonic, parameters, loose)
                location = 0

        # Create a springboard.
        instructions = [
            "PUSHIP retloc",
            f"JRI {location}",
            "retloc:"
        ]

        # Now, assemble the springboard and return that value
        return self.compile(
            origin,
            instructions,
            hint=_insnrep(mnemonic, parameters),
        )


@instruction
class ZERO(BaseMacro):
    # Zero the contents of the A register.

    def assembles(self, mnemonic: str) -> bool:
        return mnemonic == "ZERO"

    def vals(
        self,
        mnemonic: str,
        parameters: Tuple[str, ...],
        origin: int,
        labels: Dict[str, int],
        loose: bool,
    ) -> List[int]:
        _checkempty(mnemonic, parameters)
        return self.compile(
            origin,
            ["LOADI 0"],
            hint=_insnrep(mnemonic, parameters),
        )


@instruction
class PUSH(BaseMacro):
    # Decrement PC, store A/U/V/IP/SPC to PC.

    def assembles(self, mnemonic: str) -> bool:
        return mnemonic == "PUSH"

    def vals(
        self,
        mnemonic: str,
        parameters: Tuple[str, ...],
        origin: int,
        labels: Dict[str, int],
        loose: bool,
    ) -> List[int]:
        _checkoneparam(mnemonic, parameters)
        parameter = parameters[0].upper()

        if parameter == "A":
            # Super simple, but convenient to use.
            return self.compile(
                origin,
                ["DECPC", "STOREA"],
                hint=_insnrep(mnemonic, parameters),
            )
        if parameter == "U":
            # Super simple, but convenient to use.
            return self.compile(
                origin,
                ["DECPC", "STOREU"],
                hint=_insnrep(mnemonic, parameters),
            )
        if parameter == "V":
            # Super simple, but convenient to use.
            return self.compile(
                origin,
                ["DECPC", "STOREV"],
                hint=_insnrep(mnemonic, parameters),
            )
        if parameter[:2] == "IP":
            # Split the parameter by "+"
            vals = parameter.split('+', 1)
            if len(vals) == 1:
                return self.compile(
                    origin,
                    ["PUSHIP 0"],
                    hint=_insnrep(mnemonic, parameters),
                )
            else:
                return self.compile(
                    origin,
                    ["PUSHIP {vals[1].strip()}"],
                    hint=_insnrep(mnemonic, parameters),
                )
        if parameter == "SPC":
            # Super simple, but convenient to use.
            return self.compile(
                origin,
                ["PUSHSPC"],
                hint=_insnrep(mnemonic, parameters),
            )

        raise ParameterOutOfRangeException(
            f"Invalid parameter {_paramrep(parameters)} for instruction "
            + _insnrep(mnemonic, parameters)
        )


@instruction
class STOREI(BaseMacro):
    # Store immediate to PC, clobber A.

    def assembles(self, mnemonic: str) -> bool:
        return mnemonic == "STOREI"

    def vals(
        self,
        mnemonic: str,
        parameters: Tuple[str, ...],
        origin: int,
        labels: Dict[str, int],
        loose: bool,
    ) -> List[int]:
        # Super simple, but convenient to use.
        return self.compile(
            origin,
            [f"LOADI {_paramrep(parameters)}", "STOREA"],
            hint=_insnrep(mnemonic, parameters),
        )


@instruction
class PUSHI(BaseMacro):
    # Decrement PC, store immediate to PC, clobber A.

    def assembles(self, mnemonic: str) -> bool:
        return mnemonic == "PUSHI"

    def vals(
        self,
        mnemonic: str,
        parameters: Tuple[str, ...],
        origin: int,
        labels: Dict[str, int],
        loose: bool,
    ) -> List[int]:
        # Super simple, but convenient to use.
        return self.compile(
            origin,
            ["DECPC", f"LOADI {_paramrep(parameters)}", "STOREA"],
            hint=_insnrep(mnemonic, parameters),
        )


@instruction
class POP(BaseMacro):
    # Load PC to A/U/V/IP/SPC, increment PC.

    def assembles(self, mnemonic: str) -> bool:
        return mnemonic == "POP"

    def vals(
        self,
        mnemonic: str,
        parameters: Tuple[str, ...],
        origin: int,
        labels: Dict[str, int],
        loose: bool,
    ) -> List[int]:
        _checkoneparam(mnemonic, parameters)
        parameter = parameters[0].upper()

        if parameter == "A":
            # Super simple, but convenient to use.
            return self.compile(
                origin,
                ["LOADA", "INCPC"],
                hint=_insnrep(mnemonic, parameters),
            )
        if parameter == "U":
            # Super simple, but convenient to use.
            return self.compile(
                origin,
                ["LOADU", "INCPC"],
                hint=_insnrep(mnemonic, parameters),
            )
        if parameter == "V":
            # Super simple, but convenient to use.
            return self.compile(
                origin,
                ["LOADV", "INCPC"],
                hint=_insnrep(mnemonic, parameters),
            )
        if parameter == "IP":
            # Super simple, but convenient to use.
            return self.compile(
                origin,
                ["POPIP"],
                hint=_insnrep(mnemonic, parameters),
            )
        if parameter == "SPC":
            # Super simple, but convenient to use.
            return self.compile(
                origin,
                ["POPSPC"],
                hint=_insnrep(mnemonic, parameters),
            )

        raise ParameterOutOfRangeException(
            f"Invalid parameter {_paramrep(parameters)} for instruction "
            + _insnrep(mnemonic, parameters)
        )


@instruction
class LOAD(BaseMacro):
    # Load PC to A/U/V register.

    def assembles(self, mnemonic: str) -> bool:
        return mnemonic == "LOAD"

    def vals(
        self,
        mnemonic: str,
        parameters: Tuple[str, ...],
        origin: int,
        labels: Dict[str, int],
        loose: bool,
    ) -> List[int]:
        _checkoneparam(mnemonic, parameters)
        parameter = parameters[0].upper()

        if parameter == "A":
            # Super simple, but convenient to use.
            return self.compile(
                origin,
                ["LOADA"],
                hint=_insnrep(mnemonic, parameters),
            )
        if parameter == "U":
            # Super simple, but convenient to use.
            return self.compile(
                origin,
                ["LOADU"],
                hint=_insnrep(mnemonic, parameters),
            )
        if parameter == "V":
            # Super simple, but convenient to use.
            return self.compile(
                origin,
                ["LOADV"],
                hint=_insnrep(mnemonic, parameters),
            )

        raise ParameterOutOfRangeException(
            f"Invalid parameter {_paramrep(parameters)} for instruction "
            + _insnrep(mnemonic, parameters)
        )


@instruction
class STORE(BaseMacro):
    # Store A/U/V register to PC.

    def assembles(self, mnemonic: str) -> bool:
        return mnemonic == "STORE"

    def vals(
        self,
        mnemonic: str,
        parameters: Tuple[str, ...],
        origin: int,
        labels: Dict[str, int],
        loose: bool,
    ) -> List[int]:
        _checkoneparam(mnemonic, parameters)
        parameter = parameters[0].upper()

        if parameter == "A":
            # Super simple, but convenient to use.
            return self.compile(
                origin,
                ["STOREA"],
                hint=_insnrep(mnemonic, parameters),
            )
        if parameter == "U":
            # Super simple, but convenient to use.
            return self.compile(
                origin,
                ["STOREU"],
                hint=_insnrep(mnemonic, parameters),
            )
        if parameter == "V":
            # Super simple, but convenient to use.
            return self.compile(
                origin,
                ["STOREV"],
                hint=_insnrep(mnemonic, parameters),
            )

        raise ParameterOutOfRangeException(
            f"Invalid parameter {_paramrep(parameters)} for instruction "
            + _insnrep(mnemonic, parameters)
        )


@instruction
class SWAP(BaseMacro):
    # Swap contents of A/U/V or PC/SPC registers.

    def assembles(self, mnemonic: str) -> bool:
        return mnemonic == "SWAP"

    def vals(
        self,
        mnemonic: str,
        parameters: Tuple[str, ...],
        origin: int,
        labels: Dict[str, int],
        loose: bool,
    ) -> List[int]:
        _checktwoparams(mnemonic, parameters)
        reg1 = parameters[0].upper()
        reg2 = parameters[1].upper()

        if (
            (reg1 == "A" and reg2 == "U") or
            (reg2 == "A" and reg1 == "U")
        ):
            # Super simple, but convenient to use.
            return self.compile(
                origin,
                ["SWAPAU"],
                hint=_insnrep(mnemonic, parameters),
            )
        if (
            (reg1 == "A" and reg2 == "V") or
            (reg2 == "A" and reg1 == "V")
        ):
            # Super simple, but convenient to use.
            return self.compile(
                origin,
                ["SWAPAV"],
                hint=_insnrep(mnemonic, parameters),
            )
        if (
            (reg1 == "U" and reg2 == "V") or
            (reg2 == "U" and reg1 == "V")
        ):
            # Super simple, but convenient to use.
            return self.compile(
                origin,
                ["SWAPUV"],
                hint=_insnrep(mnemonic, parameters),
            )
        if (
            (reg1 == "PC" and reg2 == "SPC") or
            (reg2 == "PC" and reg1 == "SPC")
        ):
            # Super simple, but convenient to use.
            return self.compile(
                origin,
                ["SWAPPC"],
                hint=_insnrep(mnemonic, parameters),
            )

        raise ParameterOutOfRangeException(
            f"Invalid parameters {_paramrep(parameters)} for instruction "
            + _insnrep(mnemonic, parameters)
        )


@instruction
class MOV(BaseMacro):
    # Move contents of A/U/V/P/C register to appropriate destination register.

    def assembles(self, mnemonic: str) -> bool:
        return mnemonic == "MOV"

    def vals(
        self,
        mnemonic: str,
        parameters: Tuple[str, ...],
        origin: int,
        labels: Dict[str, int],
        loose: bool,
    ) -> List[int]:
        _checktwoparams(mnemonic, parameters)
        reg1 = parameters[0].upper()
        reg2 = parameters[1].upper()

        if reg1 == "A" and reg2 == "P":
            # Super simple, but convenient to use.
            return self.compile(
                origin,
                ["ATOP"],
                hint=_insnrep(mnemonic, parameters),
            )
        if reg1 == "A" and reg2 == "C":
            # Super simple, but convenient to use.
            return self.compile(
                origin,
                ["ATOC"],
                hint=_insnrep(mnemonic, parameters),
            )
        if reg1 == "P" and reg2 == "A":
            # Super simple, but convenient to use.
            return self.compile(
                origin,
                ["PTOA"],
                hint=_insnrep(mnemonic, parameters),
            )
        if reg1 == "C" and reg2 == "A":
            # Super simple, but convenient to use.
            return self.compile(
                origin,
                ["CTOA"],
                hint=_insnrep(mnemonic, parameters),
            )
        if reg1 == "A" and reg2 == "U":
            # Super simple, but convenient to use.
            return self.compile(
                origin,
                ["ATOU"],
                hint=_insnrep(mnemonic, parameters),
            )
        if reg1 == "A" and reg2 == "V":
            # Super simple, but convenient to use.
            return self.compile(
                origin,
                ["ATOV"],
                hint=_insnrep(mnemonic, parameters),
            )
        if reg1 == "U" and reg2 == "A":
            # Super simple, but convenient to use.
            return self.compile(
                origin,
                ["UTOA"],
                hint=_insnrep(mnemonic, parameters),
            )
        if reg1 == "V" and reg2 == "A":
            # Super simple, but convenient to use.
            return self.compile(
                origin,
                ["VTOA"],
                hint=_insnrep(mnemonic, parameters),
            )

        raise ParameterOutOfRangeException(
            f"Invalid parameters {_paramrep(parameters)} for instruction "
            + _insnrep(mnemonic, parameters)
        )


class ControlSignals:

    ALU_SRC_A = 1
    ALU_SRC_PC = 2
    ALU_SRC_IP = 3

    CARRY_SET = 1
    CARRY_FROM_FLAGS = 2
    CARRY_CLEAR = 3

    ADDRESS_SRC_PC = 0
    ADDRESS_SRC_IP = 1

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
        imm_6_output: Optional[bool] = None,
        # 4 bits sign-extended to 8, output on low 8 bits of the bus
        imm_4_output: Optional[bool] = None,
        # 8 bits, output on low 8 bits of the bus
        a_output: Optional[bool] = None,
        # 8 bits, output on top 8 bits of the bus
        a_high_output: Optional[bool] = None,
        # 8 bits, output on low 8 bits of the bus
        d_output: Optional[bool] = None,
        # 8 bits, output on top 8 bits of the bus
        d_high_output: Optional[bool] = None,
        # 8 bits, output on low 8 bits of the bus
        u_output: Optional[bool] = None,
        # 8 bits, output on low 8 bits of the bus
        v_output: Optional[bool] = None,
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
        u_input: Optional[bool] = None,
        v_input: Optional[bool] = None,
        sram_input: Optional[bool] = None,
        flags_input: Optional[bool] = None,

        # Address bus assertion signals

        address_src: Optional[int] = None,

        # Flags control signals

        pc_swap: Optional[bool] = None,
    ) -> None:
        self.alu_src = alu_src if alu_src is not None else self.ALU_SRC_IP
        self.carry = carry if carry is not None else self.CARRY_CLEAR
        self.alu_op = alu_op if alu_op is not None else ALU.OPERATION_NULL
        self.address_src = (
            address_src if address_src is not None else self.ADDRESS_SRC_IP
        )
        self.ip_input = ip_input or False
        self.alu_output = alu_output or False
        self.alu_low_output = alu_low_output or False
        self.imm_6_output = imm_6_output or False
        self.imm_4_output = imm_4_output or False
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
        self.u_output = u_output or False
        self.v_output = v_output or False
        self.u_input = u_input or False
        self.v_input = v_input or False


def InstructionLoadControlSignals() -> ControlSignals:
    return ControlSignals(
        address_src=ControlSignals.ADDRESS_SRC_IP,
        sram_output=True,
        ir_input=True,
    )


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
    # No operation, output indeterminate.
    OPERATION_NULL = 7

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
            return ((self.a << 1) & 0xFF) | (0x01 if self.carryin else 0)
        if self.op == self.OPERATION_SHR:
            return ((self.a >> 1) & 0xFF) | (0x80 if self.carryin else 0)
        if self.op == self.OPERATION_INV:
            return (~self.a) & 0xFF
        if self.op == self.OPERATION_AND:
            return (self.a & self.b) & 0xFF
        if self.op == self.OPERATION_OR:
            return (self.a | self.b) & 0xFF
        if self.op == self.OPERATION_XOR:
            return (self.a ^ self.b) & 0xFF
        if self.op == self.OPERATION_NULL:
            return 0xFF
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
            self.OPERATION_XOR,
            self.OPERATION_NULL,
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
        if self.op == self.OPERATION_NULL:
            return False
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
        self.u = 0
        self.v = 0

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
    def pc(self) -> int:
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
        return p + c

    @property
    def spc(self) -> int:
        pc = self.flags & self.FLAGS_PC != 0

        if self.last_instruction.pc_swap:
            pc = not pc
        sp = self.p[0 if pc else 1]
        sp = (sp << 8) & 0xFF00
        sc = self.c[0 if pc else 1]
        sc = sc & 0xFF
        return sp + sc

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
        u = self.data if self.last_instruction.u_input else self.u
        u_dec = bintoint(u & 0xFF)
        v = self.data if self.last_instruction.v_input else self.v
        v_dec = bintoint(v & 0xFF)

        print("\n".join([
            f"IP:    {hexstr(ip, 4)}",
            f"PC:    {hexstr(pandc, 4)}",
            f"SPC:   {hexstr(spandsc, 4)}",
            f"A:     {hexstr(a, 2)} (unsigned: {a}, signed: {a_dec})",
            f"U:     {hexstr(u, 2)} (unsigned: {u}, signed: {u_dec})",
            f"V:     {hexstr(v, 2)} (unsigned: {v}, signed: {v_dec})",
            f"Flags: {hexstr(flags, 3)} (cf: {cf}, zf: {zf}, pc: {pc})",
            f"NextI: {disassemble(self.ram[ip])} ({binstr(self.ram[ip], 8)})",
        ]))

    @property
    def mnemonic(self) -> str:
        ip = self.data if self.last_instruction.ip_input else self.ip
        return disassemble(self.ram[ip])

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
        instructions = [
            # Fetch instruction from RAM microcode.
            InstructionLoadControlSignals(),
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
            if self.last_instruction.u_input:
                self.u = self.data & 0xFF
            if self.last_instruction.v_input:
                self.v = self.data & 0xFF
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
            if instruction.u_output:
                self.data = (self.data & 0xFF00) + (self.u & 0xFF)
            if instruction.v_output:
                self.data = (self.data & 0xFF00) + (self.v & 0xFF)
            if instruction.alu_low_output:
                self.data = (
                    (self.data & 0xFF00) +
                    ((self.alu.result >> 8) & 0xFF)
                )
            if instruction.imm_4_output:
                self.data = (
                    (self.data & 0xFF00) +
                    (sign_extend(self.ir, 3) & 0xFF)
                )
            if instruction.imm_6_output:
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
