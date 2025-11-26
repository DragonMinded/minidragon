# Given a string value such as 1.2345 or -3.56 and an optinal fracbits which is
# the number of fractional bits in the returned fixed point integer, perform the
# conversion from the string to the fixed point integer.
# 
# Note that this only supports up to 5 digits after the decimal place.
def strtofixed(val: const[str], fracbits: uint8 = 8) -> extern[int32]: ...


# Given an integer that represents a fixed point integer, convert that integer to a
# string using the precision requested. Optionally, provide a different fracbits
# if your integer doesn't use the default fractional bits.
# 
# Note that this only supports a precision value of 0 through 5.
def fixedtostr(val: int32, precision: uint8, fracbits: uint8 = 8) -> extern[str]: ...
