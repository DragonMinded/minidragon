def _calcPrecision(precision: uint8) -> uint32:
    """
    We can calculate this by just multiplying a starting value of 1 by 10 exactly
    precision times. But, we unroll this to avoid loops. We can unroll this further
    in assembly by using an offset if we wanted to.
    """

    # We only bother to support up to 5 digits of precision because any more and we
    # either can't represent the number when converting to decimal due to running
    # out of space to multiply out, or if we have enough space to multiply, that
    # means the fractional part is too small to represent a number accurately to
    # that precision.
    if precision == 1:
        return 10
    if precision == 2:
        return 100
    if precision == 3:
        return 1000
    if precision == 4:
        return 10000
    return 100000


def strtofixed(val: const[str], fracbits: uint8 = 8) -> int32:
    """
    Given a string value such as 1.2345 or -3.56 and an optinal fracbits which is
    the number of fractional bits in the returned fixed point integer, perform the
    conversion from the string to the fixed point integer.

    Note that this only supports up to 5 digits after the decimal place.
    """

    # First, remember if it's negative.
    negative: const[bool] = val[0] == "-"

    # Second, construct a "multiplied" number by the precision.
    hasDecimal: bool = False
    actualPrecision: uint8 = 0
    noDecVal: str[32] = ""
    decVal: str[32] = ""

    pos: uint8
    for pos in range(1 if negative else 0, len(val)):
        if val[pos] == ".":
            if hasDecimal:
                # This has two decimals, cut it off.
                break
            hasDecimal = True
        else:
            if hasDecimal:
                decVal += val[pos]
                actualPrecision += 1
                if actualPrecision == 5:
                    break
            else:
                noDecVal += val[pos]

    # Fast path, convert and shift.
    converted: uint32 = int(noDecVal)
    converted <<= fracbits

    if hasDecimal:
        # Convert to a number, and then perform the arithmetic to make it a fixed point version.
        fraction: uint32 = int(decVal)
        fraction <<= fracbits
        fraction /= _calcPrecision(actualPrecision)
        converted |= fraction

    # Now, add the negative.
    return -converted if negative else converted


def fixedtostr(val: int32, precision: uint8, fracbits: uint8 = 8) -> str[16]:
    """
    Given an integer that represents a fixed point integer, convert that integer to a
    string using the precision requested. Optionally, provide a different fracbits
    if your integer doesn't use the default fractional bits.

    Note that this only supports a precision value of 0 through 5.
    """

    fracmask: uint32 = ~(0xFFFFFFFF << fracbits)
    negative: const[bool] = val < 0
    absVal: int32 = -val if negative else val
    
    # First, take care of any fractional bits, and then track whether we need to round.
    fracStr: str[9] = ""
    roundUp: bool = False
    if precision:
        fracVal: uint32 = absVal & fracmask
        fracVal *= _calcPrecision(precision)

        # We also round by 0.5 here to get better display. That round by 0.5 is done
        # by adding a number that is the same as the fracbits shifted over right 1.
        fracVal += (1 << (fracbits - 1))
        fracVal >>= fracbits

        tempFracStr: str[9] = str(fracVal)
        tempFracStrLen: uint8 = len(tempFracStr)

        if tempFracStrLen < precision:
            # We need to add zeros in front since this needs to be zero-padded.
            padAmount: uint8 = precision - tempFracStrLen
            while padAmount:
                fracStr += "0"
                padAmount -= 1
            fracStr += tempFracStr
        elif tempFracStrLen > precision:
            # We carried over into the 1's digit, need to round up.
            roundUp = True
            fracStr += tempFracStr[(tempFracStrLen - precision):]
        else:
            fracStr += tempFracStr
    else:
        # Need to round here for no-precision display.
        absVal += (1 << (fracbits - 1))

    # Now, take care of the decimal bits.
    decStr: str[16] = ""
    if negative:
        decStr += "-"

    absVal >>= fracbits
    if roundUp:
        absVal += 1

    decStr += str(absVal)

    if precision:
        decStr += "."
        decStr += fracStr

    return decStr
