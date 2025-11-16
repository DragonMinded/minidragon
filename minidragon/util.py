import os
import traceback

from colorama import Fore, Style
from ast import literal_eval
from typing import Optional, Set

from .exception import InvalidParameterException, ParameterOutOfRangeException


def signextend(val: int, msb: int) -> int:
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


def highlight(val: str, key: str, changes: Set[str]) -> str:
    if key not in changes:
        return val

    return f"{Fore.RED}{val}{Style.RESET_ALL}"


def hexstr(num: int, digits: int) -> str:
    val = hex(num)[2:]
    while len(val) < digits:
        val = "0" + val
    return val


def hexval(num: int, digits: int) -> str:
    return "0x" + hexstr(num, digits)


def binstr(num: int, digits: int) -> str:
    val = bin(num)[2:]
    while len(val) < digits:
        val = "0" + val
    return val


def bintoint(binary: int) -> int:
    return binary if binary < 0x80 else -(((~binary) & 0xFF) + 1)


def sanitize(line: str) -> str:
    if not line:
        return ""
    if ";" in line:
        # Need to be mindful of quotes.
        nocomment: str = ""
        quote: str = ""

        for ch in line:
            if ch == quote:
                nocomment += ch
                quote = ""
            elif ch in {"'", '"'}:
                if not quote:
                    quote = ch
                nocomment += ch
            elif ch == ";":
                if not quote:
                    break
                nocomment += ch
            else:
                nocomment += ch

        line = nocomment
    line = line.strip()
    return line


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

    raise InvalidParameterException(
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

    # Return it masked.
    return int(intval & ((2 ** bits) - 1))


def comment_source(extra: Optional[str] = None) -> str:
    if not os.environ.get("INSERT_CALLER_COMMENTS"):
        return ""

    lines = [line for line in traceback.format_stack() if line.strip().startswith("File")]

    # We should be the first line, so our caller is the second.
    relevant = lines[-2]
    relevant, _ = relevant.split(os.linesep, 1)
    _, details = relevant.split(", ", 1)

    if extra:
        details += f" ({extra})"

    return f"  ; {details}"
