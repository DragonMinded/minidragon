from serial import serial_send


def _calcPrecision(precision: uint8) -> uint32:
    """
    We can calculate this by just multiplying a starting value of 1 by 10 exactly
    precision times. But, we unroll this to avoid loops. We can unroll this further
    in assembly by using an offset if we wanted to.
    """

    if precision == 1:
        return 10
    if precision == 2:
        return 100
    if precision == 3:
        return 1000
    if precision == 4:
        return 10000
    if precision == 5:
        return 100000
    if precision == 6:
        return 1000000
    if precision == 7:
        return 10000000
    if precision == 8:
        return 100000000
    return 1000000000


def strtofixed(val: const[str], precision: uint8, fracbits: uint8 = 8) -> int32:
    """
    Given a string value such as 1.2345 or -3.567, a precision which is the number
    of digits after the decimal place to respect, and an optinal fracbits which is
    the number of fractional bits in the returned fixed point integer, perform the
    conversion from the string to the fixed point integer.

    Note that this only supports precision from 1 to 9 digits.
    """

    # First, remember if it's negative.
    negative: const[bool] = val[0] == "-"

    # Second, construct a "multiplied" number by the precision.
    hasDecimal: bool = False
    actualPrecision: uint8 = 0
    noDecVal: str[32] = ""

    pos: uint8
    for pos in range(1 if negative else 0, len(val)):
        if val[pos] == ".":
            if hasDecimal:
                # This has two decimals, cut it off.
                break
            hasDecimal = True
        else:
            noDecVal += val[pos]
            if hasDecimal:
                actualPrecision += 1
                if actualPrecision == precision:
                    break

    while actualPrecision != precision:
        noDecVal += "0"
        actualPrecision += 1

    # Convert to a number, and then perform the arithmetic to make it a fixed point version.
    converted: uint32 = int(noDecVal)
    converted <<= fracbits
    converted /= _calcPrecision(precision)

    # Now, add the negative.
    return -converted if negative else converted


def fixedtostr(val: int32, precision: uint8, fracbits: uint8 = 8) -> str[32]:
    """
    Given an integer that represents a fixed point integer, convert that integer to a
    string using the precision requested. Optionally, provide a different fracbits
    if your integer doesn't use the default fractional bits.
    """

    negative: const[bool] = val < 0
    absVal: int32 = -val if negative else val

    # We also round by 0.5 here to get better display. That round by 0.5 is done
    # by adding a number that is the same as the fracbits shifted over right 1.
    absVal *= _calcPrecision(precision)
    absVal += (1 << (fracbits - 1))
    absVal >>= fracbits

    valStr: str[32] = str(absVal)
    valLen: uint8 = len(valStr)
    decLoc: uint8 = valLen - precision

    if negative:
        return "-" + valStr[:decLoc] + "." + valStr[decLoc:]
    else:
        return valStr[:decLoc] + "." + valStr[decLoc:]
