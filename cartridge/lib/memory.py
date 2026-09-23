# Given a 16-bit address, executes the function at that address. Note that
# the function should take no arguments and return void for this to successfully
# execute and return.
def memory_exec(loc: uint16) -> extern[void]: ...
