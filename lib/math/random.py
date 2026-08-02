# Our XORShift seed and state.
__prng_seed: uint16 = 1


def random_step() -> void:
    """
    Ticks up the random seed by 1

    Call this inside any function where you believe the number of times
    this gets called varies based on input to the computer. Automatically
    called for you in serial read operations to take advantage of random
    behavior of keyboard input.
    """

    global __prng_seed
    __prng_seed += 1


def random() -> uint16:
    """
    Returns a pseudorandom 16 bit integer
    """

    global __prng_seed

    twist: uint16 = __prng_seed
    twist ^= twist << 7
    twist ^= twist >> 9
    twist ^= twist << 13

    __prng_seed = twist
    return __prng_seed


def random_int(minimum: uint16, maximum: uint16) -> uint16:
    """
    Returns a random integer within the specified range inclusive
    """

    val: uint16 = random()
    val -= minimum
    return val % ((maximum - minimum) + 1)


def random_choice(vals: const[str]) -> char:
    """
    Returns a random character from within the string of choices
    """

    maximum: uint16 = len(vals)
    val: uint16 = random()
    val %= maximum

    return vals[val]
