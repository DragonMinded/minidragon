# Ticks up the random seed by 1
#
# Call this inside any function where you believe the number of times
# this gets called varies based on input to the computer. Automatically
# called for you in serial read operations to take advantage of random
# behavior of keyboard input.
def random_step() -> extern[void]: ...


# Returns a pseudorandom 16 bit integer
def random() -> extern[uint16]: ...


# Returns a random integer within the specified range inclusive
def random_int(minimum: uint16, maximum: uint16) -> extern[uint16]: ...


# Returns a random character from within the string of choices
def random_choice(vals: const[str]) -> extern[char]: ...
